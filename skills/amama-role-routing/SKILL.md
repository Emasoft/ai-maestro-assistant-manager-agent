---
name: amama-role-routing
description: Use when routing user requests to specialist agents. Trigger with work delegation needs. Loaded by ai-maestro-assistant-manager-agent-main-agent
compatibility: Requires AI Maestro installed.
context: fork
agent: ai-maestro-assistant-manager-agent-main-agent
user-invocable: false
---

# Role Routing Skill

## Overview

Routes user requests to specialist team agents. AMAMA delegates **only via AMCOS** — the team's CHIEF-OF-STAFF is the sole entry point into a team (R6 v3); AMAMA never messages a team-internal agent directly. AMAMA responds to the MAESTRO directly (status, approvals, clarifications) — it obeys ONLY the currently-active MAESTRO / DELEGATE (R36/R37) — and talks to its AMCOS directly. Each team agent holds a governance title bound to its AID (R28): the 5 base titles are CHIEF-OF-STAFF / ARCHITECT / ORCHESTRATOR / INTEGRATOR / MEMBER; extra agents are MEMBER-titled (R30). See [governance-and-specializations](references/governance-and-specializations.md) for the full title model and team-creation authority (R29/R31).

## Prerequisites

- AI Maestro messaging system running
- The target team exists and is complete (COS + 5 base members) — a team missing any base member is FROZEN (R31), do not route into it
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

**Routing targets** (team-internal governance titles, **always** routed via AMCOS — the sole entry point into a team, R6 v3; never message a team agent directly):
- **AMAA** (`amaa-`) -- ARCHITECT
- **AMOA** (`amoa-`) -- ORCHESTRATOR
- **AMIA** (`amia-`) -- INTEGRATOR

| Intent Pattern | Route To | Handoff Type |
|----------------|----------|--------------|
| "design", "plan", "architect", "spec" | AMCOS (for AMAA) | work_request |
| "build", "implement", "create", "code" | AMCOS (for AMOA) | work_request |
| "review", "test", "merge", "deploy" | AMCOS (for AMIA) | work_request |
| "spawn agent", "terminate", "restart" | AMCOS | agent_lifecycle |
| "status", "progress", "update" | Handle directly | none |
| "approve", "reject", "confirm" | Handle directly | approval_response |

See routing-rules.md and handoff-protocol.md in Resources.

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

**Input:** User says "Design an auth system"
**Output:** Intent "design" → route to AMCOS for AMAA. Handoff saved, message sent.

**Input:** User says "What's the progress?"
**Output:** Intent "progress" → handle directly. No handoff needed.

## Resources

- [routing-rules](references/routing-rules.md)
  > Route to AMAA (Architect) · Route to AMOA (Orchestrator) · Route to AMIA (Integrator) · Route to AMCOS (Chief of Staff) · Handle Directly (no routing)
- [handoff-protocol](references/handoff-protocol.md)
  - Steps
  - File Naming Convention
  - Storage Location
  - Checklist
- [governance-and-specializations](references/governance-and-specializations.md)
  - Governance Titles
  - Team Creation Authority (R29/R30/R31)
  - Plugin Prefix Reference
  - Communication Hierarchy
