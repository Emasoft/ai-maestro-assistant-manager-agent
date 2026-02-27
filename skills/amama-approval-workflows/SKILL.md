---
name: eama-approval-workflows
description: Use when handling approval requests from other roles that require user decisions on code, releases, or security gates. Trigger with approval requests from ECOS or other agents.
version: 1.0.0
compatibility: Requires AI Maestro installed.
context: fork
agent: eama-main
user-invocable: false
triggers:
  - Any role sends an approval request via AI Maestro
  - User needs to make a decision about code, releases, or security
  - Quality gates require human authorization
---

# Approval Workflows Skill

## Overview

This skill provides the Assistant Manager (EAMA) with standard workflows for handling approval requests from other roles and presenting them to the user for decision.

## Prerequisites

- AI Maestro messaging system must be running
- EAMA must have access to `docs_dev/handoffs/` directory
- State file must be writable for approval tracking

## Instructions

1. Listen for approval requests from other roles via AI Maestro
2. Parse the approval request to determine type (push, merge, publish, security, design)
3. Present the approval request to the user using the appropriate template
4. Record the user's decision with timestamp
5. Send the approval response back to the requesting role
6. Update the approval state tracking file

## Plugin Prefix Reference

| Role | Prefix | Plugin Name |
|------|--------|-------------|
| Assistant Manager | `eama-` | Emasoft Assistant Manager Agent |
| Architect | `eaa-` | Emasoft Architect Agent |
| Orchestrator | `eoa-` | Emasoft Orchestrator Agent |
| Integrator | `eia-` | Emasoft Integrator Agent |

## Approval Types

### 1. Push Approval

**Trigger**: Code is ready to be pushed to remote repository

**Workflow**:
1. Receive approval request from EOA/EIA
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

### 2. Merge Approval

**Trigger**: PR is ready to be merged

**Workflow**:
1. Receive approval request from EIA
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
4. Send approval response to EIA

### 3. Publish Approval

**Trigger**: Package/release is ready to be published

**Workflow**:
1. Receive approval request from EIA
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
4. Send approval response to EIA

### 4. Security Approval

**Trigger**: Action with security implications requires authorization

**Workflow**:
1. Receive approval request from any role (EAA/EOA/EIA)
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

### 5. Design Approval

**Trigger**: EAA (Architect) has completed design document

**Workflow**:
1. Receive completion signal from EAA
2. Present to user:
   ```
   ## Design Approval Requested

   **Design**: {design_name}
   **Document**: {path_to_design_doc}
   **Modules**: {count} modules defined
   **Estimated Scope**: {scope_summary}

   Review the design document and approve to proceed with implementation.
   - [Approve] - Proceed to orchestration
   - [Request Changes] - Send back to EAA
   - [Discuss] - I have questions
   ```
3. Record user decision
4. If approved, create handoff to EOA

## Approval State Tracking

All approvals are tracked in state file:

```yaml
approvals:
  - id: "approval-{uuid}"
    type: "merge"
    requested_by: "eia"
    requested_at: "ISO-8601"
    status: "pending" | "approved" | "rejected"
    user_decision: null | "approve" | "reject" | "request_changes"
    decided_at: null | "ISO-8601"
    conditions: []
    notes: ""
```

## Escalation Rules

### Auto-Reject Conditions
- Request older than 24 hours without response
- Requesting role session terminated
- Blocking security vulnerability detected

### Auto-Approve Conditions (NEVER by default)
- No auto-approve without explicit user configuration
- All approvals require human decision

### Escalation Triggers
- Security approval with "critical" risk level
- Approval request with "urgent" priority
- Multiple failed approval attempts

## Approval Expiry Workflow

Approval requests that remain pending for too long must be automatically rejected to prevent stale requests from blocking workflows.

### Expiry Check Schedule

Check approval timestamps every hour to identify expired requests:

```bash
# Find approvals older than 24 hours
CURRENT_TIME=$(date +%s)
EXPIRY_THRESHOLD=$((24 * 60 * 60))  # 24 hours in seconds

# Using jq to find expired approvals in state file
cat docs_dev/approvals/approval-state.yaml | yq -r '
  .approvals[] |
  select(.status == "pending") |
  select((now - (.requested_at | fromdateiso8601)) > 86400) |
  .id
'
```

### Expiry Workflow Steps

**Step 1: Identify Expired Approvals**

Every hour, scan for approvals where:
- `status` is `pending`
- `requested_at` is more than 24 hours ago

**Step 2: Auto-Reject Expired Approvals**

For each expired approval:

1. **Update approval status**
   ```yaml
   approvals:
     - id: "approval-{uuid}"
       status: "rejected"
       user_decision: "auto-rejected"
       decided_at: "<current-ISO-8601>"
       notes: "EXPIRED: Auto-rejected after 24 hours without response"
   ```

2. **Send rejection notice to requesting role**
   Send an expiry rejection notice using the `agent-messaging` skill:
   - **Recipient**: `<requesting-role-session>`
   - **Subject**: "Approval Expired: <REQUEST-ID>"
   - **Content**: approval_decision type, request_id, decision "rejected", reason "EXPIRED: Request was pending for more than 24 hours without user response. Please resubmit if still needed.", expired_at, original_requested_at
   - **Type**: `approval_decision`
   - **Priority**: `normal`

   **Verify**: confirm message delivery via the skill's sent messages feature.

3. **Log to approval-log.md**
   ```markdown
   ## APPROVAL-<ID> - EXPIRED

   - **Request ID**: <REQUEST-ID>
   - **From**: <requesting-role>
   - **Requested**: <requested_at>
   - **Expired**: <current-timestamp>
   - **Decision**: REJECTED (EXPIRED)
   - **Reason**: Auto-rejected after 24 hours without user response
   - **Action Required**: Requesting role should resubmit if still needed
   ```

**Step 3: Notify User of Expirations (Optional)**

If user preference is set to receive expiry notifications:
```
Approval Requests Expired

The following approval requests were auto-rejected after 24 hours:

- <REQUEST-ID-1>: <operation-summary> (from <role>)
- <REQUEST-ID-2>: <operation-summary> (from <role>)

These requests have been returned to the requesting roles. They can resubmit if still needed.
```

### Expiry Checklist

- [ ] Hourly expiry check scheduled
- [ ] Expired approvals identified (pending > 24 hours)
- [ ] Approval status updated to "rejected" with "EXPIRED" reason
- [ ] Rejection notice sent to requesting role via AI Maestro
- [ ] Expiry logged in approval-log.md
- [ ] User notified if configured to receive expiry notifications

### Expiry Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `expiry_threshold_hours` | 24 | Hours before auto-reject |
| `expiry_check_interval_minutes` | 60 | How often to check for expired |
| `notify_user_on_expiry` | false | Send summary to user on expiry |
| `allow_resubmission` | true | Requesting role can resubmit after expiry |

## User Notification

When approval is requested:
1. Display approval request prominently
2. If user is idle, send periodic reminders
3. Block relevant workflow until decision received
4. Log all approval requests and decisions

## Examples

### Example 1: Handling a Push Approval Request

```
# Incoming message from EOA via AI Maestro
Subject: Push Approval Requested
Priority: high
Content: Branch feature/user-auth ready for push. 5 files modified. All tests passed.

# EAMA presents to user
## Push Approval Requested

**Branch**: feature/user-auth
**Changes**: Added user authentication module
**Files Modified**: 5
**Tests Status**: All 23 tests passed

Do you approve pushing these changes?
- [Approve] - Push to remote
- [Reject] - Cancel push
- [Review] - Show me the changes first

# User responds: "Approve"

# EAMA sends response to EOA
Subject: Push Approved
Content: User approved push for feature/user-auth at 2025-01-30T10:00:00Z
```

### Example 2: Security Approval with Critical Risk

```
# EAMA receives security approval request
## Security Approval Required

**Action**: Update production database schema
**Risk Level**: critical
**Affected Systems**: users, orders, payments
**Justification**: Required for GDPR compliance
**Rollback Plan**: Restore from backup-2025-01-29

This action has security implications. Do you authorize it?
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Approval request pending | No user response | Send periodic reminders; keep request active until user responds |
| Invalid approval type | Unknown type in request | Query sender for clarification |
| State file write failure | Permissions or disk issue | Retry 3 times, then escalate to user |
| Missing handoff context | Incomplete request | Return to sender with "INCOMPLETE" flag |

## Output

| Outcome | Status | Action |
|---------|--------|--------|
| User approves | `approved` | Send approval message to requesting role and update state file |
| User rejects | `rejected` | Send rejection message to requesting role and update state file |
| User requests changes | `request_changes` | Send feedback to requesting role with user comments |
| User requests review | `pending` | Display requested information and re-present approval request |
| Timeout (24 hours) | `rejected` | Auto-reject and notify requesting role |

## Checklist

Copy this checklist and track your progress:

- [ ] Listen for approval requests via AI Maestro
- [ ] Parse approval request to determine type (push/merge/publish/security/design)
- [ ] Present approval request to user using appropriate template
- [ ] Wait for user decision
- [ ] Record user decision with timestamp in state file
- [ ] Send approval response back to requesting role
- [ ] Update approval state tracking file
- [ ] Log approval request and decision
- [ ] Handle any errors or timeouts according to escalation rules

## Resources

For message templates, see the shared message templates reference. For handoff format, see the shared handoff template reference.

### Reference Documents

- [references/rule-14-enforcement.md](references/rule-14-enforcement.md) - RULE 14: User Requirements Are Immutable
- [references/best-practices.md](references/best-practices.md) - Approval workflow best practices
