# Piggyback — Write API (V1)

## Overview

The Piggyback Write API defines how users and external tools add or update context in a Piggyback workspace.

Piggyback is **event-driven**, not passive. All context changes happen through explicit API calls.

> Piggyback does not ingest chat logs automatically. Context is written intentionally by users or connected tools.

---

## Core principles

- All writes are **explicit**
- All writes are **scoped to a project**
- All writes create **new file versions**
- The API is designed to be simple, predictable, and tool-friendly

---

## Authentication (V1)

**V1**

- No auth required (local / dev mode)
- Assume trusted environment

**Future**

- API keys
- Agent-scoped tokens

---

## Base concepts

### Project

A container for context.

### File

A logical unit of context (markdown/text).

### Write

An update to a file that creates a new version.

---

## Primary write endpoints

### 1. Write / update file

Updates a file or creates it if it does not exist.

```http
POST /projects/{project_id}/files/write
```

**Request body**

```json
{
  "path": "status.md",
  "content": "We have selected 3 restaurants for Friday.",
  "mode": "replace",
  "created_by": {
    "type": "agent",
    "name": "chatgpt"
  }
}
```

**Fields**

| Field | Description |
|--------|-------------|
| `path` | File path within the project |
| `content` | Full file content |
| `mode` | Write mode: `replace` (default) or `append` |
| `created_by` | Metadata for auditing |

**Behavior**

- If the file does **not** exist: create the file and an initial version.
- If the file **exists**: create a new version and update `current_version_id`.

---

### 2. Append to file

Shortcut for appending content.

```http
POST /projects/{project_id}/files/append
```

**Request body**

```json
{
  "path": "handoff.md",
  "content": "User prefers outdoor seating.",
  "created_by": {
    "type": "agent",
    "name": "chatgpt"
  }
}
```

**Behavior**

1. Read current file content
2. Append new content
3. Create a new version

---

### 3. Create or update structured summary

Used for writing structured project state.

```http
POST /projects/{project_id}/summary
```

**Request body**

```json
{
  "type": "status",
  "content": "Dinner planning is 80% complete. Waiting on reservation.",
  "created_by": {
    "type": "agent",
    "name": "chatgpt"
  }
}
```

**Behavior**

Maps `type` to a known file, then internally calls the file write endpoint:

| Type | File |
|------|------|
| `status` | `status.md` |
| `handoff` | `handoff.md` |
| `project` | `project.md` |

---

### 4. Batch write (optional V1+)

Allows multiple updates in a single request.

```http
POST /projects/{project_id}/batch-write
```

**Request body**

```json
{
  "writes": [
    {
      "path": "status.md",
      "content": "Updated status",
      "mode": "replace"
    },
    {
      "path": "handoff.md",
      "content": "Reservation ready",
      "mode": "append"
    }
  ],
  "created_by": {
    "type": "agent",
    "name": "chatgpt"
  }
}
```

---

## Versioning behavior

Every write:

- Creates a new row in `file_versions`
- Updates `files.current_version_id`
- Preserves full history

No write overwrites previous version rows.

---

## Permissions (V1)

Basic permission concepts: **read**, **write**.

Before writing, the system checks whether the agent or user has write permission on the project. If not, return **403 Forbidden**.

---

## Response format

**Example response**

```json
{
  "file": {
    "id": "file_123",
    "path": "status.md",
    "current_version_id": "version_456"
  },
  "version": {
    "id": "version_456",
    "created_at": "2026-03-24T12:00:00Z"
  }
}
```

---

## Error handling

| Status | Meaning |
|--------|---------|
| **400 Bad Request** | Missing fields, invalid `mode`, etc. |
| **403 Forbidden** | No write permission |
| **404 Not Found** | Project not found |
| **409 Conflict** | Invalid state transition (future use) |

---

## Example flow

1. **Tool writes context** — `POST /projects/1/files/write` → writes `status.md`
2. **Piggyback stores a version** — new version created, file head updated
3. **Another tool reads context** — `GET /projects/1/files`
4. **Work continues** — no context is lost

---

## Design notes

### Why direct writes (no proposals)?

**V1**

- Simpler mental model
- Faster iteration
- Less UX complexity

**Later**

- Proposal / approval workflows
- Human review gates

### Why a file-based model?

- Human-readable
- Easy to reason about
- Flexible structure
- Compatible with many tools

### Why not store chat logs?

- Too noisy, not reusable, not task-oriented

**Piggyback stores:** decisions, summaries, state.

---

## Future extensions

- Partial updates (diff-based writes)
- Structured JSON documents
- Semantic tagging
- Automatic summarization
- Write hooks / triggers
- Agent-specific write constraints

---

## Summary

The Piggyback Write API enables explicit, controlled context updates, durable project state, and seamless continuation across tools.

**Write once. Continue anywhere.**

---

## What this unlocks next

Once this is implemented, you can:

1. Connect **ChatGPT via Actions / MCP**
2. Build a simple **“Add to Piggy”** button
3. Create your first **end-to-end demo**
4. Start testing real workflows

**Suggested next specs**

- A **read API + context retrieval** spec, or
- A **“Add to Piggy” UX flow** (where end-user value shows up most clearly)

Both are important as a follow-on.
