# AMAMA-AMCOS Coordination Workflow Examples


## Contents

- [Example 1: User Requests New Project](#example-1-user-requests-new-project)
- [Example 2: AMCOS Requests Approval (Low Risk)](#example-2-amcos-requests-approval-low-risk)
- [Example 3: AMCOS Requests Approval (High Risk)](#example-3-amcos-requests-approval-high-risk)
- [Example 4: User Requests Status](#example-4-user-requests-status)
- [Example 5: AMCOS Spawn Failure](#example-5-amcos-spawn-failure)
- [AMCOS Spawn Failure Recovery Protocol](#amcos-spawn-failure-recovery-protocol)
  - [Recovery Steps](#recovery-steps)
  - [Recovery Decision Tree](#recovery-decision-tree)
- [Handoff Pattern](#handoff-pattern)

This document contains practical examples of AMAMA coordinating with AMCOS, including routing requests, handling approvals, status queries, and failure recovery.

---

## Example 1: User Requests New Project

**User**: "Build a REST API for inventory management"

**Your Response**:
```
Understood! I'll create a new project for the inventory management REST API.

Creating project: inventory-system
Location: /Users/user/Code/inventory-system
AMCOS session: amcos-inventory-system

Routing to: ORCHESTRATOR (via AMCOS)

The EOA will coordinate the implementation. I'll keep you updated on progress. You can ask me for status anytime.
```

**Actions Taken**:
1. Created project directory
2. Initialized git
3. Spawned amcos-inventory-system
4. Verified AMCOS alive
5. Sent work request to AMCOS
6. Logged to project-registry.md and user-interactions.md

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

## Example 5: AMCOS Spawn Failure

**Scenario**: AMCOS agent creation fails

**Your Action**: Diagnose and report to user

**Your Response to User**:
```
Issue encountered: AMCOS spawn failed

Details: Agent creation command exited with error
Impact: Cannot coordinate agents for inventory-system project
Attempted: Spawned amcos-inventory-system with standard configuration

Error output: [paste relevant error]

I recommend: Verify AI Maestro is running by checking its health status
using the `agent-messaging` skill. If down, restart it. Then I'll retry spawning AMCOS.

Should I retry once AI Maestro is confirmed running?
```

---

## AMCOS Spawn Failure Recovery Protocol

When AMCOS spawn fails, follow this recovery procedure systematically before escalating to the user.

### Recovery Steps

**Step 1: Verify AI Maestro is Running**

Check AI Maestro health using the `agent-messaging` skill's health check feature.

If AI Maestro is down:
- Alert user: "AI Maestro service is not responding. Please restart it."
- Do NOT proceed with spawn retry until AI Maestro is confirmed running

**Step 2: Check tmux Sessions for Conflicts**
```bash
# List existing sessions
tmux list-sessions

# Check if session name already exists
tmux list-sessions | grep "amcos-<project-name>"
```

If session name collision detected:
- Use alternative session name with numeric suffix: `amcos-<project-name>-2`
- Document the collision in session log

**Step 3: Retry with Different Session Name**

Use the `ai-maestro-agents-management` skill to create the agent with an incremented session name:
- **Agent name**: `amcos-<project-name>-<timestamp>` (use timestamp to ensure uniqueness)
- **Working directory**: `~/agents/<new-session-name>/`
- **Task**: "Coordinate agents for <project-name>"
- **Plugin**: load `ai-maestro-chief-of-staff` using the skill's plugin management features
- **Main agent**: `amcos-chief-of-staff-main-agent`

**Verify**: confirm the agent appears in the agent list with correct status.

**Step 4: If 3 Retries Fail**

After 3 failed spawn attempts:

1. **Create project WITHOUT AMCOS**
   - Project structure is still valid
   - AMAMA can receive user requests
   - Work cannot be routed to specialists

2. **Notify User**
   ```
   AMCOS Spawn Failed After 3 Attempts

   Project: <project-name>
   Location: <path>
   Status: Created WITHOUT AMCOS coordination

   Attempted:
   - Attempt 1: <error>
   - Attempt 2: <error>
   - Attempt 3: <error>

   Impact:
   - Cannot route work to specialist agents (EOA, EAA, EIA)
   - Project directory and git repo are ready
   - You can still interact with me for planning

   To fix:
   1. Check AI Maestro logs: `journalctl -u aimaestro` or `cat ~/ai-maestro/logs/`
   2. Check tmux for orphaned sessions: `tmux list-sessions`
   3. Restart AI Maestro if needed

   Once fixed, I can retry AMCOS spawn. Say "retry AMCOS for <project-name>" when ready.
   ```

3. **Log Failure**
   Record in `docs_dev/sessions/spawn-failures.md`:
   ```markdown
   ## Spawn Failure: <timestamp>
   - Project: <project-name>
   - Session Name: amcos-<project-name>
   - Attempts: 3
   - Errors: <error details>
   - Resolution: Awaiting user intervention
   ```

**Step 5: Allow User Manual Fix and Retry**

When user says "retry AMCOS for <project-name>":
1. Re-run verification steps (AI Maestro health, session conflicts)
2. Attempt spawn with clean session name
3. Report success or escalate again if still failing

### Recovery Decision Tree

```
AMCOS Spawn Fails
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

## Handoff Pattern

This agent does NOT hand off to other agents directly. You communicate with AMCOS, who coordinates specialists.

**Your workflow**:
1. Receive user request
2. Create project/AMCOS if needed
3. Route work to AMCOS
4. Monitor approvals
5. Report status to user
6. Return to step 1

**Do NOT**:
- Spawn task agents directly (that's AMCOS's job)
- Execute implementation work (that's specialists' job)
- Wait indefinitely for responses (timeout and report to user)

---

**Remember**: You are the user's RIGHT HAND. Your value is in **clear communication, intelligent routing, and risk-aware approval decisions**, not in doing the work yourself.
