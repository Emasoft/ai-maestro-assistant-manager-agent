# Report Types and Formats - Detailed Reference

## Table of Contents
- [Report Types](#report-types)
- [Output Locations](#output-locations)
- [Report Sections](#report-sections)
- [Full Examples](#full-examples)

## Report Types

| Type | Frequency | Content | Primary Data Source |
|------|-----------|---------|---------------------|
| Quick Status | On demand | Current state summary | `/api/sessions` + `/api/agents` |
| Progress Report | Daily/Weekly | Work completed, in progress, blocked | `/api/teams/{id}/tasks` + GitHub |
| Handoff Summary | On transition | What was handed to whom | `/api/sessions` + handoff files |
| Blocker Report | As needed | What's blocking progress | `/api/teams/{id}/tasks` (pending/in_progress) |

**Note**: Blockers are reported to the user IMMEDIATELY when received, not held for the next scheduled status report.

## Output Locations

| Report Type | Format | Location |
|-------------|--------|----------|
| Quick Status | Markdown summary | `design/reports/status-{date}.md` |
| Progress Report | Markdown with sections | `design/reports/progress-{date}.md` |
| Handoff Summary | Markdown with task lists | `design/reports/handoff-{date}.md` |
| Blocker Report | Markdown with blocker details | `design/reports/blockers-{date}.md` |

## Report Sections

### Quick Status Format
- Agent sessions: online/offline counts (from `/api/sessions`)
- Session liveness: active/inactive (from `/api/sessions` — proxies agent health; no dedicated `/api/agents/health` endpoint exists)
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
- **Agent Status** (from `/api/sessions` + `/api/agents`):
  - Active sessions with uptime
  - Stale / inactive sessions (if any — these proxy "unresponsive" agents)
- **GitHub Status**: Issues closed, PRs merged (from `gh` CLI)
- Risks identified

## Full Examples

### Example 1: Quick Status Report

```markdown
## Quick Status - 2025-01-30

### Agent Sessions
| Agent | Status | Uptime | Last Heartbeat |
|-------|--------|--------|----------------|
| amaa-architect | active | 2h 15m | 30s ago |
| amoa-orchestrator | active | 1h 42m | 15s ago |
| amia-integrator | inactive | — | 45m ago |

Session status proxies agent health: `active` with recent heartbeat = alive, `inactive` with stale heartbeat = unresponsive. There is no separate `/api/agents/health` endpoint.

### Task Kanban
| Status | Count | Tasks |
|--------|-------|-------|
| backlog | 3 | Session mgmt, Logging, Metrics |
| pending | 1 | Auth middleware |
| in_progress | 2 | Login endpoint, User model |
| review | 1 | DB schema |
| completed | 4 | Setup, Config, Router, Models |

**Blockers**: AMIA integrator agent unresponsive — escalating to AMCOS
```

### Example 2: Progress Report

```markdown
## Progress Report - Week of 2025-01-27

### Period Covered
2025-01-27 to 2025-01-30

### Task Kanban Summary (from AI Maestro)
**Completed this period:**
- DB schema design (AMAA, completed 2025-01-28)
- Login endpoint implementation (AMOA, completed 2025-01-29)
- Code review for login (AMIA, completed 2025-01-30)

**In Progress:**
- Logout endpoint (AMOA, started 2025-01-30)
- Session management design (AMAA, started 2025-01-29)

**Pending:**
- Password reset endpoint (blocked by email service config)

**Backlog:**
- OAuth2 integration
- Rate limiting

### Agent Sessions
- AMAA: active, uptime 48h (heartbeat 20s ago)
- AMOA: active, uptime 36h (heartbeat 10s ago)
- AMIA: active, uptime 12h (heartbeat 5s ago)

### GitHub Status
- Issues closed: #45 (auth design), #46 (login impl)
- PRs merged: #12 (db schema), #13 (login endpoint)

### Risks Identified
- Email service integration may delay password reset feature
```
