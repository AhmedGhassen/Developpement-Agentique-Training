# Todo App — Projet du Workshop

Petite application Todo (backend Flask + frontend HTML/JS vanilla),
utilisée comme support pour le workshop *"Du ticket Jira au merge,
avec un agent IA"*.

## Lancer le projet

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

L'application est ensuite accessible sur http://localhost:5000

## Lancer les tests

```bash
pytest -v
```

## Structure

```
todo-app/
├── app.py              # API Flask (routes /api/todos)
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/
│   └── test_app.py
├── requirements.txt
└── README.md
```

## Endpoints API

| Méthode | Route              | Description                          |
|---------|---------------------|---------------------------------------|
| GET     | /api/todos           | Liste des todos (filtres combinables `?completed=` et `?category=`)|
| POST    | /api/todos           | Créer une todo (`{"title": "...", "category": "..."}` — `category` optionnel)|
| PATCH   | /api/todos/<id>      | Modifier une todo (`title`, `completed`, `category`)|
| DELETE  | /api/todos/<id>      | Supprimer une todo                    |
| GET     | /api/categories      | Liste des catégories autorisées (JSON) |

Catégories autorisées : `autre` (défaut), `travail`, `perso`, `urgent`.
