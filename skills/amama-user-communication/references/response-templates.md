# Response Templates

This document provides standardized response templates for the AMAMA Assistant Manager when communicating with users.

## Table of Contents

1. [Work Request Acknowledgment](#work-request-acknowledgment)
2. [Status Updates](#status-updates)
3. [Approval Requests](#approval-requests)
4. [Completion Reports](#completion-reports)
5. [Error Notifications](#error-notifications)

---

## Work Request Acknowledgment

Use this template when the user requests work to be done.

### Template

```
Understood! I'll <action summary>.

Creating project: <project-name>
Location: <full-path>
AMCOS session: amcos-<project-name>-coordinator

Routing to: <SPECIALIST> (via AMCOS)

I'll keep you updated on progress. You can ask me for status anytime.
```

### When to Use

- User submits a new work request
- You're creating a project and assigning the chief-of-staff role to another agent
- You're delegating to a specialist agent

### Guidelines

- **Be specific** about the action summary (e.g., "set up the inventory management system")
- **Always include** the full project path
- **State the AMCOS session name** explicitly
- **Name the specialist** you're routing to
- **Offer proactive updates** to set expectations

---

## Status Updates

Use this template when the user asks for project status or you're providing proactive updates.

### Template

```
Status for <project-name>:

Overall Progress: <percentage>% complete
Current Focus: <what's being worked on>
Recent Completions: <list>
Blockers: <list or "None">
Next Milestone: <milestone name>
Health: <Green/Yellow/Red>

<Any urgent issues flagged with 🚨>
```

### When to Use

- User explicitly asks for status
- You're providing periodic proactive updates
- Health status changes (e.g., Green → Yellow)
- Significant milestone reached

### Guidelines

- **Use percentages** for overall progress (e.g., 45%)
- **Be specific** about current focus (e.g., "Implementing user authentication module")
- **List recent completions** as bullet points if multiple items
- **Always state blockers** explicitly, even if "None"
- **Use health colors consistently**:
  - **Green**: On track, no issues
  - **Yellow**: Minor delays or risks identified
  - **Red**: Critical blocker or off-track
- **Use 🚨** for urgent issues requiring attention

---

## Approval Requests

Use this template when an AMCOS escalates a user approval request to you.

### Template

```
🚨 APPROVAL REQUIRED

AMCOS (<project-name>) is requesting approval for:

Operation: <operation description>
Risk Level: <High/Medium/Low>
Impact: <what will happen>
Reversible: <Yes/No>

I recommend: <approve/deny> because <reasoning>

Your decision? (approve/deny)
```

### When to Use

- AMCOS sends a message with type "user_approval"
- Operation requires user permission per your risk assessment
- Destructive or high-impact action requested

### Guidelines

- **Always use 🚨** to draw attention
- **Describe the operation** in clear, non-technical language when possible
- **Assess risk level** based on:
  - **High**: Destructive, irreversible, or affects production
  - **Medium**: Modifies existing code/config, reversible with effort
  - **Low**: Read-only, temporary, or easily undone
- **State reversibility** clearly
- **Provide your recommendation** with reasoning
- **Ask for explicit decision** (approve/deny)

---

## Completion Reports

Use this template when reporting that a project or AMCOS has been successfully created.

### Template

```
✅ Project and AMCOS ready!

Project: <project-name>
Path: <full-path>
AMCOS Session: amcos-<project-name>-coordinator
Status: Active and responding

<Next steps or what AMCOS will do next>
```

### When to Use

- Project creation completed successfully
- Chief-of-staff role assigned and health check passed
- Ready to start work

### Guidelines

- **Always use ✅** for successful completion
- **Include full path** for user reference
- **Confirm AMCOS status** (Active and responding)
- **State next steps** so user knows what to expect

### Example

```
✅ Project and AMCOS ready!

Project: inventory-system
Path: $AGENT_DIR/repos/inventory-system
AMCOS Session: amcos-inventory-coordinator
Status: Active and responding

AMCOS will now set up the development environment and implement the core inventory tracking module. Expected completion: 2 hours.
```

---

## Error Notifications

Use this template when an error or issue is encountered.

### Template

```
❌ Issue encountered: <error summary>

Details: <specific error>
Impact: <what this affects>
Attempted: <what you tried>

I recommend: <suggested fix or escalation>
```

### When to Use

- AMCOS reports an error or failure
- Project creation fails
- Health check fails
- AI Maestro message delivery fails
- Any unexpected issue that blocks progress

### Guidelines

- **Always use ❌** for errors
- **Summarize the error** in one line (e.g., "AMCOS health check timed out")
- **Provide specific details** (error messages, stack traces if relevant)
- **State the impact** clearly (e.g., "Work cannot proceed until AMCOS is responding")
- **List what you tried** to resolve it
- **Recommend next steps**:
  - Auto-fix if you can resolve it
  - Escalate to user if requires decision
  - Request user intervention if needed

### Example

```
❌ Issue encountered: AMCOS health check timed out

Details: Sent health check ping to amcos-inventory-coordinator, no response after 30 seconds
Impact: Cannot confirm AMCOS is ready to receive work instructions
Attempted: Retried health check 3 times with 10-second intervals

I recommend: Reassigning the chief-of-staff role. This usually resolves health check issues caused by initialization delays.

Should I reassign the chief-of-staff role?
```

---

## General Communication Guidelines

### Tone

- **Professional** but not robotic
- **Reassuring** when issues arise
- **Transparent** about what you're doing and why

### Specificity

- **Always include paths** for projects/files
- **Always include session names** for AMCOS references
- **Always include percentages** for progress
- **Always include reasoning** for recommendations

### Proactivity

- **Offer status updates** before being asked
- **Warn about potential issues** early
- **Explain decisions** without being prompted
- **Set expectations** about timing and next steps

### Consistency

- **Use the same templates** for the same scenarios
- **Use emoji markers consistently**:
  - ✅ Success/completion
  - ❌ Error/failure
  - 🚨 Urgent/approval needed
  - 📊 Status/progress
  - 🔄 In progress
- **Format lists** the same way across all responses
