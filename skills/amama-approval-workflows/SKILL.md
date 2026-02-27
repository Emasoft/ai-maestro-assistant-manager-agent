---
name: amama-approval-workflows
description: Use when handling governance approval requests that require MANAGER authorization via the GovernanceRequest API. Covers team membership, agent lifecycle, COS assignment, and agent transfers.
version: 2.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - A GovernanceRequest is created with status "pending"
  - An agent or COS submits a transfer request
  - MANAGER needs to approve/reject a governance operation
  - Quality gates or security gates require MANAGER authorization
---

# Approval Workflows Skill

## Overview

This skill provides the Assistant Manager (AMAMA) with structured workflows for handling **governance** approval requests through the GovernanceRequest API.

**Two approval tracks exist in AI Maestro:**

| Track | Scope | Mechanism | Skill |
|-------|-------|-----------|-------|
| **Governance approvals** | Team membership, COS assignment, agent lifecycle, transfers | GovernanceRequest API (`POST /api/governance/requests/{id}/approve`) | This skill (`amama-approval-workflows`) |
| **Operational approvals** | Deployments, merges, test runs, routine AMCOS operations | Message-based flow (`approval_request` / `approval_decision` messages) | `amama-amcos-coordination` skill |

Governance approvals use typed GovernanceRequest objects with a defined state machine. Operational approvals use the message-based flow described in `amama-amcos-coordination/references/message-formats.md`.

## Prerequisites

- AI Maestro v2+ with Governance API running at `$AIMAESTRO_API` (default: `http://localhost:23000`)
- Governance password must be set (see Governance Password Management below)
- AMAMA must have access to `docs_dev/handoffs/` directory
- State file must be writable for local approval tracking

## Governance Password Management

The governance password authenticates MANAGER approval/rejection actions. It is required before any GovernanceRequest can be approved or rejected.

### Initial Setup

Set the governance password on first use:

```bash
curl -X POST "$AIMAESTRO_API/api/governance/password" \
  -H "Content-Type: application/json" \
  -d '{"password": "<governance-password>"}'
```

- The password is bcrypt-hashed and stored in `~/.aimaestro/governance.json`
- The plaintext password is never stored; only the bcrypt hash is persisted
- If the password file does not exist, the first `POST` creates it
- To change the password, the existing password must be provided:

```bash
curl -X POST "$AIMAESTRO_API/api/governance/password" \
  -H "Content-Type: application/json" \
  -d '{"currentPassword": "<old-password>", "password": "<new-password>"}'
```

### Rate Limiting

- **5 failed authentication attempts** trigger a **60-second cooldown**
- During cooldown, all approval/rejection requests return `429 Too Many Requests`
- The cooldown resets after 60 seconds of no attempts
- Successful authentication resets the failure counter

### Security Rules

- NEVER store the governance password in plaintext in any file, log, or message
- NEVER include the governance password in AI Maestro messages between agents
- The password is provided by the user at runtime or read from a secure environment variable
- If the password is not set, all governance operations MUST fail with a clear error

## Instructions

1. Poll or receive webhook notifications for GovernanceRequests with status `pending`
2. Parse the GovernanceRequest to determine its type
3. Present the request to the user (MANAGER) using the appropriate template
4. On user decision, call the approve or reject API endpoint with the governance password
5. Verify the status transition completed successfully
6. Update local approval state tracking
7. Notify the requesting agent of the outcome

## Plugin Prefix Reference

| Role | Prefix | Plugin Name |
|------|--------|-------------|
| Assistant Manager | `amama-` | AI Maestro Assistant Manager Agent |
| Architect | `amaa-` | AI Maestro Architect Agent |
| Orchestrator | `amoa-` | AI Maestro Orchestrator Agent |
| Integrator | `amia-` | AI Maestro Integrator Agent |

## GovernanceRequest State Machine

Every GovernanceRequest follows this state machine:

```
pending ──► remote-approved ──► dual-approved ──► executed
   │               │
   │        pending ──► local-approved ──► dual-approved ──► executed
   │
   └──► rejected
```

### States

| State | Description |
|-------|-------------|
| `pending` | Request created, awaiting approval |
| `remote-approved` | Approved by the remote authority (e.g., API/webhook) but not yet by MANAGER locally |
| `local-approved` | Approved by MANAGER locally but not yet by remote authority |
| `dual-approved` | Both local (MANAGER) and remote approvals obtained |
| `executed` | The approved operation has been carried out |
| `rejected` | Request denied by MANAGER or auto-rejected |

### Transitions

- `pending` -> `remote-approved`: Remote authority approves first
- `pending` -> `local-approved`: MANAGER approves first
- `pending` -> `rejected`: MANAGER rejects, or auto-rejection (expiry)
- `remote-approved` -> `dual-approved`: MANAGER provides the second approval
- `local-approved` -> `dual-approved`: Remote authority provides the second approval
- `dual-approved` -> `executed`: The system executes the approved operation

## GovernanceRequest Types

### 1. add-to-team

**Trigger**: An agent needs to be added to a team.

**Request payload**:
```json
{
  "type": "add-to-team",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "role": "<role-in-team>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

**Present to MANAGER**:
```
## Governance Request: Add Agent to Team

**Request ID**: {id}
**Type**: add-to-team
**Agent**: {agentId} ({agent_name})
**Team**: {teamId} ({team_name})
**Role**: {role}
**Requested By**: {requestedBy}
**Reason**: {reason}

Approve adding this agent to the team?
- [Approve] - Add agent to team
- [Reject] - Deny request
```

### 2. remove-from-team

**Trigger**: An agent needs to be removed from a team.

**Request payload**:
```json
{
  "type": "remove-from-team",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

### 3. assign-cos

**Trigger**: A COS (Chief of Staff) role needs to be assigned to an agent for a team.

**Request payload**:
```json
{
  "type": "assign-cos",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

### 4. remove-cos

**Trigger**: A COS role needs to be revoked from an agent.

**Request payload**:
```json
{
  "type": "remove-cos",
  "agentId": "<agent-uuid>",
  "teamId": "<team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

### 5. transfer-agent

**Trigger**: An agent needs to be moved from one team to another.

**Request payload**:
```json
{
  "type": "transfer-agent",
  "agentId": "<agent-uuid>",
  "fromTeamId": "<source-team-uuid>",
  "toTeamId": "<destination-team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "note": "<transfer-justification>"
}
```

**Present to MANAGER**:
```
## Governance Request: Transfer Agent

**Request ID**: {id}
**Type**: transfer-agent
**Agent**: {agentId} ({agent_name})
**From Team**: {fromTeamId} ({from_team_name})
**To Team**: {toTeamId} ({to_team_name})
**Requested By**: {requestedBy}
**Note**: {note}

Approve transferring this agent between teams?
- [Approve] - Execute transfer
- [Reject] - Deny transfer
```

**Who can approve**: MANAGER, or the COS of the destination team.

### 6. create-agent

**Trigger**: A new agent needs to be provisioned.

**Request payload**:
```json
{
  "type": "create-agent",
  "agentName": "<agent-name>",
  "agentType": "<agent-type>",
  "teamId": "<target-team-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>",
  "config": {}
}
```

### 7. delete-agent

**Trigger**: An agent needs to be decommissioned.

**Request payload**:
```json
{
  "type": "delete-agent",
  "agentId": "<agent-uuid>",
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

### 8. configure-agent

**Trigger**: An agent's configuration needs to be modified.

**Request payload**:
```json
{
  "type": "configure-agent",
  "agentId": "<agent-uuid>",
  "changes": {},
  "requestedBy": "<requesting-agent-id>",
  "reason": "<justification>"
}
```

## GovernanceRequest API Endpoints

### List Pending Requests

```bash
curl -s "$AIMAESTRO_API/api/v1/governance/requests?status=pending" \
  -H "Content-Type: application/json"
```

### Get a Specific Request

```bash
curl -s "$AIMAESTRO_API/api/v1/governance/requests/{id}" \
  -H "Content-Type: application/json"
```

### Approve a Request (MANAGER only)

```bash
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/{id}/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "<governance-password>",
    "approvedBy": "MANAGER",
    "conditions": [],
    "notes": "<optional-notes>"
  }'
```

**Response on success**: Status transitions to `local-approved` or `dual-approved` (if remote already approved).

### Reject a Request (MANAGER only)

```bash
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/{id}/reject" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "<governance-password>",
    "rejectedBy": "MANAGER",
    "reason": "<rejection-reason>"
  }'
```

**Response on success**: Status transitions to `rejected`. The operation is permanently blocked.

### Submit a Transfer Request

```bash
curl -X POST "$AIMAESTRO_API/api/governance/transfers" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "<agent-uuid>",
    "fromTeamId": "<source-team-uuid>",
    "toTeamId": "<destination-team-uuid>",
    "note": "<transfer-justification>"
  }'
```

**Response**: Creates a GovernanceRequest of type `transfer-agent` with status `pending`. Returns the request ID.

**Who can approve transfers**:
- MANAGER (via governance password)
- COS of the destination team (via their authority token)

## Transfer Request Handling (M5)

Transfer requests have special routing rules because they involve two teams.

### Transfer Workflow

1. **Request submitted** via `POST /api/governance/transfers`
2. A GovernanceRequest of type `transfer-agent` is created with status `pending`
3. **Notifications sent** to:
   - MANAGER (AMAMA) for governance approval
   - COS of the destination team for domain approval
4. **Either** MANAGER or destination COS can approve:
   - If MANAGER approves: request moves to `local-approved`, awaiting remote (destination COS) confirmation, OR directly to `dual-approved` if COS already approved
   - If destination COS approves: request moves to `remote-approved`, awaiting MANAGER confirmation, OR directly to `dual-approved` if MANAGER already approved
5. **On dual-approved**: The transfer is executed automatically
6. **On rejected**: by either party, the transfer is cancelled

### Transfer Conflict Resolution

- If the source team COS objects, they can escalate to MANAGER
- If MANAGER and destination COS disagree, MANAGER's decision takes precedence
- Transfers that remain pending for more than 24 hours are auto-rejected

## Legacy Approval Types

The following approval types from v1 are still supported for backward compatibility with non-governance workflows (push, merge, publish, security, design). These use the standard AI Maestro messaging system rather than the GovernanceRequest API.

### Push Approval

**Trigger**: Code is ready to be pushed to remote repository

**Workflow**:
1. Receive approval request from AMOA/AMIA
2. Present to user:
   ```
   ## Push Approval Requested

   **Branch**: {branch_name}
   **Changes**: {summary_of_changes}
   **Files Modified**: {count}
   **Tests Status**: {passed/failed}

   Do you approve pushing these changes?
   - [Approve] - Push to remote
   - [Reject] - Cancel push
   - [Review] - Show me the changes first
   ```
3. Record user decision
4. Send approval response to requesting role

### Merge Approval

**Trigger**: PR is ready to be merged

**Workflow**:
1. Receive approval request from AMIA
2. Present to user:
   ```
   ## Merge Approval Requested

   **PR**: #{pr_number} - {pr_title}
   **Branch**: {source} -> {target}
   **Reviews**: {review_status}
   **CI Status**: {ci_status}
   **Conflicts**: {yes/no}

   Do you approve merging this PR?
   - [Approve] - Merge PR
   - [Reject] - Close without merging
   - [Request Changes] - Add comments
   ```
3. Record user decision
4. Send approval response to AMIA

### Publish Approval

**Trigger**: Package/release is ready to be published

**Workflow**:
1. Receive approval request from AMIA
2. Present to user:
   ```
   ## Publish Approval Requested

   **Package**: {package_name}
   **Version**: {version}
   **Target**: {npm/pypi/github releases/etc}
   **Changelog**: {summary}
   **Breaking Changes**: {yes/no}

   Do you approve publishing this release?
   - [Approve] - Publish
   - [Reject] - Cancel
   - [Review] - Show release notes
   ```
3. Record user decision
4. Send approval response to AMIA

### Security Approval

**Trigger**: Action with security implications requires authorization

**Workflow**:
1. Receive approval request from any role (AMAA/AMOA/AMIA)
2. Present to user:
   ```
   ## Security Approval Required

   **Action**: {action_description}
   **Risk Level**: {low/medium/high/critical}
   **Affected Systems**: {list}
   **Justification**: {reason_for_action}
   **Rollback Plan**: {description}

   This action has security implications. Do you authorize it?
   - [Authorize] - Proceed with action
   - [Deny] - Block action
   - [More Info] - Explain risks in detail
   ```
3. Record user decision with timestamp
4. Send authorization response

### Design Approval

**Trigger**: AMAA (Architect) has completed design document

**Workflow**:
1. Receive completion signal from AMAA
2. Present to user:
   ```
   ## Design Approval Requested

   **Design**: {design_name}
   **Document**: {path_to_design_doc}
   **Modules**: {count} modules defined
   **Estimated Scope**: {scope_summary}

   Review the design document and approve to proceed with implementation.
   - [Approve] - Proceed to orchestration
   - [Request Changes] - Send back to AMAA
   - [Discuss] - I have questions
   ```
3. Record user decision
4. If approved, create handoff to AMOA

## Approval State Tracking

All GovernanceRequests are tracked both in the API and in the local state file for redundancy:

```yaml
governance_requests:
  - id: "gov-{uuid}"
    type: "add-to-team"
    requested_by: "<agent-id>"
    requested_at: "ISO-8601"
    status: "pending" | "remote-approved" | "local-approved" | "dual-approved" | "executed" | "rejected"
    manager_decision: null | "approve" | "reject"
    decided_at: null | "ISO-8601"
    conditions: []
    notes: ""
    payload: {}

legacy_approvals:
  - id: "approval-{uuid}"
    type: "push" | "merge" | "publish" | "security" | "design"
    requested_by: "<role>"
    requested_at: "ISO-8601"
    status: "pending" | "approved" | "rejected"
    user_decision: null | "approve" | "reject" | "request_changes"
    decided_at: null | "ISO-8601"
    conditions: []
    notes: ""
```

## Escalation Rules

### Auto-Reject Conditions
- GovernanceRequest older than 24 hours without response
- Requesting agent session terminated
- Blocking security vulnerability detected
- Governance password rate-limit exceeded (requests queued until cooldown ends)

### Auto-Approve Conditions (NEVER by default)
- No auto-approve without explicit user configuration
- All governance requests require MANAGER decision

### Escalation Triggers
- Security-related GovernanceRequest (delete-agent, configure-agent with security changes)
- GovernanceRequest with "urgent" priority flag
- Multiple failed governance password attempts (potential breach)
- Transfer request contested by source team COS

## Approval Expiry Workflow

GovernanceRequests that remain pending for too long are automatically rejected to prevent stale requests from blocking workflows.

### Expiry Check Schedule

Check GovernanceRequest timestamps every hour to identify expired requests:

```bash
# Query pending governance requests older than 24 hours
curl -s "$AIMAESTRO_API/api/v1/governance/requests?status=pending&olderThan=24h" \
  -H "Content-Type: application/json"
```

### Expiry Workflow Steps

**Step 1: Identify Expired Requests**

Every hour, query for GovernanceRequests where:
- `status` is `pending`, `remote-approved`, or `local-approved`
- `requested_at` is more than 24 hours ago

**Step 2: Auto-Reject Expired Requests**

For each expired GovernanceRequest:

1. **Reject via API**
   ```bash
   curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/{id}/reject" \
     -H "Content-Type: application/json" \
     -d '{
       "password": "<governance-password>",
       "rejectedBy": "SYSTEM",
       "reason": "EXPIRED: Request pending for more than 24 hours without dual-approval"
     }'
   ```

2. **Update local state file**
   ```yaml
   governance_requests:
     - id: "gov-{uuid}"
       status: "rejected"
       manager_decision: "auto-rejected"
       decided_at: "<current-ISO-8601>"
       notes: "EXPIRED: Auto-rejected after 24 hours without response"
   ```

3. **Notify requesting agent** via AI Maestro messaging:
   - **Subject**: "GovernanceRequest Expired: {id}"
   - **Content**: type `governance_decision`, request_id, decision `rejected`, reason `EXPIRED`
   - **Priority**: `normal`

4. **Log to approval-log.md**
   ```markdown
   ## GOV-<ID> - EXPIRED

   - **Request ID**: <REQUEST-ID>
   - **Type**: <governance-request-type>
   - **From**: <requesting-agent>
   - **Requested**: <requested_at>
   - **Expired**: <current-timestamp>
   - **Decision**: REJECTED (EXPIRED)
   - **Reason**: Auto-rejected after 24 hours without dual-approval
   ```

**Step 3: Notify MANAGER of Expirations (Optional)**

If user preference is set to receive expiry notifications:
```
GovernanceRequests Expired

The following governance requests were auto-rejected after 24 hours:

- GOV-<ID-1>: <type> - <summary> (from <agent>)
- GOV-<ID-2>: <type> - <summary> (from <agent>)

These requests have been returned to the requesting agents. They can resubmit if still needed.
```

### Expiry Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `expiry_threshold_hours` | 24 | Hours before auto-reject |
| `expiry_check_interval_minutes` | 60 | How often to check for expired |
| `notify_user_on_expiry` | false | Send summary to MANAGER on expiry |
| `allow_resubmission` | true | Requesting agent can resubmit after expiry |

## User Notification

When a GovernanceRequest is created:
1. Display the request prominently with its type and payload summary
2. If user is idle, send periodic reminders
3. Block the requested operation until MANAGER decides
4. Log all requests and decisions to both the API and local state

## Examples

### Example 1: Approving a Team Membership Request

```bash
# 1. Poll for pending requests
curl -s "$AIMAESTRO_API/api/v1/governance/requests?status=pending"

# Response includes:
# {
#   "id": "gov-abc123",
#   "type": "add-to-team",
#   "status": "pending",
#   "payload": {
#     "agentId": "agent-007",
#     "teamId": "team-alpha",
#     "role": "developer",
#     "reason": "Needed for sprint 42 capacity"
#   }
# }

# 2. Present to MANAGER (user)
## Governance Request: Add Agent to Team
**Request ID**: gov-abc123
**Type**: add-to-team
**Agent**: agent-007 (CodeBot)
**Team**: team-alpha (Alpha Squad)
**Role**: developer
**Reason**: Needed for sprint 42 capacity

# 3. MANAGER approves
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-abc123/approve" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "approvedBy": "MANAGER", "notes": "Approved for sprint 42"}'

# Response: {"id": "gov-abc123", "status": "local-approved", ...}
```

### Example 2: Handling a Transfer Request

```bash
# 1. Transfer request arrives
curl -s "$AIMAESTRO_API/api/v1/governance/requests/gov-def456"

# {
#   "id": "gov-def456",
#   "type": "transfer-agent",
#   "status": "remote-approved",  <-- destination COS already approved
#   "payload": {
#     "agentId": "agent-042",
#     "fromTeamId": "team-beta",
#     "toTeamId": "team-gamma",
#     "note": "Agent expertise better suited for gamma's mission"
#   }
# }

# 2. Present to MANAGER -- note that destination COS already approved
## Governance Request: Transfer Agent
**Request ID**: gov-def456
**Status**: remote-approved (destination COS approved)
**Agent**: agent-042 (DataProcessor)
**From**: team-beta -> **To**: team-gamma
**Note**: Agent expertise better suited for gamma's mission

# 3. MANAGER approves -> transitions to dual-approved -> executed
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-def456/approve" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "approvedBy": "MANAGER"}'

# Response: {"id": "gov-def456", "status": "dual-approved", ...}
# System auto-executes the transfer -> status becomes "executed"
```

### Example 3: Rejecting a Dangerous Request

```bash
# 1. Delete-agent request arrives
# {
#   "id": "gov-ghi789",
#   "type": "delete-agent",
#   "status": "pending",
#   "payload": {
#     "agentId": "agent-001",
#     "reason": "Agent no longer needed"
#   }
# }

# 2. MANAGER rejects
curl -X POST "$AIMAESTRO_API/api/v1/governance/requests/gov-ghi789/reject" \
  -H "Content-Type: application/json" \
  -d '{"password": "***", "rejectedBy": "MANAGER", "reason": "Agent-001 is still critical for monitoring"}'

# Response: {"id": "gov-ghi789", "status": "rejected", ...}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid governance password | Prompt MANAGER to re-enter password; check for typos |
| `429 Too Many Requests` | Rate limit exceeded (5 failed attempts) | Wait 60 seconds for cooldown, then retry |
| `404 Not Found` | GovernanceRequest ID does not exist | Verify the request ID; it may have been already processed |
| `409 Conflict` | Invalid state transition (e.g., approving already rejected) | Refresh request status and present current state to MANAGER |
| Governance password not set | `~/.aimaestro/governance.json` missing | Run initial password setup via `POST /api/governance/password` |
| Transfer contested | Source COS escalates objection | Present both sides to MANAGER for final decision |
| State file write failure | Permissions or disk issue | Retry 3 times, then escalate to MANAGER |

## Output

| Outcome | Status | Action |
|---------|--------|--------|
| MANAGER approves | `local-approved` or `dual-approved` | Call approve endpoint, update state, notify requesting agent |
| MANAGER rejects | `rejected` | Call reject endpoint, update state, notify requesting agent |
| MANAGER requests more info | `pending` (unchanged) | Query additional details from requesting agent, re-present to MANAGER |
| Timeout (24 hours) | `rejected` | Auto-reject via API, notify requesting agent |
| Rate limit hit | `pending` (unchanged) | Queue the action, wait for cooldown, then retry |

## Checklist

Copy this checklist and track your progress:

- [ ] Verify governance password is set (`~/.aimaestro/governance.json` exists)
- [ ] Poll for pending GovernanceRequests via API
- [ ] Parse request type (add-to-team/remove-from-team/assign-cos/remove-cos/transfer-agent/create-agent/delete-agent/configure-agent)
- [ ] Present GovernanceRequest to MANAGER using appropriate template
- [ ] Wait for MANAGER decision
- [ ] Call approve or reject API endpoint with governance password
- [ ] Verify state transition completed (check response status)
- [ ] Update local approval state tracking file
- [ ] Notify requesting agent of the outcome via AI Maestro messaging
- [ ] Log the request and decision to approval-log.md
- [ ] Handle errors, rate limits, and timeouts according to escalation rules

## Resources

For message templates, see the shared message templates reference. For handoff format, see the shared handoff template reference.

### Reference Documents

- [references/rule-14-enforcement.md](references/rule-14-enforcement.md) - RULE 14: User Requirements Are Immutable (with GovernanceRequest type mapping)
- [references/best-practices.md](references/best-practices.md) - Approval workflow best practices
