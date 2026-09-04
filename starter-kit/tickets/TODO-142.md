# TODO-142 — Ajouter un champ `priority` sur les tâches

**Type** : évolution
**Composant** : `todo-app` / API
**Priorité** : normale
**Demandé par** : équipe produit

---

## Contexte

Les utilisateurs classent aujourd'hui leurs tâches uniquement par ordre de création.
Ils demandent de pouvoir marquer les tâches importantes et de les retrouver
rapidement.

## Attendu

- Champ `priority` sur chaque tâche.
- Valeurs autorisées, exactement ces trois : `low`, `normal`, `high`.
- Valeur par défaut `normal` — y compris pour les tâches déjà présentes au démarrage.
- Le champ est accepté à la création (`POST /api/todos`) et à la modification
  (`PATCH /api/todos/<id>`).
- Une valeur non autorisée retourne `400` avec le corps
  `{"error": "Priorité invalide"}`.
- `GET /api/todos?priority=high` filtre sur ce champ.
- Le filtre `priority` doit pouvoir se cumuler avec le filtre `completed` existant.
- `priority` apparaît dans toutes les réponses qui retournent une tâche.

## Non demandé

- Aucun tri automatique par priorité.
- Aucun changement du front `static/` : c'est un autre ticket.

## Critères d'acceptation

- [ ] `POST /api/todos` sans `priority` crée une tâche `normal`
- [ ] `POST /api/todos` avec `{"priority": "urgent"}` retourne 400
- [ ] `PATCH` accepte `priority` et refuse une valeur invalide
- [ ] `GET /api/todos?priority=high&completed=false` retourne l'intersection
- [ ] La suite de tests existante reste verte
