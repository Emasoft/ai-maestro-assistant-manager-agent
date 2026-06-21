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
| `aimaestro-teams.sh tasks <teamId>` | Team task status (Kanban) | All tasks for team with statuses (wraps GET /api/teams/<id>/tasks) |

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

aimaestro-teams.sh tasks $TEAM_ID
Returns: [.tasks[] | {id, title, status, assignee}]
```

See the `team-governance` skill for full CLI details.

## Task Query for Reports

When generating status reports, query tasks by status to build Kanban summaries.

```
aimaestro-teams.sh tasks $TEAM_ID
Returns: group_by(.status) | map({status: .[0].status, count: length, tasks: [.[].title]})

aimaestro-teams.sh tasks $TEAM_ID
Filter: .status == "in_progress" or .status == "pending"

aimaestro-teams.sh tasks $TEAM_ID
Filter: .status == "completed"
Returns: [{title, completedAt, assignee}]
```

See the `team-governance` skill for full CLI details.
