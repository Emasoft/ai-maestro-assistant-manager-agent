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

AMAMA must proactively monitor GitHub Project boards to detect changes that may require action or notification to the team's CHIEF-OF-STAFF and the user.

> **Routing invariant (comm-graph v3, R6 v3) — read before every notification below.**
> The CHIEF-OF-STAFF is the **SOLE entry point into a team**. As MANAGER you may
> message HUMAN, peer MANAGERs, CHIEF-OF-STAFF, AUTONOMOUS, and MAINTAINER —
> and **never** a team-internal agent directly (ORCHESTRATOR, ARCHITECT,
> INTEGRATOR, MEMBER, or any custom team-layer title). Every notification in this
> file therefore goes to the team's COS, who relays in-team.
> **Why this is a hard rule:** messaging an ORCHESTRATOR or a specialist directly
> leaves the COS (and often the team's own ORCHESTRATOR) uninformed or already
> issuing contradictory instructions — which produced real workflow chaos and is
> exactly what R6 v3 removed that edge to prevent. See the persona's "legitimate
> recipients" section.

### Monitoring Schedule

Poll the GitHub Project API every 5 minutes for changes to project cards:

```bash
# Poll project items (fields of interest) into a snapshot file — do NOT print to stdout
gh project item-list <PROJECT_NUMBER> --owner Emasoft --format json | jq '
  .items[] | {
    id: .id,
    title: .title,
    status: .status,
    assignees: .assignees,
    updated: .updatedAt
  }
' > /tmp/kanban-poll-$(date +%s).json
```

### Changes to Monitor

| Change Type | Detection Method | Action |
|-------------|------------------|--------|
| Status changes | Compare `status` field against previous snapshot | Notify the team's **CHIEF-OF-STAFF** of card movement |
| New assignees | Compare `assignees` array against previous snapshot | Notify the team's **CHIEF-OF-STAFF** (it relays to the assignee — never message a specialist directly) |
| New comments | Check `comments` count increase | Fetch new comments, route via the team's **CHIEF-OF-STAFF** |
| Card created | New "id" value not in previous snapshot | Route to the team's **CHIEF-OF-STAFF** for triage |
| Card archived | "id" value missing from current snapshot | Update internal tracking state |

### Monitoring Procedure

**Step 1: Capture Snapshot**
```bash
# Store current state
gh project item-list <PROJECT_NUMBER> --owner Emasoft --format json > /tmp/kanban-snapshot-$(date +%s).json
```

**Step 2: Compare with Previous Snapshot**
```bash
# Compare snapshots on ONLY the monitored fields, capture the diff to a file (do NOT print it)
diff <(jq -S '[.items[] | {id, status, assignees}]' /tmp/kanban-snapshot-previous.json) \
     <(jq -S '[.items[] | {id, status, assignees}]' /tmp/kanban-snapshot-current.json) \
     > /tmp/kanban-diff-$(date +%s).txt
# Report a summary ONLY — never the raw diff text. Per "Changes to Monitor" above,
# extract the changed card ids from the diff file and report: "N changes: [card-id list]".
```

**Step 3: Process Detected Changes**

For each detected change:

1. **Status Change Detected**
   Send a kanban update notification to the team's **CHIEF-OF-STAFF** using the `agent-messaging` skill:
   - **Recipient**: the team's `chief-of-staff` agent (**never** `orchestrator-<project>` — that edge is forbidden under R6 v3; the COS relays to the ORCHESTRATOR)
   - **Subject**: "Kanban Card Status Changed"
   - **Content**: kanban_update type with card_id, card_title, old_status, new_status, changed_at
   - **Type**: `kanban_update`
   - **Priority**: `normal`

   **Verify**: confirm message delivery via the skill's sent messages feature.

2. **New Assignee Detected**
   - If the assignee is a team-internal agent, notify the team's **CHIEF-OF-STAFF** and let it relay — do **not** message the specialist directly
   - If the assignee is an AUTONOMOUS or MAINTAINER agent, you may notify it directly (both are governance-layer peers, not team-internal)
   - If assignee is external, log for user review

3. **New Comment Detected**
   - Fetch comment content
   - Route via the team's **CHIEF-OF-STAFF** based on card context (the COS is the team's sole entry point)
   - If comment mentions user action needed, notify user

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
- [ ] Team's CHIEF-OF-STAFF notified of relevant changes (never the ORCHESTRATOR or a specialist directly — R6 v3)
- [ ] Internal state updated
- [ ] Sync log updated with timestamp

### Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `gh` command fails | Authentication expired | Re-authenticate with `gh auth login` |
| No previous snapshot | First run or file deleted | Create initial snapshot, skip comparison |
| Project not found | Invalid project number | Verify project exists with `gh project list --owner Emasoft` |
| Rate limit exceeded | Too many API calls | Increase polling interval to 10 minutes |
