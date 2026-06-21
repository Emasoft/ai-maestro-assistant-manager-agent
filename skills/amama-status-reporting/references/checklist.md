# Status Reporting Checklist

## Table of Contents
- [Status Reporting Checklist](#status-reporting-checklist)

## Checklist

Copy this checklist and track your progress:

- [ ] Determine the type of report needed (quick status, progress, handoff summary, blocker)
- [ ] Verify AI Maestro is reachable (`aimaestro-agent.sh list` exits non-zero if the server is unreachable)
- [ ] Run `aimaestro-agent.sh list` for agent session liveness (active/inactive — proxies agent health)
- [ ] Run `aimaestro-agent.sh list` for registered agents (filter output client-side by `status`)
- [ ] Run `aimaestro-teams.sh show <teamId>` for team status
- [ ] Get team task Kanban data: `aimaestro-teams.sh tasks <teamId>`
- [ ] Verify GitHub CLI is installed and authenticated
- [ ] Query GitHub for issue and PR status
- [ ] Read session memory files for context
- [ ] Compile all information into unified report format
- [ ] Create `design/reports/` directory if it doesn't exist
- [ ] Save report to `design/reports/status-{date}.md`
- [ ] Present formatted report to user
