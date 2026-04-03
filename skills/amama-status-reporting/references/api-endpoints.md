# AI Maestro Status APIs - Detailed Reference

## Table of Contents
- [API Endpoints](#api-endpoints)
- [Query Examples](#query-examples)
- [Task Query for Reports](#task-query-for-reports)

All status data MUST be sourced from AI Maestro APIs, not from manual agent queries or guesswork.

## API Endpoints

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/sessions` | GET | Agent session status | All active/inactive sessions with metadata |
| `/api/agents/health` | GET | Agent health checks | Health status per agent (alive, unresponsive, crashed) |
| `/api/teams/{id}` | GET | Team status | Team config, members, current state |
| `/api/teams/{id}/tasks` | GET | Task status (Kanban) | All tasks for team with statuses |

## Query Examples

```
GET $AIMAESTRO_API/api/sessions
Returns: [.sessions[] | {name, status, uptime}]

GET $AIMAESTRO_API/api/agents/health
Returns: [.agents[] | {name, health, lastHeartbeat}]

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
