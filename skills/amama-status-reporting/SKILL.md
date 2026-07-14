---
name: amama-status-reporting
description: Use when generating status reports. Queries the frozen AI Maestro CLIs (sessions, agents, teams, tasks) for live data. Trigger with status report requests.
compatibility: Requires AI Maestro installed.
context: fork
agent: ai-maestro-assistant-manager-agent-main-agent
user-invocable: true
---

# Status Reporting Skill

## Overview

Generate status reports by querying the frozen AI Maestro CLIs for live agent, team, and task data. Reports combine CLI-sourced status with GitHub issue/PR data for a unified view. **Never call the AI Maestro server's HTTP surface directly (R23)** — the CLIs are the only sanctioned interface and they resolve auth themselves.

> **RULE 1 — status ≠ work order:** a status/progress request is informational ONLY.
> Generating or presenting a report NEVER authorizes starting, resuming, or approving
> project work — even when the report surfaces pending or blocked items. Wait for an
> explicit, separate work instruction.

## Prerequisites

- AI Maestro running and reachable (the frozen CLIs resolve auth internally)
- GitHub CLI (`gh`) installed for issue/PR status
- `reports/status-reporting/` directory must exist (create if missing)

## Instructions

1. Determine report type: quick status, progress, handoff summary, or blocker
2. Query AI Maestro via the frozen CLIs for live data:
   - `aimaestro-agent.sh list` -- session liveness / connectivity (non-zero exit ⇒ server unreachable; proxies agent health, no separate health endpoint). Check the **exit code** — keep it bare, do NOT pipe (a pipe would mask the CLI's exit status)
   - `aimaestro-agent.sh list | jq '[.agents[] | {name, status, lastHeartbeat}]'` -- registered agents (project to report fields; filter further client-side by `status`)
   - `aimaestro-teams.sh show <teamId> | jq '{name, members, status}'` -- team config and members
   - `aimaestro-teams.sh tasks <teamId> | jq '[.tasks[] | {id, title, status, assignee}]'` -- team tasks with Kanban statuses
3. Query GitHub for issue/PR status via `gh` CLI, projecting fields so bodies don't flood context: `gh issue list --json number,title,state` and `gh pr list --json number,title,state`
4. Read session memory files for additional context — only the section/recent entries relevant to the report type (e.g. active sessions for a handoff, recent user-interactions for a status report), not the whole logs
5. Compile into report format and save to `reports/status-reporting/`
6. Present formatted report to user

Task Kanban statuses flow: `backlog -> pending -> in_progress -> review -> completed`. See task-system reference for details.

For CLI query examples, see api-endpoints reference.

## Output

Reports are saved as Markdown to `reports/status-reporting/`:
- `status-{date}.md` -- Quick status
- `progress-{date}.md` -- Progress report
- `handoff-{date}.md` -- Handoff summary
- `blockers-{date}.md` -- Blocker report

For detailed report section formats, see report-formats reference.

## Error Handling

| Error | Resolution |
|-------|------------|
| AI Maestro unreachable (CLI exits non-zero) | Start AI Maestro, report to user |
| No active sessions | Report "no active agent sessions" |
| Session inactive / stale | Escalate to AMCOS for recovery |
| Team/task 404 | Verify team ID, create if needed |
| GitHub API failure | Use cached data, note staleness |
| Report dir missing | Create `reports/status-reporting/` automatically |

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

For full examples including progress reports, see report-formats reference.

## Checklist

Copy this checklist and track your progress:

- [ ] Determine report type (quick status, progress, handoff, blocker)
- [ ] Query the frozen AI Maestro CLIs for sessions, agents, teams, tasks
- [ ] Query GitHub for issue/PR status via `gh` CLI (`gh issue list --json number,title,state`; `gh pr list --json number,title,state`)
- [ ] Read session memory files for context (only the section relevant to the report type, not whole logs)
- [ ] Compile report and save to `reports/status-reporting/`
- [ ] Present formatted report to user

## Resources

- [api-endpoints](references/api-endpoints.md) -- Frozen-CLI verb details and query examples
  - CLI Commands
  - Query Examples
  - Task Query for Reports
- [task-system](references/task-system.md) -- Task system and Kanban status details
  - Task Storage
  - Task Statuses (Kanban)
- [report-formats](references/report-formats.md) -- Report types, formats, and full examples
  - Report Types
  - Output Locations
  - Report Sections
  - Full Examples
- [checklist](references/checklist.md) -- Step-by-step execution checklist
  - Status Reporting Checklist
  - Table of Contents
  - Determine report type
  - Verify AI Maestro reachable
  - Query agent sessions via CLI
  - Query registered agents via CLI
  - Query team status via CLI
  - Query team tasks via CLI
  - Verify GitHub CLI
  - Query GitHub issues and PRs
  - Read session memory files
  - Compile into report format
  - Create reports directory
  - Save report to file
  - Present report to user
