# AI Maestro Status CLIs - Detailed Reference

## Table of Contents
- [CLI Commands](#cli-commands)
- [Query Examples](#query-examples)
- [Task Query for Reports](#task-query-for-reports)

All status data MUST be sourced from the frozen AI Maestro CLIs, not from manual agent queries or guesswork. The CLIs resolve auth internally — no manual Bearer token is required.

## CLI Commands

| Command | Purpose | Returns |
|---------|---------|---------|
| `aimaestro-agent.sh list` | Agent session liveness / connectivity | All active/inactive sessions with metadata (proxies agent health; non-zero exit ⇒ server unreachable) |
| `aimaestro-agent.sh list` | Registered agents | Full agent list; filter output client-side by `status` |
| `aimaestro-teams.sh show <teamId>` | Team status | Team config, members, current state |
| team tasks (Kanban) | Task status — <!-- DECOUPLE-BLOCKED ai-maestro#36: team tasks read — CLI verb not yet deployed --> fall back to `GET /api/teams/{id}/tasks` until a `aimaestro-teams.sh tasks` verb lands | All tasks for team with statuses |

> **Note:** There is no dedicated agent-health command — session liveness from `aimaestro-agent.sh list` (`status: active | inactive`) is the authoritative health signal. The same `list` output carries agent-level state, which you filter client-side.

## Query Examples

```
aimaestro-agent.sh list
Returns: [.sessions[] | {name, status, uptime}]

aimaestro-agent.sh list
Returns: [.agents[] | {name, status, lastHeartbeat}]
# Filter client-side, e.g. jq '.agents[] | select(.status == "available")'

aimaestro-teams.sh show $TEAM_ID
Returns: {name, members, status}

# team tasks: CLI verb not yet deployed (ai-maestro#36) — fall back to the API
GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Returns: [.tasks[] | {id, title, status, assignee}]
```

See the `team-governance` skill for full CLI details.

## Task Query for Reports

When generating status reports, query tasks by status to build Kanban summaries.

<!-- DECOUPLE-BLOCKED ai-maestro#36: team tasks read — CLI verb not yet deployed; the queries below fall back to GET /api/teams/{id}/tasks until a `aimaestro-teams.sh tasks` verb lands -->

```
GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Returns: group_by(.status) | map({status: .[0].status, count: length, tasks: [.[].title]})

GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Filter: .status == "in_progress" or .status == "pending"

GET $AIMAESTRO_API/api/teams/$TEAM_ID/tasks
Filter: .status == "completed"
Returns: [{title, completedAt, assignee}]
```

See the `team-governance` skill for full CLI details.
