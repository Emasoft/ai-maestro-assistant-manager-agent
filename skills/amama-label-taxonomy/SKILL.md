---
name: amama-label-taxonomy
description: Use when managing GitHub issue labels or priorities. Trigger with label or triage requests. Loaded by ai-maestro-assistant-manager-agent-main-agent.
compatibility: Requires AI Maestro installed.
context: fork
agent: ai-maestro-assistant-manager-agent-main-agent
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
2. **Create issue** with labels: `status:backburner`, `priority:*`, `type:*`
3. **Monitor column changes** from other agents; translate to user messages
4. **Update priorities** when user expresses urgency changes
5. **Set blocked** when the user requests a pause or `blocked-by` becomes non-empty -- record the pre-block column so the task can be restored to it when the blocker clears
6. **Facilitate human review** when AMIA escalates
7. **Report status** by querying issues with relevant labels

Every `status:*` label is derived from one of the **ratified 17 columns** -- never invent one.

**The 17 columns**:
- Lifecycle (14, in order): `backburner`, `todo`, `design`, `dispatch`, `dev`, `testing`, `ai_review`, `human_review`, `complete`, `publish`, `published`, `deploy`, `live`, `live_auditing`
- Exception (3, orthogonal): `blocked`, `failed`, `superseded`

**Sets**: `status:backburner|human_review|blocked`, all `priority:*`.
**Monitors only**: every other `status:*` (`todo`, `design`, `dispatch`, `dev`, `testing`, `ai_review`, `complete`, `publish`, `published`, `deploy`, `live`, `live_auditing`, `failed`, `superseded`), `assign:*`.
**Never sets**: `assign:*`, `review:*`, `effort:*`, `component:*`.

`failed` is NOT terminal: the task stays on the board and is retried via `dev`. The path after `complete` is chosen by `release-via` -- `publish` -> `published` (tools) or `deploy` -> `live` -> `live_auditing` (services).

See label-tables reference for full label tables and approval authority.

**Key commands**:

> **G1.1 (PRRD G1.1, GOLDEN)**: every issue, PR, and comment body MUST begin with the self-identification line, then a blank line, then the body:
> `_Posted by the Claude developing **ai-maestro-assistant-manager-agent** (the MANAGER), via the shared @owner gh auth._`

```bash
# Create issue (the --body MUST begin with the G1.1 self-id line)
gh issue create --title "$TITLE" --body "$BODY" \
  --label "status:backburner" --label "priority:$PRI" --label "type:$TYPE"
# Change priority
gh issue edit $NUM --remove-label "priority:normal" --add-label "priority:high"
# Block (record the column being left, so the unblock restores it exactly)
gh issue edit $NUM --remove-label "status:$CURRENT_COLUMN" --add-label "status:blocked"
# Unblock (restore the recorded pre-block column -- never guess one)
gh issue edit $NUM --remove-label "status:blocked" --add-label "status:$PRE_BLOCK_COLUMN"
# Status report
gh issue list --label "status:dev" --json number,title,labels
```

See commands-and-patterns reference for all commands and patterns.

## Checklist

Copy this checklist and track your progress:

- [ ] Identify priority and type from user request
- [ ] Create issue with correct labels (`status:backburner` on entry)
- [ ] Confirm creation to user
- [ ] Monitor for column changes from other agents
- [ ] Verify every `status:*` label is one of the ratified 17 columns
- [ ] Translate label changes into user-friendly updates
- [ ] Update priority, or block/unblock (restoring the pre-block column), as needed

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
  --body "$(printf '%s\n\n%s\n' '_Posted by the Claude developing **ai-maestro-assistant-manager-agent** (the MANAGER), via the shared @owner gh auth._' 'User reported urgent login page issue')" \
  --label "type:bug" --label "priority:critical" --label "status:backburner"
```

**Response**: "Created issue #123 (critical). The orchestrator will triage shortly."

### Example: Priority change

**User**: "Make that password reset high priority too."

```bash
gh issue edit 45 --remove-label "priority:normal" --add-label "priority:high"
```

**Response**: "Priority updated to high for issue #45."

See commands-and-patterns reference for more examples.

## Resources

- [label-tables](references/label-tables.md): Priority Labels, Kanban Columns (Canonical 17-Column Model), Status Labels AMAMA Updates, Labels AMAMA Monitors, Labels AMAMA Never Sets, AMAMA's Approval Authority
- [commands-and-patterns](references/commands-and-patterns.md): Label Commands, User Communication Patterns, Full Examples
