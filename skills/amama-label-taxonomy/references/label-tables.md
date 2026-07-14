# AMAMA Label Tables Reference

## Table of Contents
- [Priority Labels](#priority-labels-priority)
- [Kanban Columns (Ratified 17-Column Vocabulary)](#kanban-columns-ratified-17-column-vocabulary)
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

## Kanban Columns (Ratified 17-Column Vocabulary)

The GitHub `status:*` label taxonomy is 1:1 with the ratified 17-column kanban vocabulary
(the TRDD `column:` field). Consumers align TO it, never the reverse (ai-maestro R25 /
TRDD-YUGDER9D). The label value IS the column name verbatim:

| # | Column Code | Label | Kind | Description |
|---|-------------|-------|------|-------------|
| 1 | `backburner` | `status:backburner` | lifecycle | Entry point for new tasks, not yet prioritized |
| 2 | `todo` | `status:todo` | lifecycle | Prioritized, ready to be picked up |
| 3 | `design` | `status:design` | lifecycle | Architecture / requirements analysis |
| 4 | `dispatch` | `status:dispatch` | lifecycle | Assignee being matched |
| 5 | `dev` | `status:dev` | lifecycle | Active work |
| 6 | `testing` | `status:testing` | lifecycle | Tests / audits running |
| 7 | `ai_review` | `status:ai_review` | lifecycle | AI / integrator review |
| 8 | `human_review` | `status:human_review` | lifecycle | Escalated for user review (via AMAMA) |
| 9 | `complete` | `status:complete` | lifecycle | Done and verified |
| 10 | `publish` | `status:publish` | lifecycle | Entering the tool-release pipeline |
| 11 | `published` | `status:published` | lifecycle | Artifact live to users |
| 12 | `deploy` | `status:deploy` | lifecycle | Entering the service-deploy pipeline |
| 13 | `live` | `status:live` | lifecycle | Service live to users |
| 14 | `live_auditing` | `status:live_auditing` | lifecycle | Post-release soak |
| 15 | `blocked` | `status:blocked` | exception | Has an unmet `blocked-by:` (a flag) |
| 16 | `failed` | `status:failed` | exception | Retryable — stays OPEN |
| 17 | `superseded` | `status:superseded` | exception | Replaced by another task |

**Task Routing Rules:**
- **Small tasks**: `dev` -> `testing` -> `ai_review` -> `complete`
- **Big tasks**: `dev` -> `testing` -> `ai_review` -> `human_review` (escalate to manager) -> `complete`
- **`human_review`** is requested via AMAMA (Assistant Manager asks user to test/review)
- Not all tasks reach `human_review` -- only significant changes requiring human judgment

## Status Labels AMAMA Updates

| Label | When AMAMA Sets It |
|-------|------------------|
| `status:backburner` | When creating new issue from user request |
| `status:human_review` | When AMIA escalates a significant task for user review (via AMAMA) |
| `status:blocked` | When the user requests a pause (a flag) |

## Labels AMAMA Monitors

### Status Labels (`status:*`)

AMAMA reports status to user (see the full 17-column table above for every value):
- `status:backburner` - "Your request has been logged"
- `status:todo` - "Your request is queued and ready to start"
- `status:dev` - "Work has started on your request"
- `status:ai_review` - "The AI integrator is reviewing the work"
- `status:human_review` - "Your input is needed to review the work"
- `status:complete` - "Your request is complete"

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
