# Data model (V1 foundation)

This document describes the first Postgres schema and API resources for Piggyback. Product goals and agent rules live in [`core.md`](../core.md).

## Entity hierarchy

```text
Workspace
  └── Project
        └── File  ─── current_version → FileVersion (append-only history)
              └── ProposedUpdate (suggested content; orchestrator not implemented yet)
```

- **Workspace** — Top-level bucket (e.g. personal vs team areas in `core.md`).
- **Project** — A durable context folder (e.g. `dinner-friday`) containing markdown/text files.
- **File** — A logical path within a project (`project.md`, `handoff.md`, …). Uniqueness is `(project_id, path)`.
- **FileVersion** — Immutable snapshot of `content`. Creating or updating a file always inserts a new row; `files.current_version_id` points at the latest canonical version.
- **ProposedUpdate** — Agent-suggested body text, `status` default `pending` for future accept/reject flows. Does **not** change `File`/`FileVersion` until orchestration exists.

## Why these entities first

1. **Matches the folder mental model** in `core.md` (workspace → project → named files).
2. **Separates durable state from suggestions** — versions are truth; proposals are inputs to a future orchestrator.
3. **Leaves cross-cutting concerns out** — no users/auth, permissions, search, or external agents in this layer yet.

## API surface (this milestone)

REST endpoints mirror this tree: create/list/get workspaces and projects; create/list/get files; `PATCH` file creates a new version; list versions; create/list proposals per file. See OpenAPI at `/docs` when the API is running.

## Pagination and large bodies

Version and proposal lists return full `content` / `proposed_content` for local V1 simplicity. Expect pagination or summary fields in a later chunk if payloads grow.
