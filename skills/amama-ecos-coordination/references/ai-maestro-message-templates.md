# AI Maestro Message Templates for EAMA

**Reference for**: `eama-ecos-coordination` skill

This document provides all message templates and formats for AI Maestro inter-agent communication between EAMA and other agents (ECOS, EAA, EOA, EIA). Use the `agent-messaging` skill to send and receive all messages described here.

---

## Contents

- [1. Receiving Messages](#1-receiving-messages)
  - [1.1 Receiving approval requests from ECOS](#11-receiving-approval-requests-from-ecos)
  - [1.2 Receiving status reports from ECOS](#12-receiving-status-reports-from-ecos)
  - [1.3 Receiving health check responses (pong)](#13-receiving-health-check-responses-pong)
- [2. Sending Approval-Related Messages](#2-sending-approval-related-messages)
  - [2.1 Sending approval decisions to ECOS (approve/deny/defer)](#21-sending-approval-decisions-to-ecos-approvedenydefer)
  - [2.2 Notifying ECOS of user decisions after escalation](#22-notifying-ecos-of-user-decisions-after-escalation)
- [3. Requesting Information from ECOS](#3-requesting-information-from-ecos)
  - [3.1 Requesting status from ECOS](#31-requesting-status-from-ecos)
  - [3.2 Sending health check pings to verify ECOS is alive](#32-sending-health-check-pings-to-verify-ecos-is-alive)
- [4. Delegating Work to ECOS](#4-delegating-work-to-ecos)
  - [4.1 Routing user work requests to ECOS for specialist delegation](#41-routing-user-work-requests-to-ecos-for-specialist-delegation)
  - [4.2 Routing design work to EAA via ECOS](#42-routing-design-work-to-eaa-via-ecos)
  - [4.3 Routing implementation work to EOA via ECOS](#43-routing-implementation-work-to-eoa-via-ecos)
  - [4.4 Routing review/integration work to EIA via ECOS](#44-routing-reviewintegration-work-to-eia-via-ecos)
- [5. Standard AI Maestro API Patterns](#5-standard-ai-maestro-api-patterns)
  - [5.1 Base API format and authentication](#51-base-api-format-and-authentication)
  - [5.2 Message content structure requirements](#52-message-content-structure-requirements)
  - [5.3 Priority levels and when to use them](#53-priority-levels-and-when-to-use-them)

---

## 1. Receiving Messages

### 1.1 Receiving approval requests from ECOS

**Use this when**: ECOS requests permission for a critical operation

**Incoming message format** (what you receive from ECOS):

The message will arrive with the following structure:
- **Sender**: `ecos-<project-name>`
- **Subject**: "Approval Request: <REQUEST-ID>"
- **Priority**: `high`
- **Content fields**:
  - `type`: `approval_request`
  - `request_id`: A unique identifier for this request
  - `operation`: Description of the operation ECOS wants to perform
  - `risk_level`: One of `low`, `medium`, or `high`
  - `justification`: Why ECOS needs this approval
  - `impact`: What will happen if the operation proceeds
  - `reversible`: Whether the operation can be undone (`true` or `false`)

**How to read it**:
Check your inbox using the `agent-messaging` skill. Filter for messages with content type `approval_request`.

**Response actions**:
- Assess risk level
- Make approval decision (approve/deny/defer)
- See section 2.1 for sending approval decision back to ECOS

---

### 1.2 Receiving status reports from ECOS

**Use this when**: You requested status and ECOS responds

**Incoming message format** (what you receive):

The message will arrive with the following structure:
- **Sender**: `ecos-<project-name>`
- **Subject**: "Status Report"
- **Priority**: `normal`
- **Content fields**:
  - `type`: `status_report`
  - `overall_progress`: A percentage string (e.g., "67%")
  - `active_tasks`: A list of tasks, each with `specialist` (EOA/EAA/EIA), `task` (description), and `status` (in-progress/completed/blocked)
  - `blockers`: A list of blockers, each with `description` and `assigned_to`
  - `next_milestone`: Description of the next milestone
  - `health`: One of `green`, `yellow`, or `red`

**How to read it**:
Check your inbox using the `agent-messaging` skill. Filter for messages with content type `status_report`.

**Response actions**:
- Parse status information
- Format for user presentation
- Present to user with clear progress indicators

---

### 1.3 Receiving health check responses (pong)

**Use this when**: You sent a health check ping and ECOS responds

**Expected response format**:

The response will arrive with the following structure:
- **Sender**: `ecos-<project-name>`
- **Subject**: "Re: Health Check"
- **Content fields**:
  - `type`: `pong`
  - `status`: `alive` (confirms ECOS is running)
  - `uptime`: Number of seconds since ECOS was spawned
  - `active_specialists`: List of currently active specialist roles (e.g., "EOA", "EIA")

**How to read it**:
Check your inbox using the `agent-messaging` skill. Filter for messages with content type `pong`.

**Response actions**:
- Verify "status": "alive"
- Update session health status in logs
- If no response within 30 seconds, retry once, then report to user

---

## 2. Sending Approval-Related Messages

### 2.1 Sending approval decisions to ECOS (approve/deny/defer)

**Use this when**: Responding to ECOS approval request

Send an approval decision to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "Approval Decision: <REQUEST-ID>"
- **Content**: Must include the fields below
- **Type**: `approval_decision`
- **Priority**: `high`

**Required content fields**:
- `request_id`: Same ID from the incoming request
- `decision`: `approve`, `deny`, or `defer`
- `reason`: Explanation of the decision
- `conditions`: Any conditions for approval (if applicable)
- `approved_by`: `eama` (autonomous) or `user` (escalated)
- `user_quote`: Exact user statement (only when user approved/denied)

**Verify**: confirm message delivery via the skill's sent messages feature.

**Decision values**:
- `approve`: Operation authorized, proceed
- `deny`: Operation rejected, do not proceed
- `defer`: Need more information, request clarification

**Example (autonomous approval)**: Send an approval decision using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "Approval Decision: RUN-TESTS-001"
- **Content**: approval_decision type, request_id "RUN-TESTS-001", decision "approve", reason "Routine operation, low risk, aligns with testing workflow", approved_by "eama"
- **Priority**: `high`

**Example (user-escalated denial)**: Send an approval decision using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "Approval Decision: DELETE-DATA-002"
- **Content**: approval_decision type, request_id "DELETE-DATA-002", decision "deny", reason "User denied: operation is destructive and irreversible", approved_by "user", user_quote "No, do not delete. Archive instead."
- **Priority**: `high`

---

### 2.2 Notifying ECOS of user decisions after escalation

**Use this when**: You escalated a request to the user and got their decision

Send a user decision notification to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "User Decision: <REQUEST-ID>"
- **Content**: Must include the fields below
- **Type**: `user_decision`
- **Priority**: `urgent`

**Required content fields**:
- `request_id`: The request being decided upon
- `decision`: `approve` or `deny`
- `user_statement`: Exact quote from the user
- `timestamp`: ISO-8601 timestamp of the user's decision
- `context`: Any additional context from the user

**Verify**: confirm message delivery via the skill's sent messages feature.

**Example**: Send a user decision using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "User Decision: DEPLOY-PROD-001"
- **Content**: user_decision type, request_id "DEPLOY-PROD-001", decision "approve", user_statement "Yes, deploy to production", timestamp "2026-02-05T14:30:00Z", context "User verified all tests passing and code review complete"
- **Priority**: `urgent`

---

## 3. Requesting Information from ECOS

### 3.1 Requesting status from ECOS

**Use this when**: User asks for project status

Send a status query to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "Status Query"
- **Content**: Must include the fields below
- **Type**: `status_query`
- **Priority**: `normal`

**Required content fields**:
- `scope`: `full`, `milestone`, or `task`
- `details`: What the user asked for
- `format`: `summary` or `detailed`
- `timeout`: Response timeout in seconds (default: 30)

**Verify**: confirm message delivery via the skill's sent messages feature.

**Example**: Send a status query using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "Status Query"
- **Content**: status_query type, scope "full", details "User asked: What is the status of the API implementation?", format "summary", timeout 30
- **Priority**: `normal`

**Expected response**: See section 1.2 (Receiving status reports from ECOS)

---

### 3.2 Sending health check pings to verify ECOS is alive

**Use this when**: Verifying ECOS is responsive (after spawn, periodically, before delegating work)

Send a health check ping using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "Health Check"
- **Content**: ping type, requesting reply, with timeout
- **Type**: `ping`
- **Priority**: `normal`

**Required content fields**:
- `message`: "Verify ECOS alive"
- `expect_reply`: true
- `timeout`: 10 (seconds)

**Verify**: check inbox for a `pong` response within the timeout period using the `agent-messaging` skill.

**Example**: Send a health check using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "Health Check"
- **Content**: ping type, message "Verify ECOS alive", expect_reply true, timeout 10
- **Priority**: `normal`

**Expected response**: See section 1.3 (Receiving health check responses)

---

## 4. Delegating Work to ECOS

### 4.1 Routing user work requests to ECOS for specialist delegation

**Use this when**: User gives a work request that should be handled by a specialist (EOA, EAA, EIA) via ECOS

Send a work request to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "User Request: <brief summary>"
- **Content**: Must include the fields below
- **Type**: `work_request`
- **Priority**: `normal` (or `high` for urgent requests)

**Required content fields**:
- `specialist`: `EOA`, `EAA`, or `EIA` (which specialist should handle the work)
- `task`: Detailed task description
- `user_context`: Relevant background information
- `priority`: `high`, `normal`, or `low`
- `deadline`: If specified by the user
- `success_criteria`: What the user expects as the outcome

**Verify**: confirm message delivery via the skill's sent messages feature.

**Example**: Send a work request using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "User Request: Implement REST API"
- **Content**: work_request type, specialist "EOA", task "Build a REST API for inventory management with CRUD operations", user_context "User wants full inventory tracking system with authentication", priority "high", success_criteria "REST API with all CRUD endpoints, authentication, tests passing"
- **Priority**: `normal`

---

### 4.2 Routing design work to EAA via ECOS

**Use this when**: User requests architecture/design work

**Specialist routing**: Set specialist to `EAA` (Architect)

Send a design work request to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "User Request: <design task summary>"
- **Content**: work_request type with specialist "EAA", task description, user_context, priority, success_criteria
- **Type**: `work_request`
- **Priority**: `normal`

**Example**: Send a design work request using the `agent-messaging` skill:
- **Recipient**: `ecos-data-pipeline`
- **Subject**: "User Request: Design data pipeline architecture"
- **Content**: work_request type, specialist "EAA", task "Design architecture for real-time data pipeline processing 1M events/day", user_context "Need to process IoT sensor data from 10k devices, store in time-series DB, expose via API", priority "high", success_criteria "Architecture document with component diagrams, data flow, scalability plan"
- **Priority**: `normal`

---

### 4.3 Routing implementation work to EOA via ECOS

**Use this when**: User requests building/implementing features

**Specialist routing**: Set specialist to `EOA` (Orchestrator)

Send an implementation work request to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "User Request: <implementation task summary>"
- **Content**: work_request type with specialist "EOA", task description, user_context, priority, success_criteria
- **Type**: `work_request`
- **Priority**: `normal` (or `high` if urgent)

**Example**: Send an implementation work request using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "User Request: Build REST API"
- **Content**: work_request type, specialist "EOA", task "Implement REST API with CRUD operations for inventory items", user_context "Database schema already designed. Need endpoints for: create item, update item, delete item, list items, search items.", priority "high", success_criteria "All endpoints working, tests passing, documented with OpenAPI spec"
- **Priority**: `normal`

---

### 4.4 Routing review/integration work to EIA via ECOS

**Use this when**: User requests code review, testing, merging, or release

**Specialist routing**: Set specialist to `EIA` (Integrator)

Send a review/integration work request to ECOS using the `agent-messaging` skill:
- **Recipient**: `ecos-<project-name>`
- **Subject**: "User Request: <review/integration task summary>"
- **Content**: work_request type with specialist "EIA", task description, user_context, priority, success_criteria
- **Type**: `work_request`
- **Priority**: `normal`

**Example (code review)**: Send a review work request using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "User Request: Review API implementation"
- **Content**: work_request type, specialist "EIA", task "Review REST API implementation for code quality, security, performance", user_context "EOA completed implementation. User wants thorough review before merging to main.", priority "high", success_criteria "Code review complete, all issues addressed, PR approved and merged"
- **Priority**: `normal`

**Example (release)**: Send a release work request using the `agent-messaging` skill:
- **Recipient**: `ecos-inventory-system`
- **Subject**: "User Request: Release version 2.0"
- **Content**: work_request type, specialist "EIA", task "Create release 2.0 with all new features, update changelog, tag release", user_context "All features complete, tests passing. User ready to release.", priority "normal", success_criteria "Release 2.0 tagged, changelog updated, release notes published"
- **Priority**: `normal`

---

## 5. Standard AI Maestro Messaging Patterns

### 5.1 How to send and receive messages

Use the `agent-messaging` skill for all messaging operations. The skill handles all connection details, authentication, and API formatting automatically.

**No manual API configuration required** - the `agent-messaging` skill manages connection details internally.

---

### 5.2 Message content structure requirements

**CRITICAL**: The `content` field **MUST be an object**, NOT a string!

**CORRECT**: The `content` field must be structured with named fields:
- `type`: The message type (e.g., `work_request`)
- `message`: The human-readable message text
- Additional fields specific to the message type

**WRONG** (will fail): Passing `content` as a plain string instead of a structured object with named fields. Always include at minimum a `type` field inside `content`.

**Standard content fields**:
- `type`: Message type (required: `approval_request`, `approval_decision`, `status_query`, `status_report`, `work_request`, `ping`, `pong`, `user_decision`)
- `message`: Human-readable message (optional but recommended)
- Additional fields specific to message type (see sections above)

---

### 5.3 Priority levels and when to use them

| Priority | When to Use |
|----------|-------------|
| `urgent` | User decisions on high-risk operations, critical blockers |
| `high` | Approval requests, approval decisions, time-sensitive work |
| `normal` | Routine work requests, status queries, health checks |
| `low` | Informational messages, background tasks |

**Examples**:
- **urgent**: User approved production deployment (needs immediate action)
- **high**: ECOS requests approval for destructive operation (needs quick decision)
- **normal**: User asks for status update (no urgency)
- **low**: Logging operational metrics (no action required)

**Default**: Use `"normal"` unless there's a clear reason for higher priority.

---

## Quick Reference Table

| Use Case | Message Type | Priority | Section |
|----------|--------------|----------|---------|
| Receive approval request | `approval_request` | high | 1.1 |
| Send approval decision | `approval_decision` | high | 2.1 |
| Receive status report | `status_report` | normal | 1.2 |
| Request status | `status_query` | normal | 3.1 |
| Health check ping | `ping` | normal | 3.2 |
| Health check response | `pong` | normal | 1.3 |
| User decision notification | `user_decision` | urgent | 2.2 |
| Route work to specialist | `work_request` | normal/high | 4.1-4.4 |

---

**See also**:
- [eama-ecos-coordination/SKILL.md](../SKILL.md) - Main coordination workflow
- [eama-approval-workflows/SKILL.md](../../eama-approval-workflows/SKILL.md) - Approval decision criteria
- [eama-role-routing/SKILL.md](../../eama-role-routing/SKILL.md) - Specialist routing logic
