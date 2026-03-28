# GovernanceRequest State Machine Reference

## Table of Contents
- [States](#states)
- [Transitions](#transitions)
- [Plugin Prefix Reference](#plugin-prefix-reference)

Every GovernanceRequest follows this state machine:

```
pending --> remote-approved --> dual-approved --> executed
   |               |
   |        pending --> local-approved --> dual-approved --> executed
   |
   +---> rejected
```

## States

| State | Description |
|-------|-------------|
| `pending` | Request created, awaiting approval |
| `remote-approved` | Approved by remote authority, awaiting MANAGER |
| `local-approved` | Approved by MANAGER, awaiting remote authority |
| `dual-approved` | Both local and remote approvals obtained |
| `executed` | The approved operation has been carried out |
| `rejected` | Request denied by MANAGER or auto-rejected |

## Transitions

- `pending` -> `remote-approved`: Remote authority approves first
- `pending` -> `local-approved`: MANAGER approves first
- `pending` -> `rejected`: MANAGER rejects, or auto-rejection (expiry)
- `remote-approved` -> `dual-approved`: MANAGER provides the second approval
- `local-approved` -> `dual-approved`: Remote authority provides the second approval
- `dual-approved` -> `executed`: The system executes the approved operation

## Plugin Prefix Reference

| Title | Prefix | Plugin Name |
|-------|--------|-------------|
| MANAGER | `amama-` | AI Maestro Assistant Manager Agent |
| ORCHESTRATOR | `amoa-` | AI Maestro Orchestrator Agent |
| MEMBER (Architect) | `amaa-` | AI Maestro Architect Agent |
| MEMBER (Integrator) | `amia-` | AI Maestro Integrator Agent |
