# Workflow Checklists

## Contents

- [Checklist: Creating New Team](#checklist-creating-new-team)
- [Checklist: Granting the COS Mandate](#checklist-granting-the-cos-mandate)
- [Checklist: Processing AMCOS Approval Request](#checklist-processing-amcos-approval-request)
- [Checklist: Routing User Request to AMCOS](#checklist-routing-user-request-to-amcos)
- [Checklist: Providing Status to User](#checklist-providing-status-to-user)

Use these checklists to ensure complete execution of each workflow. Check off items as you complete them.

## Checklist: Creating New Team

When a new project team is needed (you create it yourself — R29, no user approval):

- [ ] **Parse the request** for project name, purpose, and requirements
- [ ] **Clarify ambiguities** if team scope or agent assignments are not specified
- [ ] **Verify team name available** (no existing team with that name via `aimaestro-teams.sh list`)
- [ ] **Create the team yourself** via `aimaestro-teams.sh create --name N --type closed [...]` (R29) — the server auto-creates the COS
- [ ] **Verify team created** via `aimaestro-teams.sh list`, and `chiefOfStaff` set via `aimaestro-teams.sh show <team-id>`
- [ ] **Wake the COS** via `aimaestro-agent.sh wake <cos-id>` and grant its mandate (see "Checklist: Granting the COS Mandate")
- [ ] **Send health check ping** to the COS using the `agent-messaging` skill (mandatory)
- [ ] **Verify AMCOS responding** (check inbox for pong within 30 seconds)
- [ ] **Confirm the 5 base members** are being completed (team FROZEN until 5/5, R31)
- [ ] **Register team** in `docs_dev/projects/project-registry.md`
- [ ] **Report to user** with team ID and AMCOS session name
- [ ] **Log session creation** in `docs_dev/sessions/active-amcos-sessions.md`

**Success Criteria**: You created the team via the teams CLI (R29), the server auto-created the COS, you granted its mandate (R30), AMCOS responds to health ping, the 5 base members are completing (R31), team registered in logs.

## Checklist: Granting the COS Mandate

When granting the auto-created COS its team-creation mandate (R30):

- [ ] **Determine the COS session name** (the agent the server set as `chiefOfStaff`)
- [ ] **Verify the COS is set** via `aimaestro-teams.sh show <team-id>` (`chiefOfStaff` field)
- [ ] **Wake the COS** via `aimaestro-agent.sh wake <cos-id>`
- [ ] **Send cos-mandate message** to the COS using the `agent-messaging` skill:
  - **Recipient**: `<cos-session-name>`
  - **Subject**: "COS Mandate — Team Creation"
  - **Type**: `cos-mandate`
  - **Content**: team ID, project name, `mandate: team-creation` (authorizes the 5-member base + project MEMBERs, R30)
  - **Priority**: `high`
- [ ] **Wait for cos-mandate-accepted response** (check inbox within 30 seconds using the `agent-messaging` skill)
- [ ] **Send health check ping** using the `agent-messaging` skill (mandatory):
  - **Recipient**: `<cos-session-name>`
  - **Subject**: "Health Check"
  - **Type**: `ping`
  - **Priority**: `normal`
- [ ] **Verify AMCOS response** (check inbox for pong within 30 seconds using the `agent-messaging` skill)
- [ ] **Register AMCOS session** in active sessions log
- [ ] **Report AMCOS ready** to user (team unfreezes once the 5 base members exist, R31)

**Success Criteria**: COS woken and mandated (R30), COS accepted the mandate, responds to health ping, completing the 5 base members (R31), registered in logs.

## Checklist: Processing AMCOS Approval Request

When AMCOS sends an approval request:

- [ ] **Read approval request** from inbox using the `agent-messaging` skill
- [ ] **Parse request details**:
  - Request ID
  - Operation description
  - Risk level (if provided)
  - Justification
- [ ] **Assess risk level**:
  - Is operation destructive? (file deletion, table drops)
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
  - If no team/COS exists for this project, create the team yourself via `aimaestro-teams.sh create` (R29) — the server auto-creates the COS
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
