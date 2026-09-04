"""
Tests pour l'API Todo.
"""

import copy

import pytest
import app as app_module
from app import app as flask_app


@pytest.fixture(autouse=True)
def restore_todos():
    """
    Restaure l'état initial de la liste todos après chaque test.

    Plusieurs routes mutent (voire réassignent, cf. DELETE) le global
    `todos` de app.py. Sans ce nettoyage, le résultat d'un test dépend
    de l'ordre d'exécution. On prend un snapshot profond avant le test
    et on le restaure ensuite.
    """
    snapshot = copy.deepcopy(app_module.todos)
    yield
    app_module.todos = snapshot


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_get_all_todos(client):
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert len(res.get_json()) >= 1


def test_create_todo(client):
    res = client.post("/api/todos", json={"title": "Nouvelle tâche de test"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["title"] == "Nouvelle tâche de test"
    assert body["completed"] is False


def test_create_todo_without_title_fails(client):
    res = client.post("/api/todos", json={})
    assert res.status_code == 400


def test_get_todo_returns_matching_todo(client):
    todo = client.get("/api/todos").get_json()[0]

    res = client.get(f"/api/todos/{todo['id']}")

    assert res.status_code == 200
    assert res.get_json() == todo


def test_get_todo_returns_404_when_missing(client):
    res = client.get("/api/todos/999999")

    assert res.status_code == 404
    assert res.get_json() == {"error": "Todo introuvable"}


def test_filter_completed_true_returns_only_completed(client):
    """
    GET /api/todos?completed=true doit renvoyer UNIQUEMENT
    les tâches terminées (completed == True).
    """
    res = client.get("/api/todos?completed=true")
    assert res.status_code == 200
    body = res.get_json()

    assert len(body) > 0, "Le filtre ne doit pas renvoyer une liste vide ici"
    for todo in body:
        assert todo["completed"] is True, (
            f"Tâche '{todo['title']}' renvoyée par ?completed=true "
            f"mais completed={todo['completed']}"
        )


def test_filter_completed_false_returns_only_incomplete(client):
    res = client.get("/api/todos?completed=false")
    assert res.status_code == 200
    body = res.get_json()

    for todo in body:
        assert todo["completed"] is False, (
            f"Tâche '{todo['title']}' renvoyée par ?completed=false "
            f"mais completed={todo['completed']}"
        )


def test_stats_keys_and_types(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    body = res.get_json()

    assert set(body.keys()) == {"total", "completed", "pending", "completion_rate"}
    assert isinstance(body["total"], int)
    assert isinstance(body["completed"], int)
    assert isinstance(body["pending"], int)
    assert isinstance(body["completion_rate"], float)


def test_stats_matches_todo_list(client):
    todos = client.get("/api/todos").get_json()
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    pending = total - completed
    expected_rate = round(completed / total * 100, 1) if total else 0.0

    body = client.get("/api/stats").get_json()

    assert body["total"] == total
    assert body["completed"] == completed
    assert body["pending"] == pending
    assert body["completion_rate"] == expected_rate
    assert body["total"] == body["completed"] + body["pending"]


def test_stats_completion_rate_updates_after_toggle(client):
    create_res = client.post("/api/todos", json={"title": "Tâche stats"})
    todo_id = create_res.get_json()["id"]

    client.patch(f"/api/todos/{todo_id}", json={"completed": True})

    todos = client.get("/api/todos").get_json()
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    expected_rate = round(completed / total * 100, 1) if total else 0.0

    body = client.get("/api/stats").get_json()
    assert body["completion_rate"] == expected_rate


def test_stats_completion_rate_empty_list(client):
    """
    Liste de tâches vide : completion_rate vaut 0.0 et aucune
    exception (division par zéro) n'est levée.
    """
    app_module.todos = []

    res = client.get("/api/stats")
    assert res.status_code == 200

    body = res.get_json()
    assert body["total"] == 0
    assert body["completed"] == 0
    assert body["pending"] == 0
    assert body["completion_rate"] == 0.0


def test_stats_completion_rate_all_completed(client):
    """Toutes les tâches terminées : completion_rate vaut 100.0."""
    app_module.todos = [
        {"id": 1, "title": "A", "completed": True},
        {"id": 2, "title": "B", "completed": True},
        {"id": 3, "title": "C", "completed": True},
    ]

    res = client.get("/api/stats")
    assert res.status_code == 200
    assert res.get_json()["completion_rate"] == 100.0


def test_stats_completion_rate_one_of_sixteen(client):
    """
    1 tâche terminée sur 16 : le taux brut vaut 1 / 16 * 100 == 6.25.

    Valeur documentée : en Python, round(6.25, 1) == 6.2 (et NON 6.3).
    Python utilise l'arrondi "round half to even" (arrondi bancaire) et
    6.25 est exactement représentable en flottant binaire ; l'arrondi se
    fait donc vers la décimale paire la plus proche, soit 6.2.
    """
    assert round(6.25, 1) == 6.2  # comportement de référence de Python

    app_module.todos = [
        {"id": i, "title": f"T{i}", "completed": (i == 0)}
        for i in range(16)
    ]

    res = client.get("/api/stats")
    assert res.status_code == 200
    assert res.get_json()["completion_rate"] == 6.2


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

    get_res = client.get("/api/todos")
    ids = [t["id"] for t in get_res.get_json()]
    assert todo_id not in ids
