# AMAMA-AMCOS Coordination Workflow Examples


## Contents

- [Example 1: User Requests New Project](#example-1-user-requests-new-project)
- [Example 2: AMCOS Requests Approval (Low Risk)](#example-2-amcos-requests-approval-low-risk)
- [Example 3: AMCOS Requests Approval (High Risk)](#example-3-amcos-requests-approval-high-risk)
- [Example 4: User Requests Status](#example-4-user-requests-status)
- [Example 5: COS Role Assignment Failure](#example-5-cos-role-assignment-failure)
- [COS Role Assignment Failure Recovery Protocol](#cos-role-assignment-failure-recovery-protocol)
- [Handoff Pattern](#handoff-pattern)

This document contains practical examples of AMAMA coordinating with AMCOS, including routing requests, handling approvals, status queries, and failure recovery.

---

## Example 1: User Requests New Project

**User**: "Build a REST API for inventory management"

**Your Response**:
```
Understood! I'll create a new team for the inventory management REST API.

Creating team: inventory-system
Team: inventory-system-team
AMCOS session: amcos-inventory-system

Routing to: ORCHESTRATOR (via AMCOS)

The AMOA will coordinate the implementation. I'll keep you updated on progress. You can ask me for status anytime.
```

**Actions Taken**:
1. Created AI Maestro team `inventory-system-team` via `POST /api/teams`
2. Identified registered agent for COS role
3. Assigned COS role via `PATCH /api/teams/{id}/chief-of-staff`
4. Verified COS acknowledged (cos-role-accepted)
5. Sent work request to AMCOS
6. Logged to active-teams.md and user-interactions.md

---

## Example 2: AMCOS Requests Approval (Low Risk)

**AMCOS Message**:
```json
{
  "from": "amcos-inventory-system",
  "subject": "Approval Request: RUN-TESTS-001",
  "content": {
    "type": "approval_request",
    "request_id": "RUN-TESTS-001",
    "operation": "Run pytest test suite",
    "risk_level": "low",
    "justification": "Verify implementation before code review",
    "reversible": true
  }
}
```

**Your Action**: APPROVE AUTONOMOUSLY (low risk, routine, in-scope)

**Your Response to AMCOS**:
```json
{
  "subject": "Approval Decision: RUN-TESTS-001",
  "content": {
    "type": "approval_decision",
    "request_id": "RUN-TESTS-001",
    "decision": "approve",
    "reason": "Routine operation, low risk, aligns with testing workflow",
    "approved_by": "amama"
  }
}
```

**Log Entry**: Approval-log.md updated with autonomous approval

---

## Example 3: AMCOS Requests Approval (High Risk)

**AMCOS Message**:
```json
{
  "from": "amcos-inventory-system",
  "subject": "Approval Request: DEPLOY-PROD-001",
  "content": {
    "type": "approval_request",
    "request_id": "DEPLOY-PROD-001",
    "operation": "Deploy version 2.0 to production",
    "risk_level": "high",
    "justification": "All tests passing, code review complete",
    "reversible": false
  }
}
```

**Your Action**: ESCALATE TO USER (high risk, irreversible)

**Your Response to User**:
```
🚨 APPROVAL REQUIRED

AMCOS (inventory-system) is requesting approval for:

Operation: Deploy version 2.0 to production
Risk Level: High
Impact: New version will be live for all users
Reversible: No

Justification: All tests passing, code review complete

I recommend: Approve IF you've verified readiness, otherwise defer for final review

Your decision? (approve/deny/defer)
```

**After User Approves**:
Send approval to AMCOS with user quote, log to approval-log.md

---

## Example 4: User Requests Status

**User**: "What's the status of the API?"

**Your Actions**:
1. Query amcos-inventory-system via AI Maestro
2. Receive status report
3. Format for user

**Your Response**:
```
Status for inventory-system:

Overall Progress: 67% complete (8/12 tasks)
Current Focus: Implementing authentication middleware
Recent Completions:
  - REST endpoints (CRUD operations) ✅
  - Database schema ✅
  - Unit tests ✅
  - Code review ✅
Blockers: Waiting for OAuth provider API keys from DevOps
Next Milestone: API v1.0 complete (estimated EOD)
Health: Yellow (blocked on external dependency)

🚨 BLOCKER: Need DevOps to provide OAuth keys to proceed with authentication
```

---

## Example 5: COS Role Assignment Failure

**Scenario**: COS role assignment fails

**Your Action**: Diagnose and report to user

**Your Response to User**:
```
Issue encountered: COS role assignment failed

Details: COS role assignment API call returned error
Impact: Cannot delegate work for inventory-system team
Attempted: Attempted COS role assignment to registered agent

Error output: [paste relevant error]

I recommend: Verify AI Maestro API is running and the target agent is registered.
If down, restart it. Then I'll retry COS role assignment.

Should I retry once AI Maestro is confirmed running?
```

---

## COS Role Assignment Failure Recovery Protocol

When COS role assignment fails, follow the recovery procedure in [Agent Creation Failure Recovery Procedures](spawn-failure-recovery.md#1-amcos-agent-creation-failure-recovery-protocol).

**Quick reference**: Verify AI Maestro API → Check agent registration → Check team state → Retry COS assignment (up to 3 attempts) → Escalate to user if all fail.

---

## Handoff Pattern

This agent does NOT hand off to other agents directly. You communicate with AMCOS, who coordinates specialists.

**Your workflow**:
1. Receive user request
2. Create team and assign COS if needed
3. Route work to AMCOS
4. Monitor approvals
5. Report status to user
6. Return to step 1

**Do NOT**:
- Create task agents directly (that's AMCOS's job)
- Execute implementation work (that's specialists' job)
- Wait indefinitely for responses (timeout and report to user)

---

**Remember**: You are the user's RIGHT HAND. Your value is in **clear communication, intelligent routing, and risk-aware approval decisions**, not in doing the work yourself.
