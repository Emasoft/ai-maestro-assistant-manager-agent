# Responding to AMCOS Approval Requests

## Use-Case TOC

- When AMCOS sends an approval request -> Section 1
- How to format the response message -> Section 2
- What evaluation criteria to use -> Section 3
- When to escalate to user -> Section 3

## Table of Contents

1. Decision Options
2. Response Format
3. Response Workflow

---

## 1. Decision Options

When AMCOS sends an approval request, AMAMA responds with one of:

| Decision | Code | Effect |
|----------|------|--------|
| **Approve** | `approve` | AMCOS proceeds with the operation |
| **Deny** | `deny` | AMCOS cancels the operation |
| **Defer** | `defer` | AMCOS must provide more information or modify and resubmit |

### When to Use Each Decision

**Approve** (`approve`): Use when:
- Operation aligns with user preferences
- Risk is acceptable
- Resources are available

**Deny** (`deny`): Use when:
- Operation violates policies
- Risk is too high
- User explicitly forbids this type of action

**Defer** (`defer`): Use when:
- Operation is acceptable but scope needs adjustment
- Additional safeguards are required
- More information is needed before deciding

---

## 2. Response Format

AMAMA sends responses using the `agent-messaging` skill:

- **Recipient**: `amcos-<project-name>`
- **Subject**: "AMAMA Approval Response: <request_id>"
- **Priority**: `high`
- **Content**: Include the following fields:
  - `type`: `approval_decision`
  - `request_id`: Must match the original request ID from AMCOS
  - `decision`: One of `approve`, `deny`, or `defer`
  - `comment`: Optional explanation for the decision
  - `conditions`: Optional list of conditions AMCOS must follow if approved
  - `responded_at`: ISO-8601 timestamp of the response

**Verify**: confirm message delivery via the `agent-messaging` skill's sent messages feature.

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `request_id` | Yes | Must match the original request ID from AMCOS |
| `decision` | Yes | One of: `approve`, `deny`, `defer` |
| `comment` | No | Explanation for the decision |
| `conditions` | No | Array of conditions AMCOS must follow if approved |
| `responded_at` | Yes | ISO-8601 timestamp of the response |

---

## 3. Response Workflow

1. **Receive AMCOS approval request**
   - Parse the incoming AI Maestro message
   - Extract request_id, category, and operation details

2. **Evaluate against criteria:**
   - User preferences and policies
   - Current project state
   - Risk assessment
   - Resource constraints

3. **If uncertain, present to user with recommendation**
   - Provide summary of the request
   - Give your recommendation
   - Wait for user decision

4. **Record decision in state tracking**
   - Update AMAMA state file
   - Log for audit trail

5. **Send response to AMCOS**
   - Use the response format above
   - Include conditions if applicable

6. **Log decision for audit trail**
   - Record timestamp, decision, and reasoning
   - Track who made the decision (AMAMA or user)
