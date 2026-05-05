# AI Maestro Message Formats for AMCOS Communication

## Table of Contents
- [1. AMCOS Approval Request Format](#1-amcos-approval-request-format)
- [2. AMAMA Response Format](#2-amama-response-format)
- [3. Autonomy Messages](#3-autonomy-messages)
- [4. Completion Notification Format](#4-completion-notification-format)

> **Note**: For comprehensive AMCOS message templates, see [ai-maestro-message-templates.md](ai-maestro-message-templates.md). This file provides a quick reference subset.

---

## 1. AMCOS Approval Request Format

This is the format AMCOS uses when sending approval requests to AMAMA. The message arrives via the `agent-messaging` skill with the following structure:

- **Sender**: `amcos-<project-name>`
- **Subject**: "AMCOS Approval Request: <operation summary>"
- **Priority**: `high` or `normal`
- **Content fields**:
  - `type`: `approval_request`
  - `request_id`: Unique request identifier (format: `amcos-req-<uuid>`)
  - `category`: Operation category (e.g., `critical-operation`, `policy-exception`, `routine-operation`, `minor-decision`)
  - `operation`: A nested structure containing:
    - `type`: Kind of operation (`deployment`, `merge`, `publish`, etc.)
    - `description`: Detailed description of what AMCOS wants to do
    - `affected_resources`: List of resources affected
    - `risk_level`: One of `low`, `medium`, `high`, or `critical`
    - `reversible`: Whether the operation can be undone (`true` or `false`)
  - `context`: A nested structure containing:
    - `triggered_by`: Which role or event initiated this request
    - `related_issues`: List of related GitHub issue numbers
    - `related_handoffs`: List of related handoff UUIDs
  - `recommendation`: AMCOS's own recommendation (`approve`, `reject`, or `ai-review`)
  - `requested_at`: ISO-8601 timestamp of when the request was made

### Field Descriptions

| Field | Description |
|-------|-------------|
| `request_id` | Unique identifier for tracking |
| `category` | Operation category (see request categories in SKILL.md) |
| `operation.type` | What kind of operation |
| `operation.risk_level` | Risk assessment |
| `operation.reversible` | Can the operation be undone |
| `context.triggered_by` | Which role or event initiated this |
| `recommendation` | AMCOS's own recommendation |

---

## 2. AMAMA Response Format

See [approval-response-workflow.md](approval-response-workflow.md) for the full response format and workflow.

---

## 3. Autonomy Messages

### Grant Message

Send an autonomy grant using the `agent-messaging` skill:
- **Recipient**: `amcos-<project-name>`
- **Subject**: "AMAMA Autonomous Mode Grant"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `autonomy_grant`
  - `operation_types`: List of operation types AMCOS can perform autonomously (e.g., `routine-operation`, `minor-decision`)
  - `expires_at`: ISO-8601 timestamp when autonomous mode ends
  - `scope_limits`: A nested structure containing:
    - `max_files_per_operation`: Maximum number of files AMCOS can modify per operation
    - `allowed_branches`: List of branch patterns AMCOS can work on (e.g., `feature/*`)
  - `notification_level`: How often AMCOS reports back (`all`, `important`, or `critical-only`)

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### Revoke Message

Send an autonomy revocation using the `agent-messaging` skill:
- **Recipient**: `amcos-<project-name>`
- **Subject**: "AMAMA Autonomous Mode Revoked"
- **Priority**: `urgent`
- **Content**: Include the following fields:
  - `type`: `autonomy_revoke`
  - `reason`: One of `User request`, `Scope exceeded`, `Security concern`, or `Timeout`
  - `effective_immediately`: `true` (revocation always takes effect immediately)
  - `revoked_at`: ISO-8601 timestamp of revocation

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

See [delegation-rules.md](delegation-rules.md) for full details on autonomy configuration.

---

## 4. Completion Notification Format

This is the format AMCOS uses when reporting completed operations. The message arrives via the `agent-messaging` skill with the following structure:

- **Sender**: `amcos-<project-name>`
- **Subject**: "AMCOS Operation Complete: <operation summary>"
- **Priority**: `normal`
- **Content fields**:
  - `type`: `operation_complete`
  - `request_id`: The original request ID (format: `amcos-req-<uuid>`) or `autonomous-<uuid>` for autonomous operations
  - `operation`: A nested structure containing:
    - `type`: Kind of operation completed (`deployment`, `merge`, `publish`, etc.)
    - `description`: What was completed
    - `result`: One of `success`, `partial`, or `failed`
    - `details`: Summary of the outcome
  - `autonomous_mode`: Whether this was performed under autonomous mode (`true` or `false`)
  - `completed_at`: ISO-8601 timestamp of completion

### Field Descriptions

| Field | Description |
|-------|-------------|
| `request_id` | Matches original request ID or `autonomous-{uuid}` for autonomous ops |
| `operation.result` | Outcome of the operation |
| `operation.details` | Summary of what happened |
| `autonomous_mode` | Whether this was done under autonomous mode |
