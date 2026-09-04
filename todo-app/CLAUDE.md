# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

This repo has two unrelated parts:

- **`workshop1/`** — a minimal Flask todo app used as the workshop exercise material
  ("Du ticket Jira au merge, avec un agent IA"). All app code, tests, and the frontend live here.
- **`run_category_subagents.py`** (repo root) — a standalone orchestration script that fans out
  three headless `claude -p` processes on the same prompt, then makes a 4th call to compare their
  proposals. Unrelated to the Flask app except that it points `claude` at `workshop1/` as its cwd.

## Commands

The Flask app and its tests assume `workshop1/` as the working directory (tests do `from app import app`).

```bash
# one-time setup (existing .venv lives at the repo root, not in workshop1/)
python -m venv .venv && .venv\Scripts\activate   # Windows; use `source .venv/bin/activate` elsewhere
pip install -r workshop1/requirements.txt

cd workshop1
python app.py            # serves http://localhost:5000 (frontend + API)
pytest -q                # run all tests
pytest -q tests/test_app.py::test_toggle_todo   # run a single test
```

Currently `pytest` reports `2 failed, 5 passed` — the two failures are the seeded bug below.

Running the subagent orchestrator (needs the `claude` binary on PATH; each call can take minutes):

```bash
python run_category_subagents.py
```

## Architecture

- **Backend** (`workshop1/app.py`): single-file Flask API. Todos are held in a module-level `todos`
  list with an `itertools.count` id generator — no database, no persistence. State resets on restart,
  and mutations from tests leak across tests within a run (tests are written to tolerate this).
  Routes: `GET/POST /api/todos`, `PATCH/DELETE /api/todos/<int:id>`.
- **Frontend** (`workshop1/static/`): vanilla HTML/CSS/JS, no build step. Flask serves it via
  `static_url_path=""`, so `index.html` is the site root. `script.js` talks to `/api/todos` and
  drives the `all | true | false` filter buttons.

## Workshop constraint — do not "fix" the seeded bug

`app.py` contains a deliberate bug in the `?completed=` filter of `get_todos()`
(`want_completed = completed_param.lower() != "true"` — the comparison is inverted). The header
comment says not to fix it before the exercise, and `tests/test_app.py` has two tests
(`test_filter_completed_*`) that currently fail because of it. Leave it alone unless the task is
explicitly about doing that exercise.
