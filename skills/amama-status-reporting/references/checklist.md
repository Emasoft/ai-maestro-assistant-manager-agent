# Status Reporting Checklist

<!-- TOC -->
(Single-section checklist -- no subsections)
<!-- /TOC -->

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
- [ ] Create `design/reports/` directory if it doesn't exist
- [ ] Save report to `design/reports/status-{date}.md`
- [ ] Present formatted report to user
