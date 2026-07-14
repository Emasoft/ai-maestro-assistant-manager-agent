---
name: proactive-kanban-monitoring
description: Proactive GitHub Project board monitoring and notification routing.
version: 1.0.0
parent-skill: amama-github-routing
---

## Table of Contents
- [Proactive Kanban Monitoring](#proactive-kanban-monitoring)
  - [Monitoring Schedule](#monitoring-schedule)
  - [Changes to Monitor](#changes-to-monitor)
  - [Monitoring Procedure](#monitoring-procedure)
  - [Kanban Monitoring Checklist](#kanban-monitoring-checklist)
  - [Error Handling](#error-handling)

---

## Proactive Kanban Monitoring

AMAMA must proactively monitor GitHub Project boards to detect changes that may require action or notification. **Comm-graph v3 (R6 v3):** the MANAGER may NOT message a team-internal agent (ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER) directly — the team's **CHIEF-OF-STAFF is the sole in-team gateway** and relays to the orchestrator/specialists on your behalf. So every in-team notification below is addressed to the team's CHIEF-OF-STAFF; the user (HUMAN) remains directly reachable.

### Monitoring Schedule

Poll the GitHub Project API every 5 minutes for changes to project cards:

```bash
# Get project items with status
gh project item-list <PROJECT_NUMBER> --owner Emasoft --format json | jq '
  .items[] | {
    id: .id,
    title: .title,
    status: .status,
    assignees: .assignees,
    updated: .updatedAt
  }
'
```

### Changes to Monitor

| Change Type | Detection Method | Action |
|-------------|------------------|--------|
| Status changes | Compare `status` field against previous snapshot | Notify the team's CHIEF-OF-STAFF of card movement (COS relays to the orchestrator in-team) |
| New assignees | Compare `assignees` array against previous snapshot | Notify the team's CHIEF-OF-STAFF (COS relays to the relevant specialist in-team) |
| New comments | Check `comments` count increase | Fetch new comments, route to the team's CHIEF-OF-STAFF (COS relays to the appropriate agent) |
| Card created | New "id" value not in previous snapshot | Route to the team's CHIEF-OF-STAFF for triage (COS relays to the orchestrator) |
| Card archived | "id" value missing from current snapshot | Update internal tracking state |

### Monitoring Procedure

**Step 1: Capture Snapshot**
```bash
# Store current state
gh project item-list <PROJECT_NUMBER> --owner Emasoft --format json > /tmp/kanban-snapshot-$(date +%s).json
```

**Step 2: Compare with Previous Snapshot**
```bash
# Compare snapshots to find changes
diff <(jq -S '.items' /tmp/kanban-snapshot-previous.json) \
     <(jq -S '.items' /tmp/kanban-snapshot-current.json)
```

**Step 3: Process Detected Changes**

For each detected change:

1. **Status Change Detected**
   Send a kanban update notification to the team's CHIEF-OF-STAFF using the `agent-messaging` skill (the COS relays it to the orchestrator in-team — R6 v3 forbids a direct MANAGER→orchestrator edge):
   - **Recipient**: the team's CHIEF-OF-STAFF (`cos-<team>`)
   - **Subject**: "Kanban Card Status Changed"
   - **Content**: kanban_update type with card_id, card_title, old_status, new_status, changed_at
   - **Type**: `kanban_update`
   - **Priority**: `normal`

   **Verify**: confirm message delivery via the skill's sent messages feature.

2. **New Assignee Detected**
   - If assignee is a known specialist agent, notify the team's CHIEF-OF-STAFF, which relays to that specialist in-team (R6 v3 — MANAGER may not message a specialist directly)
   - If assignee is external, log for user review

3. **New Comment Detected**
   - Fetch comment content
   - Route to the team's CHIEF-OF-STAFF based on card context (COS relays to the appropriate agent in-team)
   - If comment mentions user action needed, notify the user directly (MANAGER→HUMAN is an allowed edge)

**Step 4: Update Internal State**
```bash
# Update tracking file
echo "Last sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> docs_dev/kanban/sync-log.md
mv /tmp/kanban-snapshot-current.json /tmp/kanban-snapshot-previous.json
```

### Kanban Monitoring Checklist

- [ ] GitHub CLI (`gh`) authenticated with project access
- [ ] Previous snapshot exists for comparison
- [ ] Current snapshot captured successfully
- [ ] Changes detected and categorized
- [ ] Team's CHIEF-OF-STAFF notified of relevant changes (COS relays in-team; no direct MANAGER→orchestrator/specialist edge, R6 v3)
- [ ] Internal state updated
- [ ] Sync log updated with timestamp

### Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `gh` command fails | Authentication expired | Re-authenticate with `gh auth login` |
| No previous snapshot | First run or file deleted | Create initial snapshot, skip comparison |
| Project not found | Invalid project number | Verify project exists with `gh project list --owner Emasoft` |
| Rate limit exceeded | Too many API calls | Increase polling interval to 10 minutes |
