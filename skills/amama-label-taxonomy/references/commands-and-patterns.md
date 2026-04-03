# AMAMA Label Commands & Communication Patterns

## Table of Contents
- [Label Commands](#label-commands)
- [User Communication Patterns](#user-communication-patterns)
- [Full Examples](#full-examples)

## Label Commands

### When User Creates Request

```bash
# Create issue with initial labels
gh issue create \
  --title "$USER_REQUEST_TITLE" \
  --body "$USER_REQUEST_BODY" \
  --label "status:backlog" \
  --label "priority:$PRIORITY" \
  --label "type:$TYPE"
```

### When User Changes Priority

```bash
# Update priority
gh issue edit $ISSUE_NUMBER --remove-label "priority:normal" --add-label "priority:high"
```

### When User Puts on Hold

```bash
# Mark blocked
gh issue edit $ISSUE_NUMBER --remove-label "status:in-progress" --add-label "status:blocked"
```

### When Facilitating Human Review

```bash
# Present the task to the user for review (escalated from Review)
gh issue view $ISSUE_NUMBER --json title,body,labels
# After user approves:
gh issue edit $ISSUE_NUMBER --remove-label "status:review" --add-label "status:completed"
# After user requests changes:
gh issue edit $ISSUE_NUMBER --remove-label "status:review" --add-label "status:in-progress"
```

### When Generating Status Report

```bash
# Get all active issues for user
gh issue list --label "status:in-progress" --json number,title,labels

# Get issues in review
gh issue list --label "status:review" --json number,title,labels

# Get completed issues
gh issue list --label "status:completed" --state closed --json number,title
```

---

## User Communication Patterns

### Explaining Labels to User

When user asks "What's happening with my request?":

```markdown
**Issue #42: Add user authentication**

- **Status**: In Progress (`status:in-progress`)
- **Priority**: High (`priority:high`)
- **Assigned to**: Implementation Agent 1 (`assign:implementer-1`)
- **Type**: New Feature (`type:feature`)

The implementation agent is actively working on this task.
```

### Translating User Requests to Labels

| User Says | Labels to Apply |
|-----------|-----------------|
| "This is urgent!" | `priority:critical` |
| "When you get a chance..." | `priority:low` |
| "Something is broken" | `type:bug`, `priority:high` |
| "Can you add..." | `type:feature` |
| "Put this on hold" | `status:blocked` |
| "Resume this" | Remove `status:blocked`, add `status:pending` |

---

## Full Examples

### Example 1: Creating Issue with Labels

**User request**: "The login page is broken, fix it urgently!"

**AMAMA actions**:
```bash
gh issue create \
  --title "Login page broken" \
  --body "User reported urgent login page issue" \
  --label "type:bug" \
  --label "priority:critical" \
  --label "status:backlog"
```

**User response**: "Created issue #123 with critical priority. The orchestrator will triage this shortly."

### Example 2: Reporting Status with Labels

**User request**: "What's the status of my authentication work?"

**AMAMA actions**:
```bash
gh issue list --label "component:auth" --json number,title,labels
```

**User response**:
```markdown
**Authentication Issues**:

- **#42**: Add OAuth support
  - Status: In Progress (`status:in-progress`)
  - Priority: High (`priority:high`)
  - Assigned to: Implementation Agent 1

- **#45**: Fix password reset
  - Status: Blocked (`status:blocked`)
  - Priority: Normal (`priority:normal`)
  - Blocker: Waiting for email service setup
```

### Example 3: Updating Priority

**User request**: "Actually, make that password reset high priority too."

**AMAMA actions**:
```bash
gh issue edit 45 --remove-label "priority:normal" --add-label "priority:high"
```

**User response**: "Priority updated to high for issue #45."
