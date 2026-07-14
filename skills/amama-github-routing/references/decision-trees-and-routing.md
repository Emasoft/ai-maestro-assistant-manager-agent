# Decision Trees and Routing Matrices

## Table of Contents

- [Issue Operations Decision Tree](#issue-operations-decision-tree)
- [Pull Request Operations Decision Tree](#pull-request-operations-decision-tree)
- [Kanban/Projects Operations Decision Tree](#kanbanprojects-operations-decision-tree)
- [Release Operations Decision Tree](#release-operations-decision-tree)

## Issue Operations Decision Tree

```
┌─────────────────────────────────┐
│ Issue operation requested       │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ Does issue have team label?     │
│ If NO: determine team, apply    │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ Is this linked to a design doc? │
└───────────────┬─────────────────┘
        ┌───────┴───────┐
        │ YES           │ NO
        ▼               ▼
┌───────────────┐  ┌─────────────────────┐
│ What action?  │  │ Is this a module    │
└───────┬───────┘  │ implementation task?│
        │          └──────────┬──────────┘
    ┌───┴───┐          ┌──────┴───────┐
    │       │          │ YES          │ NO
    ▼       ▼          ▼              ▼
CREATE   UPDATE   ┌──────────┐   ┌──────────┐
LINK     LINK     │ Route to │   │ Route to │
    │       │     │ AMOA      │   │ AMIA      │
    │       │     └──────────┘   └──────────┘
    ▼       ▼
┌──────────────┐
│ Route to AMAA │
│ with design  │
│ UUID         │
└──────────────┘
        │
        ▼
┌──────────────────────────┐
│ Sync new issue/status    │
│ to tasks-{teamId}.json   │
└──────────────────────────┘
```

### Issue Routing Matrix

| Scenario | Route To | Handoff Content | Team Label |
|----------|----------|-----------------|------------|
| Create bug report | AMIA | Issue template, reproduction steps | Required: `team:{teamId}` |
| Create feature request | AMIA | Issue template, requirements | Required: `team:{teamId}` |
| Create issue FROM design | AMAA | Design UUID, section reference | Inherit from design team |
| Link existing issue to design | AMAA | Issue number, design UUID | Verify team match |
| Update issue labels/status | AMIA | Issue number, changes | Verify team ownership |
| Close issue with verification | AMIA | Issue number, verification results | Sync `complete` to task file (then the `release-via` path, if any) |
| Create module task issue | AMOA | Module UUID, task details | Inherit from module team |
| Track implementation progress | AMOA | Issue number, module UUID | Sync status to task file |

## Pull Request Operations Decision Tree

```
┌─────────────────────────────────┐
│ PR operation requested          │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ What operation type?            │
└───────────────┬─────────────────┘
                │
    ┌───────────┼───────────┬────────────┐
    │           │           │            │
    ▼           ▼           ▼            ▼
 CREATE      REVIEW      MERGE       UPDATE
    │           │           │            │
    ▼           ▼           ▼            ▼
┌────────┐ ┌────────┐ ┌────────┐  ┌────────┐
│ Route  │ │ Route  │ │ Route  │  │ Route  │
│ to AMIA │ │ to AMIA │ │ to AMIA │  │ to AMIA │
└────────┘ └────────┘ └────────┘  └────────┘
    │           │           │            │
    └───────────┴───────────┴────────────┘
                │
                ▼
    ┌────────────────────────────────┐
    │ On merge: sync linked issues   │
    │ to `ai_review` or `complete`   │
    └────────────────────────────────┘
```

**Note**: All PR operations go to AMIA. AMIA may consult with AMAA for design validation or AMOA for implementation verification. PR merges trigger task status sync for linked issues.

### PR Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Create PR | AMIA | Branch, description, linked issues, team label | Linked issues to `testing` |
| Review PR | AMIA | PR number, review criteria | Linked issues to `ai_review` (or `human_review` when escalated) |
| Request changes | AMIA | PR number, requested changes | Linked issues back to `dev` |
| Approve PR | AMIA | PR number, approval notes | None |
| Merge PR | AMIA | PR number, merge strategy | Linked issues to `complete` |
| Close PR without merge | AMIA | PR number, reason | Linked issues back to `dev` |

## Kanban/Projects Operations Decision Tree

```
┌─────────────────────────────────┐
│ Kanban/Project operation        │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ What operation type?            │
└───────────────┬─────────────────┘
                │
    ┌───────────┼───────────┬───────────────┐
    │           │           │               │
    ▼           ▼           ▼               ▼
  SYNC      CREATE       MOVE           STATUS
  BOARD      ITEM        CARD           QUERY
    │           │           │               │
    ▼           ▼           ▼               ▼
┌────────┐ ┌─────────────────────┐   ┌──────────┐
│ Route  │ │ Is item a design    │   │ Handle   │
│ to AMIA │ │ or module?          │   │ locally  │
│ + sync │ └──────────┬──────────┘   │ (AMAMA)  │
│ task   │            │              └──────────┘
│ file   │    ┌───────┴───────┐
└────────┘    │ DESIGN        │ MODULE
              ▼               ▼
        ┌──────────┐   ┌──────────┐
        │ Route to │   │ Route to │
        │ AMAA      │   │ AMOA      │
        │ + sync   │   │ + sync   │
        │ task file│   │ task file│
        └──────────┘   └──────────┘
```

**All card movements MUST be synced to `~/.aimaestro/teams/tasks-{teamId}.json`.**

### Kanban Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Sync board with GitHub | AMIA | Project ID, sync scope | Full reconciliation with task file |
| Create design card | AMAA | Design UUID, card details, team label | Create task entry as `backburner` |
| Create module card | AMOA | Module UUID, card details, team label | Create task entry as `backburner` |
| Move card (non-specific) | AMIA | Card ID, target column, team label | Update task column |
| Move design card | AMAA | Card ID, design context | Update task column |
| Move module card | AMOA | Card ID, module context | Update task column |
| Query board status | AMAMA (local) | Project ID | Read from task file for fast response |
| Archive terminal items | AMIA | Project ID, archive criteria | Remove `published` / `live` / `superseded` tasks older than threshold. NEVER archive `failed` — it stays on the board and is retried |

### Kanban-to-Task Sync Procedure

When a Kanban card moves:

1. Identify the GitHub issue linked to the card
2. Determine the team from the issue's `team:{teamId}` label
3. Map the target Kanban column to one of the ratified 17 AI Maestro columns
4. Update `~/.aimaestro/teams/tasks-{teamId}.json`:
   - Set `column` to the new AI Maestro column
   - When moving to `blocked`, first stash the current column into `preBlockColumn`; when
     unblocking, restore from it (never guess the column to return to)
   - Append to `columnHistory`
   - Update `updatedAt` timestamp
5. If the task does not exist in the file, create it
6. Validate the column transition is legal (see the Task Column Model in [task-system-sync.md](task-system-sync.md))

## Release Operations Decision Tree

```
┌─────────────────────────────────┐
│ Release operation requested     │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ All operations go to AMIA        │
│ (Integrator owns releases)      │
└───────────────┬─────────────────┘
                │
                ▼
          ┌──────────┐
          │ Route to │
          │ AMIA      │
          └──────────┘
                │
                ▼
    ┌────────────────────────────┐
    │ On release: sync all       │
    │ included issues along their│
    │ `release-via` path —       │
    │ `published` (tools) or     │
    │ `live` (services)          │
    └────────────────────────────┘
```

### Release Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Create release | AMIA | Version, changelog, assets | Move included issues `complete` -> `publish` (tools) or `complete` -> `deploy` (services), per `release-via` |
| Draft release notes | AMIA | Version, commit range | None |
| Tag version | AMIA | Tag name, commit SHA | None |
| Publish release | AMIA | Release ID, publish settings | Mark included issues `published` (tools) or `live` (services), per `release-via` |
| Update release | AMIA | Release ID, changes | None |
