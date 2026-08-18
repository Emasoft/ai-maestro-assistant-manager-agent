# AI Maestro Status CLIs - Detailed Reference

## Table of Contents
- [CLI Commands](#cli-commands)
- [Query Examples](#query-examples)
- [Task Query for Reports](#task-query-for-reports)

All status data MUST be sourced from the frozen AI Maestro CLIs, not from manual agent queries or guesswork. The CLIs resolve auth internally — **never assemble a Bearer header, an endpoint URL, or a curl command (R23)**.

## CLI Commands

| Command | Purpose | Returns |
|---------|---------|---------|
| `aimaestro-agent.sh list` | Agent session liveness / connectivity | All active/inactive sessions with metadata (proxies agent health; non-zero exit ⇒ server unreachable) |
| `aimaestro-agent.sh list` | Registered agents | Full agent list; filter output client-side by `status` |
| `aimaestro-teams.sh show <teamId>` | Team status | Team config, members, current state |
| `aimaestro-teams.sh tasks <teamId>` | Task status (Kanban) | All tasks for the team with statuses |

> **Note:** There is no dedicated agent-health command — session liveness from `aimaestro-agent.sh list` (`status: active | inactive`) is the authoritative health signal. The same `list` output carries agent-level state, which you filter client-side.

## Query Examples

```
aimaestro-agent.sh list | jq '[.sessions[] | {name, status, uptime}]'

aimaestro-agent.sh list | jq '[.agents[] | {name, status, lastHeartbeat}]'
# Narrow further client-side, e.g. append | jq '[.agents[] | select(.status == "available")]'

aimaestro-teams.sh show $TEAM_ID | jq '{name, members, status}'

aimaestro-teams.sh tasks $TEAM_ID | jq '[.tasks[] | {id, title, status, assignee}]'
```

See the `team-governance` skill for full CLI details.

## TRDD-Corpus Queries (per-project, offline)

For the project-level TRDD board (the 3-pillars SSOT, distinct from the server team
kanban) use the pillar tools from the project root — no server round-trip:

```
trddgrep                # the board (per-column card list)
trddgrep next           # workable cards ranked by what finishing them frees
trddgrep roots          # root blockers — the critical path for a blocker report
trddgrep why <id8>      # one card's transitive blocker chain
prrdgrep <pattern>      # PRRD rules · specgrep <pattern> for normative specs
```

Exit trichotomy: 0 clean · 1 findings · 2 could-not-run (empty corpus = 2; check
`trddgrep env`). Never `trddgrep validate || …`.

## Task Query for Reports

When generating status reports, query tasks by status to build Kanban summaries. `aimaestro-teams.sh tasks` prints JSON on stdout, so pipe it straight into `jq`.

```
aimaestro-teams.sh tasks $TEAM_ID | jq '.tasks | group_by(.status) | map({status: .[0].status, count: length, tasks: [.[].title]})'

aimaestro-teams.sh tasks $TEAM_ID | jq '[.tasks[] | select(.status == "in_progress" or .status == "pending")]'

aimaestro-teams.sh tasks $TEAM_ID | jq '[.tasks[] | select(.status == "completed") | {title, completedAt, assignee}]'
```

See the `team-governance` skill for full CLI details.
