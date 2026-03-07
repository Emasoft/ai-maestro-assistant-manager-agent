# AI Maestro Status APIs - Detailed Reference

<!-- TOC -->
- [API Endpoints](#api-endpoints)
- [Query Examples](#query-examples)
- [Task Query for Reports](#task-query-for-reports)
<!-- /TOC -->

All status data MUST be sourced from AI Maestro APIs, not from manual agent queries or guesswork.

## API Endpoints

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/sessions` | GET | Agent session status | All active/inactive sessions with metadata |
| `/api/agents/health` | GET | Agent health checks | Health status per agent (alive, unresponsive, crashed) |
| `/api/teams/{id}` | GET | Team status | Team config, members, current state |
| `/api/teams/{id}/tasks` | GET | Task status (Kanban) | All tasks for team with statuses |

## Query Examples

```bash
# Get all active agent sessions
curl -s "$AIMAESTRO_API/api/sessions" | jq '.sessions[] | {name, status, uptime}'

# Get agent health status
curl -s "$AIMAESTRO_API/api/agents/health" | jq '.agents[] | {name, health, lastHeartbeat}'

# Get team status
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID" | jq '{name, members, status}'

# Get team tasks (Kanban board)
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq '.tasks[] | {id, title, status, assignee}'
```

## Task Query for Reports

When generating status reports, query tasks by status to build Kanban summaries:

```bash
# Get all tasks grouped by status
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq 'group_by(.status) | map({status: .[0].status, count: length, tasks: [.[].title]})'

# Get only blocked/in-progress tasks
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq '[.tasks[] | select(.status == "in_progress" or .status == "pending")]'

# Get completed tasks for progress report
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq '[.tasks[] | select(.status == "completed") | {title, completedAt, assignee}]'
```
