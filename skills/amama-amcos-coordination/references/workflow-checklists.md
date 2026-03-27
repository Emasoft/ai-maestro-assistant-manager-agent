# Workflow Checklists


## Contents

- [Checklist: Creating New Team](#checklist-creating-new-team)
- [Checklist: Assigning COS Role](#checklist-assigning-cos-role)
- [Checklist: Processing AMCOS Approval Request](#checklist-processing-amcos-approval-request)
- [Checklist: Routing User Request to AMCOS](#checklist-routing-user-request-to-amcos)
- [Checklist: Providing Status to User](#checklist-providing-status-to-user)

Use these checklists to ensure complete execution of each workflow. Check off items as you complete them.

## Checklist: Creating New Team

When user requests a new project team:

- [ ] **Parse user request** for project name, purpose, and requirements
- [ ] **Clarify ambiguities** if team scope or agent assignments are not specified
- [ ] **Verify team name available** (no existing team with that name via `GET $AIMAESTRO_API/api/teams`)
- [ ] **Request user to create team via dashboard** with recommended name, project, and description
- [ ] **Verify team created** by user via `GET $AIMAESTRO_API/api/teams`
- [ ] **Identify available registered agent** for COS role (see "Checklist: Assigning COS Role")
- [ ] **Request user to assign COS role** to the selected agent via dashboard
- [ ] **Send health check ping** to the COS agent using the `agent-messaging` skill (mandatory)
- [ ] **Verify AMCOS responding** (check inbox for pong within 30 seconds)
- [ ] **Register team** in `docs_dev/projects/project-registry.md`
- [ ] **Report to user** with team ID and AMCOS session name
- [ ] **Log session creation** in `docs_dev/sessions/active-amcos-sessions.md`

**Success Criteria**: User created AI Maestro team via dashboard, user assigned COS role via dashboard, AMCOS responds to health ping, team registered in logs.

## Checklist: Assigning COS Role

When assigning the Chief-of-Staff (COS) role to an existing registered agent:

- [ ] **Determine AMCOS session name** (format: `amcos-<project-name>`)
- [ ] **Identify available registered agent** suitable for COS role:
  ```
  GET $AIMAESTRO_API/api/agents?status=available
  ```
- [ ] **Verify agent is registered and reachable** (agent must already exist in AI Maestro)
- [ ] **Request user to assign COS role** to the agent via the dashboard
- [ ] **Send cos-role-assignment message** to the agent using the `agent-messaging` skill:
  - **Recipient**: `amcos-<project-name>`
  - **Subject**: "COS Role Assignment"
  - **Type**: `cos-role-assignment`
  - **Content**: team ID, project name, role expectations
  - **Priority**: `high`
- [ ] **Wait for cos-role-accepted response** (check inbox within 30 seconds using the `agent-messaging` skill)
- [ ] **Send health check ping** using the `agent-messaging` skill (mandatory):
  - **Recipient**: `amcos-<project-name>`
  - **Subject**: "Health Check"
  - **Type**: `ping`
  - **Priority**: `normal`
- [ ] **Verify AMCOS response** (check inbox for pong within 30 seconds using the `agent-messaging` skill)
- [ ] **Register AMCOS session** in active sessions log
- [ ] **Report AMCOS ready** to user

**Success Criteria**: User assigned COS role via dashboard, agent accepted role, responds to health ping, registered in logs.

## Checklist: Processing AMCOS Approval Request

When AMCOS sends an approval request:

- [ ] **Read approval request** from inbox using the `agent-messaging` skill
- [ ] **Parse request details**:
  - Request ID
  - Operation description
  - Risk level (if provided)
  - Justification
- [ ] **Assess risk level**:
  - Is operation destructive? (delete files, drop tables)
  - Is operation irreversible? (deploy prod, publish release)
  - Is operation within AMCOS documented scope?
  - Does operation align with user's stated goals?
- [ ] **Make decision**:
  - **If high risk OR out of scope**: Escalate to user for approval
  - **If routine and in-scope**: Approve autonomously
  - **If misaligned with goals**: Deny and explain
- [ ] **If escalating to user**:
  - [ ] Present request to user with risk assessment
  - [ ] Wait for user decision
  - [ ] Record user decision verbatim
- [ ] **Send approval decision** to AMCOS using the `agent-messaging` skill:
  - **Recipient**: `amcos-<project>`
  - **Subject**: "Approval Decision: <REQUEST-ID>"
  - **Content**: approval_decision type with request_id, decision (approve/deny), and reason
  - **Type**: `approval_decision`
  - **Priority**: `high`
- [ ] **Log approval** in `docs_dev/approvals/approval-log.md`
- [ ] **Verify AMCOS acknowledgment** (if expected)

**Success Criteria**: Approval decision made, sent to AMCOS, logged, acknowledged.

## Checklist: Routing User Request to AMCOS

When user gives a work request:

- [ ] **Parse user request** for intent (build, design, test, etc.)
- [ ] **Identify target specialist** using routing table:
  - Design/plan → ARCHITECT (via AMCOS)
  - Build/implement → ORCHESTRATOR (via AMCOS)
  - Review/test/release → INTEGRATOR (via AMCOS)
- [ ] **Identify target AMCOS** (which project?)
- [ ] **Verify AMCOS exists and is alive**
  - Check active sessions log
  - Send health ping (mandatory every time)
  - Request user to assign COS role via dashboard if no AMCOS exists for this project
- [ ] **Format work request** for AMCOS
- [ ] **Send request** to AMCOS using the `agent-messaging` skill:
  - **Recipient**: `amcos-<project>`
  - **Subject**: "User Request: <summary>"
  - **Content**: work_request type with specialist (AMOA/AMAA/AMIA), task description, and user_context
  - **Type**: `work_request`
  - **Priority**: `normal`
- [ ] **Acknowledge to user** that request routed
- [ ] **Log interaction** in `docs_dev/sessions/user-interactions.md`

**Success Criteria**: Request parsed, routed to correct AMCOS/specialist, user acknowledged.

## Checklist: Providing Status to User

When user requests status:

- [ ] **Parse status request** for scope (entire project? specific task?)
- [ ] **Identify relevant agents** to query
- [ ] **Send status query** to AMCOS using the `agent-messaging` skill:
  - **Recipient**: `amcos-<project>`
  - **Subject**: "Status Query"
  - **Content**: status_query type with scope (full/milestone/task)
  - **Type**: `status_query`
  - **Priority**: `normal`
- [ ] **Wait for responses** (30 second timeout per agent)
- [ ] **Aggregate responses** into human-readable summary
- [ ] **Format status report** for user:
  - Overall progress percentage
  - Current focus (what's being worked on now)
  - Recent completions
  - Blockers/issues
  - Next milestones
- [ ] **Present to user**
- [ ] **Handle follow-up questions**

**Success Criteria**: Status collected, aggregated, presented to user, acknowledged.
