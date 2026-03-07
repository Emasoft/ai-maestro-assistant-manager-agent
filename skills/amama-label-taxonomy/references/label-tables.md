# AMAMA Label Tables Reference

<!-- TOC -->
- [Priority Labels](#priority-labels-priority)
- [Kanban Columns (Canonical 8-Column System)](#kanban-columns-canonical-8-column-system)
- [Status Labels AMAMA Updates](#status-labels-amama-updates)
- [Labels AMAMA Monitors](#labels-amama-monitors)
- [Labels AMAMA Never Sets](#labels-amama-never-sets)
- [AMAMA's Approval Authority](#amamas-approval-authority)
<!-- /TOC -->

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

## Kanban Columns (Canonical 8-Column System)

| # | Column Code | Display Name | Label | Description |
|---|-------------|-------------|-------|-------------|
| 1 | `backlog` | Backlog | `status:backlog` | Entry point for new tasks |
| 2 | `todo` | Todo | `status:todo` | Ready to start |
| 3 | `in-progress` | In Progress | `status:in-progress` | Active work |
| 4 | `ai-review` | AI Review | `status:ai-review` | Integrator agent reviews ALL tasks |
| 5 | `human-review` | Human Review | `status:human-review` | User reviews BIG tasks only (via AMAMA) |
| 6 | `merge-release` | Merge/Release | `status:merge-release` | Ready to merge |
| 7 | `done` | Done | `status:done` | Completed |
| 8 | `blocked` | Blocked | `status:blocked` | Blocked at any stage |

**Task Routing Rules:**
- **Small tasks**: In Progress -> AI Review -> Merge/Release -> Done
- **Big tasks**: In Progress -> AI Review -> Human Review -> Merge/Release -> Done
- **Human Review** is requested via AMAMA (Assistant Manager asks user to test/review)
- Not all tasks go through Human Review -- only significant changes requiring human judgment

## Status Labels AMAMA Updates

| Label | When AMAMA Sets It |
|-------|------------------|
| `status:backlog` | When creating new issue from user request |
| `status:human-review` | When AMIA escalates a significant task for user review |
| `status:blocked` | When user requests pause or issue cannot proceed |

## Labels AMAMA Monitors

### Status Labels (`status:*`)

AMAMA reports status to user:
- `status:backlog` - "Your request has been logged"
- `status:todo` - "Your request is queued and ready to start"
- `status:in-progress` - "Work has started on your request"
- `status:ai-review` - "The AI integrator is reviewing the work"
- `status:human-review` - "This needs your review and testing"
- `status:merge-release` - "Code is approved and ready to merge"
- `status:blocked` - "There's a blocker, may need your input"
- `status:done` - "Your request is complete"

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
