---
name: amama-label-taxonomy
description: Use when managing GitHub issue labels or priorities. Trigger with label or triage requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# AMAMA Label Taxonomy

## Overview

Label taxonomy for AMAMA. Manages priority labels, status labels, and translates label states into user messages.

## Prerequisites

1. GitHub CLI (`gh`) available
2. Repo with GitHub issue tracking enabled
3. AMAMA role context (user communication, role routing)

## Instructions

1. **Analyze request** -- determine priority (`priority:critical|high|normal|low`) and type (`type:bug|feature|...`)
2. **Create issue** with labels: `status:backlog`, `priority:*`, `type:*`
3. **Monitor status changes** from other agents; translate to user messages
4. **Update priorities** when user expresses urgency changes
5. **Set blocked** (as a flag) when user requests pause
6. **Facilitate review** when AMIA escalates
7. **Report status** by querying issues with relevant labels

**Sets**: `status:backlog|review`, all `priority:*`.
**Monitors only**: `status:pending|in_progress|review|completed`, `assign:*`.
**Never sets**: `assign:*`, `review:*`, `effort:*`, `component:*`.

See [label-tables](references/label-tables.md) for full label tables and approval authority.

**Key commands**:

```bash
# Create issue
gh issue create --title "$TITLE" --body "$BODY" \
  --label "status:backlog" --label "priority:$PRI" --label "type:$TYPE"
# Change priority
gh issue edit $NUM --remove-label "priority:normal" --add-label "priority:high"
# Block/unblock
gh issue edit $NUM --add-label "status:blocked"
# Status report
gh issue list --label "status:in-progress" --json number,title,labels
```

See [commands-and-patterns](references/commands-and-patterns.md) for all commands and patterns.

## Checklist

Copy this checklist and track your progress:

- [ ] Identify priority and type from user request
- [ ] Create issue with correct labels
- [ ] Confirm creation to user
- [ ] Monitor for status changes from other agents
- [ ] Translate label changes into user-friendly updates
- [ ] Update priority or blocked status as needed

## Output

| Output Type | Format |
|-------------|--------|
| Issue creation | GitHub issue URL with labels |
| Label update | Confirmation (e.g., "Priority updated to high") |
| Status report | Markdown table of issues and labels |
| Label explanation | Plain text label meaning |

## Error Handling

| Error | Resolution |
|-------|------------|
| Label not found | Create label or fix typo |
| Permission denied | Request repo access from user |
| Issue not found | Verify issue number with user |
| Conflicting labels | Remove old label before adding new |
| API rate limit | Wait and retry, batch operations |

## Examples

### Example: User reports urgent bug

**User**: "The login page is broken, fix it urgently!"

```bash
gh issue create --title "Login page broken" \
  --body "User reported urgent login page issue" \
  --label "type:bug" --label "priority:critical" --label "status:backlog"
```

**Response**: "Created issue #123 (critical). The orchestrator will triage shortly."

### Example: Priority change

**User**: "Make that password reset high priority too."

```bash
gh issue edit 45 --remove-label "priority:normal" --add-label "priority:high"
```

**Response**: "Priority updated to high for issue #45."

See [commands-and-patterns](references/commands-and-patterns.md) for more examples.

## Resources

- [label-tables](references/label-tables.md) -- Label tables, kanban columns, approval authority
- [commands-and-patterns](references/commands-and-patterns.md) -- Commands, patterns, examples
- **AGENT_OPERATIONS.md** -- Agent operational patterns
- **amama-status-reporting** -- Status communication
- **amama-user-communication** -- Communication style
- **amama-role-routing** -- Role delegation

