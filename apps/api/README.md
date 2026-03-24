# Piggyback API

FastAPI application with Postgres-backed workspaces, projects, files, versions, and proposals.

## Run locally

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
```

Set `DATABASE_URL` in `.env` (see repo root `.env.example`) pointing at Postgres. Migrations in `migrations/*.sql` run **automatically on startup** when `DATABASE_URL` is set.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Without `DATABASE_URL`, `/health` still responds; domain routes return **503** until the database is configured.

### Apply migrations only (optional)

```bash
set DATABASE_URL=postgresql://...
python -m app.db.migrate
```

## Docker

The image copies `migrations/` next to the app package; Compose sets `DATABASE_URL` so the API migrates on boot.

## Development tests

```bash
pip install -e ".[dev]"
set DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
pytest
```

Tests are skipped if `DATABASE_URL` is unset. Use a dedicated database if you want to avoid leaving smoke data in a shared instance.

## Docs

See [`docs/data-model.md`](../../docs/data-model.md) for entity relationships and [`docs/trust-model.md`](../../docs/trust-model.md) for agents, grants, and proposal lifecycle.
