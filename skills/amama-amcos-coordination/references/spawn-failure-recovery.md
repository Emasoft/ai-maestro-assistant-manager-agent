# Agent Creation Failure Recovery Procedures


## Contents

- [Overview](#overview)
- [1. AMCOS Agent Creation Failure Recovery Protocol](#1-amcos-agent-creation-failure-recovery-protocol)
  - [Recovery Steps](#recovery-steps)
  - [Recovery Decision Tree](#recovery-decision-tree)
- [2. Communication Breakdown Recovery](#2-communication-breakdown-recovery)
  - [When AMCOS Doesn't Respond](#when-amcos-doesnt-respond)
- [3. Approval Request Handling Failures](#3-approval-request-handling-failures)
  - [When Approval Request Unclear](#when-approval-request-unclear)
  - [When Multiple Conflicting Requests](#when-multiple-conflicting-requests)
- [4. Agent Creation Failures (General)](#4-agent-creation-failures-general)
  - [Symptoms](#symptoms)
  - [Recovery Procedure](#recovery-procedure)
- [5. Logging and Audit Trail](#5-logging-and-audit-trail)
  - [Log Locations](#log-locations)
  - [Log Entry Template](#log-entry-template)
- [Failure: <timestamp>](#failure-timestamp)
- [6. Timeliness Requirements](#6-timeliness-requirements)
- [7. Example Scenarios](#7-example-scenarios)
  - [Example 1: AMCOS Agent Creation Fails (AI Maestro Down)](#example-1-amcos-agent-creation-fails-ai-maestro-down)
  - [Example 2: AMCOS Not Responding to Routing Request](#example-2-amcos-not-responding-to-routing-request)
  - [Example 3: Conflicting Approval Requests](#example-3-conflicting-approval-requests)
- [Summary](#summary)

## Overview

This document provides recovery procedures for handling failures in AMCOS creation, agent creation, and inter-agent communication within the AMAMA system.

---

## 1. AMCOS Agent Creation Failure Recovery Protocol

When AMCOS agent creation fails, follow this recovery procedure systematically before escalating to the user.

### Recovery Steps

#### Step 1: Verify AI Maestro is Running

Check AI Maestro health using the `agent-messaging` skill's health check feature.

If AI Maestro is down:
- Alert user: "AI Maestro service is not responding. Please restart it."
- Do NOT proceed with creation retry until AI Maestro is confirmed running

#### Step 2: Check tmux Sessions for Conflicts

```bash
# List existing sessions
tmux list-sessions

# Check if session name already exists
tmux list-sessions | grep "amcos-<project-name>"
```

If session name collision detected:
- Use alternative session name with numeric suffix: `amcos-<project-name>-2`
- Document the collision in session log

#### Step 3: Retry with Different Session Name

Use the `ai-maestro-agents-management` skill to create the agent with an incremented session name:
- **Agent name**: `amcos-<project-name>-<timestamp>` (use timestamp to ensure uniqueness)
- **Working directory**: `~/agents/<new-session-name>/`
- **Task**: "Coordinate agents for <project-name>"
- **Plugin**: load `ai-maestro-chief-of-staff` using the skill's plugin management features
- **Main agent**: `amcos-chief-of-staff-main-agent`

**Verify**: confirm the agent appears in the agent list with correct status.

#### Step 4: If 3 Retries Fail

After 3 failed creation attempts:

1. **Create project WITHOUT AMCOS**
   - Project structure is still valid
   - AMAMA can receive user requests
   - Work cannot be routed to specialists

2. **Notify User**
   ```
   AMCOS Agent Creation Failed After 3 Attempts

   Project: <project-name>
   Location: <path>
   Status: Created WITHOUT AMCOS coordination

   Attempted:
   - Attempt 1: <error>
   - Attempt 2: <error>
   - Attempt 3: <error>

   Impact:
   - Cannot route work to specialist agents (AMOA, AMAA, AMIA)
   - Project directory and git repo are ready
   - You can still interact with me for planning

   To fix:
   1. Check AI Maestro logs: `journalctl -u aimaestro` or `cat ~/ai-maestro/logs/`
   2. Check tmux for orphaned sessions: `tmux list-sessions`
   3. Restart AI Maestro if needed

   Once fixed, I can retry AMCOS agent creation. Say "retry AMCOS for <project-name>" when ready.
   ```

3. **Log Failure**
   Record in `docs_dev/sessions/spawn-failures.md`:
   ```markdown
   ## Agent Creation Failure: <timestamp>
   - Project: <project-name>
   - Session Name: amcos-<project-name>
   - Attempts: 3
   - Errors: <error details>
   - Resolution: Awaiting user intervention
   ```

#### Step 5: Allow User Manual Fix and Retry

When user says "retry AMCOS for <project-name>":
1. Re-run verification steps (AI Maestro health, session conflicts)
2. Attempt agent creation with clean session name
3. Report success or escalate again if still failing

### Recovery Decision Tree

```
AMCOS Agent Creation Fails
    |
    v
Is AI Maestro running? ──NO──> Alert user, STOP
    |
   YES
    v
Is session name collision? ──YES──> Use alternative name, RETRY
    |
   NO
    v
Retry count < 3? ──YES──> Wait 10 seconds, RETRY
    |
   NO
    v
Create project WITHOUT AMCOS
Notify user with diagnostic info
Log failure
Wait for user to fix and request retry
```

---

## 2. Communication Breakdown Recovery

When AMCOS or other agents fail to respond to messages.

### When AMCOS Doesn't Respond

**Symptoms:**
- No response to health ping
- No acknowledgment of routing request
- Messages sent via AI Maestro but no reply received

**Recovery Procedure:**

1. **Wait 30 seconds**
   - Allow time for AMCOS to process message
   - AMCOS may be busy with approval workflow

2. **Retry health ping once**
   Send a health check message using the `agent-messaging` skill:
   - **Recipient**: `amcos-<project-name>`
   - **Subject**: "Health Check"
   - **Type**: `health_check`
   - **Priority**: `normal`

   **Verify**: check inbox for response within 30 seconds.

3. **If still no response, report to user**
   ```
   Communication Issue: AMCOS Not Responding

   Project: <project-name>
   Session: amcos-<project-name>
   Issue: No response to messages after 30s + 1 retry

   Checked:
   - AI Maestro API: Running
   - Message sent successfully: Yes
   - Response received: No

   Possible causes:
   1. AMCOS session crashed
   2. AMCOS overloaded or stuck
   3. AI Maestro routing issue

   Actions you can take:
   1. Check AMCOS session: `tmux attach -t amcos-<project-name>`
   2. Check AMCOS logs (if available)
   3. Restart AMCOS if needed

   I can retry routing once AMCOS is confirmed working.
   ```

4. **Log the communication failure**
   Record in `docs_dev/sessions/communication-failures.md`:
   ```markdown
   ## Communication Failure: <timestamp>
   - From: AMAMA
   - To: amcos-<project-name>
   - Message: <subject>
   - Attempts: 2 (initial + 1 retry)
   - Timeout: 30s + 30s
   - Status: No response
   - Resolution: Escalated to user
   ```

---

## 3. Approval Request Handling Failures

When approval workflow encounters errors.

### When Approval Request Unclear

**Symptoms:**
- AMCOS approval request lacks required fields
- Risk level ambiguous or missing
- Proposed action description incomplete

**Recovery Procedure:**

1. **Do NOT approve by default**
   - Missing information = deny by default
   - Never guess user intent

2. **Request clarification from AMCOS**
   Send a clarification request using the `agent-messaging` skill:
   - **Recipient**: `amcos-<project-name>`
   - **Subject**: "Approval Clarification Needed"
   - **Content**: clarification_request type, message "Approval request incomplete. Missing: <field1>, <field2>. Please resend with full context."
   - **Type**: `clarification_request`
   - **Priority**: `high`

   **Verify**: confirm message delivery via the skill's sent messages feature.

3. **If still unclear, escalate to user**
   ```
   Approval Blocked: Unclear Request

   Project: <project-name>
   Request from: AMCOS
   Issue: Missing required approval information

   Details:
   - Risk level: <missing/unclear>
   - Proposed action: <incomplete description>
   - Impact: <not specified>

   I need your decision:
   - Approve anyway? (not recommended)
   - Deny and request more info?
   - Let me ask AMCOS for clarification?
   ```

### When Multiple Conflicting Requests

**Symptoms:**
- Two approval requests for same resource
- Conflicting actions proposed simultaneously
- Priority conflict (e.g., deploy vs. rollback)

**Recovery Procedure:**

1. **Pause all approvals**
   - Do not process either request
   - Send "HOLD" response to both

2. **Escalate to user immediately**
   ```
   Conflict Detected: Multiple Approval Requests

   Project: <project-name>

   Request A:
   - From: <agent/AMCOS>
   - Action: <action1>
   - Risk: <level>

   Request B:
   - From: <agent/AMCOS>
   - Action: <action2>
   - Risk: <level>

   Conflict: Both requests target <resource> but propose incompatible actions

   Which should proceed?
   - Approve Request A only?
   - Approve Request B only?
   - Approve both in sequence (A then B)?
   - Deny both and investigate?
   ```

3. **Wait for user to resolve conflict**
   - Do not proceed until user provides clear direction
   - Do not attempt to resolve conflicts autonomously

---

## 4. Agent Creation Failures (General)

When creating specialist agents (AMOA, AMAA, AMIA) fails.

### Symptoms

- Agent creation command exits with non-zero code
- Session created but agent doesn't respond
- Plugin loading errors in creation output

### Recovery Procedure

1. **Check AI Maestro health** (same as Step 1 for AMCOS)

2. **Verify plugin availability**
   ```bash
   # Check if specialist plugin exists
   ls -la ~/agents/<session-name>/.claude/plugins/ai-maestro-orchestrator-agent
   ls -la ~/agents/<session-name>/.claude/plugins/ai-maestro-architect-agent
   ls -la ~/agents/<session-name>/.claude/plugins/ai-maestro-integrator-agent
   ```

3. **Check for tmux session zombie processes**
   ```bash
   # List sessions
   tmux list-sessions

   # Kill orphaned sessions if needed
   tmux kill-session -t <zombie-session-name>
   ```

4. **Retry with clean environment**
   - Use fresh session name with timestamp
   - Ensure plugin directory is accessible
   - Verify all --plugin-dir paths are valid

5. **After 2 retries, escalate to user**
   ```
   Agent Creation Failed: <agent-type>

   Session: <session-name>
   Attempts: 2
   Plugin: <plugin-name>
   Error: <error output>

   Diagnostic info:
   - AI Maestro: Running
   - Session name: Available
   - Plugin path: <verified/missing>

   Recommended actions:
   1. Check plugin installation
   2. Verify plugin compatibility
   3. Review agent logs: `cat ~/agents/<session>/spawn.log`

   Should I:
   - Try alternate plugin version?
   - Create without this plugin?
   - Abort and manual investigation?
   ```

---

## 5. Logging and Audit Trail

All failures MUST be logged for debugging and audit purposes.

### Log Locations

| Failure Type | Log File | Format |
|--------------|----------|--------|
| AMCOS creation failures | `docs_dev/sessions/spawn-failures.md` | Markdown |
| Communication failures | `docs_dev/sessions/communication-failures.md` | Markdown |
| Approval conflicts | `docs_dev/sessions/approval-conflicts.md` | Markdown |
| Agent creation failures | `docs_dev/sessions/agent-spawn-failures.md` | Markdown |

### Log Entry Template

```markdown
## Failure: <timestamp>
- Type: <agent-creation/communication/approval>
- Component: <AMCOS/agent/messaging>
- Project: <project-name>
- Session: <session-name>
- Attempts: <count>
- Error: <error message>
- Recovery Actions: <list of actions taken>
- Resolution: <escalated/retry scheduled/fixed>
- User Notified: <yes/no>
```

---

## 6. Timeliness Requirements

**Response times for failure handling:**

- AMCOS creation failure detection: Immediate (exit code check)
- Communication timeout: 30 seconds before first retry
- Approval request clarification: Within 60 seconds
- User escalation: Within 2 minutes of detection
- Retry intervals: 10 seconds between creation retries

**Do NOT:**
- Wait indefinitely for responses
- Retry more than 3 times without user input
- Approve unclear requests "to unblock work"
- Hide failures from user to "avoid concern"

**DO:**
- Report failures promptly and clearly
- Provide actionable diagnostic information
- Offer concrete next steps to user
- Log all failure events for audit

---

## 7. Example Scenarios

### Example 1: AMCOS Agent Creation Fails (AI Maestro Down)

**Scenario**: AMCOS agent creation fails with exit code 1

**Your Action**: Diagnose and report to user

**Your Response to User**:
```
Issue encountered: AMCOS agent creation failed

Details: Agent creation command exited with error code 1
Impact: Cannot coordinate agents for inventory-system project
Attempted: Created amcos-inventory-system with standard configuration

Error output: [paste relevant error]

I recommend: Verify AI Maestro is running by checking its health status
using the `agent-messaging` skill. If down, restart it. Then I'll retry creating the AMCOS agent.

Should I retry once AI Maestro is confirmed running?
```

### Example 2: AMCOS Not Responding to Routing Request

**Scenario**: Sent routing request 30s ago, no response

**Your Actions**:
1. Wait 30 seconds (already elapsed)
2. Send health check message
3. Wait 30 more seconds
4. No response → escalate

**Your Response to User**:
```
Communication issue detected with AMCOS for inventory-system.

I sent a work routing request 60 seconds ago but received no response.

Status:
- AI Maestro API: Running ✅
- Message delivered: Yes ✅
- AMCOS response: None ❌

This could mean:
- AMCOS session crashed
- AMCOS is stuck processing another request
- Messaging route is broken

Can you check the AMCOS session? `tmux attach -t amcos-inventory-system`

Once you confirm AMCOS status, I can retry routing your request.
```

### Example 3: Conflicting Approval Requests

**Scenario**: Two approvals arrive simultaneously

**Your Actions**:
1. Pause both
2. Escalate immediately

**Your Response to User**:
```
⚠️ Conflict Detected: Need Your Decision

Project: inventory-system

Request A (from AMOA via AMCOS):
- Action: Deploy to staging
- Risk: Medium (database migration included)

Request B (from AMIA via AMCOS):
- Action: Rollback staging (critical bug found)
- Risk: High (data loss possible)

These conflict! Both target staging environment.

What should I do?
1. Approve rollback first (safe, but delays deploy)
2. Approve deploy first (risky if bug critical)
3. Deny both and investigate the critical bug
4. Something else?
```

---

## Summary

Recovery from failures requires:

1. **Systematic diagnosis** - Check AI Maestro, sessions, plugins
2. **Automatic retries** - Up to 3 attempts with delays
3. **Clear user escalation** - Provide diagnostic info and options
4. **Comprehensive logging** - Audit trail for all failures
5. **Timeliness** - Don't block indefinitely; escalate quickly

**Key Principle**: When in doubt, escalate to user with clear options. Do NOT guess, assume, or hide failures.
