---
name: eama-user-communication
description: Use when communicating with users for clarification, presenting options, requesting approval, or reporting completion. Trigger with user requests or communication needs.
version: 1.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: eama-main
user-invocable: false
triggers:
  - when clarifying requirements
  - when presenting options to user
  - when requesting approval
  - when reporting completion
---

# User Communication Skill

## Overview

This skill teaches how to communicate with users effectively and consistently.

## ECOS Coordination

For ECOS coordination procedures (approval requests, autonomous mode, completions), see eama-ecos-coordination skill.

## Prerequisites

None required. This skill provides communication patterns that can be used immediately.

## Instructions

1. Identify the communication type needed (clarification, options, approval, completion)
2. Use the appropriate template from the Communication Patterns section
3. Fill in all placeholders with specific information
4. Follow the Quality Rules to ensure clarity
5. Include relevant UUIDs, issue numbers, and file paths for traceability

### Checklist

Copy this checklist and track your progress:

- [ ] Identify communication type (clarification/options/approval/completion)
- [ ] Select appropriate template
- [ ] Fill in all placeholders
- [ ] Review against Quality Rules
- [ ] Include UUIDs and references
- [ ] Send communication

## Output

| Output Type | Format | When to Use |
|-------------|--------|-------------|
| Clarification Request | Structured questions with specific information needs | When user input is incomplete or ambiguous |
| Option Presentation | Comparison table with pros/cons/effort estimates | When multiple approaches are viable |
| Approval Request | Action/Impact/Reversibility statement | Before any significant or irreversible operation |
| Completion Report | Summary with changes, verification steps, next actions | When task or subtask is finished |
| ECOS Handoff | AI Maestro message with handoff file UUID | When routing work to specialist agents |
| Status Update | Brief progress summary with blockers if any | During long-running operations |

## Communication Patterns

### 1. Clarification Request

When user input is incomplete:
```
I need clarification on the following:

1. [Specific question]
2. [Specific question]

Please provide:
- [What you need]
- [Format expected]
```

### 2. Option Presentation

When presenting choices:
```
I've identified [N] options:

**Option A: [Name]**
- Pros: [list]
- Cons: [list]
- Effort: [estimate]

**Option B: [Name]**
...

Which would you prefer?
```

### 3. Approval Request

When needing approval:
```
**Approval Requested**

Action: [What will happen]
Impact: [What changes]
Reversible: Yes/No

Please respond with:
- "approve" to proceed
- "deny" to cancel
- "modify" to adjust
```

### 4. Completion Report

When work is done:
```
**Task Complete**

Summary: [1-2 sentences]
Changes made:
- [file: change]

Verification: [How to check]
Next steps: [What happens now]
```

## Blocker Communication

When tasks are blocked and require user decisions, use the blocker notification templates. See [references/blocker-notification-templates.md](references/blocker-notification-templates.md):

- When to notify the user about blockers (immediate vs batch vs skip)
- Blocker notification message format (standard, urgent, cascade)
- Handling user response to blockers (routing decisions back to agents)
- Timeout handling when user does not respond (4h, 8h, 24h, 48h escalation)
- Blocker resolution routing (decision tree for routing user's response)

### When to Use Blocker Notifications

| Blocker Type | Notification Timing | Severity |
|--------------|---------------------|----------|
| Critical-path task with <48h deadline | Immediate | Critical |
| Cascade blocker (multiple tasks) | Immediate | High |
| Requires user credentials/access | Immediate | High |
| RULE 14 requirement conflict | Immediate | Critical |
| Non-critical task with no deadline | Next status report | Medium |
| External dependency | Next status report | Low |
| Technical blocker (agents can resolve) | No notification | N/A |

## Quality Rules

1. **Be Specific**: Never say "some files" - list them
2. **Be Actionable**: Always tell user what to do next
3. **Be Honest**: Admit uncertainty, don't guess
4. **Be Concise**: Use bullets, avoid walls of text
5. **Be Traceable**: Include UUIDs, issue numbers

## Examples

### Example 1: Clarification Request

```markdown
I need clarification on the following:

1. Should the login support both email and username?
2. What is the session timeout duration?

Please provide:
- Your preference for login identifiers
- Timeout in minutes (e.g., 30, 60, 120)
```

### Example 2: Completion Report

```markdown
**Task Complete**

Summary: Implemented user login endpoint with OAuth2 support.

Changes made:
- src/auth/login.py: Added login handler
- src/auth/oauth.py: Added OAuth2 flow
- tests/test_login.py: Added 15 test cases

Verification: Run `pytest tests/test_login.py` - all tests should pass

Next steps: Proceed with logout endpoint implementation
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No user response | User inactive | Wait, then send gentle reminder |
| Ambiguous user input | Unclear response | Ask for specific clarification |
| Template mismatch | Wrong pattern selected | Re-evaluate and use correct template |

## Workflow Examples

### Workflow 1: Routing Implementation Request

```
User: "I need to implement a new authentication module for the project. It should support OAuth2 and JWT tokens."

EAMA Response: "I understand you need a new authentication module with OAuth2 and JWT support. Let me route this to the Orchestrator for implementation.

Creating handoff file and routing to ECOS, which will coordinate with the Orchestrator agent to implement the authentication module with the specified requirements."
```

### Workflow 2: Granting ECOS Autonomous Mode

```
User: "Let ECOS handle routine development tasks for the next 4 hours while I'm in a meeting."

EAMA Response: "I'll grant ECOS autonomous mode for routine development operations with a 4-hour expiration.

Sending autonomy grant to ECOS with scope limited to routine-operation and minor-decision types on feature/* branches. ECOS will operate autonomously for these tasks but will still notify you of important completions and request approval for any critical operations."

[Send AI Maestro message with autonomy-grant type]
```

### Workflow 3: Presenting ECOS Approval Request to User

```
[ECOS sends approval request for staging deployment]

EAMA presents to user:

## ECOS Approval Request

**Operation**: Deploy v2.1.0 to staging environment
**Risk Level**: Medium (reversible)
**Affected Resources**: staging-server, staging-db
**Related Issues**: #89, #92
**ECOS Recommendation**: Approve

Do you approve this deployment?
- [Approve] - ECOS will proceed
- [Reject] - ECOS will cancel
- [Needs Revision] - ECOS will modify request
```

## Handoff Protocol

When routing work:

1. Create handoff .md file with UUID
2. Include all relevant context
3. Send via AI Maestro message to ECOS
4. ECOS routes to appropriate specialist
5. Track handoff status
6. Report completion to user

## Proactive ECOS Monitoring

EAMA must proactively monitor ECOS health and responsiveness to prevent communication failures and ensure timely approval processing.

### Monitoring Schedule

| Check Type | Frequency | Trigger |
|------------|-----------|---------|
| ECOS Health Check | Every 10 minutes | During active work sessions |
| AI Maestro Inbox | Every 2 minutes | For pending approval requests |
| ECOS Responsiveness Ping | When 15 minutes without response | After sending any message to ECOS |

### Health Check Procedure

Send a periodic ECOS health check every 10 minutes during active work using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "Periodic Health Check"
- **Content**: ping type, message "Routine health check", expect_reply true, timeout 60
- **Type**: `ping`
- **Priority**: `low`

**Verify**: check inbox for a `pong` response within the timeout period.

### AI Maestro Inbox Check

Check your inbox every 2 minutes for approval requests using the `agent-messaging` skill. Filter for messages with content type `approval_request`.

### Responsiveness Ping (15 Minute Timeout)

If no response from ECOS after 15 minutes since last message sent, send an urgent ping using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "URGENT: Response Required"
- **Content**: ping type, message "No response received for 15 minutes. Please acknowledge.", expect_reply true, timeout 30
- **Type**: `ping`
- **Priority**: `urgent`

### Actions When ECOS Unresponsive

If ECOS fails to respond after the urgent ping (30 second timeout):

1. **Verify ECOS Session Exists**
   Use the `ai-maestro-agents-management` skill to list agents and check if the ECOS session is still active.

2. **Check AI Maestro Health**
   Use the `agent-messaging` skill's health check feature to verify AI Maestro is running.

3. **Notify User**
   ```
   ECOS (ecos-<project-name>) is unresponsive.
   Last successful contact: <timestamp>
   Attempted recovery: <steps taken>

   Options:
   - [Restart ECOS] - Attempt to respawn ECOS session
   - [Continue Without] - Proceed with reduced coordination
   - [Investigate] - Check logs for error details
   ```

4. **Attempt Recovery**
   - If AI Maestro is down: Alert user to restart AI Maestro
   - If ECOS session crashed: Respawn ECOS using standard spawn procedure
   - If network issue: Wait 5 minutes and retry

5. **Log Incident**
   Record the unresponsive incident in `docs_dev/sessions/ecos-health-log.md`

## Design Document Scripts

This script helps locate design documents when communicating with users:

| Script | Purpose | Usage |
|--------|---------|-------|
| `eama_design_search.py` | Search design documents for user queries | `python scripts/eama_design_search.py --type <TYPE> --status <STATUS>` |

Use `eama_design_search.py` when:
- A user asks about project status or design progress
- Looking up design specifications to reference in responses
- Finding related designs to provide context in user communication

### Script Location

The script is located at `../../scripts/eama_design_search.py` relative to this skill.

## Resources

- See eama-ecos-coordination skill - ECOS coordination and autonomous mode
- See eama-approval-workflows skill - Approval communication patterns
- See eama-role-routing skill - Routing communication patterns
- See shared/message_templates.md in plugin root

### Reference Documents

| Reference | Description |
|-----------|-------------|
| [response-templates.md](references/response-templates.md) | User communication response templates |
| [blocker-notification-templates.md](references/blocker-notification-templates.md) | Templates for communicating task blockers to the user and handling their responses |
