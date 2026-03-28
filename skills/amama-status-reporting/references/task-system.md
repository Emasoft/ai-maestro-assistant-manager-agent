# AI Maestro Task System - Detailed Reference

<!-- TOC -->
- [Task Storage](#task-storage)
- [Task Statuses (Kanban)](#task-statuses-kanban)
<!-- /TOC -->

AI Maestro maintains its own task system, separate from GitHub Issues. Tasks are managed per-team.

## Task Storage

Tasks are stored in: `$AGENT_DIR/teams/tasks-{teamId}.json`

## Task Statuses (Kanban)

Tasks flow through exactly 5 statuses:

```
backlog -> pending -> in_progress -> review -> completed
```

| Status | Meaning |
|--------|---------|
| `backlog` | Acknowledged but not yet scheduled |
| `pending` | Scheduled, waiting to start |
| `in_progress` | Actively being worked on by an agent |
| `review` | Work done, awaiting review/validation |
| `completed` | Finished and verified |
