"""
Todo App - API Flask minimaliste
Workshop : n8n / Claude Code / Git

Ce fichier contient volontairement UN BUG pour les besoins du workshop.
Ne pas corriger avant l'exercice !
"""

from flask import Flask, jsonify, request, send_from_directory
from itertools import count

app = Flask(__name__, static_folder="static", static_url_path="")

_id_counter = count(1)
VALID_CATEGORIES = {"travail", "perso", "urgent"}

# Petit jeu de données en mémoire (pas de vraie base pour rester simple)
todos = [
    {
        "id": next(_id_counter),
        "title": "Préparer le workshop",
        "completed": True,
        "category": "travail",
    },
    {
        "id": next(_id_counter),
        "title": "Relire le ticket JIRA-142",
        "completed": False,
        "category": "travail",
    },
    {
        "id": next(_id_counter),
        "title": "Configurer Claude Code",
        "completed": False,
        "category": "urgent",
    },
    {
        "id": next(_id_counter),
        "title": "Boire un café",
        "completed": True,
        "category": "perso",
    },
]


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/todos", methods=["GET"])
def get_todos():
    """
    Retourne la liste des todos.
    Supporte les filtres optionnels ?completed=true|false et ?category=...
    """
    completed_param = request.args.get("completed")
    category_param = request.args.get("category")

    if completed_param is None and category_param is None:
        return jsonify(todos)

    filtered = todos
    if completed_param is not None:
        want_completed = completed_param.lower() == "true"
        filtered = [t for t in filtered if t["completed"] == want_completed]

    if category_param is not None:
        filtered = [t for t in filtered if t.get("category") == category_param]

    return jsonify(filtered)


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Retourne des statistiques sur les todos :
    total, completed, pending et completion_rate (%, arrondi à 1 décimale).
    """
    total = len(todos)
    completed = sum(1 for t in todos if t["completed"])
    pending = total - completed
    completion_rate = round(completed / total * 100, 1) if total else 0.0

    return jsonify(
        {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": completion_rate,
        }
    )


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    category = data.get("category", "perso")

    if not title:
        return jsonify({"error": "Le champ 'title' est requis"}), 400
    if not isinstance(category, str) or category not in VALID_CATEGORIES:
        return jsonify({"error": "La catégorie doit être travail, perso ou urgent"}), 400

    todo = {
        "id": next(_id_counter),
        "title": title,
        "completed": False,
        "category": category,
    }
    todos.append(todo)
    return jsonify(todo), 201


@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    todo = next((t for t in todos if t["id"] == todo_id), None)

    if todo is None:
        return jsonify({"error": "Todo introuvable"}), 404

    return jsonify(todo)


@app.route("/api/todos/<int:todo_id>", methods=["PATCH"])
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}
    todo = next((t for t in todos if t["id"] == todo_id), None)

    if todo is None:
        return jsonify({"error": "Todo introuvable"}), 404

    if "completed" in data:
        todo["completed"] = bool(data["completed"])
    if "title" in data:
        todo["title"] = data["title"]
    if "category" in data:
        if (
            not isinstance(data["category"], str)
            or data["category"] not in VALID_CATEGORIES
        ):
            return jsonify(
                {"error": "La catégorie doit être travail, perso ou urgent"}
            ), 400
        todo["category"] = data["category"]

    return jsonify(todo)


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    before = len(todos)
    todos = [t for t in todos if t["id"] != todo_id]

    if len(todos) == before:
        return jsonify({"error": "Todo introuvable"}), 404

    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
