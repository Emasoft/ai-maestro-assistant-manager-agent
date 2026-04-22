# AI Maestro Status APIs - Detailed Reference

## Table of Contents
- [API Endpoints](#api-endpoints)
- [Query Examples](#query-examples)
- [Task Query for Reports](#task-query-for-reports)

All status data MUST be sourced from AI Maestro APIs, not from manual agent queries or guesswork.

## API Endpoints

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/sessions` | GET | Agent session liveness | All active/inactive sessions with metadata (proxies agent health) |
| `/api/agents` | GET | Registered agents | Full agent list; filter response client-side by `status` |
| `/api/teams/{id}` | GET | Team status | Team config, members, current state |
| `/api/teams/{id}/tasks` | GET | Task status (Kanban) | All tasks for team with statuses |

> **Note:** There is no `/api/agents/health` endpoint — session liveness from `/api/sessions` (`status: active | inactive`) is the authoritative health signal. Agent-level state comes from `/api/agents`, which you filter client-side.

## Query Examples

```
GET $AIMAESTRO_API/api/sessions
Returns: [.sessions[] | {name, status, uptime}]

GET $AIMAESTRO_API/api/agents
Returns: [.agents[] | {name, status, lastHeartbeat}]
# Filter client-side, e.g. jq '.agents[] | select(.status == "available")'

GET $AIMAESTRO_API/api/teams/$TEAM_ID
Returns: {name, members, status}

GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Returns: [.tasks[] | {id, title, status, assignee}]
```

See the `team-governance` skill for full API details.

## Task Query for Reports

When generating status reports, query tasks by status to build Kanban summaries:

```
GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Returns: group_by(.status) | map({status: .[0].status, count: length, tasks: [.[].title]})

GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Filter: .status == "in_progress" or .status == "pending"

GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Filter: .status == "completed"
Returns: [{title, completedAt, assignee}]
```

See the `team-governance` skill for full API details.
