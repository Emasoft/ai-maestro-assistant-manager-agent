# AI Maestro Task System Sync

## Table of Contents
- [Task Column Model (the ratified 17 columns)](#task-column-model-the-ratified-17-columns)
- [Exception Columns](#exception-columns)
- [Release Path Selection](#release-path-selection)
- [Task File Format](#task-file-format)
- [Sync Operations](#sync-operations)
- [Bidirectional Sync Rules](#bidirectional-sync-rules)
- [Column Mapping: GitHub Project Status Options to AI Maestro Columns](#column-mapping-github-project-status-options-to-ai-maestro-columns)

All Kanban card movements and issue status changes must be synced with AI Maestro's task system at `~/.aimaestro/teams/tasks-{teamId}.json`.

## Task Column Model (the ratified 17 columns)

AI Maestro's board has exactly **17 columns**, 1:1 with the TRDD `column:` field. This
vocabulary is CANONICAL: the GitHub Project's "Status" single-select options, the
`status:*` labels, and the task file's `column` value all align **to** it — never the
reverse. Do not invent columns, rename them, or collapse them.

**14 lifecycle columns**, in pipeline order:

| # | Column | Description | GitHub Project Status option | Transitions From | Transitions To |
|---|--------|-------------|------------------------------|------------------|----------------|
| 1 | `backburner` | Captured, not yet prioritized | Backburner | (entry) | `todo` |
| 2 | `todo` | Prioritized, ready to be picked up | Todo | `backburner` | `design` |
| 3 | `design` | Being decomposed and specced (ARCHITECT) | Design | `todo` | `dispatch` |
| 4 | `dispatch` | Design done, awaiting assignment to a member | Dispatch | `design` | `dev` |
| 5 | `dev` | Actively being implemented | Dev | `dispatch`, `testing`, `ai_review`, `human_review`, `failed` | `testing` |
| 6 | `testing` | Gates running (lint, types, unit/e2e, CI) | Testing | `dev` | `ai_review` (all gates PASSED), `dev` (a gate FAILED) |
| 7 | `ai_review` | AI reviewer inspecting the work | AI Review | `testing` | `human_review`, `complete`, `dev` (rejected) |
| 8 | `human_review` | Escalated to a human, surfaced by the MANAGER | Human Review | `ai_review` | `complete`, `dev` |
| 9 | `complete` | Done and verified; not yet released | Complete | `ai_review`, `human_review` | `publish`, `deploy`, or terminal (`release-via: none`) |
| 10 | `publish` | Release pipeline running (tools) | Publish | `complete` | `published` |
| 11 | `published` | Released to its registry/marketplace | Published | `publish` | (terminal) |
| 12 | `deploy` | Deployment pipeline running (services) | Deploy | `complete` | `live` |
| 13 | `live` | Running in production | Live | `deploy` | `live_auditing` |
| 14 | `live_auditing` | Post-deploy soak / audit window | Live Auditing | `live` | `live` (soak clean), `dev` (defect found) |

## Exception Columns

The remaining **3 columns are exceptions** — orthogonal to the pipeline, not a stage in it:

| Column | Description | GitHub Project Status option | Rules |
|--------|-------------|------------------------------|-------|
| `blocked` | Cannot proceed until a dependency clears | Blocked | Applies whenever `blocked-by:` is non-empty. On entry, record `pre-block-column` (the column the task was in). When `blocked-by:` empties, restore the task to `pre-block-column` — never to a guessed column. |
| `failed` | An attempt failed | Failed | **NOT terminal and NOT archived.** A `failed` task STAYS on the board and is retried: fix the cause, then move it back to `dev`. Only an explicit decision to give up converts it to `cancelled` (an archival lifecycle value, not a board column). |
| `superseded` | Replaced by another task | Superseded | Terminal. Record the superseding task's id; the card leaves the board on the next archival pass. |

## Release Path Selection

Which columns a task visits after `complete` is decided by its `release-via` value —
it is never a free choice:

| `release-via` | Path after `complete` |
|---------------|-----------------------|
| `publish` (tools, plugins, packages) | `complete` -> `publish` -> `published` |
| `deploy` (services) | `complete` -> `deploy` -> `live` -> `live_auditing` |
| `none` | `complete` is terminal |

## Task File Format

**Location**: `~/.aimaestro/teams/tasks-{teamId}.json`

The `column` field holds one of the 17 ratified columns. `preBlockColumn` is set only
while `column` is `blocked`, and `releaseVia` selects the post-`complete` path above.

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
      "column": "dev",
      "preBlockColumn": null,
      "blockedBy": [],
      "releaseVia": "publish",
      "assignedAgent": "amoa-backend-auth",
      "teamLabel": "team:backend",
      "designUuid": "abc-123",
      "moduleUuid": "def-456",
      "columnHistory": [
        {"column": "backburner", "timestamp": "2025-01-28T10:00:00Z", "actor": "amama-main"},
        {"column": "todo", "timestamp": "2025-01-29T09:00:00Z", "actor": "amama-main"},
        {"column": "design", "timestamp": "2025-01-29T11:00:00Z", "actor": "amaa-backend"},
        {"column": "dispatch", "timestamp": "2025-01-29T16:00:00Z", "actor": "amcos-backend"},
        {"column": "dev", "timestamp": "2025-01-30T14:00:00Z", "actor": "amoa-backend-auth"}
      ],
      "createdAt": "2025-01-28T10:00:00Z",
      "updatedAt": "2025-01-30T14:00:00Z"
    }
  ]
}
```

## Sync Operations

Every GitHub column change triggers a sync to the task file:

```bash
# Read current task state
TASK_FILE="$HOME/.aimaestro/teams/tasks-${TEAM_ID}.json"

# Update task column (using jq for atomic JSON update)
jq --arg taskId "$TASK_ID" --arg newColumn "$NEW_COLUMN" --arg actor "$SESSION_NAME" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '(.tasks[] | select(.id == $taskId)) |= (
    .column = $newColumn |
    .updatedAt = $ts |
    .columnHistory += [{"column": $newColumn, "timestamp": $ts, "actor": $actor}]
  ) | .lastUpdated = $ts' \
  "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
```

Blocking and unblocking are the two moves that also touch `preBlockColumn`:

```bash
# Block: stash the current column BEFORE overwriting it, so the restore is exact
jq --arg taskId "$TASK_ID" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '(.tasks[] | select(.id == $taskId)) |= (
    .preBlockColumn = .column | .column = "blocked" | .updatedAt = $ts
  ) | .lastUpdated = $ts' \
  "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"

# Unblock: restore to the stashed column — never guess a column here
jq --arg taskId "$TASK_ID" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '(.tasks[] | select(.id == $taskId)) |= (
    .column = .preBlockColumn | .preBlockColumn = null | .updatedAt = $ts
  ) | .lastUpdated = $ts' \
  "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
```

## Bidirectional Sync Rules

| Direction | Trigger | Action |
|-----------|---------|--------|
| GitHub to AI Maestro | Kanban card moved | Update `tasks-{teamId}.json` with the new column |
| GitHub to AI Maestro | Issue closed after a clean release | Set the task column to `published` (tools) or `live` (services), per `releaseVia` |
| GitHub to AI Maestro | Issue closed with no release step (`releaseVia: none`) | Set the task column to `complete` |
| GitHub to AI Maestro | Issue reopened | Set the task column to `dev` |
| GitHub to AI Maestro | Blocking dependency added (`blocked-by` non-empty) | Stash `preBlockColumn`, set column to `blocked` |
| GitHub to AI Maestro | Blocking dependency cleared | Restore the column from `preBlockColumn` |
| AI Maestro to GitHub | Task column changed via API | Move the corresponding Kanban card to the matching Status option |
| AI Maestro to GitHub | New task created | Create a GitHub issue with the team label and `status:backburner` |

## Column Mapping: GitHub Project Status Options to AI Maestro Columns

The GitHub Project's "Status" single-select **must** offer exactly these 17 options —
one per ratified column, in this order:

| # | GitHub Project Status option | AI Maestro Column | Label |
|---|------------------------------|-------------------|-------|
| 1 | Backburner | `backburner` | `status:backburner` |
| 2 | Todo | `todo` | `status:todo` |
| 3 | Design | `design` | `status:design` |
| 4 | Dispatch | `dispatch` | `status:dispatch` |
| 5 | Dev | `dev` | `status:dev` |
| 6 | Testing | `testing` | `status:testing` |
| 7 | AI Review | `ai_review` | `status:ai_review` |
| 8 | Human Review | `human_review` | `status:human_review` |
| 9 | Complete | `complete` | `status:complete` |
| 10 | Publish | `publish` | `status:publish` |
| 11 | Published | `published` | `status:published` |
| 12 | Deploy | `deploy` | `status:deploy` |
| 13 | Live | `live` | `status:live` |
| 14 | Live Auditing | `live_auditing` | `status:live_auditing` |
| 15 | Blocked | `blocked` | `status:blocked` |
| 16 | Failed | `failed` | `status:failed` |
| 17 | Superseded | `superseded` | `status:superseded` |

A board may GROUP columns for a coarser display (e.g. a 4-lane summary view), but every
mutation must round-trip back to the full 17-column vocabulary.

If a GitHub project uses custom column names, AMAMA must maintain a mapping of those
names onto these 17 columns in:
`~/.aimaestro/teams/kanban-column-map-{teamId}.json`
