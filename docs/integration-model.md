# Piggyback — Integration Model (V1)

## Overview

Piggyback is a **user-owned, self-hosted AI workspace** that stores durable project context and allows AI tools to build on that context over time.

Piggyback does **not** attempt to automatically ingest all conversations from all AI tools.

Instead, it operates on a simple principle:

> Context is added intentionally — by the user or by connected tools — not passively collected.

---

## Core Philosophy

- Context lives in **projects and files**, not chat logs
- Only **durable, useful information** is stored
- Users maintain **full control** over what enters the system
- AI tools can **read and write context** only when explicitly connected
- The system is **event-driven**, not always listening

---

## What Piggyback Is NOT

Piggyback is not:
- A chat logger
- A passive listener of all AI conversations
- A universal background sync engine
- A system that stores every message or token

Piggyback does **not assume**:
- Access to chat logs from tools like ChatGPT, Claude, or Gemini
- That external AI tools will automatically stream data

---

## How Piggyback Actually Works

Piggyback is triggered by **explicit events**, not passive monitoring.

### Orchestrator Trigger Model

The orchestrator runs when:
- A user saves or updates context
- An external tool calls Piggyback’s API
- A connected system sends structured updates

Example triggers:

- `save_summary(project_id, content)`
- `update_file(path, content)`
- `append_handoff(project_id, content)`
- `update_status(project_id, content)`

There is no background ingestion of conversations.

---

## Deployment Model (V1)

Piggyback is designed to be **self-hosted**.

### User-Hosted (Internet-Reachable)

Piggyback runs inside the user’s environment:
- personal server
- VPS
- private cloud
- home lab
- secure internal network

### Services

- `piggyback-api` — backend service
- `postgres` — database
- `piggyback-web` — optional UI

### Access

Users access Piggyback via:
- a browser (web UI)
- API (for tools and integrations)


Example:
https://piggyback.yourdomain.com

### Data Flow
Browser / AI Tool → Piggyback API → Postgres

All data remains within the user’s environment.

---

## Why This Model

This approach provides:

- **Trust** — no external storage required
- **Control** — user decides what is saved
- **Security** — data stays in user infrastructure
- **Flexibility** — works with multiple tools

---

## Integration Model

Piggyback integrates with external AI tools via:

### 1. Direct API Access
Tools can:
- read files
- update files
- append summaries
- retrieve project state

### 2. Tool/Action Integrations
When supported by the AI platform:
- GPT Actions
- MCP / Apps integrations
- custom connectors

These allow AI tools to call Piggyback directly.

### 3. User-Initiated Actions (V1 Core)

The most important mechanism in V1:

> The user explicitly decides what gets added.

Examples:
- “Add this to Piggyback”
- “Save this as project status”
- “Update my plan”

This can be:
- manual copy/paste
- UI button
- simple command

---

## "Add to Piggy" Concept

Piggyback centers around:

> **User-controlled context curation**

Instead of automatic logging:

- The user chooses what matters
- Only meaningful context is stored
- Noise is avoided

Examples of what gets saved:
- decisions
- plans
- summaries
- constraints
- task state
- handoff information

---

## V1 Write Model

Piggyback uses a **direct write model**:

- Agents/tools with permission can:
  - read
  - write (update files)

- Every write:
  - creates a new version
  - updates current file state
  - is tracked in history

### Permissions

- `read`
- `write`

(No proposal/approval workflow in V1)

---

## Versioning

Every file update:
- creates a new version
- preserves history
- allows inspection of changes

This provides:
- traceability
- safety
- transparency

---

## Example Workflow

### Step 1 — Planning

User works in ChatGPT:
- plans dinner
- narrows down options

### Step 2 — User Saves Context

User triggers:
> “Add this to Piggyback”

Piggyback stores:
- `status.md`
- `reservation_details.md`

### Step 3 — External Tool Reads Context

Another tool:
- reads project files
- continues the task

### Step 4 — Tool Updates Context

Tool writes:
- updated reservation info
- new status

Piggyback:
- creates a new version
- updates project state

---

## Key Insight

Piggyback is not trying to know everything.

It is designed to:

> **know what matters — because the user (or connected tool) chose to store it.**

---

## Future Considerations (Not in V1)

- automatic summarization
- background context suggestions
- proposal/approval workflows
- file-level permissions
- richer integrations
- desktop/browser extensions

---

## Summary

Piggyback is:

> A self-hosted, user-controlled workspace where AI tools can build on shared context over time.

It works by:
- storing structured project state
- exposing that state through an API
- allowing controlled updates
- relying on explicit actions, not passive data collection