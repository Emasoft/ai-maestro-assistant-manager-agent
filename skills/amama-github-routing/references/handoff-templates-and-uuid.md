# Handoff Content Requirements and UUID Tracking

## Table of Contents

- [For AMIA (Integrator) GitHub Handoffs](#for-amia-integrator-github-handoffs)
- [For AMAA (Architect) Design-GitHub Handoffs](#for-amaa-architect-design-github-handoffs)
- [For AMOA (Orchestrator) Module-GitHub Handoffs](#for-amoa-orchestrator-module-github-handoffs)
- [The 17-Column Vocabulary (for every `Task Sync Required` block above)](#the-17-column-vocabulary-for-every-task-sync-required-block-above)
- [UUID Tracking Across GitHub Operations](#uuid-tracking-across-github-operations)

## For AMIA (Integrator) GitHub Handoffs

```markdown
## GitHub Operation Handoff

**Operation Type**: [issue|pr|kanban|release]
**Action**: [create|update|close|merge|sync|etc.]
**Target**: [repo, issue number, PR number, project ID]
**Team Label**: team:{teamId}

### Details
- Specific operation parameters
- Any linked references

### Expected Outcome
- What success looks like
- Verification criteria

### Task Sync Required
- AI Maestro task column to set: [one of the ratified 17 columns — see task-system-sync.md]
- Task file: ~/.aimaestro/teams/tasks-{teamId}.json
```

## For AMAA (Architect) Design-GitHub Handoffs

```markdown
## Design-GitHub Link Handoff

**Design UUID**: [uuid]
**Design Path**: [path to design doc]
**GitHub Target**: [issue/card number or ID]
**Team Label**: team:{teamId}

### Link Context
- Why this link exists
- What the GitHub item represents in the design

### Expected Outcome
- Design doc updated with GitHub reference
- GitHub item updated with design reference

### Task Sync Required
- AI Maestro task column to set: [one of the ratified 17 columns — see task-system-sync.md]
- Task file: ~/.aimaestro/teams/tasks-{teamId}.json
```

## For AMOA (Orchestrator) Module-GitHub Handoffs

```markdown
## Module-GitHub Handoff

**Module UUID**: [uuid]
**Design Reference**: [design UUID]
**GitHub Target**: [issue/card number or ID]
**Team Label**: team:{teamId}

### Implementation Context
- Module's role in overall implementation
- Dependencies on other modules

### Task Details
- Specific implementation task
- Acceptance criteria

### Task Sync Required
- AI Maestro task column to set: [one of the ratified 17 columns — see task-system-sync.md]
- Task file: ~/.aimaestro/teams/tasks-{teamId}.json
```

## The 17-Column Vocabulary (for every `Task Sync Required` block above)

Every handoff's `Task Sync Required` column MUST be one of the ratified 17 — never a
value invented at the handoff site:

- **Lifecycle (14, in order)**: `backburner`, `todo`, `design`, `dispatch`, `dev`,
  `testing`, `ai_review`, `human_review`, `complete`, `publish`, `published`, `deploy`,
  `live`, `live_auditing`
- **Exception (3, orthogonal)**: `blocked`, `failed`, `superseded`

The path after `complete` is chosen by `release-via`: `publish` -> `published` (tools),
or `deploy` -> `live` -> `live_auditing` (services). See
[task-system-sync.md](task-system-sync.md) for the transition table and the
`blocked` / `failed` rules.

## UUID Tracking Across GitHub Operations

### UUID Reference Format in GitHub

When creating GitHub items linked to designs/modules, include UUID reference and team label:

**In Issue Body**:
```markdown
<!-- AMAMA-LINK: design-uuid=abc123 -->
<!-- AMAMA-LINK: module-uuid=def456 -->
<!-- AMAMA-TEAM: team:backend -->
```

**In PR Description**:
```markdown
## Related Design
Design UUID: `abc123` (path: `design/feature-x/DESIGN.md`)
Team: `team:backend`

## Implementing Modules
- Module UUID: `def456` (component-a)
- Module UUID: `ghi789` (component-b)
```

**In Kanban Card Notes**:
```
DESIGN: abc123
MODULE: def456
TEAM: backend
```

### Searching by UUID

AMAMA can find GitHub items by UUID using:
```bash
gh issue list --search "AMAMA-LINK: design-uuid=abc123" --json number,title,url
gh pr list --search "Design UUID: abc123" --json number,title,url
gh issue list --label "team:backend" --search "AMAMA-LINK: module-uuid=def456" --json number,title,url
```
