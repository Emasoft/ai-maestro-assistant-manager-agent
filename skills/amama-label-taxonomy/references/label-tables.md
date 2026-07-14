# AMAMA Label Tables Reference

## Table of Contents
- [Priority Labels](#priority-labels-priority)
- [Kanban Columns (Canonical 17-Column Model)](#kanban-columns-canonical-17-column-model)
- [Status Labels AMAMA Updates](#status-labels-amama-updates)
- [Labels AMAMA Monitors](#labels-amama-monitors)
- [Labels AMAMA Never Sets](#labels-amama-never-sets)
- [AMAMA's Approval Authority](#amamas-approval-authority)

## Priority Labels (`priority:*`)

**AMAMA has authority to set and change priorities based on user input.**

| Label | Description | When AMAMA Sets It |
|-------|-------------|-------------------|
| `priority:critical` | Must fix immediately | User reports production issue |
| `priority:high` | High priority | User emphasizes importance |
| `priority:normal` | Standard priority | Default for new issues |
| `priority:low` | Nice to have | User indicates low urgency |

**AMAMA Priority Responsibilities:**
- Set initial priority based on user request
- Escalate priority when user expresses urgency
- De-escalate when user indicates reduced urgency

## Kanban Columns (Canonical 17-Column Model)

The board has exactly **17 columns**, 1:1 with the TRDD `column:` field. Every
`status:*` label is derived mechanically from a column name — one label per column,
no extras, no renames. This vocabulary is CANONICAL: the labels align TO the columns,
never the reverse.

**14 lifecycle columns**, in pipeline order:

| # | Column Code | Display Name | Label | Description |
|---|-------------|--------------|-------|-------------|
| 1 | `backburner` | Backburner | `status:backburner` | Entry point — captured, not yet prioritized |
| 2 | `todo` | Todo | `status:todo` | Prioritized, ready to be picked up |
| 3 | `design` | Design | `status:design` | Being decomposed and specced (architect-skilled member) |
| 4 | `dispatch` | Dispatch | `status:dispatch` | Design done, awaiting assignment to a member |
| 5 | `dev` | Dev | `status:dev` | Active implementation work |
| 6 | `testing` | Testing | `status:testing` | Gates running (lint, types, unit/e2e, CI) |
| 7 | `ai_review` | AI Review | `status:ai_review` | AI reviewer inspects the work |
| 8 | `human_review` | Human Review | `status:human_review` | Escalated to the user for human judgment (surfaced by AMAMA) |
| 9 | `complete` | Complete | `status:complete` | Done and verified; not yet released |
| 10 | `publish` | Publish | `status:publish` | Release pipeline running (tools) |
| 11 | `published` | Published | `status:published` | Released to its registry/marketplace (terminal) |
| 12 | `deploy` | Deploy | `status:deploy` | Deployment pipeline running (services) |
| 13 | `live` | Live | `status:live` | Running in production |
| 14 | `live_auditing` | Live Auditing | `status:live_auditing` | Post-deploy soak / audit window |

**3 exception columns** — orthogonal to the pipeline, not a stage in it:

| # | Column Code | Display Name | Label | Description |
|---|-------------|--------------|-------|-------------|
| 15 | `blocked` | Blocked | `status:blocked` | Applies whenever `blocked-by` is non-empty. Record `pre-block-column` on entry and restore to it when the blocker clears |
| 16 | `failed` | Failed | `status:failed` | **NOT terminal, NOT archived** — the card stays on the board and is retried via `dev`. Only an explicit decision to give up converts it to `cancelled` (an archival value, not a board column) |
| 17 | `superseded` | Superseded | `status:superseded` | Replaced by another task; terminal, leaves the board on the next archival pass |

**Task Routing Rules:**
- **Standard path**: `dev` -> `testing` -> `ai_review` -> `complete`
- **Escalated path**: `dev` -> `testing` -> `ai_review` -> `human_review` -> `complete`
- Only significant changes needing human judgment reach `human_review`; AMAMA is the one
  who asks the user to test/review, and relays the verdict back
- A failed gate sends the task back to `dev` (via `failed` when the attempt is recorded)
- **After `complete`, the path is chosen by `release-via`**, never freely:
  - `publish` (tools) -> `publish` -> `published`
  - `deploy` (services) -> `deploy` -> `live` -> `live_auditing`
  - `none` -> `complete` is terminal

## Status Labels AMAMA Updates

| Label | When AMAMA Sets It |
|-------|------------------|
| `status:backburner` | When creating a new issue from a user request |
| `status:human_review` | When AMIA escalates a significant task for user review (via AMAMA) |
| `status:blocked` | When the user pauses the work, or `blocked-by` becomes non-empty (AMAMA records the pre-block column so the task can be restored to it) |

## Labels AMAMA Monitors

### Status Labels (`status:*`)

AMAMA reports status to the user in plain language:

- `status:backburner` - "Your request has been logged"
- `status:todo` - "Your request is queued and ready to start"
- `status:design` - "The design for your request is being worked out"
- `status:dispatch` - "The design is done; the work is being assigned"
- `status:dev` - "Work has started on your request"
- `status:testing` - "The work is being tested (lint, types, tests, CI)"
- `status:ai_review` - "The AI integrator is reviewing the work"
- `status:human_review` - "This needs your review — I'll walk you through it"
- `status:complete` - "The work is done and verified"
- `status:publish` - "The release is being published"
- `status:published` - "It's released"
- `status:deploy` - "The change is being deployed"
- `status:live` - "It's live in production"
- `status:live_auditing` - "It's live; we're watching it during the soak window"
- `status:blocked` - "This is paused, waiting on something else"
- `status:failed` - "An attempt failed; it's queued for another try, not dropped"
- `status:superseded` - "This was replaced by newer work"

### Assignment Labels (`assign:*`)

AMAMA explains assignments to user:
- `assign:implementer-*` - "An AI agent is working on this"
- `assign:human` - "This needs human attention"
- `assign:orchestrator` - "The orchestrator is handling this"

## Labels AMAMA Never Sets

- `assign:*` - Set by AMOA/AMCOS
- `review:*` - Managed by AMIA
- `effort:*` - Set by AMOA during triage
- `component:*` - Set by AMOA/AMAA

## AMAMA's Approval Authority

AMAMA can approve:
- Priority changes requested by other agents
- Scope changes that affect user expectations
- Deadline/milestone changes

AMAMA must approve:
- Any change to `priority:critical`
- Reassignment to `assign:human`
- Project-level decisions
