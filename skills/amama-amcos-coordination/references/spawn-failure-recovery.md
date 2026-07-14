# Agent Creation Failure Recovery Procedures

## Contents

- [Overview](#overview)
- [1. Team + COS Creation Failure Recovery Protocol](#1-team--cos-creation-failure-recovery-protocol)
- [2. Communication Breakdown Recovery](#2-communication-breakdown-recovery)
- [3. Approval Request Handling Failures](#3-approval-request-handling-failures)
- [4. Agent Creation Failures (General)](#4-agent-creation-failures-general)
- [5. Logging and Audit Trail](#5-logging-and-audit-trail)
- [6. Timeliness Requirements](#6-timeliness-requirements)
- [7. Example Scenarios](#7-example-scenarios)
- [Summary](#summary)

## Overview

This document provides recovery procedures for handling failures in team + COS creation (R29), agent registration, and inter-agent communication within the AMAMA system. All operations go through the frozen CLIs (`aimaestro-teams.sh`, `aimaestro-agent.sh`), which resolve AID auth internally (R28) — never a sudo/governance password (R32).

---

## 1. Team + COS Creation Failure Recovery Protocol

When team creation (and its auto-created COS, R29) fails via the frozen CLI, follow this recovery procedure systematically. You (the MANAGER) own team + COS lifecycle (R29), so recovery is yours to drive — recreate the team yourself; only escalate to the user for an environment failure you cannot fix (e.g. the server is unreachable).

> **Note on retry counts:** Team + COS creation gets 3 retries because it is critical for project coordination. General agent creation failures (Section 4) get 2 retries before escalation, since specialist agents can be re-added later without disrupting the team structure.

### Recovery Steps

#### Step 1: Verify AI Maestro API is Running

```
aimaestro-agent.sh list >/dev/null 2>&1; echo $?
```

(liveness only — consume just the exit code; non-zero exit ⇒ server unreachable)

If AI Maestro API is down or not responding:
- Alert user: "AI Maestro API is not responding. Please restart it." (server health is an environment issue only the user can fix)
- Do NOT proceed with team creation retry until API health is confirmed

#### Step 2: Verify Any Pre-Required Agent is Registered

```
aimaestro-agent.sh list > /tmp/amama-agents.txt
```

(then `grep` the scratch file for `<agent-name>` — don't read the raw listing into context)

If a pre-required agent is not registered:
- Register the agent using `aimaestro-agent.sh create <name>` or the `ai-maestro-agents-management` skill.
- Verify registration succeeded before proceeding

#### Step 3: Re-Create the Team Yourself (R29)

```
aimaestro-teams.sh create --name <team-name> --type closed [...]
```

If the team does not exist or was created without a COS:
- Re-run team creation yourself (R29) — the server auto-creates the COS for a `closed` team. Never fall back to a sudo/password path (R32)
- Document the issue in session log

See the `team-governance` skill for full CLI details.

#### Step 4: Check if the COS Was Auto-Created

```
aimaestro-teams.sh show <team-id>
```

If `chiefOfStaff` is set, the COS exists:
- Wake it (`aimaestro-agent.sh wake <cos-id>`) and grant its mandate (R30)
- If the existing COS is functioning, no recreation needed

#### Step 5: Recreate the Team if the COS Is Missing

The COS is auto-created with the team (R29). If `chiefOfStaff` is unset after creation, the creation did not complete:
- Delete the partial team (`aimaestro-teams.sh delete <team-id>`) and re-create it (R29) so a fresh COS is auto-created
- This is your call to make (R29) — do NOT wait on the user, and do NOT use a sudo/password path (R32)

Track the recovery in the session state file `docs_dev/sessions/cos-creation-retries.md` with timestamp, team ID, and findings.

#### Step 6: If Team + COS Creation Continues to Fail

If creation fails after 3 retries:

1. **Team has no COS — FROZEN (R31)**
   - A team without its COS + 5 base members is FROZEN: only the COS active, all others hibernated (R31)
   - AMAMA can still receive user requests
   - AMAMA cannot delegate to specialists until the COS + 5 base members exist

2. **Provide Diagnostic Info to User** (environment-failure escalation only)
   ```
   Team + COS Creation Diagnostics

   Team: <team-id>
   Status: Team creation not completing (no COS auto-created)

   Diagnostic checks:
   1. AI Maestro connectivity: `aimaestro-agent.sh list` (non-zero exit ⇒ server unreachable)
   2. Team status: `aimaestro-teams.sh show <team-id>`
   3. Retries attempted: 3 (R29 — MANAGER re-created the team each time)

   This looks like a server/environment issue. Please verify AI Maestro health; I will re-create the team once it is healthy.
   ```

3. **Log Failure**
   Record in `docs_dev/sessions/spawn-failures.md`:
   ```markdown
   ## Team + COS Creation Failure: <timestamp>
   - Team: <team-id>
   - Issues found: <diagnostic details>
   - Resolution: MANAGER re-created 3× (R29); escalated server-health issue to user
   ```

### Recovery Decision Tree

```
Team + COS Creation Fails
    |
    v
Is AI Maestro API running? ──NO──> Alert user (server health), STOP
(aimaestro-agent.sh list)
    |
   YES
    v
Is any pre-required agent registered? ──NO──> Register agent first, RETRY
(aimaestro-agent.sh list, filter by name)
    |
   YES
    v
Does the team exist (type=closed)? ──NO──> Create it yourself (R29), RETRY
(aimaestro-teams.sh show <team-id>)              (aimaestro-teams.sh create --type closed)
    |
   YES
    v
Was the COS auto-created (chiefOfStaff set)? ──YES──> Wake it + grant mandate (R30)
(aimaestro-teams.sh show <team-id>)
    |
   NO
    v
Delete + re-create the team yourself (R29) so a fresh COS is auto-created
Log findings; never use a sudo/password path (R32)
Escalate to user ONLY for a server-health issue you cannot fix
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
   1. Check AMCOS agent status: `aimaestro-agent.sh show amcos-<project-name>`
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
   aimaestro-agent.sh list >/dev/null 2>&1; echo $?
   ```
   (liveness only — consume just the exit code; non-zero exit ⇒ server unreachable)

2. **Verify agent is registered in AI Maestro**
   ```
   aimaestro-agent.sh list > /tmp/amama-agents.txt
   ```
   (then `grep` the scratch file for `<agent-name>` — don't read the raw listing into context)

3. **Check team membership**
   ```
   aimaestro-teams.sh show <team-id>
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
   1. Check AI Maestro connectivity: `aimaestro-agent.sh list` (non-zero exit ⇒ server unreachable)
   2. Check agent registry: `aimaestro-agent.sh list`
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

### Example 1: Team + COS Creation Fails (AI Maestro Down)

**Scenario**: `aimaestro-teams.sh create` returns an error (server unreachable)

**Your Action**: Diagnose; recreate the team yourself once the server is healthy (R29). Escalate only the server-health issue to the user.

**Your Response to User**:
```
Issue encountered: team + COS creation failed

Details: `aimaestro-teams.sh create` returned an error — the AI Maestro server appears unreachable
Impact: Cannot coordinate agents for inventory-system project (no team/COS yet)
Attempted: Creating the team myself (R29) — the server auto-creates the COS

Error output: [paste relevant error]

This looks like a server/environment issue (the one thing only you can fix). Verify AI Maestro is reachable
by running `aimaestro-agent.sh list` (non-zero exit ⇒ server unreachable). Once it is healthy, I will re-create
the team and grant the COS its mandate (R30).

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

I sent a work request 60s ago and the COS has not responded, even after a health-check retry.

Checked:
- AI Maestro API: Running
- Message sent successfully: Yes
- Response received: No

Possible causes: COS session crashed, overloaded, or an AI Maestro routing issue.

Actions: check the COS status (`aimaestro-agent.sh show <cos-id>`); if it is unresponsive I can
delete + recreate the team so a fresh COS is auto-created (R29). I will not use a sudo/password path (R32).
```
