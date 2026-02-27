# Team Boundaries and Labels

All GitHub issues must be tagged with a team label to enforce team boundaries. Team labels follow the format `team:{teamId}`.

## Team Label Rules

1. **Every issue MUST have exactly one team label** - Issues without team labels are invalid and must be labeled before routing.
2. **Team labels determine visibility** - Agents only see and operate on issues belonging to their team.
3. **Cross-team operations require explicit approval** - An agent from team-A cannot modify issues labeled `team:team-B` without AMAMA escalation.
4. **Label format**: `team:{teamId}` (e.g., `team:frontend`, `team:backend`, `team:infra`, `team:design`)

## Team Label Application

When creating or routing an issue:

```bash
# Add team label on issue creation
gh issue create --title "Fix login timeout" --label "bug,team:backend"

# Add team label to existing issue
gh issue edit 42 --add-label "team:frontend"

# Query issues for a specific team
gh issue list --label "team:backend"
```

## Team Boundary Enforcement Decision

```
GitHub operation received
          │
          ▼
┌────────────────────────────┐
│  Does issue have team      │
│  label?                    │
└──────────────┬─────────────┘
        ┌──────┴──────┐
        │ YES         │ NO
        ▼             ▼
┌──────────────┐  ┌──────────────────────┐
│ Does the     │  │ Determine owning     │
│ requesting   │  │ team from context:   │
│ agent belong │  │ - Module ownership   │
│ to this team?│  │ - Design ownership   │
└──────┬───────┘  │ - User specification │
       │          └──────────┬───────────┘
  ┌────┴────┐                │
  │YES  │NO │          Apply team label
  ▼     ▼   │          then proceed
PROCEED  ESCALATE            │
         to AMAMA            ▼
         for cross-    PROCEED with
         team approval routing
```
