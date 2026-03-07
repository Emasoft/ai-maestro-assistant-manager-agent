# What is a COS-Assigned Agent

<!-- TOC -->
- [Definition](#definition)
- [Hierarchy](#hierarchy)
- [Responsibilities Split](#responsibilities-split)
- [Key Difference from v1](#key-difference-from-v1)
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
| AMAMA | User communication, final approvals, high-level decisions, COS assignment |
| COS-assigned agent | Task coordination, routine operations, delegation management within team |

## Key Difference from v1

In v1, AMAMA spawned dedicated AMCOS instances. In v2, AMAMA assigns the COS role to an already-registered agent. The agent retains its identity but gains additional COS responsibilities and constraints for the team it is assigned to.
