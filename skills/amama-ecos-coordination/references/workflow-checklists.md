# Workflow Checklists


## Contents

- [Checklist: Creating New Project](#checklist-creating-new-project)
- [Checklist: Spawning ECOS](#checklist-spawning-ecos)
- [Checklist: Processing ECOS Approval Request](#checklist-processing-ecos-approval-request)
- [Checklist: Routing User Request to ECOS](#checklist-routing-user-request-to-ecos)
- [Checklist: Providing Status to User](#checklist-providing-status-to-user)

Use these checklists to ensure complete execution of each workflow. Check off items as you complete them.

## Checklist: Creating New Project

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
- [ ] **Spawn ECOS for this project** using the `ai-maestro-agents-management` skill
- [ ] **Verify ECOS responding** via health check ping
- [ ] **Register project** in `docs_dev/projects/project-registry.md`
- [ ] **Report to user** with project path and ECOS session name
- [ ] **Log session creation** in `docs_dev/sessions/active-ecos-sessions.md`

**Success Criteria**: Project directory exists, git initialized, ECOS alive and registered.

## Checklist: Spawning ECOS

When creating a new ECOS instance:

- [ ] **Determine ECOS session name** (format: `ecos-<project-name>`)
- [ ] **Identify working directory** (project root)
- [ ] **Identify plugins to load** (emasoft-chief-of-staff required)
- [ ] **Prepare agent creation** using the `ai-maestro-agents-management` skill:
  - **Agent name**: `ecos-<project-name>`
  - **Working directory**: `~/agents/ecos-<project-name>/`
  - **Task**: "Coordinate agents for <project-name> development"
  - **Plugin**: load `emasoft-chief-of-staff` (must be copied to agent's local plugins directory first)
  - **Main agent**: `ecos-chief-of-staff-main-agent`
- [ ] **Execute agent creation** using the `ai-maestro-agents-management` skill
- [ ] **Verify creation success** (exit code 0)
- [ ] **Wait 5 seconds** for ECOS initialization
- [ ] **Send health check ping** using the `agent-messaging` skill:
  - **Recipient**: `ecos-<project-name>`
  - **Subject**: "Health Check"
  - **Type**: `ping`
  - **Priority**: `normal`
- [ ] **Verify ECOS response** (check inbox for pong within 30 seconds using the `agent-messaging` skill)
- [ ] **Register ECOS session** in active sessions log
- [ ] **Report ECOS ready** to user

**Success Criteria**: ECOS session exists, responds to ping, registered in logs.

## Checklist: Processing ECOS Approval Request

When ECOS sends an approval request:

- [ ] **Read approval request** from inbox using the `agent-messaging` skill
- [ ] **Parse request details**:
  - Request ID
  - Operation description
  - Risk level (if provided)
  - Justification
- [ ] **Assess risk level**:
  - Is operation destructive? (delete files, drop tables)
  - Is operation irreversible? (deploy prod, publish release)
  - Is operation within ECOS documented scope?
  - Does operation align with user's stated goals?
- [ ] **Make decision**:
  - **If high risk OR out of scope**: Escalate to user for approval
  - **If routine and in-scope**: Approve autonomously
  - **If misaligned with goals**: Deny and explain
- [ ] **If escalating to user**:
  - [ ] Present request to user with risk assessment
  - [ ] Wait for user decision
  - [ ] Record user decision verbatim
- [ ] **Send approval decision** to ECOS using the `agent-messaging` skill:
  - **Recipient**: `ecos-<project>`
  - **Subject**: "Approval Decision: <REQUEST-ID>"
  - **Content**: approval_decision type with request_id, decision (approve/deny), and reason
  - **Type**: `approval_decision`
  - **Priority**: `high`
- [ ] **Log approval** in `docs_dev/approvals/approval-log.md`
- [ ] **Verify ECOS acknowledgment** (if expected)

**Success Criteria**: Approval decision made, sent to ECOS, logged, acknowledged.

## Checklist: Routing User Request to ECOS

When user gives a work request:

- [ ] **Parse user request** for intent (build, design, test, etc.)
- [ ] **Identify target specialist** using routing table:
  - Design/plan → ARCHITECT (via ECOS)
  - Build/implement → ORCHESTRATOR (via ECOS)
  - Review/test/release → INTEGRATOR (via ECOS)
- [ ] **Identify target ECOS** (which project?)
- [ ] **Verify ECOS exists and is alive**
  - Check active sessions log
  - Send health ping if uncertain
  - Create ECOS if not exists
- [ ] **Format work request** for ECOS
- [ ] **Send request** to ECOS using the `agent-messaging` skill:
  - **Recipient**: `ecos-<project>`
  - **Subject**: "User Request: <summary>"
  - **Content**: work_request type with specialist (EOA/EAA/EIA), task description, and user_context
  - **Type**: `work_request`
  - **Priority**: `normal`
- [ ] **Acknowledge to user** that request routed
- [ ] **Log interaction** in `docs_dev/sessions/user-interactions.md`

**Success Criteria**: Request parsed, routed to correct ECOS/specialist, user acknowledged.

## Checklist: Providing Status to User

When user requests status:

- [ ] **Parse status request** for scope (entire project? specific task?)
- [ ] **Identify relevant agents** to query
- [ ] **Send status query** to ECOS using the `agent-messaging` skill:
  - **Recipient**: `ecos-<project>`
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
