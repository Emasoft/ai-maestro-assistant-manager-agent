# Agent Creation Failure Recovery Procedures


## Contents

- [Overview](#overview)
- [1. AMCOS COS Assignment Failure Recovery Protocol](#1-amcos-cos-assignment-failure-recovery-protocol)
- [2. Communication Breakdown Recovery](#2-communication-breakdown-recovery)
- [3. Approval Request Handling Failures](#3-approval-request-handling-failures)
- [4. Agent Creation Failures (General)](#4-agent-creation-failures-general)
- [5. Logging and Audit Trail](#5-logging-and-audit-trail)
- [6. Timeliness Requirements](#6-timeliness-requirements)
- [7. Example Scenarios](#7-example-scenarios)
- [Summary](#summary)

## Overview

This document provides recovery procedures for handling failures in COS (Chief of Staff) role assignment, agent registration, and inter-agent communication within the AMAMA system. All operations use the AI Maestro v2 API.

---

## 1. AMCOS COS Assignment Failure Recovery Protocol

When COS (Chief of Staff) role assignment fails via the AI Maestro API, follow this recovery procedure systematically before escalating to the user.

> **Note on retry counts:** AMCOS (COS) assignment gets 3 retries because it is critical for project coordination. General agent creation failures (Section 4) get 2 retries before escalation, since specialist agents can be re-added later without disrupting the team structure.

### Recovery Steps

#### Step 1: Verify AI Maestro API is Running

```
GET $AIMAESTRO_API/api/sessions
```

If AI Maestro API is down or not responding:
- Alert user: "AI Maestro API is not responding. Please restart it."
- Do NOT proceed with COS assignment retry until API health is confirmed

#### Step 2: Verify the Target Agent is Registered

```
GET $AIMAESTRO_API/api/agents?name=<agent-name>
```

If the target agent is not registered:
- Register the agent using `aimaestro-agent.sh` or the `ai-maestro-agents-management` skill.
- Verify registration succeeded before proceeding

#### Step 3: Verify the Team Exists and is Type `closed`

```
GET $AIMAESTRO_API/api/teams/<team-id>
```

If the team does not exist or is not type `closed`:
- Escalate to user: request user to create the team or update its type via dashboard
- Document the issue in session log

See the `team-governance` skill for full API details.

#### Step 4: Check if Team Already Has a COS Assigned

```
GET $AIMAESTRO_API/api/teams/<team-id>
```

If a COS is already assigned:
- Determine if re-assignment is needed (e.g., replacing a non-responsive COS)
- If the existing COS is functioning, no action needed

#### Step 5: Escalate to User for COS Assignment

**AMAMA cannot assign COS roles.** Report the verification findings to the user and request them to assign COS via the dashboard.

Provide the user with:
- The team ID and recommended COS agent
- Any issues found during verification (API health, agent registration, team state)
- Recommended actions to resolve issues before attempting COS assignment

Track escalation in the session state file `docs_dev/sessions/cos-assignment-retries.md` with timestamp, team ID, target agent, and findings.

#### Step 6: If COS Assignment Continues to Fail

If the user reports COS assignment failures:

1. **Team continues WITHOUT COS**
   - The team still exists in AI Maestro -- it just lacks a COS
   - AMAMA can still receive user requests
   - AMAMA cannot delegate to specialists until a COS is assigned

2. **Provide Diagnostic Info to User**
   ```
   COS Assignment Diagnostics

   Team: <team-id>
   Target Agent: <agent-name>
   Status: Team exists WITHOUT COS coordination

   Diagnostic checks:
   1. AI Maestro API health: `GET $AIMAESTRO_API/api/sessions`
   2. Agent registration: `GET $AIMAESTRO_API/api/agents?name=<agent-name>`
   3. Team status: `GET $AIMAESTRO_API/api/teams/<team-id>`

   Please retry COS assignment via the dashboard once issues are resolved.
   ```

3. **Log Failure**
   Record in `docs_dev/sessions/spawn-failures.md`:
   ```markdown
   ## COS Assignment Failure: <timestamp>
   - Team: <team-id>
   - Target Agent: <agent-name>
   - Issues found: <diagnostic details>
   - Resolution: Awaiting user to assign COS via dashboard
   ```

### Recovery Decision Tree

```
COS Assignment Fails
    |
    v
Is AI Maestro API running? ──NO──> Alert user, STOP
(GET /api/sessions)
    |
   YES
    v
Is target agent registered? ──NO──> Register agent first, RETRY
(GET /api/agents?name=<name>)
    |
   YES
    v
Does team exist and type=closed? ──NO──> Escalate to user: request team creation/fix via dashboard
(GET /api/teams/<team-id>)
    |
   YES
    v
Does team already have COS? ──YES──> Verify if re-assignment needed
(GET /api/teams/<team-id>)
    |
   NO
    v
Escalate to user: request COS assignment via dashboard
Provide diagnostic info and recommended COS candidate
Log findings
Wait for user to assign COS via dashboard
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
   1. Check AMCOS agent status: `GET $AIMAESTRO_API/api/agents?name=amcos-<project-name>`
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

See the `agent-messaging` skill for full messaging API details.

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

> **Note:** General agent creation failures get 2 retries before escalation, compared to 3 retries for AMCOS (COS) assignment (Section 1). COS assignment is more critical because it is required for project coordination, while specialist agents can be re-added later.

### Symptoms

- Agent registration API call returns error
- Agent registered but not responding to messages
- Agent not appearing in AI Maestro registry after creation

### Recovery Procedure

1. **Check AI Maestro API health**
   ```
   GET $AIMAESTRO_API/api/sessions
   ```

2. **Verify agent is registered in AI Maestro**
   ```
   GET $AIMAESTRO_API/api/agents?name=<agent-name>
   ```

3. **Check team membership**
   ```
   GET $AIMAESTRO_API/api/teams/<team-id>
   ```

4. **Retry agent registration**
   - Register the agent using `aimaestro-agent.sh` or the `ai-maestro-agents-management` skill.
   - Verify the agent appears in the registry with correct status
   - Confirm the agent can receive messages

5. **After 2 retries, escalate to user**
   ```
   Agent Creation Failed: <agent-type>

   Agent: <agent-name>
   Attempts: 2
   Team: <team-id>
   Error: <error output>

   Diagnostic info:
   - AI Maestro API: Running
   - Agent in registry: <yes/no>
   - Team exists: <yes/no>

   Recommended actions:
   1. Check AI Maestro API health: `GET $AIMAESTRO_API/api/sessions`
   2. Check agent registry: `GET $AIMAESTRO_API/api/agents`
   3. Review AI Maestro logs for registration errors

   Should I:
   - Retry with a different agent configuration?
   - Skip this specialist and continue without it?
   - Abort and investigate manually?
   ```

---

## 5. Logging and Audit Trail

All failures MUST be logged for debugging and audit purposes.

### Log Locations

| Failure Type | Log File | Format |
|--------------|----------|--------|
| COS assignment failures | `docs_dev/sessions/spawn-failures.md` | Markdown |
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

- COS assignment failure detection: Immediate (API response check)
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

### Example 1: COS Assignment Fails (AI Maestro Down)

**Scenario**: COS role assignment API call returns an error

**Your Action**: Diagnose and report to user

**Your Response to User**:
```
Issue encountered: COS role assignment failed

Details: COS role assignment API call returned error (PATCH /api/teams/<team-id>/chief-of-staff)
Impact: Cannot coordinate agents for inventory-system project
Attempted: Assigning COS role to amcos-inventory-system agent

Error output: [paste relevant error]

I recommend: Verify AI Maestro API is running by checking `GET /api/sessions`.
If down, restart it. Then please retry COS assignment via the dashboard.

Would you like me to check the AI Maestro health status?
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

I sent a work
