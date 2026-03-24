# Data model (V1 foundation)

This document describes the first Postgres schema and API resources for Piggyback. Product goals and agent rules live in [`core.md`](../core.md).

## Entity hierarchy

```text
Workspace
  └── Project  ←── Permission → AgentConnection
        └── File  ─── current_version → FileVersion (append-only history)
              └── ProposedUpdate (pending | accepted | rejected)
```

- **Workspace** — Top-level bucket (e.g. personal vs team areas in `core.md`).
- **Project** — A durable context folder (e.g. `dinner-friday`) containing markdown/text files.
- **File** — A logical path within a project (`project.md`, `handoff.md`, …). Uniqueness is `(project_id, path)`.
- **FileVersion** — Immutable snapshot of `content`. Creating or updating a file always inserts a new row; `files.current_version_id` points at the latest canonical version.
- **AgentConnection** — Registered agent identity (`name`, `agent_type`). No auth yet.
- **Permission** — Links an agent to a **project** with `read` or `propose_update`. Unique on `(agent_connection_id, project_id, permission_type)`.
- **ProposedUpdate** — Suggested file body; `status` is `pending`, `accepted`, or `rejected`. **Accept** appends a `FileVersion` and updates the file head; **reject** only changes status. See [`trust-model.md`](./trust-model.md).

## Why these entities first

1. **Matches the folder mental model** in `core.md` (workspace → project → named files).
2. **Separates durable state from suggestions** — versions are truth; proposals are inputs to a future orchestrator.
3. **Trust data is additive** — grants and proposal lifecycle live alongside CRUD; route-level enforcement and auth are still deferred.

## API surface (this milestone)

REST endpoints include: workspaces, projects, project **permissions**, **agent-connections**, files, `PATCH` file (dev shortcut), versions, proposals on a file, and **accept/reject** on a proposal by id. See OpenAPI at `/docs` when the API is running.

## Pagination and large bodies

Version and proposal lists return full `content` / `proposed_content` for local V1 simplicity. Expect pagination or summary fields in a later chunk if payloads grow.
