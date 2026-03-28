---
name: amama-role-routing
description: Use when routing user requests to specialist agents based on skills. Trigger with work delegation needs.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# Role Routing Skill

## Overview

Routes user requests to the appropriate specialist agent via AMCOS (chief-of-staff). AMAMA never contacts specialists directly. 4 governance titles: `MANAGER`, `CHIEF-OF-STAFF`, `ORCHESTRATOR`, `MEMBER`. ORCHESTRATOR is a governance title (primary kanban manager), not just a specialization. Architect/Integrator are specializations via `skills`/`tags`. See `references/governance-and-specializations.md`.

## Prerequisites

- AI Maestro messaging system running
- Specialist agents (AMAA, AMOA, AMIA) registered with `role: 'member'`
- `docs_dev/handoffs/` directory exists and is writable

## Instructions

1. Parse user message to identify primary intent
2. Match intent to routing rule (see decision matrix below)
3. If direct (status, approval, clarification): respond immediately
4. If routing: create handoff with UUID, save to `docs_dev/handoffs/`
5. Send handoff to AMCOS via AI Maestro
6. Track handoff status, report routing decision to user

Copy this checklist and track your progress:

- [ ] Parse intent
- [ ] Match routing rule
- [ ] Create handoff or respond directly
- [ ] Send via AI Maestro
- [ ] Track and report

**Routing targets** (routed via AMCOS):
- **AMAA** (`amaa-`) -- MEMBER title, architect specialization
- **AMOA** (`amoa-`) -- ORCHESTRATOR title, primary kanban manager
- **AMIA** (`amia-`) -- MEMBER title, integrator specialization

| Intent Pattern | Route To | Handoff Type |
|----------------|----------|--------------|
| "design", "plan", "architect", "spec" | AMCOS (for AMAA) | work_request |
| "build", "implement", "create", "code" | AMCOS (for AMOA) | work_request |
| "review", "test", "merge", "deploy" | AMCOS (for AMIA) | work_request |
| "spawn agent", "terminate", "restart" | AMCOS | agent_lifecycle |
| "status", "progress", "update" | Handle directly | none |
| "approve", "reject", "confirm" | Handle directly | approval_response |

Full routing rules: `references/routing-rules.md`. Handoff protocol: `references/handoff-protocol.md`.

## Output

| Decision | Handoff File | Message |
|----------|-------------|---------|
| Route to specialist | `handoff-{uuid}-amama-to-amcos.md` | AI Maestro message to AMCOS |
| Handle directly | None | Direct response to user |
| Ambiguous intent | None | Request clarification |

## Error Handling

| Error | Resolution |
|-------|------------|
| Ambiguous intent | Ask user for clarification |
| Target agent unavailable | Queue handoff, notify user, retry |
| Handoff dir missing | Create `docs_dev/handoffs/` automatically |
| UUID collision | Generate new UUID and retry |

## Examples

**Example 1 -- Design request routed to AMCOS:**

User says: "Design an auth system with OAuth2 support"

Intent matched: "design" -> route to AMCOS for AMAA. AI Maestro message sent:

```json
{
  "to": "amcos-chief-of-staff",
  "subject": "Work request: Design auth system",
  "priority": "normal",
  "content": {
    "type": "work_request",
    "message": "Route to AMAA: Design auth system with OAuth2 support",
    "handoff_id": "handoff-a1b2c3-amama-to-amcos.md",
    "target_specialist": "amaa-architect"
  }
}
```

Handoff file saved to `docs_dev/handoffs/handoff-a1b2c3-amama-to-amcos.md`.

**Example 2 -- Status request handled directly:**

User says: "What's the progress on the API?" -> intent "progress" -> handle directly. No handoff. Query agents and respond with status summary.

## Resources

- Routing rules: `references/routing-rules.md`
- Handoff protocol: `references/handoff-protocol.md`
- Governance roles: `references/governance-and-specializations.md`
- Design/orchestration routing: `references/design-and-orchestration-routing.md`
- GitHub operations: see **amama-github-routing** skill
