---
name: amama-label-taxonomy
description: Use when managing GitHub issue labels, priorities, or status taxonomy. Trigger with label or triage requests.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# AMAMA Label Taxonomy

## Overview

Provides the label taxonomy for the Assistant Manager Agent (AMAMA). AMAMA manages priority labels, initial status labels, and translates label states into user-friendly messages. Each role plugin has its own label-taxonomy skill.

## Prerequisites

1. GitHub CLI (`gh`) available
2. Repository with GitHub issue tracking enabled
3. Understanding of AMAMA role (user communication and role routing)

## Instructions

1. **Analyze user request** -- determine priority (`priority:critical|high|normal|low`) and type (`type:bug|feature|...`)
2. **Create issue** with labels: `status:backlog`, `priority:*`, `type:*`
3. **Monitor status changes** from other agents; translate to user-friendly messages
4. **Update priorities** when user expresses urgency changes
5. **Set blocked status** (`status:blocked`) when user requests pause
6. **Facilitate human review** when Integrator (AMIA) escalates via `status:human-review`
7. **Report status** by querying issues with relevant labels

**AMAMA sets**: `status:backlog`, `status:human-review`, `status:blocked`, all `priority:*` labels.
**AMAMA monitors but does not set**: `status:todo|in-progress|ai-review|merge-release|done`, `assign:*`.
**AMAMA never sets**: `assign:*`, `review:*`, `effort:*`, `component:*`.

See `references/label-tables.md` for full label tables, kanban columns, and approval authority details.

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

See `references/commands-and-patterns.md` for all commands, human review flow, and status report queries.

## Output

| Output Type | Format |
|-------------|--------|
| Issue creation | GitHub issue URL with labels |
| Label update | Confirmation message (e.g., "Priority updated to high") |
| Status report | Markdown table of issues and labels |
| Label explanation | Plain text translation of label meaning |

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

**Response**: "Created issue #123 with critical priority. The orchestrator will triage this shortly."

### Example: Priority change

**User**: "Make that password reset high priority too."

```bash
gh issue edit 45 --remove-label "priority:normal" --add-label "priority:high"
```

**Response**: "Priority updated to high for issue #45."

See `references/commands-and-patterns.md` for more examples including status reports and human review facilitation.

## Resources

- `references/label-tables.md` -- Full label tables, kanban columns, approval authority
- `references/commands-and-patterns.md` -- All gh commands, communication patterns, full examples
- **AGENT_OPERATIONS.md** -- Core agent operational patterns
- **amama-status-reporting** -- User communication patterns
- **amama-user-communication** -- Communication style guidelines
- **amama-role-routing** -- Role delegation patterns
