"""
Todo App - API Flask minimaliste
Workshop : n8n / Claude Code / Git
"""

from flask import Flask, jsonify, request, send_from_directory
from itertools import count

app = Flask(__name__, static_folder="static", static_url_path="")

_id_counter = count(1)

# Catégories autorisées pour une todo.
# La première valeur ("autre") sert aussi de valeur par défaut.
CATEGORIES = ["autre", "travail", "perso", "urgent"]
DEFAULT_CATEGORY = CATEGORIES[0]

# Priorités autorisées pour une todo (exactement ces trois).
PRIORITIES = ["low", "normal", "high"]
DEFAULT_PRIORITY = "normal"

# Petit jeu de données en mémoire (pas de vraie base pour rester simple)
todos = [
    {"id": next(_id_counter), "title": "Préparer le workshop", "completed": True, "category": "travail"},
    {"id": next(_id_counter), "title": "Relire le ticket JIRA-142", "completed": False, "category": "travail"},
    {"id": next(_id_counter), "title": "Configurer Claude Code", "completed": False, "category": "urgent"},
    {"id": next(_id_counter), "title": "Boire un café", "completed": True, "category": "perso"},
]

# Valeur par défaut pour les tâches déjà présentes au démarrage.
for _todo in todos:
    _todo.setdefault("priority", DEFAULT_PRIORITY)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Retourne la liste des catégories autorisées (utile pour le frontend)."""
    return jsonify(CATEGORIES)


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Retourne des statistiques sur les todos :
      - total : nombre total de tâches
      - completed : nombre de tâches terminées
      - pending : nombre de tâches non terminées
      - completion_rate : pourcentage de tâches terminées, arrondi à une décimale
                          (0.0 si la liste est vide)
    """
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    pending = total - completed
    completion_rate = round(completed / total * 100, 1) if total else 0.0

    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": completion_rate,
    })


@app.route("/api/todos", methods=["GET"])
def get_todos():
    """
    Retourne la liste des todos.
    Supporte trois filtres optionnels et combinables :
      - ?completed=true|false
      - ?category=<valeur>   (une catégorie inconnue renvoie une liste vide)
      - ?priority=<valeur>   (une priorité inconnue renvoie une liste vide)

    Pagination (TODO-150) :
      - ?limit=<entier>   défaut 50, max 200 ; hors bornes -> 400
      - ?offset=<entier>  défaut 0 ; négatif ou non entier -> 400

    Réponse : {"items": [...], "total": N, "next_offset": <entier ou null>}
    où `total` est le nombre de tâches après filtrage, avant pagination.
    """
    completed_param = request.args.get("completed")
    category_param = request.args.get("category")
    priority_param = request.args.get("priority")

    try:
        limit = int(request.args.get("limit", 50))
    except (TypeError, ValueError):
        return jsonify({"error": "Le paramètre 'limit' doit être un entier"}), 400
    if limit < 0 or limit > 200:
        return jsonify({"error": "Le paramètre 'limit' doit être entre 0 et 200"}), 400

    try:
        offset = int(request.args.get("offset", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Le paramètre 'offset' doit être un entier"}), 400
    if offset < 0:
        return jsonify({"error": "Le paramètre 'offset' ne peut pas être négatif"}), 400

    result = todos

    if completed_param is not None:
        want_completed = completed_param.lower() == "true"
        result = [t for t in result if t["completed"] == want_completed]

    if category_param is not None:
        result = [t for t in result if t["category"] == category_param]

    if priority_param is not None:
        result = [t for t in result if t["priority"] == priority_param]

    total = len(result)
    page = result[offset:offset + limit]
    next_offset = offset + limit if offset + limit < total else None

    return jsonify({"items": page, "total": total, "next_offset": next_offset})


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    #title = data.get("title", "")

    if not title:
        return jsonify({"error": "Le champ 'title' est requis"}), 400

    category = data.get("category", DEFAULT_CATEGORY)
    if category not in CATEGORIES:
        return jsonify({
            "error": f"Catégorie invalide : '{category}'. Valeurs autorisées : {CATEGORIES}"
        }), 400

    priority = data.get("priority", DEFAULT_PRIORITY)
    if priority not in PRIORITIES:
        return jsonify({"error": "Priorité invalide"}), 400

    todo = {
        "id": next(_id_counter),
        "title": title,
        "completed": False,
        "category": category,
        "priority": priority,
    }
    todos.append(todo)
    return jsonify(todo), 201


@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}
    todo = next((t for t in todos if t["id"] == todo_id), None)

    if todo is None:
        return jsonify({"error": "Todo introuvable"}), 404

    if "category" in data:
        category = data["category"]
        if category not in CATEGORIES:
            return jsonify({
                "error": f"Catégorie invalide : '{category}'. Valeurs autorisées : {CATEGORIES}"
            }), 400
        todo["category"] = category
    if "priority" in data:
        priority = data["priority"]
        if priority not in PRIORITIES:
            return jsonify({"error": "Priorité invalide"}), 400
        todo["priority"] = priority
    if "completed" in data:
        todo["completed"] = bool(data["completed"])
    if "title" in data:
        todo["title"] = data["title"]

    return jsonify(todo)


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    before = len(todos)
    todos = [t for t in todos if t["id"] == todo_id]

    if len(todos) == before:
        return jsonify({"error": "Todo introuvable"}), 404

    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
