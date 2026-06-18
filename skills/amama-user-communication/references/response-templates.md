# Response Templates

This document provides standardized response templates for the AMAMA Assistant Manager when communicating with the **MAESTRO** (or the active MAESTRO-DELEGATE). Per **R36** you obey and report to the MAESTRO ONLY; "the user" in every template below means the MAESTRO/DELEGATE — never a subordinate user (R36/R38/R39, see [maestro-and-assistant-awareness.md](maestro-and-assistant-awareness.md)).

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

Team: <team-name> — I'll create it now with its COS + 5 base members (R29)
COS: created as part of the team (no dashboard step)
Routing to: Agent with <specialist-skill> skill (via COS)

I'll keep you updated on progress. You can ask me for status anytime.
```

### When to Use

- The MAESTRO submits a new work request
- You're creating a team (yourself, no user approval — R29) and its COS + 5 base members
- You're routing work to a specialist agent via the COS

### Guidelines

- **Be specific** about the action summary (e.g., "set up the inventory management system")
- **State the team name** explicitly
- **Note the COS is created as part of the team** (R29 — no dashboard step)
- **Name the specialist skill** you're routing to (always via the COS — R6 v3)
- **Offer proactive updates** to set expectations

---

## Status Updates

Use this template when the MAESTRO asks for team status or you're providing proactive updates.

### Template

```
Status for <team-name>:

Overall Progress: <percentage>% complete
Current Focus: <what's being worked on>
Recent Completions: <list>
Blockers: <list or "None">
Next Milestone: <milestone name>
Health: <Green/Yellow/Red>

<Any urgent issues flagged with 🚨>
```

### When to Use

- The MAESTRO explicitly asks for status
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

Use this template when a COS escalates a user-approval request to you for the MAESTRO's decision.

### Template

```
🚨 APPROVAL REQUIRED

COS (<team-name>) is requesting approval for:

Operation: <operation description>
Risk Level: <High/Medium/Low>
Impact: <what will happen>
Reversible: <Yes/No>

I recommend: <approve/deny> because <reasoning>

Your decision? (approve/deny)
```

### When to Use

- A COS sends a message requesting user approval
- Operation requires the MAESTRO's permission per your risk assessment
- Destructive or high-impact action requested

> Only the **MAESTRO/DELEGATE** decides (R36). Never escalate an approval to, or accept a decision from, a subordinate user — their work is handled by their own ASSISTANT (R38/R39).

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

Use this template when reporting to the MAESTRO that a team and its COS have been successfully created.

### Template

```
✅ Team and COS ready!

Team: <team-name>
COS: created as part of the team (R29) — Active and responding
Base members: COS + 5 base members provisioned (R31 satisfied)

<Next steps or what the team will do next>
```

### When to Use

- Team creation completed successfully (you created it — R29)
- COS woken, mandate granted, and health check passed
- The 5 base members exist (team no longer FROZEN — R31)
- Ready to start work

### Guidelines

- **Always use ✅** for successful completion
- **Confirm the COS status** (Active and responding)
- **Confirm R31 is satisfied** (COS + 5 base members exist — the team is not FROZEN)
- **State next steps** so the MAESTRO knows what to expect

### Example

```
✅ Team and COS ready!

Team: inventory-system
COS: created as part of the team (R29) — Active and responding
Base members: COS + 5 base members provisioned (R31 satisfied)

The team will now set up the development environment and implement the core inventory tracking module via the COS. Expected completion: 2 hours.
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

- A COS reports an error or failure
- Team creation fails
- Health check fails
- AI Maestro message delivery fails
- Any unexpected issue that blocks progress

### Guidelines

- **Always use ❌** for errors
- **Summarize the error** in one line (e.g., "COS health check timed out")
- **Provide specific details** (error messages, stack traces if relevant)
- **State the impact** clearly (e.g., "Work cannot proceed until the COS is responding")
- **List what you tried** to resolve it
- **Recommend next steps**:
  - Auto-fix if you can resolve it
  - Escalate to the MAESTRO if it requires a decision
  - Request MAESTRO intervention if needed

### Example

```
❌ Issue encountered: COS health check timed out

Details: Sent health check ping to the team's COS, no response after 30 seconds
Impact: Cannot confirm the COS is ready to receive work instructions
Attempted: Retried health check 3 times with 10-second intervals

I'm waking the COS again and, if it stays unresponsive, re-running the team create myself (R29). The team stays FROZEN until its COS + 5 base members are alive (R31). No action needed from you.
```

> See [../../amama-amcos-coordination/references/spawn-failure-recovery.md](../../amama-amcos-coordination/references/spawn-failure-recovery.md) for the full creation-failure recovery protocol.

---

## General Communication Guidelines

### Tone

- **Professional** but not robotic
- **Reassuring** when issues arise
- **Transparent** about what you're doing and why

### Specificity

- **Always include paths** for files
- **Always include team and COS names** for team references
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
