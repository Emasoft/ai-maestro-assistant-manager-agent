# Governance Titles vs. Agent Specializations

<!-- TOC -->
- [Governance Titles](#governance-titles)
- [Plugin Prefix Reference](#plugin-prefix-reference)
- [Communication Hierarchy](#communication-hierarchy)
<!-- /TOC -->

## Governance Titles

AI Maestro defines exactly **4 governance titles**:

| Governance Title | Purpose | Kanban Access |
|------------------|---------|---------------|
| `MANAGER` | Singleton. Full authority over all teams and agents. | Can manage (secondary) |
| `CHIEF-OF-STAFF` | Leads a team. Manages membership, routes external messages. | Can manage (secondary) |
| `ORCHESTRATOR` | Primary kanban manager. Direct MANAGER communication. Task distribution. | **Primary manager** |
| `MEMBER` | Default. Standard team member. Reports to Orchestrator. | View only |

**ORCHESTRATOR IS a governance title**, not just a specialization. It sits alongside MANAGER, CHIEF-OF-STAFF, and MEMBER in the governance model.

**Architect** and **Integrator** are NOT governance titles. They are **plugin-level specializations** expressed through agent skills, metadata, and tags. When creating or registering agents, set `title: 'MEMBER'` for architect/integrator agents. The specialization is conveyed via the agent's `skills` array and `tags` metadata, not the `title` field.

All teams are closed. Each agent belongs to at most ONE team at a time.

```jsonc
// CORRECT -- architect is a MEMBER with specialization via skills/tags
{
  "name": "amaa-architect",
  "title": "MEMBER",
  "skills": ["architecture", "design", "requirements-analysis"],
  "tags": ["specialization:architect"]
}

// CORRECT -- orchestrator has its own governance title
{
  "name": "amoa-orchestrator",
  "title": "ORCHESTRATOR",
  "skills": ["task-management", "kanban", "coordination"],
  "tags": []
}

// WRONG -- do NOT use specialization names as governance titles
{
  "name": "amaa-architect",
  "title": "architect"  // <- INVALID: not a governance title
}
```

## Plugin Prefix Reference

| Agent | Prefix | Plugin Name | Governance Title |
|-------|--------|-------------|------------------|
| Assistant Manager | `amama-` | AI Maestro Assistant Manager Agent | `MANAGER` |
| Chief of Staff | `amcos-` | AI Maestro Chief of Staff | `CHIEF-OF-STAFF` |
| Orchestrator | `amoa-` | AI Maestro Orchestrator Agent | `ORCHESTRATOR` |
| Architect | `amaa-` | AI Maestro Architect Agent | `MEMBER` |
| Integrator | `amia-` | AI Maestro Integrator Agent | `MEMBER` |

## Communication Hierarchy

```
USER <-> AMAMA (MANAGER) <-> AMCOS (CHIEF-OF-STAFF) <-> AMOA (ORCHESTRATOR) <-> AMAA (Architect, MEMBER)
                                                    <-> AMIA (Integrator, MEMBER)
                          <-> AMOA (ORCHESTRATOR can message MANAGER directly)
```

**Governance titles in this hierarchy:**
- AMAMA: `MANAGER`
- AMCOS: `CHIEF-OF-STAFF`
- AMOA: `ORCHESTRATOR` (can message MANAGER directly, no COS relay needed)
- AMAA, AMIA: `MEMBER` (with specialization expressed via skills/tags)

**CRITICAL**:
- AMAMA is the ONLY agent that communicates directly with the USER
- AMCOS manages agent lifecycle and sits between AMAMA and specialist agents
- ORCHESTRATOR can message MANAGER directly (no COS relay needed)
- AMAA and AMIA do NOT communicate directly with AMAMA
- All teams are closed. There are no open teams.
- Each agent belongs to at most ONE team at a time
- ORCHESTRATOR is the PRIMARY kanban manager; COS and MANAGER are secondary
