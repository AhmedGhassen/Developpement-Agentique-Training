"""
Tests pour l'API Todo.
"""

import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def get_items(client, path="/api/todos"):
    """
    Helper : GET /api/todos renvoie désormais une enveloppe paginée
    {"items": [...], "total": N, "next_offset": ...} (TODO-150).
    Ce helper vérifie le 200 et renvoie la liste `items`.
    """
    res = client.get(path)
    assert res.status_code == 200
    return res.get_json()["items"]


def test_get_all_todos(client):
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert len(res.get_json()["items"]) >= 1


def test_create_todo(client):
    res = client.post("/api/todos", json={"title": "Nouvelle tâche de test"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["title"] == "Nouvelle tâche de test"
    assert body["completed"] is False


def test_create_todo_without_title_fails(client):
    res = client.post("/api/todos", json={})
    assert res.status_code == 400


def test_filter_completed_true_returns_only_completed(client):
    """
    GET /api/todos?completed=true doit renvoyer UNIQUEMENT
    les tâches terminées (completed == True).
    """
    res = client.get("/api/todos?completed=true")
    assert res.status_code == 200
    body = res.get_json()["items"]

    assert len(body) > 0, "Le filtre ne doit pas renvoyer une liste vide ici"
    for todo in body:
        assert todo["completed"] is True, (
            f"Tâche '{todo['title']}' renvoyée par ?completed=true "
            f"mais completed={todo['completed']}"
        )


def test_filter_completed_false_returns_only_incomplete(client):
    res = client.get("/api/todos?completed=false")
    assert res.status_code == 200
    body = res.get_json()["items"]

    for todo in body:
        assert todo["completed"] is False, (
            f"Tâche '{todo['title']}' renvoyée par ?completed=false "
            f"mais completed={todo['completed']}"
        )


def test_toggle_todo(client):
    create_res = client.post("/api/todos", json={"title": "À cocher"})
    todo_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/api/todos/{todo_id}", json={"completed": True})
    assert patch_res.status_code == 200
    assert patch_res.get_json()["completed"] is True


def test_delete_todo(client):
    create_res = client.post("/api/todos", json={"title": "À supprimer"})
    todo_id = create_res.get_json()["id"]

    delete_res = client.delete(f"/api/todos/{todo_id}")
    assert delete_res.status_code == 204

    ids = [t["id"] for t in get_items(client)]
    assert todo_id not in ids


# ---------------------------------------------------------------------------
# Tests fonctionnalité "catégories"
# ---------------------------------------------------------------------------

CATEGORIES_ATTENDUES = ["autre", "travail", "perso", "urgent"]


def test_toutes_les_todos_ont_une_categorie_valide(client):
    """GET /api/todos : chaque todo expose un champ `category` autorisé."""
    body = get_items(client)
    assert len(body) >= 1
    for todo in body:
        assert "category" in todo, f"Todo sans champ category : {todo}"
        assert todo["category"] in CATEGORIES_ATTENDUES, (
            f"Catégorie inattendue '{todo['category']}' pour '{todo['title']}'"
        )


def test_get_categories_renvoie_la_liste_autorisee(client):
    """GET /api/categories : 200 + tableau JSON nu des 4 catégories."""
    res = client.get("/api/categories")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    for cat in CATEGORIES_ATTENDUES:
        assert cat in body, f"Catégorie '{cat}' absente de {body}"


def test_post_sans_categorie_utilise_autre_par_defaut(client):
    """POST sans `category` → 201 et category == 'autre'."""
    res = client.post("/api/todos", json={"title": "Todo sans catégorie"})
    assert res.status_code == 201
    assert res.get_json()["category"] == "autre"


def test_post_avec_categorie_valide(client):
    """POST avec `category` valide → 201 et catégorie reflétée."""
    res = client.post(
        "/api/todos", json={"title": "Todo travail", "category": "travail"}
    )
    assert res.status_code == 201
    assert res.get_json()["category"] == "travail"


def test_post_avec_categorie_invalide_renvoie_400(client):
    """POST avec `category` inconnue → 400."""
    res = client.post(
        "/api/todos", json={"title": "Todo cassée", "category": "bidon"}
    )
    assert res.status_code == 400


def test_patch_change_la_categorie_et_persiste(client):
    """PATCH `category` → 200, nouvelle valeur, et persistance vérifiée par re-GET."""
    create_res = client.post(
        "/api/todos", json={"title": "Todo à recatégoriser", "category": "autre"}
    )
    todo_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/api/todos/{todo_id}", json={"category": "urgent"})
    assert patch_res.status_code == 200
    assert patch_res.get_json()["category"] == "urgent"

    todo = next(t for t in get_items(client) if t["id"] == todo_id)
    assert todo["category"] == "urgent"


def test_patch_avec_categorie_invalide_renvoie_400(client):
    """PATCH `category` inconnue → 400."""
    create_res = client.post(
        "/api/todos", json={"title": "Todo patch invalide", "category": "perso"}
    )
    todo_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/api/todos/{todo_id}", json={"category": "bidon"})
    assert patch_res.status_code == 400


def test_filtre_par_categorie_travail(client):
    """GET /api/todos?category=travail : uniquement des todos 'travail', au moins une (seed)."""
    body = get_items(client, "/api/todos?category=travail")
    assert len(body) >= 1, "Le seed contient au moins une todo 'travail'"
    for todo in body:
        assert todo["category"] == "travail"


def test_filtre_par_categorie_inconnue_renvoie_liste_vide(client):
    """GET /api/todos?category=<inconnue> → 200 + []."""
    res = client.get("/api/todos?category=categorie-qui-nexiste-pas")
    assert res.status_code == 200
    assert res.get_json()["items"] == []
    assert res.get_json()["total"] == 0


def test_integration_categorie_combinee_avec_completed(client):
    """
    Bout en bout : création d'une todo 'perso', passage en completed via PATCH,
    puis vérification du filtre combiné ?category=perso&completed=...
    Objectif : prouver que `category` se combine correctement avec `completed`.
    """
    create_res = client.post(
        "/api/todos",
        json={"title": "Todo perso intégration", "category": "perso"},
    )
    assert create_res.status_code == 201
    todo_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/api/todos/{todo_id}", json={"completed": True})
    assert patch_res.status_code == 200
    assert patch_res.get_json()["completed"] is True

    # completed=true => notre todo terminée 'perso' apparaît, et rien d'autre catégorie
    body_true = get_items(client, "/api/todos?category=perso&completed=true")
    assert all(t["category"] == "perso" and t["completed"] is True for t in body_true)
    assert any(t["id"] == todo_id for t in body_true), (
        "La todo terminée 'perso' doit apparaître sous ?category=perso&completed=true"
    )

    # completed=false => tâches 'perso' non terminées, donc pas la nôtre
    body_false = get_items(client, "/api/todos?category=perso&completed=false")
    assert all(t["category"] == "perso" and t["completed"] is False for t in body_false)
    assert all(t["id"] != todo_id for t in body_false), (
        "La todo terminée 'perso' ne doit PAS apparaître sous ?completed=false"
    )


def test_stats_structure_et_coherence(client):
    """GET /api/stats : 200, 4 clés, et total == completed + pending."""
    res = client.get("/api/stats")
    assert res.status_code == 200
    body = res.get_json()

    assert set(body.keys()) == {"total", "completed", "pending", "completion_rate"}
    assert body["total"] == body["completed"] + body["pending"]
    assert body["total"] >= 4  # le seed contient 4 todos


def test_stats_completion_rate_arrondi_une_decimale(client):
    """completion_rate = 100 * completed / total, arrondi à une décimale."""
    res = client.get("/api/stats")
    body = res.get_json()

    attendu = round(body["completed"] / body["total"] * 100, 1)
    assert body["completion_rate"] == attendu
    # arrondi à une décimale : au plus un chiffre après la virgule
    assert round(body["completion_rate"], 1) == body["completion_rate"]


def test_stats_evolue_apres_creation_et_completion(client):
    """Après ajout d'une todo puis passage en completed, les compteurs suivent."""
    avant = client.get("/api/stats").get_json()

    create_res = client.post("/api/todos", json={"title": "Todo stats"})
    todo_id = create_res.get_json()["id"]

    apres_creation = client.get("/api/stats").get_json()
    assert apres_creation["total"] == avant["total"] + 1
    assert apres_creation["pending"] == avant["pending"] + 1

    client.patch(f"/api/todos/{todo_id}", json={"completed": True})

    apres_completion = client.get("/api/stats").get_json()
    assert apres_completion["completed"] == apres_creation["completed"] + 1
    assert apres_completion["pending"] == apres_creation["pending"] - 1


def test_regression_post_puis_get_sans_param(client):
    """Régression : après POST, GET sans param renvoie la todo créée ET tout le seed."""
    res = client.post(
        "/api/todos", json={"title": "Todo régression", "category": "travail"}
    )
    assert res.status_code == 201
    nouvel_id = res.get_json()["id"]

    items = get_items(client)
    titres = [t["title"] for t in items]
    ids = [t["id"] for t in items]

    assert nouvel_id in ids
    for titre_seed in [
        "Préparer le workshop",
        "Relire le ticket JIRA-142",
        "Configurer Claude Code",
        "Boire un café",
    ]:
        assert titre_seed in titres, f"Todo seed disparue : {titre_seed}"


# ---------------------------------------------------------------------------
# Tests fonctionnalité "priority" (TODO-142)
# ---------------------------------------------------------------------------

PRIORITES_ATTENDUES = ["low", "normal", "high"]


def test_toutes_les_todos_ont_une_priorite_valide(client):
    """GET /api/todos : chaque todo expose un champ `priority` autorisé."""
    body = get_items(client)
    assert len(body) >= 1
    for todo in body:
        assert "priority" in todo, f"Todo sans champ priority : {todo}"
        assert todo["priority"] in PRIORITES_ATTENDUES, (
            f"Priorité inattendue '{todo['priority']}' pour '{todo['title']}'"
        )


def test_seed_a_priorite_normal_par_defaut(client):
    """Les tâches présentes au démarrage ont priority == 'normal'."""
    titres = [t["title"] for t in get_items(client, "/api/todos?priority=normal")]
    for titre_seed in [
        "Préparer le workshop",
        "Relire le ticket JIRA-142",
        "Configurer Claude Code",
        "Boire un café",
    ]:
        assert titre_seed in titres, f"Todo seed sans priorité 'normal' : {titre_seed}"


def test_post_sans_priorite_cree_une_tache_normal(client):
    """POST sans `priority` → 201 et priority == 'normal'."""
    res = client.post("/api/todos", json={"title": "Todo sans priorité"})
    assert res.status_code == 201
    assert res.get_json()["priority"] == "normal"


def test_post_avec_priorite_valide(client):
    """POST avec `priority` valide → 201 et priorité reflétée."""
    res = client.post("/api/todos", json={"title": "Todo importante", "priority": "high"})
    assert res.status_code == 201
    assert res.get_json()["priority"] == "high"


def test_post_avec_priorite_invalide_renvoie_400(client):
    """POST avec `priority` inconnue → 400 + corps exact."""
    res = client.post("/api/todos", json={"title": "Todo cassée", "priority": "urgent"})
    assert res.status_code == 400
    assert res.get_json() == {"error": "Priorité invalide"}


def test_patch_change_la_priorite_et_persiste(client):
    """PATCH `priority` → 200, nouvelle valeur, persistance vérifiée par re-GET."""
    create_res = client.post("/api/todos", json={"title": "Todo à reprioriser"})
    todo_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/api/todos/{todo_id}", json={"priority": "low"})
    assert patch_res.status_code == 200
    assert patch_res.get_json()["priority"] == "low"

    todo = next(t for t in get_items(client) if t["id"] == todo_id)
    assert todo["priority"] == "low"


def test_patch_avec_priorite_invalide_renvoie_400(client):
    """PATCH `priority` inconnue → 400 + corps exact, valeur inchangée."""
    create_res = client.post("/api/todos", json={"title": "Todo patch invalide", "priority": "high"})
    todo_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/api/todos/{todo_id}", json={"priority": "bidon"})
    assert patch_res.status_code == 400
    assert patch_res.get_json() == {"error": "Priorité invalide"}

    todo = next(t for t in get_items(client) if t["id"] == todo_id)
    assert todo["priority"] == "high"


def test_filtre_par_priorite_high(client):
    """GET /api/todos?priority=high : uniquement des todos 'high'."""
    client.post("/api/todos", json={"title": "Urgente A", "priority": "high"})
    body = get_items(client, "/api/todos?priority=high")
    assert len(body) >= 1
    for todo in body:
        assert todo["priority"] == "high"


def test_filtre_par_priorite_inconnue_renvoie_liste_vide(client):
    """GET /api/todos?priority=<inconnue> → 200 + []."""
    res = client.get("/api/todos?priority=priorite-qui-nexiste-pas")
    assert res.status_code == 200
    assert res.get_json()["items"] == []


def test_cumul_filtres_priority_et_completed(client):
    """
    GET /api/todos?priority=high&completed=false renvoie l'intersection :
    tâches 'high' ET non terminées, dans les deux sens.
    """
    # non terminée + high → doit apparaître
    r1 = client.post("/api/todos", json={"title": "High en cours", "priority": "high"})
    id_pending_high = r1.get_json()["id"]

    # terminée + high → ne doit PAS apparaître sous completed=false
    r2 = client.post("/api/todos", json={"title": "High terminée", "priority": "high"})
    id_done_high = r2.get_json()["id"]
    client.patch(f"/api/todos/{id_done_high}", json={"completed": True})

    # non terminée + low → ne doit PAS apparaître sous priority=high
    r3 = client.post("/api/todos", json={"title": "Low en cours", "priority": "low"})
    id_pending_low = r3.get_json()["id"]

    body = get_items(client, "/api/todos?priority=high&completed=false")

    for todo in body:
        assert todo["priority"] == "high" and todo["completed"] is False

    ids = [t["id"] for t in body]
    assert id_pending_high in ids
    assert id_done_high not in ids
    assert id_pending_low not in ids


# ---------------------------------------------------------------------------
# Tests fonctionnalité "pagination" (TODO-150)
# ---------------------------------------------------------------------------


def test_pagination_enveloppe_par_defaut(client):
    """
    GET /api/todos sans param : enveloppe {items, total, next_offset}.
    Par défaut limit=50 > nombre de tâches du seed → tout tient sur une page
    et next_offset vaut null.
    """
    res = client.get("/api/todos")
    assert res.status_code == 200
    body = res.get_json()

    assert set(body.keys()) == {"items", "total", "next_offset"}
    assert isinstance(body["items"], list)
    assert body["total"] == len(body["items"])
    assert body["total"] >= 4  # seed
    assert body["next_offset"] is None


def test_pagination_limit_2(client):
    """?limit=2 → au plus 2 items, total inchangé, next_offset == 2."""
    total_reel = client.get("/api/todos").get_json()["total"]
    assert total_reel > 2, "Ce test suppose plus de 2 tâches (seed = 4)"

    res = client.get("/api/todos?limit=2")
    assert res.status_code == 200
    body = res.get_json()

    assert len(body["items"]) == 2
    assert body["total"] == total_reel
    assert body["next_offset"] == 2


def test_pagination_limit_201_renvoie_400(client):
    """?limit=201 dépasse le max (200) → 400."""
    res = client.get("/api/todos?limit=201")
    assert res.status_code == 400


def test_pagination_limit_200_est_accepte(client):
    """?limit=200 est la borne haute autorisée → 200."""
    res = client.get("/api/todos?limit=200")
    assert res.status_code == 200


def test_pagination_offset_negatif_renvoie_400(client):
    """?offset=-1 → 400."""
    res = client.get("/api/todos?offset=-1")
    assert res.status_code == 400


def test_pagination_limit_non_entier_renvoie_400(client):
    """?limit=abc → 400."""
    res = client.get("/api/todos?limit=abc")
    assert res.status_code == 400


def test_pagination_derniere_page_next_offset_null(client):
    """
    En parcourant jusqu'à la dernière page, next_offset finit par valoir null
    et l'union des pages couvre exactement `total` items sans doublon.
    """
    total = client.get("/api/todos").get_json()["total"]

    vus = []
    offset = 0
    limit = 2
    while True:
        body = client.get(f"/api/todos?limit={limit}&offset={offset}").get_json()
        vus.extend(t["id"] for t in body["items"])
        if body["next_offset"] is None:
            break
        assert body["next_offset"] == offset + limit
        offset = body["next_offset"]

    assert len(vus) == total
    assert len(set(vus)) == total  # pas de doublon entre pages


def test_pagination_offset_au_dela_du_total(client):
    """offset >= total → page vide, total renseigné, next_offset null."""
    total = client.get("/api/todos").get_json()["total"]

    res = client.get(f"/api/todos?offset={total + 10}")
    assert res.status_code == 200
    body = res.get_json()
    assert body["items"] == []
    assert body["total"] == total
    assert body["next_offset"] is None


def test_pagination_se_cumule_avec_completed(client):
    """
    ?completed=false&limit=1 : total = nombre de tâches non terminées (filtrage
    AVANT pagination), items limité à 1, et cet item est bien non terminé.
    """
    non_terminees = client.get("/api/todos?completed=false").get_json()["total"]
    assert non_terminees >= 2, "Le seed compte au moins 2 tâches non terminées"

    res = client.get("/api/todos?completed=false&limit=1")
    assert res.status_code == 200
    body = res.get_json()

    assert body["total"] == non_terminees
    assert len(body["items"]) == 1
    assert body["items"][0]["completed"] is False
    assert body["next_offset"] == 1


def test_pagination_total_coherent_avec_filtrage(client):
    """
    `total` de la réponse filtrée == nombre d'items d'une réponse non paginée
    filtrée de la même façon, et <= total global.
    """
    global_total = client.get("/api/todos").get_json()["total"]

    for qs in ("category=travail", "priority=normal", "completed=true"):
        filtre = client.get(f"/api/todos?{qs}").get_json()
        # sans limite basse : items == total pour le seed
        assert filtre["total"] == len(filtre["items"])
        assert filtre["total"] <= global_total


# Placé en dernier : ce test vide entièrement la liste des todos.
def test_stats_liste_vide_completion_rate_zero(client):
    """Liste vide → total 0 et completion_rate == 0.0."""
    for todo in get_items(client):
        client.delete(f"/api/todos/{todo['id']}")

    body = client.get("/api/stats").get_json()
    assert body["total"] == 0
    assert body["completed"] == 0
    assert body["pending"] == 0
    assert body["completion_rate"] == 0.0
