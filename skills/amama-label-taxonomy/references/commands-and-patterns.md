# AMAMA Label Commands & Communication Patterns

## Table of Contents
- [Label Commands](#label-commands)
- [User Communication Patterns](#user-communication-patterns)
- [Full Examples](#full-examples)

## Label Commands

### When User Creates Request

> **G1.1 (PRRD G1.1, GOLDEN)**: every issue, PR, and comment body MUST begin with the self-identification line, then a blank line, then the body:
> `_Posted by the Claude developing **ai-maestro-assistant-manager-agent** (the MANAGER), via the shared @owner gh auth._`

Every `status:*` label below is one of the **ratified 17 columns** — `backburner`, `todo`,
`design`, `dispatch`, `dev`, `testing`, `ai_review`, `human_review`, `complete`, `publish`,
`published`, `deploy`, `live`, `live_auditing` (lifecycle), plus `blocked`, `failed`,
`superseded` (exception). Never invent a column.

```bash
# Create issue with initial labels (the --body MUST begin with the G1.1 self-id line)
gh issue create \
  --title "$USER_REQUEST_TITLE" \
  --body "$USER_REQUEST_BODY" \
  --label "status:backburner" \
  --label "priority:$PRIORITY" \
  --label "type:$TYPE"
```

### When User Changes Priority

```bash
# Update priority
gh issue edit $ISSUE_NUMBER --remove-label "priority:normal" --add-label "priority:high"
```

### When User Puts on Hold (or a Blocker Appears)

`blocked` applies whenever `blocked-by` is non-empty. Record the column being left as the
pre-block column so the unblock restores it exactly — never guess a column to return to.

```bash
# Mark blocked (here the task was in `dev`; record that as the pre-block column)
PRE_BLOCK_COLUMN=dev
gh issue edit $ISSUE_NUMBER --remove-label "status:$PRE_BLOCK_COLUMN" --add-label "status:blocked"
gh issue comment $ISSUE_NUMBER --body "$(printf '%s\n\n%s\n' '_Posted by the Claude developing **ai-maestro-assistant-manager-agent** (the MANAGER), via the shared @owner gh auth._' "pre-block-column: $PRE_BLOCK_COLUMN")"

# Unblock: restore the recorded pre-block column
gh issue edit $ISSUE_NUMBER --remove-label "status:blocked" --add-label "status:$PRE_BLOCK_COLUMN"
```

### When Facilitating Human Review

```bash
# Present the task to the user for review (escalated from ai_review to human_review)
gh issue view $ISSUE_NUMBER --json title,body,labels
# After user approves:
gh issue edit $ISSUE_NUMBER --remove-label "status:human_review" --add-label "status:complete"
# After user requests changes:
gh issue edit $ISSUE_NUMBER --remove-label "status:human_review" --add-label "status:dev"
```

### When a Gate or Attempt Fails

`failed` is NOT terminal and is NOT archived — the issue stays on the board and is retried.

```bash
# Record the failed attempt
gh issue edit $ISSUE_NUMBER --remove-label "status:testing" --add-label "status:failed"
# Retry once the cause is fixed (the normal path out of `failed`)
gh issue edit $ISSUE_NUMBER --remove-label "status:failed" --add-label "status:dev"
```

### When Releasing (path chosen by `release-via`)

```bash
# Tools: complete -> publish -> published
gh issue edit $ISSUE_NUMBER --remove-label "status:complete" --add-label "status:publish"
gh issue edit $ISSUE_NUMBER --remove-label "status:publish" --add-label "status:published"

# Services: complete -> deploy -> live -> live_auditing
gh issue edit $ISSUE_NUMBER --remove-label "status:complete" --add-label "status:deploy"
gh issue edit $ISSUE_NUMBER --remove-label "status:deploy" --add-label "status:live"
gh issue edit $ISSUE_NUMBER --remove-label "status:live" --add-label "status:live_auditing"
```

### When Generating Status Report

```bash
# Get all actively-worked issues for user
gh issue list --label "status:dev" --json number,title,labels

# Get issues under review (AI, then escalated to human)
gh issue list --label "status:ai_review" --json number,title,labels
gh issue list --label "status:human_review" --json number,title,labels

# Get issues needing attention: blocked and failed (failed = retryable, still on the board)
gh issue list --label "status:blocked" --json number,title,labels
gh issue list --label "status:failed" --json number,title,labels

# Get finished issues
gh issue list --label "status:complete" --json number,title
gh issue list --label "status:published" --state closed --json number,title
gh issue list --label "status:live" --json number,title
```

---

## User Communication Patterns

### Explaining Labels to User

When user asks "What's happening with my request?":

```markdown
**Issue #42: Add user authentication**

- **Status**: Dev (`status:dev`)
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
| "Put this on hold" | `status:blocked` (record the column being left as the pre-block column) |
| "Resume this" | Remove `status:blocked`, restore the recorded pre-block column (e.g. `status:dev`) |
| "Try that again" (after a failure) | Remove `status:failed`, add `status:dev` |

---

## Full Examples

### Example 1: Creating Issue with Labels

**User request**: "The login page is broken, fix it urgently!"

**AMAMA actions**:
```bash
gh issue create \
  --title "Login page broken" \
  --body "$(printf '%s\n\n%s\n' '_Posted by the Claude developing **ai-maestro-assistant-manager-agent** (the MANAGER), via the shared @owner gh auth._' 'User reported urgent login page issue')" \
  --label "type:bug" \
  --label "priority:critical" \
  --label "status:backburner"
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
  - Status: Dev (`status:dev`)
  - Priority: High (`priority:high`)
  - Assigned to: Implementation Agent 1

- **#45**: Fix password reset
  - Status: Blocked (`status:blocked`, pre-block column: `dev`)
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
