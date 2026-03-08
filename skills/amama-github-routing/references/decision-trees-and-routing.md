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
| Close issue with verification | AMIA | Issue number, verification results | Sync `completed` to task file |
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
    │ to `review` or `completed`     │
    └────────────────────────────────┘
```

**Note**: All PR operations go to AMIA. AMIA may consult with AMAA for design validation or AMOA for implementation verification. PR merges trigger task status sync for linked issues.

### PR Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Create PR | AMIA | Branch, description, linked issues, team label | Linked issues to `review` |
| Review PR | AMIA | PR number, review criteria | None |
| Request changes | AMIA | PR number, requested changes | Linked issues back to `in_progress` |
| Approve PR | AMIA | PR number, approval notes | None |
| Merge PR | AMIA | PR number, merge strategy | Linked issues to `completed` |
| Close PR without merge | AMIA | PR number, reason | Linked issues back to `in_progress` |

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
| Create design card | AMAA | Design UUID, card details, team label | Create task entry as `backlog` |
| Create module card | AMOA | Module UUID, card details, team label | Create task entry as `backlog` |
| Move card (non-specific) | AMIA | Card ID, target column, team label | Update task status |
| Move design card | AMAA | Card ID, design context | Update task status |
| Move module card | AMOA | Card ID, module context | Update task status |
| Query board status | AMAMA (local) | Project ID | Read from task file for fast response |
| Archive completed items | AMIA | Project ID, archive criteria | Remove `completed` tasks older than threshold |

### Kanban-to-Task Sync Procedure

When a Kanban card moves:

1. Identify the GitHub issue linked to the card
2. Determine the team from the issue's `team:{teamId}` label
3. Map the target Kanban column to an AI Maestro status
4. Update `~/.aimaestro/teams/tasks-{teamId}.json`:
   - Set `status` to the new AI Maestro status
   - Append to `statusHistory`
   - Update `updatedAt` timestamp
5. If the task does not exist in the file, create it
6. Validate the status transition is legal (see Status Model in [task-system-sync.md](task-system-sync.md))

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
    │ included issues to         │
    │ `completed` in task files  │
    └────────────────────────────┘
```

### Release Routing Matrix

| Operation | Route To | Handoff Content | Task Sync |
|-----------|----------|-----------------|-----------|
| Create release | AMIA | Version, changelog, assets | Mark included issues `completed` |
| Draft release notes | AMIA | Version, commit range | None |
| Tag version | AMIA | Tag name, commit SHA | None |
| Publish release | AMIA | Release ID, publish settings | Mark included issues `completed` |
| Update release | AMIA | Release ID, changes | None |
