---
name: amama-status-reporting
description: Use when generating status reports. Queries AI Maestro APIs (sessions, health, teams, tasks) for live data. Trigger with status report requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: true
---

# Status Reporting Skill

## Overview

Generate status reports by querying AI Maestro APIs for live agent, team, and task data. Reports combine API-sourced status with GitHub issue/PR data for a unified view.

## Prerequisites

- AI Maestro running, API reachable at `$AIMAESTRO_API` (default: `http://localhost:23000`)
- GitHub CLI (`gh`) installed for issue/PR status
- `design/reports/` directory must exist (create if missing)

## Instructions

1. Determine report type: quick status, progress, handoff summary, or blocker
2. Query AI Maestro APIs for live data:
   - `GET /api/sessions` -- agent sessions and status
   - `GET /api/agents/health` -- agent health (alive/unresponsive/crashed)
   - `GET /api/teams/{id}` -- team config and members
   - `GET /api/teams/{id}/tasks` -- tasks with Kanban statuses
3. Query GitHub for issue/PR status via `gh` CLI
4. Read session memory files for additional context
5. Compile into report format and save to `design/reports/`
6. Present formatted report to user

Task Kanban statuses flow: `backlog -> pending -> in_progress -> review -> completed`. See `references/task-system.md` for details.

For API query examples, see `references/api-endpoints.md`.

## Output

Reports are saved as Markdown to `design/reports/`:
- `status-{date}.md` -- Quick status
- `progress-{date}.md` -- Progress report
- `handoff-{date}.md` -- Handoff summary
- `blockers-{date}.md` -- Blocker report

For detailed report section formats, see `references/report-formats.md`.

## Error Handling

| Error | Resolution |
|-------|------------|
| API unreachable | Start AI Maestro, report to user |
| No active sessions | Report "no active agent sessions" |
| Agent health: crashed | Escalate to AMCOS for recovery |
| Team/task 404 | Verify team ID, create if needed |
| GitHub API failure | Use cached data, note staleness |
| Report dir missing | Create `design/reports/` automatically |

## Examples

**Quick Status** (abbreviated):
```
## Quick Status - 2025-01-30
### Agent Sessions
| Agent | Status | Uptime |
| amaa-architect | active | 2h 15m |
| amoa-orchestrator | active | 1h 42m |
### Task Kanban
| Status | Count |
| in_progress | 2 |
| completed | 4 |
**Blockers**: AMIA unresponsive -- escalating
```

For full examples including progress reports, see `references/report-formats.md`.

## Checklist

Copy this checklist and track your progress:

- [ ] Determine report type (quick status, progress, handoff, blocker)
- [ ] Query AI Maestro APIs for sessions, health, teams, tasks
- [ ] Query GitHub for issue/PR status via `gh` CLI
- [ ] Read session memory files for context
- [ ] Compile report and save to `design/reports/`
- [ ] Present formatted report to user

For the detailed step-by-step checklist, see `references/checklist.md`.

## Resources

- **AI Maestro API** -- `$AIMAESTRO_API` (default: `http://localhost:23000`)
- **Task storage** -- `~/.aimaestro/teams/tasks-{teamId}.json`
- **amama-role-routing SKILL** -- Agent routing
- **amama-approval-workflows SKILL** -- Approval status
- **amama-session-memory SKILL** -- Session memory access
- `references/api-endpoints.md` -- Full API endpoint details and query examples
- `references/task-system.md` -- Task system and Kanban status details
- `references/report-formats.md` -- Report types, formats, sections, and full examples
- `references/checklist.md` -- Step-by-step execution checklist
