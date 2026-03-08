# AI Maestro Task System Sync

## Table of Contents
- [Task Status Model](#task-status-model)
- [Task File Format](#task-file-format)
- [Sync Operations](#sync-operations)
- [Bidirectional Sync Rules](#bidirectional-sync-rules)
- [Status Mapping: GitHub Kanban Columns to AI Maestro Statuses](#status-mapping-github-kanban-columns-to-ai-maestro-statuses)

All Kanban card movements and issue status changes must be synced with AI Maestro's task system at `~/.aimaestro/teams/tasks-{teamId}.json`.

## Task Status Model

AI Maestro uses a 5-status pipeline for all tasks:

| Status | Description | GitHub Kanban Column | Transitions From | Transitions To |
|--------|-------------|---------------------|------------------|----------------|
| `backlog` | Identified but not yet prioritized | Backlog | (entry) | `pending` |
| `pending` | Prioritized and ready to be picked up | To Do / Ready | `backlog` | `in_progress` |
| `in_progress` | Actively being worked on | In Progress | `pending` | `review` |
| `review` | Work complete, awaiting review/approval | In Review | `in_progress` | `completed`, `in_progress` |
| `completed` | Done and verified | Done | `review` | (terminal) |

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
      "status": "in_progress",
      "assignedAgent": "amoa-backend-auth",
      "teamLabel": "team:backend",
      "designUuid": "abc-123",
      "moduleUuid": "def-456",
      "statusHistory": [
        {"status": "backlog", "timestamp": "2025-01-28T10:00:00Z", "actor": "amama-main"},
        {"status": "pending", "timestamp": "2025-01-29T09:00:00Z", "actor": "amama-main"},
        {"status": "in_progress", "timestamp": "2025-01-30T14:00:00Z", "actor": "amoa-backend-auth"}
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
| GitHub to AI Maestro | Issue closed | Set task status to `completed` |
| GitHub to AI Maestro | Issue reopened | Set task status to `in_progress` |
| AI Maestro to GitHub | Task status changed via API | Move corresponding Kanban card |
| AI Maestro to GitHub | New task created | Create GitHub issue with team label |

## Status Mapping: GitHub Kanban Columns to AI Maestro Statuses

| GitHub Kanban Column | AI Maestro Status |
|---------------------|-------------------|
| Backlog | `backlog` |
| To Do / Ready | `pending` |
| In Progress | `in_progress` |
| In Review / Review | `review` |
| Done / Closed | `completed` |

If a GitHub project uses custom column names, AMAMA must maintain a mapping in:
`~/.aimaestro/teams/kanban-column-map-{teamId}.json`
