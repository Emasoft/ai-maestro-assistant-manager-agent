---
name: amama-status-reporting
description: Use when generating status reports. Queries AI Maestro APIs (sessions, health, teams, tasks) for live data. Trigger with status report requests.
version: 2.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-main
user-invocable: true
triggers:
  - when user asks for status
  - when generating progress reports
  - when summarizing work across agents
---

# Status Reporting Skill

## Overview

Generate comprehensive status reports by querying AI Maestro APIs for live agent, team, and task data. Reports combine API-sourced status with GitHub issue/PR data for a unified view.

## Prerequisites

- AI Maestro messaging system must be running
- AI Maestro API must be reachable at `$AIMAESTRO_API` (default: `http://localhost:23000`)
- GitHub CLI (`gh`) must be installed for issue/PR status
- Session memory files must be accessible
- `docs_dev/reports/` directory must exist

## AI Maestro Status APIs

All status data MUST be sourced from AI Maestro APIs, not from manual agent queries or guesswork.

### API Endpoints

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/sessions` | GET | Agent session status | All active/inactive sessions with metadata |
| `/api/agents/health` | GET | Agent health checks | Health status per agent (alive, unresponsive, crashed) |
| `/api/teams/{id}` | GET | Team status | Team config, members, current state |
| `/api/teams/{id}/tasks` | GET | Task status (Kanban) | All tasks for team with statuses |

### Query Examples

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

## AI Maestro Task System

AI Maestro maintains its own task system, separate from GitHub Issues. Tasks are managed per-team.

### Task Storage

Tasks are stored in: `~/.aimaestro/teams/tasks-{teamId}.json`

### Task Statuses (Kanban)

Tasks flow through exactly 5 statuses:

```
backlog → pending → in_progress → review → completed
```

| Status | Meaning |
|--------|---------|
| `backlog` | Acknowledged but not yet scheduled |
| `pending` | Scheduled, waiting to start |
| `in_progress` | Actively being worked on by an agent |
| `review` | Work done, awaiting review/validation |
| `completed` | Finished and verified |

### Task Query for Reports

When generating status reports, query tasks by status to build Kanban summaries:

```bash
# Get all tasks grouped by status
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq 'group_by(.status) | map({status: .[0].status, count: length, tasks: [.[].title]})'

# Get only blocked/in-progress tasks
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq '[.tasks[] | select(.status == "in_progress" or .status == "pending")]'

# Get completed tasks for progress report
curl -s "$AIMAESTRO_API/api/teams/$TEAM_ID/tasks" | jq '[.tasks[] | select(.status == "completed") | {title, completedAt, assignee}]'
```

## Instructions

1. Determine the type of report needed (quick status, progress, handoff summary, blocker)
2. Query AI Maestro APIs for live data:
   - `GET /api/sessions` — enumerate all agent sessions and their status
   - `GET /api/agents/health` — check agent health (alive, unresponsive, crashed)
   - `GET /api/teams/{id}` — get team configuration and member list
   - `GET /api/teams/{id}/tasks` — get all tasks with Kanban statuses
3. Query GitHub for issue and PR status using `gh` CLI
4. Read session memory files for additional context
5. Compile all information into unified report format
6. Save report to `docs_dev/reports/status-{date}.md`
7. Present formatted report to user

## Report Types

| Type | Frequency | Content | Primary Data Source |
|------|-----------|---------|---------------------|
| Quick Status | On demand | Current state summary | `/api/sessions` + `/api/agents/health` |
| Progress Report | Daily/Weekly | Work completed, in progress, blocked | `/api/teams/{id}/tasks` + GitHub |
| Handoff Summary | On transition | What was handed to whom | `/api/sessions` + handoff files |
| Blocker Report | As needed | What's blocking progress | `/api/teams/{id}/tasks` (pending/in_progress) |

**Note**: Blockers are reported to the user IMMEDIATELY when received, not held for
the next scheduled status report. Status reports should include a summary of
currently blocked tasks and their status (waiting for user, waiting for resource, etc.)
but the initial notification always happens immediately.

## Report Generation Workflow

1. Query `GET /api/sessions` for all agent session statuses
2. Query `GET /api/agents/health` for agent health
3. Query `GET /api/teams/{id}/tasks` for task Kanban data
4. Query GitHub for issue/PR status
5. Read session memory files for context
6. Compile into unified report with API-sourced data
7. Format for user consumption

## Output

| Report Type | Format | Location |
|-------------|--------|----------|
| Quick Status | Markdown summary | `docs_dev/reports/status-{date}.md` |
| Progress Report | Markdown with sections | `docs_dev/reports/progress-{date}.md` |
| Handoff Summary | Markdown with task lists | `docs_dev/reports/handoff-{date}.md` |
| Blocker Report | Markdown with blocker details | `docs_dev/reports/blockers-{date}.md` |

## Report Sections

### Quick Status Format
- Agent sessions: online/offline counts (from `/api/sessions`)
- Agent health: alive/unresponsive/crashed (from `/api/agents/health`)
- Current active tasks (from `/api/teams/{id}/tasks` where status = `in_progress`)
- Next milestone
- Blockers (if any)

### Progress Report Format
- Period covered
- **Kanban Summary** (from `/api/teams/{id}/tasks`):
  - Tasks in `backlog`: count and titles
  - Tasks `pending`: count and titles
  - Tasks `in_progress`: count, titles, assignees
  - Tasks in `review`: count and titles
  - Tasks `completed` (this period): count, titles, completion dates
- **Agent Status** (from `/api/sessions` + `/api/agents/health`):
  - Active sessions with uptime
  - Agent health issues (if any)
- **GitHub Status**: Issues closed, PRs merged (from `gh` CLI)
- Risks identified

## Output Location

Reports saved to: `docs_dev/reports/status-{date}.md`

## Examples

### Example 1: Quick Status Report

```markdown
## Quick Status - 2025-01-30

### Agent Sessions
| Agent | Status | Uptime |
|-------|--------|--------|
| eaa-architect | active | 2h 15m |
| eoa-orchestrator | active | 1h 42m |
| eia-integrator | inactive | — |

### Agent Health
| Agent | Health | Last Heartbeat |
|-------|--------|----------------|
| eaa-architect | alive | 30s ago |
| eoa-orchestrator | alive | 15s ago |
| eia-integrator | unresponsive | 45m ago |

### Task Kanban
| Status | Count | Tasks |
|--------|-------|-------|
| backlog | 3 | Session mgmt, Logging, Metrics |
| pending | 1 | Auth middleware |
| in_progress | 2 | Login endpoint, User model |
| review | 1 | DB schema |
| completed | 4 | Setup, Config, Router, Models |

**Blockers**: EIA integrator agent unresponsive — escalating to AMCOS
```

### Example 2: Progress Report

```markdown
## Progress Report - Week of 2025-01-27

### Period Covered
2025-01-27 to 2025-01-30

### Task Kanban Summary (from AI Maestro)
**Completed this period:**
- DB schema design (EAA, completed 2025-01-28)
- Login endpoint implementation (EOA, completed 2025-01-29)
- Code review for login (EIA, completed 2025-01-30)

**In Progress:**
- Logout endpoint (EOA, started 2025-01-30)
- Session management design (EAA, started 2025-01-29)

**Pending:**
- Password reset endpoint (blocked by email service config)

**Backlog:**
- OAuth2 integration
- Rate limiting

### Agent Health
- EAA: alive, uptime 48h
- EOA: alive, uptime 36h
- EIA: alive, uptime 12h

### GitHub Status
- Issues closed: #45 (auth design), #46 (login impl)
- PRs merged: #12 (db schema), #13 (login endpoint)

### Risks Identified
- Email service integration may delay password reset feature
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| API unreachable | AI Maestro not running | Start AI Maestro, report to user |
| `/api/sessions` returns empty | No active sessions | Report "no active agent sessions" |
| `/api/agents/health` shows crashed | Agent failure | Escalate to AMCOS for recovery |
| `/api/teams/{id}/tasks` 404 | Team not found | Verify team ID, create team if needed |
| GitHub API failure | Auth or rate limit | Use cached data, note staleness |
| Memory file not found | Not initialized | Report "no session data available" |
| Report directory missing | First report | Create `docs_dev/reports/` automatically |
| Task file missing | `~/.aimaestro/teams/tasks-{teamId}.json` not created | Initialize via API or report empty |

## Resources

- **AI Maestro API** — `$AIMAESTRO_API` (default: `http://localhost:23000`)
- **Task storage** — `~/.aimaestro/teams/tasks-{teamId}.json`
- **amama-role-routing SKILL** — Agent routing
- **amama-approval-workflows SKILL** — Approval status
- **amama-session-memory SKILL** — Session memory access

## Checklist

Copy this checklist and track your progress:

- [ ] Determine the type of report needed (quick status, progress, handoff summary, blocker)
- [ ] Verify AI Maestro API is reachable at `$AIMAESTRO_API`
- [ ] Query `GET /api/sessions` for agent session statuses
- [ ] Query `GET /api/agents/health` for agent health data
- [ ] Query `GET /api/teams/{id}` for team status
- [ ] Query `GET /api/teams/{id}/tasks` for task Kanban data
- [ ] Verify GitHub CLI is installed and authenticated
- [ ] Query GitHub for issue and PR status
- [ ] Read session memory files for context
- [ ] Compile all information into unified report format
- [ ] Create `docs_dev/reports/` directory if it doesn't exist
- [ ] Save report to `docs_dev/reports/status-{date}.md`
- [ ] Present formatted report to user
