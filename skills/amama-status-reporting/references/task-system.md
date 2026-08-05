# AI Maestro Task System - Detailed Reference

## Table of Contents
- [Task Storage](#task-storage)
- [Task Statuses (Kanban)](#task-statuses-kanban)

AI Maestro maintains its own task system, separate from GitHub Issues. Tasks are managed per-team.

## Task Storage

Tasks are stored in: `~/.aimaestro/teams/tasks-{teamId}.json`

## Task Statuses (Kanban)

Tasks use the ratified **17-column** vocabulary — 14 lifecycle columns plus 3 exception
columns. It is the same enum as the TRDD `column:` field: the server and every UI align
TO these columns, never the reverse. A coarser view may GROUP columns for display, but it
must round-trip mutations back to the full vocabulary.

```
backburner -> todo -> design -> dispatch -> dev -> testing -> ai_review
  -> human_review -> complete -> publish -> published -> deploy -> live
  -> live_auditing
```

Exception columns, outside the flow: `blocked`, `failed`, `superseded`.

| Status | Meaning |
|--------|---------|
| `backburner` | Deliberately deferred; a resting state, not a stall |
| `todo` | Queued and ready to be pulled |
| `design` | Being specified |
| `dispatch` | Ready to assign to a worker |
| `dev` | Actively being worked on by an agent |
| `testing` | Implementation done, under test |
| `ai_review` | Under automated/agent review |
| `human_review` | Awaiting the USER's review |
| `complete` | Finished and verified (terminal when `release-via: none`) |
| `publish` / `published` | Release branch, `release-via: publish` |
| `deploy` / `live` / `live_auditing` | Deploy branch, `release-via: deploy` |
| `blocked` | `blocked-by:` is non-empty; record `pre-block-column:` and restore on clear |
| `failed` | Retryable — stays ON the board, never archived as failed |
| `superseded` | Replaced; leaves the board on the next archival pass |

**Provisioning caveat (ai-maestro#43):** provision teams with the **default 17-column
config**, or any set retaining the 11 gate-critical ids. A hand-rolled 14-stage set is
rejected with HTTP 400 for the missing `failed` / `superseded` columns — the exception
columns are load-bearing to the server's gates, not decoration.
