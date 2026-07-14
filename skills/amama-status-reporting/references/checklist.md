# Status Reporting Checklist

## Table of Contents
- [Status Reporting Checklist](#status-reporting-checklist)

## Checklist

Copy this checklist and track your progress:

- [ ] Determine the type of report needed (quick status, progress, handoff summary, blocker)
- [ ] Verify AI Maestro is reachable (`aimaestro-agent.sh list` exits non-zero if the server is unreachable — check the exit code, keep it bare so a pipe can't mask it)
- [ ] Run `aimaestro-agent.sh list | jq '[.sessions[] | {name, status, uptime}]'` for agent session liveness (active/inactive — proxies agent health)
- [ ] Run `aimaestro-agent.sh list | jq '[.agents[] | {name, status, lastHeartbeat}]'` for registered agents (filter output further client-side by `status`)
- [ ] Run `aimaestro-teams.sh show <teamId> | jq '{name, members, status}'` for team status
- [ ] Run `aimaestro-teams.sh tasks <teamId> | jq '[.tasks[] | {id, title, status, assignee}]'` for team task Kanban data
- [ ] Verify GitHub CLI is installed and authenticated
- [ ] Query GitHub for issue and PR status (`gh issue list --json number,title,state`; `gh pr list --json number,title,state`)
- [ ] Read session memory files for context (only the section relevant to the report type, not whole logs)
- [ ] Compile all information into unified report format
- [ ] Create `reports/status-reporting/` directory if it doesn't exist
- [ ] Save report to `reports/status-reporting/status-{date}.md`
- [ ] Present formatted report to user
