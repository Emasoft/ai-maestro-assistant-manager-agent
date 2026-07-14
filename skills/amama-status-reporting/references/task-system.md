# AI Maestro Task System - Detailed Reference

## Table of Contents
- [Task Storage](#task-storage)
- [Task Statuses (Kanban)](#task-statuses-kanban)

AI Maestro maintains its own task system, separate from GitHub Issues. Tasks are managed per-team.

## Task Storage

Tasks are stored in: `~/.aimaestro/teams/tasks-{teamId}.json`

## Task Statuses (Kanban)

Tasks use the **ratified 17-column kanban vocabulary**, 1:1 with the TRDD `column:` field.
It is the single source of truth — consumers align TO it, never the reverse (ai-maestro
R25 / TRDD-YUGDER9D). 14 lifecycle columns flow:

```
backburner -> todo -> design -> dispatch -> dev -> testing -> ai_review -> human_review -> complete
  -> publish -> published        (tools)
  -> deploy -> live -> live_auditing   (services)
```

plus 3 orthogonal exception columns: `blocked`, `failed`, `superseded`.

| Status | Meaning |
|--------|---------|
| `backburner` | Acknowledged but not yet prioritized |
| `todo` | Prioritized, waiting to start |
| `design` | Architecture / requirements analysis |
| `dispatch` | Assignee being matched |
| `dev` | Actively being worked on by an agent |
| `testing` | Tests / audits running |
| `ai_review` | AI / integrator review |
| `human_review` | Awaiting user review/validation |
| `complete` | Finished and verified |
| `publish` / `published` | Tool-release pipeline |
| `deploy` / `live` / `live_auditing` | Service-release pipeline |
| `blocked` | Has an unmet `blocked-by:` (a flag) |
| `failed` | Retryable — stays OPEN |
| `superseded` | Replaced by another task |
