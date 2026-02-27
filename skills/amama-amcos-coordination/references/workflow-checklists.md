# Workflow Checklists


## Contents

- [Checklist: Creating New Project](#checklist-creating-new-project)
- [Checklist: Creating AMCOS Agent](#checklist-creating-amcos-agent)
- [Checklist: Processing AMCOS Approval Request](#checklist-processing-amcos-approval-request)
- [Checklist: Routing User Request to AMCOS](#checklist-routing-user-request-to-amcos)
- [Checklist: Providing Status to User](#checklist-providing-status-to-user)

Use these checklists to ensure complete execution of each workflow. Check off items as you complete them.

## Checklist: Creating New Project and Team

When user requests a new project:

- [ ] **Parse user request** for project name, purpose, and requirements
- [ ] **Clarify ambiguities** if location/structure not specified
- [ ] **Verify project name available** (directory doesn't exist)
- [ ] **Create project directory** at agreed location
- [ ] **Initialize git repository**
  ```bash
  cd /path/to/new-project
  git init
  git config user.name "Emasoft"
  git config user.email "713559+Emasoft@users.noreply.github.com"
  ```
- [ ] **Create initial structure**
  - README.md with project description
  - .gitignore appropriate for project type
  - docs_dev/, scripts_dev/ directories
- [ ] **Commit initial structure**
  ```bash
  git add -A
  git commit -m "Initial project structure"
  ```
- [ ] **Create AI Maestro team** for this project using the `team-governance` skill
- [ ] **Create AMCOS agent for this project** using the `ai-maestro-agents-management` skill
- [ ] **Assign COS role** to the AMCOS agent via the `team-governance` skill
- [ ] **Verify AMCOS responding** via health check ping
- [ ] **Register project** in `docs_dev/projects/project-registry.md`
- [ ] **Report to user** with project path and AMCOS session name
- [ ] **Log session creation** in `docs_dev/sessions/active-amcos-sessions.md`

**Success Criteria**: Project directory exists, git initialized, AMCOS alive and registered.

## Checklist: Creating AMCOS Agent

When creating a new AMCOS agent:

- [ ] **Determine AMCOS session name** (format: `amcos-<project-name>`)
- [ ] **Identify working directory** (project root)
- [ ] **Identify plugins to load** (ai-maestro-chief-of-staff required)
- [ ] **Prepare agent creation** using the `ai-maestro-agents-management` skill:
  - **Agent name**: `amcos-<project-name>`
  - **Working directory**: `~/agents/amcos-<project-name>/`
  - **Task**: "Coordinate agents for <project-name> development"
  - **Plugin**: load `ai-maestro-chief-of-staff` (must be copied to agent's local plugins directory first)
  - **Main agent**: `amcos-chief-of-staff-main-agent`
- [ ] **Execute agent creation** using the `ai-maestro-agents-management` skill
- [ ] **Assign COS role** to the new agent via `team-governance` skill
- [ ] **Verify creation success** (exit code 0)
- [ ] **Wait 5 seconds** for AMCOS initialization
- [ ] **Send health check ping** using the `agent-messaging` skill:
  - **Recipient**: `amcos-<project-name>`
  - **Subject**: "Health Check"
  - **Type**: `ping`
  - **Priority**: `normal`
- [ ] **Verify AMCOS response** (check inbox for pong within 30 seconds using the `agent-messaging` skill)
- [ ] **Register AMCOS session** in active sessions log
- [ ] **Report AMCOS ready** to user

**Success Criteria**: AMCOS agent created, COS role assigned, responds to ping, registered in logs.

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
  - Send health ping if uncertain
  - Create AMCOS agent if not exists
- [ ] **Format work request** for AMCOS
- [ ] **Send request** to AMCOS using the `agent-messaging` skill:
  - **Recipient**: `amcos-<project>`
  - **Subject**: "User Request: <summary>"
  - **Content**: work_request type with specialist (EOA/EAA/EIA), task description, and user_context
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
