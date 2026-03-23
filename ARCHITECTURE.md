# Piggyback — architecture summary

## Product anchor

Product direction and V1 scope live in [`core.md`](./core.md). Piggyback is a user-owned AI workspace: durable project context (markdown/text), agents that read shared state, and **orchestrator-controlled writes** with project/file-level permissions—implemented in later milestones.

## Stack choices

| Layer | Choice | Why |
|--------|--------|-----|
| API | **FastAPI** | API-first, async-friendly, OpenAPI out of the box; orchestration stays in Python alongside the server. |
| Data | **PostgreSQL** | Fits workspaces, projects, files, versions, permissions, proposals, and handoffs as relational data; markdown/text in the DB for V1. Schema and relationships are summarized in [`docs/data-model.md`](./docs/data-model.md). |
| UI | **Next.js + TypeScript** | Typed UI, App Router, straightforward local dev against the API. |
| Local env | **Docker Compose** | One command for Postgres + API; optional profile for the web app. |
| Search (later) | **Keyword / full-text** | Start with `ILIKE` or Postgres full-text (`tsvector`); no vector DB in V1. |

## V1 engineering scope (current)

- Monorepo: `apps/api`, `apps/web`, `packages/` (placeholder for shared contracts).
- API: liveness `GET /health`, DB connectivity `GET /health/db`, CORS for local web.
- **Domain data:** SQL migrations under `apps/api/migrations/` (applied at API startup when `DATABASE_URL` is set), connection pooling (`psycopg-pool`), CRUD for workspaces → projects → files, append-only `file_versions`, and `proposed_updates` create/list. Plain SQL + Pydantic; no ORM.

## Intentionally deferred

- Authentication and user sessions.
- Authenticated agent APIs, proposal accept/reject workflow, handoffs.
- Orchestrator logic (curation, merge, user confirmation).
- Vector databases, Kubernetes, microservices, message buses.
- Production deployment, CI/CD, and hardening.

## Security note

This repository targets **local development**. Do not commit real secrets; use `.env` from `.env.example` only for dev defaults.
