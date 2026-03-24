# Piggyback — Core Product Definition

## Overview

Piggyback is a **user-owned AI workspace** that allows multiple AI tools to continue work across systems without requiring the user to restate context.

The core idea is simple:

> Context should live in a persistent project workspace, not inside isolated chat sessions.

Instead of relying on chat history inside individual tools, Piggyback stores durable project state in a structured workspace that both humans and AI tools can read from and update over time.

Piggyback is designed around:

- persistent project context
- explicit, user-controlled updates
- self-hosted deployment
- scoped access for external tools
- versioned files as the core unit of state

---

## Problem

Today, AI tools are mostly siloed.

A user can:

- plan something in ChatGPT
- continue it in another tool
- revisit it later

But in practice, that usually means:

- re-explaining the context
- copy/pasting summaries
- losing track of decisions
- relying on fragile chat memory

Each system remembers context only inside its own boundaries.

This creates a broken workflow:

- project state is trapped in individual chats
- external tools have no reliable context handoff
- users become the manual orchestrator

Piggyback exists to solve that problem.

---

## Product thesis

Piggyback is not a chat logger and not a passive memory collector.

Piggyback is:

> A self-hosted, user-controlled project workspace where AI tools can build on shared context over time.

The product is based on a few core beliefs:

1. **Context should be project-based, not chat-based**
2. **Only durable, useful information should be stored**
3. **Users should control what enters the shared context**
4. **AI tools should access context through explicit integration, not passive surveillance**
5. **Version history is enough for trust in V1; proposal workflows can come later**

---

## What Piggyback is

Piggyback is a workspace system for AI-assisted work.

It stores and organizes:

- project summaries
- current status
- decisions
- constraints
- task handoffs
- execution details
- other durable text-based artifacts

Piggyback allows:

- humans to inspect and manage context through a web UI
- external AI tools to read and write context through an API
- multiple tools to continue the same project without starting from scratch

---

## What Piggyback is not

Piggyback is not:

- a universal background listener for all AI chats
- a passive log ingestion system
- a transcript archive
- a universal AI operating system (at least not in V1)
- a hosted SaaS that must store user data on our infrastructure
- a proposal/review workflow system in V1

Piggyback does **not** assume:

- OpenAI or other providers will stream chat logs to it
- access to all chat transcripts by default
- direct access to a user’s computer or local file explorer
- silent synchronization between every AI tool

---

## Core product model

The core model is:

### 1. Workspace

A top-level space owned by the user.

Examples: personal, work, side-projects.

### 2. Project

A scoped context area inside a workspace.

Examples: dinner-friday, product-launch, company-x-interview, trip-planning.

### 3. Files

The durable state of the project.

These are usually markdown or text files such as:

- `project.md`
- `status.md`
- `handoff.md`
- `reservation_details.md`
- `decisions.md`

### 4. Versions

Every file update creates a new version.

This allows:

- history
- transparency
- rollback possibilities later
- trust without a full proposal system

### 5. Agent connections

External AI tools or systems that can access Piggyback.

Examples: ChatGPT, Claude, Alexa, internal orchestrator, future MCP/action integrations.

### 6. Permissions

Agents can be granted scoped project access.

For V1, permissions are intentionally simple:

- `read`
- `write`

---

## V1 product philosophy

Piggyback V1 is intentionally simple.

### V1 prioritizes

- explicit updates
- self-hosting
- file-based project state
- version history
- direct reads/writes
- a browser UI for humans
- an API for tools

### V1 avoids

- passive chat ingestion
- automatic saving of everything
- complicated proposal systems
- file-level permission complexity
- semantic memory systems too early
- vector databases and overbuilt retrieval systems
- multi-service orchestration complexity

---

## User-controlled context is a core principle

One of the original product goals was:

> The user should directly control what gets added to shared context.

That remains a central design choice.

Piggyback should not become a giant junk drawer of AI conversations.

Instead:

- the user decides what matters
- connected tools can explicitly write useful state
- only durable, relevant project information is stored

This principle may later appear as an explicit UX action like:

> “Add to Piggy”

That concept is highly aligned with the product: it is intentional, understandable, and gives the user control over context curation.

This may become a major product feature later, but the philosophy already shapes the architecture.

---

## Why we are not doing passive chat ingestion

A major design question was whether Piggyback could simply receive chat logs automatically from tools like ChatGPT.

The conclusion so far is:

> Piggyback should not assume universal passive access to conversation logs.

Reasons:

- most tools do not provide open passive streaming of chats
- integrations are usually explicit (Actions, MCP, APIs, connectors)
- background syncing would create major trust and privacy concerns
- storing raw logs is often less useful than storing project state

Therefore, Piggyback is designed as an **event-driven system**.

The orchestrator is triggered by:

- user actions
- API calls from connected tools
- explicit writes to project files

Not by ambient monitoring.

---

## Event-driven integration model

Piggyback works when something explicitly updates it.

Examples of valid triggers:

- a user saves a summary
- an external tool writes a file
- a status file is updated
- a handoff file is generated
- a future “Add to Piggy” action is used

This is the current model:

> Piggyback is a shared state system, not a universal listener.

---

## Deployment model

Piggyback is designed to be **self-hosted**.

This is a critical design decision.

### Why self-hosted?

- user trust
- privacy
- flexibility
- lower requirements for us as a vendor
- easier to position as user-owned infrastructure

### Where Piggyback runs

Examples:

- local machine
- home server
- VPS
- internal company environment
- private cloud / VPC

### Core services

- API server
- Postgres database
- optional web UI

The web UI does **not** mean Piggyback becomes a hosted SaaS.

Instead, the web app is simply:

> a browser-based interface served from the same self-hosted stack.

That means all data can still remain inside the user’s environment.

---

## How the web app fits

The web app exists for humans.

Its purpose is to let users:

- view workspaces
- browse projects
- inspect files
- review version history
- manage permissions
- understand what the system currently knows

The web app is not the source of trust risk.

Trust depends on **where the system is hosted**, not whether the interface is a browser.

If Piggyback is self-hosted, then the browser UI is just a local or internal interface to local or internal data.

---

## High-level user flow

### Example: dinner planning

1. User plans a dinner in one AI tool
2. Useful project state is identified: shortlist of restaurants, preferences, reservation details
3. The user or connected tool writes that context into Piggyback
4. Another tool later reads that state and continues the task
5. User does not need to restate the original context

This is exactly the kind of workflow Piggyback is built for: one tool plans, another tool continues, and the context lives in the project—not the chat.

---

## File and folder model

The main user-facing abstraction is a project workspace made of files.

### Example structure

```text
/workspaces
  /personal
    /dinner-friday
      project.md
      status.md
      preferences.md
      reservation_details.md
      handoff.md
```

### File purposes

| File | Purpose |
|------|---------|
| **project.md** | Defines the project: goal, scope, intended outcome |
| **status.md** | Current state: what has been decided, what remains open, next steps |
| **preferences.md** | Relevant user preferences: constraints, likes/dislikes, persistent context |
| **reservation_details.md** | Execution-ready information: date, time, party size, chosen options |
| **handoff.md** | Minimal summary another tool can use to continue the task |

This file/folder structure is central to the product.

---

## Current technology decisions

| Layer | Choice | Rationale |
|--------|--------|-----------|
| **Backend** | Python, FastAPI | API-first architecture; easy external tool integration; good fit for orchestrator logic |
| **Database** | PostgreSQL | Strong relational model; workspaces/projects/files/versions/permissions; enough for V1 content storage |
| **Frontend** | Next.js + TypeScript | Browser UI for humans; clean structure; good fit for internal/self-hosted UI |
| **Infra** | Docker / Docker Compose | Simple local/self-hosted deployment; user-owned runtime |
| **Search** | Keyword / full-text first | No vector DB in V1 |
| **Storage** | Markdown/text in Postgres (V1) | Richer file support deferred |

---

## Architecture decisions made so far

1. **Self-hosted first** — Piggyback should run in the user’s environment.
2. **User-controlled context** — Only useful state should be stored, intentionally.
3. **Event-driven, not passive** — Piggyback does not depend on passive ingestion of external chat logs.
4. **File-based project state** — Markdown/text files are the primary V1 state model.
5. **Browser UI is allowed** — A web app is useful and does not violate the trust model as long as it is self-hosted.
6. **Direct write model for V1** — Proposal/approval workflows are deferred. Authorized agents can write directly if they have permission. Version history provides traceability.
7. **Permissions stay simple in V1** — Only read and write.
8. **Version history is mandatory** — Every write creates a new file version.
9. **No passive transcript storage** — We store project state, not full chat logs.
10. **Build in chunks** — Avoid overbuilding; implement one coherent layer at a time.

---

## API model direction

Piggyback is intended to be **API-driven**.

- Humans interact through the UI.
- Tools interact through the API.

**Core capabilities** (directional):

- list projects
- list files
- read file
- write/update file
- append handoff or summary content
- manage permissions
- list version history

This API-first design is what makes Piggyback interoperable.

---

## Current backend capabilities

At this point in development, the backend already includes:

**Persistence**

- workspaces
- projects
- files
- `file_versions`
- `agent_connections`
- `permissions`

**Trust / control**

- project-level permissions
- direct write model
- version tracking

**Proposal system**

A proposal model exists from earlier exploration, but it is not part of the intended V1 direction anymore.

**Stated direction**

- direct writes with permissions
- version history as the trust mechanism
- proposals deferred unless needed later

---

## What V1 should actually be

Piggyback V1 should be defined as:

> A self-hosted project workspace for AI context, where users and explicitly connected tools can read and write durable project state over time.

### V1 includes

- self-hosted API
- Postgres-backed persistence
- browser UI
- workspaces
- projects
- files
- file versions
- agent connections
- project-level permissions (read, write)
- explicit writes through API
- human-readable markdown/text files

### V1 does not include

- passive chat ingestion
- universal AI connectors
- proposal approval workflow
- semantic vector retrieval
- rich file/media support
- advanced orchestration automation
- deep enterprise security features
- hosted SaaS data storage

---

## Future features (deferred, not V1)

These are possible later, but explicitly deferred:

- “Add to Piggy” UX actions
- browser extension or desktop companion
- MCP / Actions / external connector support
- automatic summarization suggestions
- proposal/review workflow
- file-level permissions
- richer handoff packaging
- semantic search / embeddings
- richer artifact support (wireframes, images, attachments)
- orchestrator automation beyond direct writes

---

## Why this product still matters

Piggyback is useful because it solves a very real problem: AI tools are individually useful, but project continuity across them is broken.

People are currently the glue between systems.

Piggyback aims to become that glue: safely, intentionally, transparently, in a user-owned way.

---

## Summary

Piggyback is a self-hosted AI workspace that stores durable project context in files and lets multiple AI tools continue work across systems without requiring the user to restate everything.

The current product direction is: self-hosted, event-driven, file-based, user-controlled, API-first, versioned, and simple in V1.

It is not trying to capture every conversation automatically.

It is trying to become **the place where meaningful AI-assisted work lives between tools**.
