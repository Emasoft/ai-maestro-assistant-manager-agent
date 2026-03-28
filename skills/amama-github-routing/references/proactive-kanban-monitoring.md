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

AMAMA must proactively monitor GitHub Project boards to detect changes that may require action or notification to the orchestrator and the user.

### Monitoring Schedule

Poll the GitHub Project API every 5 minutes for changes to project cards:

```bash
# Get project items with status (use amp-kanban-list.sh when available)
gh project item-list <PROJECT_NUMBER> --owner "$OWNER" --format json | jq '
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
| Status changes | Compare `status` field against previous snapshot | Notify orchestrator of card movement |
| New assignees | Compare `assignees` array against previous snapshot | Notify relevant specialist |
| New comments | Check `comments` count increase | Fetch new comments, route to appropriate agent |
| Card created | New `id` not in previous snapshot | Route to orchestrator for triage |
| Card archived | `id` missing from current snapshot | Update internal tracking state |

### Monitoring Procedure

**Step 1: Capture Snapshot**
```bash
# Store current state (inside agent folder, NEVER in /tmp/)
gh project item-list <PROJECT_NUMBER> --owner "$OWNER" --format json > "$AGENT_DIR/tmp/kanban-snapshot-$(date +%s).json"
```

**Step 2: Compare with Previous Snapshot**
```bash
# Compare snapshots to find changes
diff <(jq -S '.items' "$AGENT_DIR/tmp/kanban-snapshot-previous.json") \
     <(jq -S '.items' "$AGENT_DIR/tmp/kanban-snapshot-current.json")
```

**Step 3: Process Detected Changes**

For each detected change:

1. **Status Change Detected**
   Send a kanban update notification to the orchestrator using the `agent-messaging` skill:
   - **Recipient**: `orchestrator-<project>`
   - **Subject**: "Kanban Card Status Changed"
   - **Content**: kanban_update type with card_id, card_title, old_status, new_status, changed_at
   - **Type**: `kanban_update`
   - **Priority**: `normal`

   **Verify**: confirm message delivery via the skill's sent messages feature.

2. **New Assignee Detected**
   - If assignee is a known specialist agent, notify that agent
   - If assignee is external, log for user review

3. **New Comment Detected**
   - Fetch comment content
   - Route to appropriate agent based on card context
   - If comment mentions user action needed, notify user

**Step 4: Update Internal State**
```bash
# Update tracking file
echo "Last sync: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$AGENT_DIR/reports/kanban-sync-log.md"
mv "$AGENT_DIR/tmp/kanban-snapshot-current.json" "$AGENT_DIR/tmp/kanban-snapshot-previous.json"
```

### Kanban Monitoring Checklist

- [ ] GitHub CLI (`gh`) authenticated with project access
- [ ] Previous snapshot exists for comparison
- [ ] Current snapshot captured successfully
- [ ] Changes detected and categorized
- [ ] Orchestrator notified of relevant changes
- [ ] Internal state updated
- [ ] Sync log updated with timestamp

### Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `gh` command fails | Authentication expired | Re-authenticate with `gh auth login` |
| No previous snapshot | First run or file deleted | Create initial snapshot, skip comparison |
| Project not found | Invalid project number | Verify project exists with `gh project list --owner "$OWNER"` |
| Rate limit exceeded | Too many API calls | Increase polling interval to 10 minutes |
