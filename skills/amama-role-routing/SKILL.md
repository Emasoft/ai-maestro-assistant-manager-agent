---
name: amama-role-routing
description: Use when routing user requests to specialist agents based on skills. Trigger with work delegation needs.
version: 2.3.2
compatibility: Requires AI Maestro installed.
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
triggers:
  - User submits a new request or task
  - Assistant Manager needs to delegate work
  - Handoff between specialist agents is required
---

# Role Routing Skill

## Overview

Routes user requests to the appropriate specialist agent based on skills and specialization. All specialist routing goes through AMCOS (chief-of-staff) -- AMAMA never contacts specialists directly. Only 3 governance roles exist: `manager`, `chief-of-staff`, `member`. Architect/Orchestrator/Integrator are specializations expressed via `skills`/`tags`, not the `role` field. See `references/governance-and-specializations.md`.

## Prerequisites

- AI Maestro messaging system running
- All specialist agents (AMAA, AMOA, AMIA) registered with `role: 'member'`
- `docs_dev/handoffs/` directory exists and is writable
- UUID generation capability required

## Instructions

1. Parse user message to identify primary intent
2. Match intent to routing rule (see decision matrix below)
3. If handling directly (status, approval, clarification), respond immediately
4. If routing: create handoff with UUID, save to `docs_dev/handoffs/`, send to AMCOS via AI Maestro
5. Track handoff status and report routing decision to user

**Routing targets** (all `role: member`, routed via AMCOS):
- **AMAA** (prefix `amaa-`) -- architect specialization
- **AMOA** (prefix `amoa-`) -- orchestrator specialization
- **AMIA** (prefix `amia-`) -- integrator specialization

For detailed per-agent routing rules, see `references/routing-rules.md`.

## Routing Decision Matrix

| User Intent Pattern | Route To | Handoff Type |
|---------------------|----------|--------------|
| "design", "plan", "architect", "spec", "requirements" | AMCOS (for AMAA) | work_request |
| "build", "implement", "create", "develop", "code" | AMCOS (for AMOA) | work_request |
| "review", "test", "merge", "release", "deploy" | AMCOS (for AMIA) | work_request |
| "spawn agent", "terminate", "restart", "agent health" | AMCOS | agent_lifecycle |
| "status", "progress", "update" | Handle directly | none |
| "approve", "reject", "confirm" | Handle directly | approval_response |

## Output

| Decision | Handoff File | Message |
|----------|-------------|---------|
| Route to specialist (via AMCOS) | `handoff-{uuid}-amama-to-amcos.md` | AI Maestro message to AMCOS |
| Handle directly | None | Direct response to user |
| Ambiguous intent | None | Request clarification |

## Handoff Protocol (Summary)

1. Identify intent and match routing rule
2. Validate: all fields present, UUID unique, target agent alive, no placeholders
3. Create `handoff-{uuid}-{from}-to-{to}.md` in `docs_dev/handoffs/`
4. Send via AI Maestro with appropriate priority
5. Track status as "pending", monitor for acknowledgment
6. Report routing decision to user

Full protocol with validation checklist: `references/handoff-protocol.md`.

## Error Handling

| Error | Resolution |
|-------|------------|
| Ambiguous intent | Ask user for clarification |
| Target agent unavailable | Queue handoff, notify user, retry |
| Handoff dir missing | Create `docs_dev/handoffs/` automatically |
| UUID collision | Generate new UUID and retry |

## Examples

**Design request**: User says "Design auth system" -- intent matches "design" -- route to AMCOS for AMAA. Create handoff with requirements, save to `docs_dev/handoffs/`, send AI Maestro message.

**Status request**: User says "What's the status?" -- intent matches "status" -- handle directly. Query agents, compile report, respond to user. No handoff created.

## Resources

- Detailed routing rules: `references/routing-rules.md`
- Handoff protocol and validation: `references/handoff-protocol.md`
- Governance roles and prefixes: `references/governance-and-specializations.md`
- Design/orchestration routing: `references/design-and-orchestration-routing.md`
- GitHub operations routing: see **amama-github-routing** skill
- Proactive Handoff Protocol: see amama-session-memory skill references
