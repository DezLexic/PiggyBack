# Trust model (V1)

This document describes how Piggyback separates **reading**, **proposing**, and **canonical writes** at the API/data layer. Product context remains in [`core.md`](../core.md).

## Agents and project permissions

- An **agent connection** (`agent_connections`) is a registered actor (name + `agent_type` string). There is **no authentication** in this milestone; rows are identifiers for future enforcement.
- **Permissions** are **project-scoped**: each row ties an `agent_connection_id` to a `project_id` with `permission_type` either `read` or `propose_update`.
- This is the **first access boundary** in V1. **File-level** permissions and runtime **enforcement** (rejecting HTTP calls that lack a grant) are **not** implemented yet; grants are stored and listed for operators and upcoming middleware.

## Proposals vs canonical file state

- Agents (or clients acting on their behalf) create **proposals** (`proposed_updates`) with suggested body text. Pending proposals have `status = 'pending'`.
- **Accepting** a proposal (`POST /proposals/{id}/accept`):
  - Appends a new **`file_versions`** row using the proposal’s `proposed_content`
  - Updates the file’s **`current_version_id`** and `updated_at`
  - Sets the proposal’s `status` to **`accepted`**
- **Rejecting** a proposal only sets `status` to **`rejected`**; the file’s canonical content is unchanged.
- Calling **accept** or **reject** again on a non-pending proposal returns **409 Conflict** (idempotent enough for local dev: no double application of content).

## Direct file PATCH (local dev)

`PATCH /files/{file_id}` still updates canonical content by inserting a new version **without** going through a proposal. That is intentional for **human / local development** shortcuts until orchestration and enforcement align on “proposal-only” writes for automated agents.

## Next steps (out of scope here)

- Authenticate callers and map them to `agent_connection_id`
- Enforce `read` / `propose_update` on relevant routes
- Orchestrator automation for batching, deduplication, and user confirmation flows
