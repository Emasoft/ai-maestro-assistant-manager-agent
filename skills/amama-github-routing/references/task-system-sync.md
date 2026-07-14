# AI Maestro Task System Sync

## Table of Contents
- [Task Status Model](#task-status-model)
- [Task File Format](#task-file-format)
- [Sync Operations](#sync-operations)
- [Bidirectional Sync Rules](#bidirectional-sync-rules)
- [Status Mapping: GitHub Kanban Columns to AI Maestro Statuses](#status-mapping-github-kanban-columns-to-ai-maestro-statuses)

All Kanban card movements and issue status changes must be synced with AI Maestro's task system at `~/.aimaestro/teams/tasks-{teamId}.json`.

## Task Status Model

AI Maestro's task status is the **ratified 17-column kanban vocabulary**, 1:1 with the
TRDD `column:` field. It is the single source of truth — every consumer (this task file,
the GitHub Project board, `amp-kanban-*.sh`, role-plugins) aligns TO it, never the reverse
(ai-maestro R25 / TRDD-YUGDER9D). The set is **14 lifecycle** columns followed by **3
exception** columns:

| # | Status | Kind | GitHub Project Status option |
|---|--------|------|------------------------------|
| 1 | `backburner` | lifecycle | Backburner |
| 2 | `todo` | lifecycle | To Do |
| 3 | `design` | lifecycle | Design |
| 4 | `dispatch` | lifecycle | Dispatch |
| 5 | `dev` | lifecycle | Dev |
| 6 | `testing` | lifecycle | Testing |
| 7 | `ai_review` | lifecycle | AI Review |
| 8 | `human_review` | lifecycle | Human Review |
| 9 | `complete` | lifecycle | Complete |
| 10 | `publish` | lifecycle | Publish |
| 11 | `published` | lifecycle | Published |
| 12 | `deploy` | lifecycle | Deploy |
| 13 | `live` | lifecycle | Live |
| 14 | `live_auditing` | lifecycle | Live Auditing |
| 15 | `blocked` | exception | Blocked |
| 16 | `failed` | exception | Failed |
| 17 | `superseded` | exception | Superseded |

Lifecycle order: `backburner → todo → design → dispatch → dev → testing → ai_review →
human_review → complete`, then `publish → published` (tools) or `deploy → live →
live_auditing` (services). The exception columns are orthogonal: `blocked` (has an unmet
`blocked-by:`), `failed` (retryable — stays OPEN), `superseded`. GitHub-Project Status
options mirror these 17 labels exactly.

## Task File Format

**Location**: `~/.aimaestro/teams/tasks-{teamId}.json`

```json
{
  "teamId": "backend",
  "lastUpdated": "2025-01-30T15:00:00Z",
  "tasks": [
    {
      "id": "task-uuid-001",
      "githubIssue": 45,
      "githubRepo": "owner/repo",
      "title": "Implement user auth",
      "status": "dev",
      "assignedAgent": "amoa-backend-auth",
      "teamLabel": "team:backend",
      "designUuid": "abc-123",
      "moduleUuid": "def-456",
      "statusHistory": [
        {"status": "backburner", "timestamp": "2025-01-28T10:00:00Z", "actor": "amama-main"},
        {"status": "todo", "timestamp": "2025-01-29T09:00:00Z", "actor": "amama-main"},
        {"status": "dev", "timestamp": "2025-01-30T14:00:00Z", "actor": "amoa-backend-auth"}
      ],
      "createdAt": "2025-01-28T10:00:00Z",
      "updatedAt": "2025-01-30T14:00:00Z"
    }
  ]
}
```

## Sync Operations

Every GitHub status change triggers a sync to the task file:

```bash
# Read current task state
TASK_FILE="$HOME/.aimaestro/teams/tasks-${TEAM_ID}.json"

# Update task status (using jq for atomic JSON update)
jq --arg taskId "$TASK_ID" --arg newStatus "$NEW_STATUS" --arg actor "$SESSION_NAME" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '(.tasks[] | select(.id == $taskId)) |= (
    .status = $newStatus |
    .updatedAt = $ts |
    .statusHistory += [{"status": $newStatus, "timestamp": $ts, "actor": $actor}]
  ) | .lastUpdated = $ts' \
  "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
```

## Bidirectional Sync Rules

| Direction | Trigger | Action |
|-----------|---------|--------|
| GitHub to AI Maestro | Kanban card moved | Update `tasks-{teamId}.json` with new status |
| GitHub to AI Maestro | Issue closed | Set task status to `complete` |
| GitHub to AI Maestro | Issue reopened | Set task status to `dev` |
| AI Maestro to GitHub | Task status changed via API | Move corresponding Kanban card |
| AI Maestro to GitHub | New task created | Create GitHub issue with team label |

## Status Mapping: GitHub Kanban Columns to AI Maestro Statuses

The canonical GitHub-Project Status field carries all 17 columns 1:1 (see the Task Status
Model table above). A board that renders a coarser summary view GROUPS columns for display,
but every mutation must round-trip back to the full 17-column vocabulary:

| Coarse GitHub board column | AI Maestro Status(es) it groups |
|----------------------------|---------------------------------|
| Backlog | `backburner` |
| To Do / Ready | `todo`, `design`, `dispatch` |
| In Progress | `dev`, `testing` |
| In Review | `ai_review`, `human_review` |
| Done | `complete`, `publish`, `published`, `deploy`, `live`, `live_auditing` |
| Blocked / Failed | `blocked`, `failed`, `superseded` |

If a GitHub project uses custom column names, AMAMA must maintain a mapping in:
`~/.aimaestro/teams/kanban-column-map-{teamId}.json` — but the mapping always resolves to
one of the ratified 17 columns; never invent a new column value.
