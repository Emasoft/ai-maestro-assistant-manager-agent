# Blocker Notification Templates

## Contents

- [1. When to notify the user about blockers](#1-when-to-notify-the-user-about-blockers)
- [2. Blocker notification message format](#2-blocker-notification-message-format)
- [3. Handling user response to blockers](#3-handling-user-response-to-blockers)
- [4. Timeout handling when user does not respond](#4-timeout-handling-when-user-does-not-respond)
- [5. Blocker resolution routing](#5-blocker-resolution-routing)

---

## 1. When to notify the user about blockers

### 1.1 ALL blockers require IMMEDIATE user notification

**IRON RULE**: Every blocker must be communicated to the user IMMEDIATELY upon receipt
from EOA or ECOS. There are no blockers that should be "batched" or "held" for the next
status report. The user may have the solution ready in minutes — but only if they know
about the problem.

A task is BLOCKED when an agent cannot continue working on it and must wait for an
external resolution before resuming. Categories of blockers:

| Category | Description | Examples |
|----------|-------------|---------|
| **Task Dependency** | Waiting for another task to complete | Feature B depends on Feature A's API |
| **Problem Resolution** | Waiting for architect or user solution | Design decision needed; requirement unclear |
| **Missing Resource** | Lacking a resource to be provided or set up | Library to install; server to set up; Docker container to build |
| **Access or Credentials** | Missing keys, tokens, or permissions | API key not configured; GitHub secret not set; password needed |
| **Missing Approval** | Waiting for user approval | Deployment approval; budget decision; scope change |
| **External Dependency** | Waiting for external party or system | Third-party API unavailable; upstream service outage |

### 1.2 Do NOT notify for non-blockers

Do NOT notify the user for issues agents can resolve themselves:
- Test failures (agents fix the code)
- Merge conflicts (agents resolve them)
- Linting errors (agents fix formatting)
- Transient errors (agents retry)

---

## 2. Blocker notification message format

### 2.1 Standard blocker notification

When communicating a blocker to the user, use this format:

```
## Blocked Task Alert

**Task**: [Task title] (Issue #[number])
**Blocker Issue**: #[blocker issue number] (tracking the blocking problem)
**Blocked Since**: [date/time]
**Severity**: [Critical/High/Medium]

### What's Blocked
[Clear, non-technical description of what cannot proceed]

### Why It's Blocked
[Root cause in user-friendly language]

### What We Need From You
[Specific, actionable request — what exactly the user must provide or decide]

### Options (if applicable)
1. **[Option A]**: [Description, trade-offs, impact]
2. **[Option B]**: [Description, trade-offs, impact]
3. **[Option C]**: [Description, trade-offs, impact]

**Recommended**: Option [N] because [reason]

### Impact if Unresolved
- [What other work is waiting]
- [Deadline at risk, if any]
- [Number of agents waiting]
```

### 2.2 Urgent blocker notification

For blockers with deadlines within 24 hours, prefix with:

```
## URGENT: Blocker Requires Immediate Decision

**Deadline**: [time remaining]
**Impact**: [what will be missed if not resolved]

[Standard blocker format follows]
```

### 2.3 Cascade blocker notification

When multiple tasks are blocked by the same issue:

```
## Cascade Blocker Alert

**Root Cause**: [Single issue causing multiple blocks]
**Tasks Affected**: [count] tasks across [count] agents
**Most Critical**: [Task name] (deadline: [date])

### Affected Tasks
| Task | Agent | Status | Deadline |
|------|-------|--------|----------|
| [task1] | [agent1] | Blocked | [date] |
| [task2] | [agent2] | Blocked | [date] |

### Resolution Needed
[What the user must do to unblock ALL affected tasks]
```

---

## 3. Handling user response to blockers

### 3.1 When user provides a decision

1. Acknowledge the user's response immediately
2. Route the decision to the appropriate agent:
   - If the blocker originated from EOA → Send AI Maestro message to EOA
   - If the blocker originated from ECOS → Send AI Maestro message to ECOS
3. Include the user's exact words in the routing message (do NOT paraphrase requirements — RULE 14)
4. Confirm to the user that the resolution has been routed

### 3.2 AI Maestro message template for routing resolution

Send a blocker resolution using the `agent-messaging` skill:
- **Recipient**: The agent that originally escalated the blocker (EOA or ECOS session name)
- **Subject**: "RESOLUTION: Blocker for task <task-id> resolved by user"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `blocker-resolution`
  - `message`: "User has provided the following decision for the blocked task."
  - `task_uuid`: The unique identifier of the blocked task
  - `issue_number`: The GitHub issue number tracking the blocker
  - `user_decision`: The user's exact response (do NOT modify per RULE 14)
  - `selected_option`: Which option was chosen (if options were presented to the user)
  - `additional_context`: Any extra information the user provided
  - `resolved_at`: ISO-8601 timestamp of the resolution

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 3.3 When user asks for more information

If the user needs more details before deciding:
1. Route the question to the originating agent (EOA or ECOS) via AI Maestro
2. Await their response
3. Relay the additional information to the user
4. Do NOT make decisions on behalf of the user

### 3.4 After unblocking

When the user provides a resolution and it's routed back to EOA:
- EOA will close the blocker issue (the separate GitHub issue tracking the blocking problem)
- EOA will move the blocked task back to the column it was in BEFORE being blocked
  (e.g., if it was in "Testing" when blocked, it returns to "Testing", not "In Progress")
- The assigned agent resumes work on the task
- Include the unblocking update in the next status report to the user

---

## 4. Timeout handling when user does not respond

### 4.1 Escalation timeline for user response

| Duration | Action |
|----------|--------|
| 0-4 hours | Wait for user response |
| 4-8 hours | Send a gentle reminder with the original blocker summary |
| 8-24 hours | Send an urgent reminder highlighting deadline impact |
| 24-48 hours | If non-critical: note in status report that task remains blocked |
| 24-48 hours | If critical: escalate urgency, highlight what will be missed |
| >48 hours | Mark task as deferred, notify agents to work on other tasks |

### 4.2 Reminder message format

```
## Reminder: Pending Decision Needed

**Original Request**: [date/time]
**Task**: [Task title] (Issue #[number])
**Time Blocked**: [duration]

A decision is still needed for this blocked task.
[Brief summary of what's needed]

**Impact**: [What's waiting on this decision]
```

---

## 5. Blocker resolution routing

### 5.1 Decision tree for routing user's response

```
User provides blocker resolution
  │
  ├─ Was the blocker escalated by EOA?
  │   └─ YES → Route resolution to EOA via AI Maestro
  │
  ├─ Was the blocker escalated by ECOS?
  │   └─ YES → Route resolution to ECOS via AI Maestro
  │
  └─ Was the blocker detected in status report?
      └─ YES → Route to the relevant role agent via ECOS
```

**Verify**: after routing the resolution via the `agent-messaging` skill, confirm message delivery via the skill's sent messages feature.

### 5.2 Confirmation to user

After routing the resolution, confirm to the user:
```
Thank you. I've routed your decision to [agent/team].
The blocked task [Task title] should resume shortly.
I'll include the update in the next status report.
```

---

## 6. Checklists

### 6.1 Checklist: Receiving a Blocker Escalation from EOA or ECOS

Copy this checklist and track your progress:

- [ ] Read the blocker-escalation message from EOA or ECOS
- [ ] Identify the blocked task (issue number) and the blocker issue (blocker issue number)
- [ ] Determine the blocker category (Task Dependency, Problem Resolution, Missing Resource, Access/Credentials, Missing Approval, External Dependency)
- [ ] Compose user notification using the appropriate template (section 2.1, 2.2, or 2.3)
- [ ] Include the Blocker Issue number in the notification so the user can track it
- [ ] Present options to the user if available (from the escalation message)
- [ ] Deliver the notification to the user IMMEDIATELY (do not batch or delay)

### 6.2 Checklist: When User Provides a Decision for a Blocked Task

Copy this checklist and track your progress:

- [ ] Acknowledge the user's response immediately
- [ ] Determine who escalated the blocker (EOA or ECOS)
- [ ] Compose blocker-resolution AI Maestro message (section 3.2 template)
- [ ] Include the user's exact words (do NOT paraphrase — RULE 14)
- [ ] Include the selected option if options were presented
- [ ] Send the resolution message to the original escalator (EOA or ECOS)
- [ ] Confirm to the user that the resolution has been routed
- [ ] Note: EOA will close the blocker issue and restore the task to its previous column

### 6.3 Checklist: When User Does Not Respond to a Blocker (Timeout)

Copy this checklist and track your progress:

- [ ] After 4 hours: Send a gentle reminder with the original blocker summary
- [ ] After 8 hours: Send an urgent reminder highlighting deadline impact
- [ ] After 24 hours (non-critical): Note in status report that task remains blocked
- [ ] After 24 hours (critical): Escalate urgency, highlight what will be missed
- [ ] After 48 hours: Mark task as deferred, notify agents to work on other tasks

---

## See Also

- [ai-maestro-message-templates.md](../../eama-ecos-coordination/references/ai-maestro-message-templates.md) - Inter-agent message templates
- [response-templates.md](response-templates.md) - Standard response templates
