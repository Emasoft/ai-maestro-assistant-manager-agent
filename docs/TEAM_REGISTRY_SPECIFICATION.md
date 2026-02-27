# Team Registry Specification

## Storage

| Item | Path |
|------|------|
| Global registry | `~/.aimaestro/teams/registry.json` |
| Per-repo registry | `<repo-root>/.aimaestro/team-registry.json` |

## API

| Operation | Endpoint |
|-----------|----------|
| Create team | `POST /api/teams` |
| List teams | `GET /api/teams` |
| Get team | `GET /api/teams/{id}` |
| Update team | `PATCH /api/teams/{id}` |
| Delete team | `DELETE /api/teams/{id}` |
| Assign COS | `POST /api/teams/{id}/cos` |
| Add member | `POST /api/teams/{id}/members` |
| Remove member | `DELETE /api/teams/{id}/members/{agent}` |

## Team Types

| Type | COS | Description |
|------|-----|-------------|
| `open` | Optional | Loose coordination |
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

## Roles in Registry

| Role | Count per Team | Notes |
|------|---------------|-------|
| `manager` | 0 (org-wide) | Not listed in team; singleton |
| `chief-of-staff` | 0 or 1 | Required for closed teams |
| `member` | 1+ | Skills field determines specialization |

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

Agents resolve addresses from registry:
```bash
curl -s "$AIMAESTRO_API/api/teams/{id}/members" | jq '.[].name'
```

## Validation Rules

- Team name must be globally unique
- Agent name must be unique within team
- Closed teams must have exactly one COS
- At least one member per team
