# AMAMA-AMCOS Coordination Workflow Examples


## Contents

- [Example 1: User Requests New Project](#example-1-user-requests-new-project)
- [Example 2: AMCOS Requests Approval (Low Risk)](#example-2-amcos-requests-approval-low-risk)
- [Example 3: AMCOS Requests Approval (High Risk)](#example-3-amcos-requests-approval-high-risk)
- [Example 4: User Requests Status](#example-4-user-requests-status)
- [Example 5: Team + COS Creation Failure](#example-5-team--cos-creation-failure)
- [Team + COS Creation Failure Recovery Protocol](#team--cos-creation-failure-recovery-protocol)
- [Handoff Pattern](#handoff-pattern)

This document contains practical examples of AMAMA coordinating with AMCOS, including routing requests, handling approvals, status queries, and failure recovery.

---

## Example 1: User Requests New Project

**User**: "Build a REST API for inventory management"

**Your Response**:
```
Understood! I'll set up the inventory management REST API work.

I'm creating team: inventory-system (type: closed) — the server will auto-create its COS (R29).
I'll then wake the COS, grant its mandate (R30), and route the work to it.
```

**Actions Taken**:
1. Created the team yourself: `aimaestro-teams.sh create --name inventory-system --type closed` (R29)
2. Verified the server auto-created the COS (`aimaestro-teams.sh show` shows `chiefOfStaff` set)
3. Woke the COS and granted its team-creation mandate (R30); verified it acknowledged (cos-mandate-accepted)
4. Confirmed the COS is completing the 5 base members (team FROZEN until 5/5, R31)
5. Sent work request to AMCOS
6. Logged to active-teams.md and user-interactions.md

---

## Example 2: AMCOS Requests Approval (Low Risk)

**AMCOS Message**:
```json
{
  "from": "amcos-inventory-coordinator",
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
  "from": "amcos-inventory-coordinator",
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
1. Query amcos-inventory-coordinator via AI Maestro
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

## Example 5: Team + COS Creation Failure

**Scenario**: `aimaestro-teams.sh create` fails (no COS auto-created)

**Your Action**: Diagnose; recreate the team yourself (R29). Escalate only a server-health issue to the user.

**Your Response to User**:
```
Issue encountered: team + COS creation failed

Details: `aimaestro-teams.sh create` returned an error — no COS was auto-created
Impact: Cannot delegate work for inventory-system team (team FROZEN until COS + 5 base members, R31)
Attempted: Creating the team myself (R29), then deleting + re-creating it on failure

Error output: [paste relevant error]

I re-created the team 3× (R29). If the server is reachable, the COS auto-creates on success; this looks like a
server-health issue (the one thing only you can fix). Verify AI Maestro is running and I will re-create the team.

Would you like me to run diagnostic checks on the AI Maestro health status?
```

---

## Team + COS Creation Failure Recovery Protocol

When team + COS creation fails, follow the recovery procedure in [Team + COS Creation Failure Recovery Procedures](spawn-failure-recovery.md#1-team--cos-creation-failure-recovery-protocol).

**Quick reference**: Verify AI Maestro API → register any pre-required agent → re-create the team yourself (R29) → check the COS was auto-created → delete + recreate if missing → escalate only a server-health issue to the user (R32: never use a sudo/password path).

---

## Handoff Pattern

This agent does NOT hand off to other agents directly. You communicate with AMCOS, who coordinates specialists.

**Your workflow**:
1. Receive user request
2. Create the team yourself if needed (R29) — the server auto-creates the COS; wake it and grant its mandate (R30)
3. Route work to AMCOS once the team + COS + 5 base members exist (team unfreezes at 5/5, R31)
4. Monitor approvals
5. Report status to user
6. Return to step 1

**Do NOT**:
- Create task agents directly (that's AMCOS's job)
- Execute implementation work (that's specialists' job)
- Wait indefinitely for responses (timeout and report to user)

---

**Remember**: You are the user's RIGHT HAND. Your value is in **clear communication, intelligent routing, and risk-aware approval decisions**, not in doing the work yourself.
