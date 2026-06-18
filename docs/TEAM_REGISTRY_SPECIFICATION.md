# Team Registry Specification

Team and COS lifecycle here follows R26-R40 (GOVERNANCE-RULES.md); rule numbers
are cited inline. The persona is the authoritative source.

## Storage

| Item | Path |
|------|------|
| Global registry | `~/.aimaestro/teams/registry.json` |
| Per-repo registry | `<repo-root>/.aimaestro/team-registry.json` |

## CLI

All team-lifecycle CLIs resolve the MANAGER's AID auth internally — AMAMA passes
no Bearer token and no governance/sudo password (R28/R32). Team create and delete
are MANAGER actions with NO user approval (R29).

| Operation | Command |
|-----------|---------|
| Create team (incl. auto-created COS + base, R29) | `aimaestro-teams.sh create --name N [--type T] [--agents u1,u2]` |
| List teams | `aimaestro-teams.sh list` |
| Get team | `aimaestro-teams.sh show <teamId>` |
| Update team | `aimaestro-teams.sh update <teamId> [opts]` |
| Delete team (R29) | `aimaestro-teams.sh delete <teamId> [--delete-agents]` |
| Re-assign COS (R29) | MANAGER action via the teams CLI (no dashboard / USER-only step); if no deployed verb covers this sub-case yet it is a transition residual — never a sudo/password path (R32) |
| Add member | `aimaestro-teams.sh add-agent <teamId> <agent>` |
| Remove member | `aimaestro-teams.sh remove-agent <teamId> <agent>` |

The COS is **created by the MANAGER as part of `create`** (the server auto-creates
it, R29) — there is no separate "assign COS" step and no USER-only / dashboard
assignment. A deployed CLI's `--password` flag on create/delete is a USER/UI
residual that AMAMA never supplies (R32).

## Team Types

| Type | COS | Description |
|------|-----|-------------|
| `open` | Optional | Loose coordination |
| `closed` | Required | Formal COS-managed coordination |

## Registry Schema (registry.json)

The `members` array below is abbreviated to show the JSON shape; a real closed
team carries the COS + all 5 base members (R31, see Roles in Registry).

```json
{
  "version": "2.0.0",
  "teams": [
    {
      "id": "uuid",
      "name": "svgbbox-library-team",
      "type": "closed",
      "repository": "https://github.com/Emasoft/svgbbox",
      "cos": "svgbbox-cos",
      "members": [
        { "name": "svgbbox-impl-01", "role": "member", "skills": ["implementer"], "status": "active" },
        { "name": "svgbbox-tester-01", "role": "member", "skills": ["tester"], "status": "active" }
      ],
      "created_by": "manager",
      "created_at": "2026-02-03T10:00:00Z"
    }
  ]
}
```

## Roles in Registry

| Role | Count per Team | Notes |
|------|---------------|-------|
| `manager` | 0 (host-wide) | Not listed in team; singleton |
| `chief-of-staff` | 1 | Auto-created with the team (R29); required for closed teams |
| `orchestrator` / `architect` / `integrator` | 1 each | Part of the 5 base members (R31) |
| `member` | 1+ | One base MEMBER + project-specific extras; extras must be MEMBER-titled (R30); skills determine specialization |

A closed team's mandatory baseline is the COS + 5 base members (CHIEF-OF-STAFF,
ORCHESTRATOR, ARCHITECT, INTEGRATOR, MEMBER). A team missing any base member is
FROZEN until the base is complete (R31).

## Agent Naming

Format: `<team-prefix>-<descriptor>[-<instance>]`

| Example | Meaning |
|---------|---------|
| `svgbbox-cos` | COS for svgbbox team |
| `svgbbox-impl-01` | First implementer member |
| `svgbbox-tester-01` | First tester member |

## Member Status Values

| Status | Meaning |
|--------|---------|
| `active` | Available and working |
| `hibernated` | Suspended, can be woken |
| `offline` | Unreachable |
| `terminated` | Removed from team |

## Messaging Lookup

Agents resolve addresses from the team registry using the `team-governance` skill's member lookup capability, or via:
```
aimaestro-teams.sh show <teamId>
```

## Validation Rules

- Team name must be globally unique
- Agent name must be unique within team
- Closed teams must have exactly one COS (auto-created with the team, R29)
- A closed team must carry its 5 base members; one that is missing any base
  member is FROZEN until complete (R31)
- Extra (non-base) agents must be MEMBER-titled on the member-agent role plugin
  (R30)
