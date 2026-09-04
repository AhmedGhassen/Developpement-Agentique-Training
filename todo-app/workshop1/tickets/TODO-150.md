# TODO-150 - Pagination de GET /api/todos

## Comportement attendu

Deux parametres nouveaux :
- limit  : entier, defaut 50, max 200. Au-dela -> 400
- offset : entier, defaut 0. Negatif -> 400

La reponse devient : {"items": [...], "total": N, "next_offset": N ou null}
total = nombre de taches apres filtrage, avant pagination.
Les filtres completed / category / priority restent cumulables.

## Perimetre

- app.py, fonction get_todos uniquement
- tests/test_app.py
- static/script.js n'est PAS dans le perimetre

## Critere de verification

python -m pytest -q passe, et couvre : defaut, limit=2, limit=201 -> 400,
offset negatif -> 400, derniere page avec next_offset null,
cumul ?completed=false&limit=1, total coherent avec le filtrage.

## Ne pas toucher

- Les autres routes
- Les tests existants : aucune assertion modifiee
