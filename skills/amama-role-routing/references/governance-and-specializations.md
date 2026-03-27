# Governance Roles vs. Agent Specializations

<!-- TOC -->
- [Governance Roles](#governance-roles)
- [Plugin Prefix Reference](#plugin-prefix-reference)
- [Communication Hierarchy](#communication-hierarchy)
<!-- /TOC -->

## Governance Roles

AI Maestro defines exactly **3 governance roles**:

| Governance Role | Purpose |
|-----------------|---------|
| `manager` | Team manager with full administrative authority |
| `chief-of-staff` | Agent lifecycle, permissions, failure recovery |
| `member` | All other agents -- the default role |

**Architect**, **Orchestrator**, and **Integrator** are NOT governance roles. They are **plugin-level specializations** expressed through agent skills, metadata, and tags. When creating or registering agents, always set `role: 'member'` for all non-COS agents. The specialization (architect, orchestrator, integrator) is conveyed via the agent's `skills` array and `tags` metadata, not the `role` field.

```jsonc
// CORRECT -- specialization via skills/tags, governance role is 'member'
{
  "name": "amaa-architect",
  "role": "member",
  "skills": ["architecture", "design", "requirements-analysis"],
  "tags": ["specialization:architect"]
}

// WRONG -- do NOT use specialization names as governance roles
{
  "name": "amaa-architect",
  "role": "architect"  // <- INVALID: not a governance role
}
```

## Plugin Prefix Reference

| Specialization | Prefix | Plugin Name | Governance Role |
|----------------|--------|-------------|-----------------|
| Assistant Manager | `amama-` | AI Maestro Assistant Manager Agent | `manager` |
| Chief of Staff | `amcos-` | AI Maestro Chief of Staff | `chief-of-staff` |
| Architect | `amaa-` | AI Maestro Architect Agent | `member` |
| Orchestrator | `amoa-` | AI Maestro Orchestrator Agent | `member` |
| Integrator | `amia-` | AI Maestro Integrator Agent | `member` |

## Communication Hierarchy

```
USER <-> AMAMA (Assistant Manager) <-> AMCOS (Chief of Staff) <-> AMAA (Architect skill agent)
                                                            <-> AMOA (Orchestrator skill agent)
                                                            <-> AMIA (Integrator skill agent)
```

**Governance roles in this hierarchy:**
- AMAMA: `manager`
- AMCOS: `chief-of-staff`
- AMAA, AMOA, AMIA: `member` (with specialization expressed via skills/tags)

**CRITICAL**:
- AMAMA is the ONLY agent that communicates directly with the USER
- AMAMA has UNRESTRICTED messaging -- it CAN message any agent directly (MANAGER privilege)
- AMCOS manages agent lifecycle and is the preferred route for delegating work to specialists
- AMAA, AMOA, and AMIA CAN communicate with AMAMA when AMAMA contacts them directly
- Routing via AMCOS is preferred for delegation but not required -- AMAMA may contact specialists directly if urgent
- All specialist agents use governance `role: 'member'` -- their specialization is metadata, not a governance concept
