# Handoff Document Template

This template defines the standard format for handoff documents between roles in the 4-plugin architecture.

## Plugin Prefixes

| Plugin | Prefix | Full Name |
|--------|--------|-----------|
| Assistant Manager | `amama-` | AI Maestro Assistant Manager Agent |
| Architect | `amaa-` | AI Maestro Architect Agent |
| Orchestrator | `amoa-` | AI Maestro Orchestrator Agent |
| Integrator | `amia-` | AI Maestro Integrator Agent |

## Handoff File Format

**Note on `amcos` in role fields**: The value `amcos` refers to the COS governance role, not the agent's session identity. In v2, any registered agent can be assigned the COS role — its session name may differ (e.g., `coordinator-alpha`). Use `amcos` in `from_role`/`to_role` to indicate the agent is acting in its COS capacity. The actual recipient session name is resolved via the team's `chief_of_staff` field in the AI Maestro API.

```yaml
---
uuid: "handoff-{uuid}"
from_role: "amama" | "amcos" | "amaa" | "amoa" | "amia"
to_role: "amama" | "amcos" | "amaa" | "amoa" | "amia"
created: "ISO-8601 timestamp"
github_issue: "#issue_number"  # Optional
subject: "Brief description"
priority: "urgent" | "high" | "normal" | "low"
requires_ack: true | false
status: "pending" | "acknowledged" | "completed" | "rejected"
---

## Context

[Background information and context for this handoff]

## Requirements / Deliverables

[What needs to be done or what is being delivered]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Dependencies

- Depends on: [list of dependencies]
- Blocks: [list of blocked items]

## Notes

[Additional notes or considerations]
```

## Communication Hierarchy

```
USER <-> AMAMA (manager) <-> AMCOS (chief-of-staff) <-> AMAA (architect, role: member)
                                                    <-> AMOA (orchestrator, role: member)
                                                    <-> AMIA (integrator, role: member)
```

**CRITICAL**: All specialist agents (amaa-, amoa-, amia-) communicate through AMCOS (chief-of-staff), NOT directly with AMAMA. AMAMA communicates only with AMCOS. Specialists do NOT communicate directly with each other.

## Handoff Types

### 1. User Request -> AMCOS Delegation
- From: amama (assistant-manager)
- To: amcos (chief-of-staff)
- Purpose: Route user request to AMCOS for specialist delegation

### 2. Design Complete -> Orchestration
- From: amaa -> amcos (chief-of-staff)
- To: amoa (via amcos)
- Purpose: Hand off approved design for implementation

### 3. Implementation Complete -> Integration
- From: amoa -> amcos (chief-of-staff)
- To: amia (via amcos)
- Purpose: Signal work ready for quality gates

### 4. Quality Gate Results -> User
- From: amia -> amcos -> amama
- To: user (via amama)
- Purpose: Report integration status and request approvals

## File Naming Convention

```
handoff-{uuid}-{from}-to-{to}.md

Examples:
- handoff-a1b2c3d4-amama-to-amcos.md   # AM delegates to AMCOS
- handoff-e5f6g7h8-amcos-to-amama.md   # AMCOS reports to AM
- handoff-i9j0k1l2-amcos-to-amaa.md    # AMCOS assigns to Architect
- handoff-m3n4o5p6-amaa-to-amcos.md    # Architect reports to AMCOS
- handoff-q7r8s9t0-amcos-to-amoa.md    # AMCOS assigns to Orchestrator
- handoff-u1v2w3x4-amoa-to-amcos.md    # Orchestrator reports to AMCOS
```

## Storage Location

All handoff files are stored in: `docs_dev/handoffs/`
