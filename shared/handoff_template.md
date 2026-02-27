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

```yaml
---
uuid: "handoff-{uuid}"
from_role: "amama" | "amaa" | "amoa" | "amia"
to_role: "amama" | "amaa" | "amoa" | "amia"
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
USER <-> AMAMA (manager) <-> AMCOS (chief-of-staff) <-> EAA (architect, role: member)
                                                    <-> EOA (orchestrator, role: member)
                                                    <-> EIA (integrator, role: member)
```

**CRITICAL**: All specialist agents (amaa-, amoa-, amia-) communicate through AMCOS (chief-of-staff), NOT directly with AMAMA. AMAMA communicates only with AMCOS. Specialists do NOT communicate directly with each other.

## Handoff Types

### 1. User Request -> Role Assignment
- From: amama (assistant-manager)
- To: amaa | amoa | amia
- Purpose: Route user request to appropriate specialist

### 2. Design Complete -> Orchestration
- From: amaa (via amama)
- To: amoa (via amama)
- Purpose: Hand off approved design for implementation

### 3. Implementation Complete -> Integration
- From: amoa (via amama)
- To: amia (via amama)
- Purpose: Signal work ready for quality gates

### 4. Quality Gate Results -> User
- From: amia (via amama)
- To: user
- Purpose: Report integration status and request approvals

## File Naming Convention

```
handoff-{uuid}-{from}-to-{to}.md

Examples:
- handoff-a1b2c3d4-amama-to-amaa.md    # AM assigns to Architect
- handoff-e5f6g7h8-amaa-to-amama.md    # Architect reports to AM
- handoff-i9j0k1l2-amama-to-amoa.md    # AM assigns to Orchestrator
- handoff-m3n4o5p6-amoa-to-amama.md    # Orchestrator reports to AM
- handoff-q7r8s9t0-amama-to-amia.md    # AM assigns to Integrator
- handoff-u1v2w3x4-amia-to-amama.md    # Integrator reports to AM
```

## Storage Location

All handoff files are stored in: `docs_dev/handoffs/`
