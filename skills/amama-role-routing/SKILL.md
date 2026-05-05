---
name: amama-role-routing
description: Use when routing user requests to specialist agents. Trigger with work delegation needs. Loaded by ai-maestro-assistant-manager-agent-main-agent
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# Role Routing Skill

## Overview

Routes requests to specialist agents. AMAMA can message directly; routing via AMCOS preferred but not required. 3 governance roles: `manager`, `chief-of-staff`, `member`.

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

**Routing targets** (all `role: member`, preferably routed via AMCOS for delegation, or directly if urgent):
- **AMAA** (`amaa-`) -- architect specialization
- **AMOA** (`amoa-`) -- orchestrator specialization
- **AMIA** (`amia-`) -- integrator specialization

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
  - Governance Roles
  - Plugin Prefix Reference
  - Communication Hierarchy
