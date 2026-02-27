# AI Maestro Message Templates

Standard message formats for inter-role communication via AI Maestro.

## Message Types

### 1. Task Assignment

Send a task assignment using the `agent-messaging` skill:
- **Recipient**: The target agent session name
- **Subject**: "[TASK] <brief description>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `task_assignment`
  - `message`: Detailed instructions for the task
  - `handoff_file`: Path to the handoff file (format: `docs_dev/handoffs/handoff-<uuid>-amama-to-<role>.md`)
  - `github_issue`: The associated GitHub issue number (format: `#<number>`)
  - `deadline`: ISO-8601 timestamp, or `null` if no deadline

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 2. Status Request

Send a status request using the `agent-messaging` skill:
- **Recipient**: The target agent session name
- **Subject**: "[STATUS] Request for <project or task name>"
- **Priority**: `normal`
- **Content**: Include the following fields:
  - `type`: `status_request`
  - `message`: "Please provide status update on <task description>"
  - `fields_requested`: List of fields to include in the response (e.g., `progress_percent`, `blockers`, `eta`, `next_steps`)

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 3. Status Update

Send a status update using the `agent-messaging` skill:
- **Recipient**: The AMAMA session name (e.g., `amama-main-manager`)
- **Subject**: "[UPDATE] <task name> - <status>"
- **Priority**: `normal`
- **Content**: Include the following fields:
  - `type`: `status_update`
  - `message`: Summary of the current status
  - `progress_percent`: Numeric percentage of completion (e.g., 75)
  - `blockers`: List of current blockers (if any)
  - `completed_items`: List of items completed so far
  - `next_steps`: List of planned next steps
  - `eta`: Estimated completion time as ISO-8601 timestamp

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 4. Completion Signal

Send a completion signal using the `agent-messaging` skill:
- **Recipient**: The AMAMA session name (e.g., `amama-main-manager`)
- **Subject**: "[COMPLETE] <task name>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `completion`
  - `message`: Summary of what was delivered
  - `handoff_file`: Path to the handoff file (format: `docs_dev/handoffs/handoff-<uuid>-<role>-to-amama.md`)
  - `github_issue`: The associated GitHub issue number (format: `#<number>`)
  - `artifacts`: List of paths to deliverable artifacts
  - `verification_status`: One of `passed`, `failed`, or `partial`

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 5. Approval Request

Send an approval request using the `agent-messaging` skill:
- **Recipient**: The AMAMA session name (e.g., `amama-main-manager`)
- **Subject**: "[APPROVAL] <approval type> for <item>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `approval_request`
  - `message`: Description of what needs approval
  - `approval_type`: One of `push`, `merge`, `publish`, `security`, or `release`
  - `affected_items`: List of items affected by the operation
  - `risk_assessment`: One of `low`, `medium`, or `high`
  - `rollback_plan`: Description of how to undo the operation if needed

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 6. Approval Response

Send an approval response using the `agent-messaging` skill:
- **Recipient**: The agent session that sent the approval request
- **Subject**: "[APPROVED/REJECTED] <approval type> for <item>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `approval_response`
  - `message`: User feedback (if any)
  - `decision`: One of `approved`, `rejected`, or `needs_revision`
  - `conditions`: List of conditions that must be met (if approving with conditions)
  - `user_comment`: Optional verbatim user comment

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 7. Question / Clarification

Send a question or clarification request using the `agent-messaging` skill:
- **Recipient**: The AMAMA session name (e.g., `amama-main-manager`)
- **Subject**: "[QUESTION] <brief topic>"
- **Priority**: `normal`
- **Content**: Include the following fields:
  - `type`: `question`
  - `message`: The detailed question being asked
  - `context`: Relevant background context for the question
  - `options`: List of possible answers or choices (if applicable)
  - `blocking`: Whether work is blocked until the question is answered (`true` or `false`)

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### 8. Error / Issue Report

Send an error or issue report using the `agent-messaging` skill:
- **Recipient**: The AMAMA session name (e.g., `amama-main-manager`)
- **Subject**: "[ERROR] <error type> in <component>"
- **Priority**: `urgent`
- **Content**: Include the following fields:
  - `type`: `error_report`
  - `message`: Description of the error
  - `error_type`: One of `build_failure`, `test_failure`, `integration_issue`, or `blocker`
  - `affected_components`: List of components affected by the error
  - `attempted_solutions`: List of solutions already attempted
  - `needs_user_input`: Whether user input is required to resolve (`true` or `false`)

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

## Session Name Convention

| Role | Prefix | Session Name Pattern |
|------|--------|---------------------|
| Assistant Manager | `amama-` | `amama-{project}-session` |
| Architect | `amaa-` | `amaa-{project}-session` |
| Orchestrator | `amoa-` | `amoa-{project}-session` |
| Integrator | `amia-` | `amia-{project}-session` |

**Prefix Legend:**
- `am` = AI Maestro (product identifier)
- `ama` = Assistant Manager Agent
- `aa` = Architect Agent
- `oa` = Orchestrator Agent
- `ia` = Integrator Agent

## Priority Levels

| Priority | Use Case |
|----------|----------|
| `urgent` | Blocking issues, critical errors, security issues |
| `high` | Completion signals, approval requests, important updates |
| `normal` | Status updates, questions, routine communication |
| `low` | Non-blocking information, FYI messages |
