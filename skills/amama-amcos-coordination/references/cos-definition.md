# What is a COS-Assigned Agent

<!-- TOC -->
- [Definition](#definition)
- [Hierarchy](#hierarchy)
- [Responsibilities Split](#responsibilities-split)
- [How the COS Is Created](#how-the-cos-is-created)
<!-- /TOC -->

## Definition

A COS-assigned agent is an existing registered agent that has been given the Chief of Staff role within a team. The COS role designates the agent as the operational coordinator for that team, managing day-to-day tasks. The COS sits between AMAMA and the specialized roles (Architect, Orchestrator, Integrator).

## Hierarchy

```
USER
  |
AMAMA (Assistant Manager) - User's direct interface
  |
COS-assigned agent (Chief of Staff role) - Operational coordinator for a team
  |
+-- AMAA (Architect)
+-- AMOA (Orchestrator)
+-- AMIA (Integrator)
```

## Responsibilities Split

| Role | Responsibilities |
|------|------------------|
| AMAMA (MANAGER) | User communication, final approvals, high-level decisions, team + COS creation (R29), granting the COS its mandate (R30) |
| COS | Task coordination, routine operations, delegation management within team, completing the team's 5 base members under its mandate (R30) |

## How the COS Is Created

The MANAGER creates AND deletes teams on its own with NO user approval (R29). When the MANAGER runs `aimaestro-teams.sh create` for a closed team, the AI Maestro server **auto-creates** that team's COS; the MANAGER then wakes it and grants its mandate (R30). The COS retains its own identity but holds the CHIEF-OF-STAFF title for that team. A team missing any of its 5 base members is FROZEN — only the COS active — until the COS completes the base (R31).
