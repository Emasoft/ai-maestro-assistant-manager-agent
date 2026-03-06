# Agent Creation Failure Recovery Procedures


## Contents

- [Overview](#overview)
- [1. AMCOS COS Assignment Failure Recovery Protocol](#1-amcos-cos-assignment-failure-recovery-protocol)
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
  - [Example 1: COS Assignment Fails (AI Maestro Down)](#example-1-cos-assignment-fails-ai-maestro-down)
  - [Example 2: AMCOS Not Responding to Routing Request](#example-2-amcos-not-responding-to-routing-request)
  - [Example 3: Conflicting Approval Requests](#example-3-conflicting-approval-requests)
- [Summary](#summary)

## Overview

This document provides recovery procedures for handling failures in COS (Chief of Staff) role assignment, agent registration, and inter-agent communication within the AMAMA system. All operations use the AI Maestro v2 API.

---

## 1. AMCOS COS Assignment Failure Recovery Protocol

When COS (Chief of Staff) role assignment fails via the AI Maestro API, follow this recovery procedure systematically before escalating to the user.

> **Note on retry counts:** AMCOS (COS) assignment gets 3 retries because it is critical for project coordination. General agent creation failures (Section 4) get 2 retries before escalation, since specialist agents can be re-added later without disrupting the team structure.

### Recovery Steps

#### Step 1: Verify AI Maestro API is Running

```bash
curl -s "http://localhost:23000/api/health" | jq .
```

If AI Maestro API is down or not responding:
- Alert user: "AI Maestro API is not responding. Please restart it."
- Do NOT proceed with COS assignment retry until API health is confirmed

#### Step 2: Verify the Target Agent is Registered

```bash
curl -s "http://localhost:23000/api/agents?name=<agent-name>" | jq .
```

If the target agent is not registered:
- Register the agent first via the AI Maestro API
- Verify registration succeeded before proceeding

#### Step 3: Verify the Team Exists and is Type `closed`

```bash
curl -s "http://localhost:23000/api/teams/<team-id>" | jq '{id, name, type, chief_of_staff}'
```

If the team does not exist or is not type `closed`:
- Create the team or update its type as needed
- Document the issue in session log

#### Step 4: Check if Team Already Has a COS Assigned

```bash
curl -s "http://localhost:23000/api/teams/<team-id>" | jq '.chief_of_staff'
```

If a COS is already assigned:
- Determine if re-assignment is needed (e.g., replacing a non-responsive COS)
- If the existing COS is functioning, no action needed

#### Step 5: Retry COS Assignment

```bash
curl -X PATCH "http://localhost:23000/api/teams/<team-id>/chief-of-staff" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent-id>"}'
```

Retry with the same agent, or if repeated failures occur, try assigning a different eligible agent.

Track retry count in the session state file `docs_dev/sessions/cos-assignment-retries.md` with timestamp, team ID, target agent, and attempt number:
```markdown
## COS Assignment Retry: <timestamp>
- Team ID: <team-id>
- Target Agent: <agent-name>
- Attempt: <1|2|3>
- Result: <success|error-details>
```

#### Step 6: If 3 Retries Fail

After 3 failed COS assignment attempts:

1. **Team continues WITHOUT COS**
   - The team still exists in AI Maestro — it just lacks a COS
   - AMAMA can still receive user requests
   - AMAMA cannot delegate to specialists until a COS is assigned

2. **Notify User**
   ```
   COS Assignment Failed After 3 Attempts

   Team: <team-id>
   Target Agent: <agent-name>
   Status: Team exists WITHOUT COS coordination

   Attempted:
   - Attempt 1: <error>
   - Attempt 2: <error>
   - Attempt 3: <error>

   Impact:
   - Cannot delegate to specialist agents (AMOA, AMAA, AMIA)
   - Team structure is intact in AI Maestro
   - You can still interact with me for planning

   To fix:
   1. Check AI Maestro API health: `curl -s http://localhost:23000/api/health`
   2. Check agent registration: `curl -s http://localhost:23000/api/agents?name=<agent-name>`
   3. Check team status: `curl -s http://localhost:23000/api/teams/<team-id>`
   4. Restart AI Maestro if needed

   Once fixed, I can retry COS assignment. Say "retry COS for <team-id>" when ready.
   ```

3. **Log Failure**
   Record in `docs_dev/sessions/spawn-failures.md`:
   ```markdown
   ## COS Assignment Failure: <timestamp>
   - Team: <team-id>
   - Target Agent: <agent-name>
   - Attempts: 3
   - Errors: <error details>
   - Resolution: Awaiting user intervention
   ```

#### Step 7: Allow User Manual Fix and Retry

When user says "retry COS for <team-id>":
1. Re-run verification steps (API health, agent registration, team status)
2. Attempt COS assignment with same or different agent
3. Report success or escalate again if still failing

### Recovery Decision Tree

```
COS Assignment Fails
    |
    v
Is AI Maestro API running? ──NO──> Alert user, STOP
(GET /api/health)
    |
   YES
    v
Is target agent registered? ──NO──> Register agent first, RETRY
(GET /api/agents?name=<name>)
    |
   YES
    v
Does team exist and type=closed? ──NO──> Create/fix team, RETRY
(GET /api/teams/<team-id>)
    |
   YES
    v
Does team already have COS? ──YES──> Verify if re-assignment needed
(GET /api/teams/<team-id>)
    |
   NO
    v
Retry count < 3? ──YES──> Wait 10 seconds, RETRY COS assignment
(Track in docs_dev/sessions/cos-assignment-retries.md)
    |
   NO
    v
Team continues WITHOUT COS
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
   1. Check AMCOS agent status: `curl -s http://localhost:23000/api/agents?name=amcos-<project-name>`
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

> **Note:** General agent creation failures get 2 retries before escalation, compared to 3 retries for AMCOS (COS) assignment (Section 1). COS assignment is more critical because it is required for project coordination, while specialist agents can be re-added later.

### Symptoms

- Agent registration API call returns error
- Agent registered but not responding to messages
- Agent not appearing in AI Maestro registry after creation

### Recovery Procedure

1. **Check AI Maestro API health**
   ```bash
   curl -s "http://localhost:23000/api/health" | jq .
   ```

2. **Verify agent is registered in AI Maestro**
   ```bash
   # Check if the agent exists in the registry
   curl -s "http://localhost:23000/api/agents?name=<agent-name>" | jq .
   ```

3. **Check team membership**
   ```bash
   # Verify the agent's team assignment
   curl -s "http://localhost:23000/api/teams/<team-id>" | jq '.members'
   ```

4. **Retry agent registration**
   - Re-register the agent via the AI Maestro API
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
   1. Check AI Maestro API health: `curl -s http://localhost:23000/api/health`
   2. Check agent registry: `curl -s http://localhost:23000/api/agents`
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

I recommend: Verify AI Maestro API is running by checking `GET /api/health`.
If down, restart it. Then I'll retry COS assignment.

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

Can you check the AMCOS agent status? `curl -s http://localhost:23000/api/agents?name=amcos-inventory-system`

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

1. **Systematic diagnosis** - Check AI Maestro API health, agent registry, team status
2. **Automatic retries** - Up to 3 attempts with delays
3. **Clear user escalation** - Provide diagnostic info and options
4. **Comprehensive logging** - Audit trail for all failures
5. **Timeliness** - Don't block indefinitely; escalate quickly

**Key Principle**: When in doubt, escalate to user with clear options. Do NOT guess, assume, or hide failures.
