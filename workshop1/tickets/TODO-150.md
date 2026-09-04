# TODO-150 — Pagination de GET /api/todos

## Comportement attendu

Deux paramètres nouveaux :
- `limit` : entier, défaut 50, max 200. Au-delà -> 400
- `offset` : entier, défaut 0. Négatif -> 400

La réponse devient : {"items": [...], "total": N, "next_offset": N ou null}
`total` = nombre de tâches après filtrage, avant pagination.
Les filtres completed / category / priority restent cumulables.

## Périmètre

- `app.py`, fonction `get_todos` uniquement
- `tests/test_app.py`
- `static/script.js` n'est PAS dans le périmètre

## Critère de vérification

`python -m pytest -q` passe, et couvre : défaut, limit=2, limit=201 -> 400,
offset négatif -> 400, dernière page avec next_offset null,
cumul ?completed=false&limit=1, total cohérent avec le filtrage.

## Ne pas toucher

- Les autres routes
