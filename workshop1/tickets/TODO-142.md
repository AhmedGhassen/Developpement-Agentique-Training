# TODO-142 — Add a `priority` field to tasks

**Type**: enhancement
**Component**: `todo-app` / API
**Priority**: normal
**Requested by**: product team

---

## Context

Users currently classify their tasks only by creation order.
They are asking to be able to mark important tasks and find them
quickly.

## Expected

- Add a `priority` field to each task.
- Allowed values, exactly these three: `low`, `normal`, `high`.
- Default value `normal` — including for tasks that already exist at startup.
- The field is accepted when creating a task (`POST /api/todos`) and updating
  a task (`PATCH /api/todos/<id>`).
- An unauthorized value returns `400` with the body
  `{"error": "Invalid priority"}`.
- `GET /api/todos?priority=high` filters by this field.
- The `priority` filter must be combinable with the existing `completed` filter.
- `priority` appears in all responses that return a task.

## Not requested

- No automatic sorting by priority.
- No changes to the `static/` frontend: this is a separate ticket.

## Acceptance Criteria

- [ ] `POST /api/todos` without `priority` creates a `normal` task
- [ ] `POST /api/todos` with `{"priority": "urgent"}` returns 400
- [ ] `PATCH` accepts `priority` and rejects an invalid value
- [ ] `GET /api/todos?priority=high&completed=false` returns the intersection
- [ ] The existing test suite remains green
