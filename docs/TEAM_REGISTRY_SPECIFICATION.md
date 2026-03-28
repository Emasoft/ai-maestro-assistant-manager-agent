# Team Registry Specification

## Storage

| Item | Path |
|------|------|
| Team registry | Managed by AI Maestro server (query via API) |
| Local cache | `$AGENT_DIR/teams/registry.json` |

## API

| Operation | Endpoint |
|-----------|----------|
| Create team | `POST /api/teams` |
| List teams | `GET /api/teams` |
| Get team | `GET /api/teams/{id}` |
| Update team | `PATCH /api/teams/{id}` |
| Delete team | `DELETE /api/teams/{id}` |
| Assign COS | `PATCH /api/teams/{id}/chief-of-staff` |
| Add member | `POST /api/teams/{id}/members` |
| Remove member | `DELETE /api/teams/{id}/members/{agent}` |

## Team Types

**All teams are closed.** There are no open teams. Each agent belongs to at most ONE team.

| Type | COS | Description |
|------|-----|-------------|
| `closed` | Required | Formal COS-managed coordination |

## Registry Schema (registry.json)

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

## Titles in Registry

| Title | Count per Team | Notes |
|-------|---------------|-------|
| `MANAGER` | 0 (org-wide) | Not listed in team; singleton |
| `CHIEF-OF-STAFF` | 1 | Required for every team |
| `ORCHESTRATOR` | 0 or 1 | Primary kanban manager |
| `MEMBER` | 1+ | Skills field determines specialization |

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
GET $AIMAESTRO_API/api/teams/{id}/members
```

## Validation Rules

- Team name must be globally unique
- Agent name must be unique within team
- All teams are closed and must have exactly one COS
- At least one member per team
- Each agent belongs to at most one team
