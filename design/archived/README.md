# `design/archived/` — once-approved TRDDs in a terminal-DONE state

This zone holds TRDDs that **were approved** (reached `design/tasks/`) and
later reached a terminal-DONE state. They are kept here (never deleted) as
the project's audit trail. Three terminal states live here:

| State | `column:` | When |
|---|---|---|
| **completed** | `completed` | the work finished / shipped (its release-via terminal reached) |
| **cancelled** | `cancelled` | the work was withdrawn — no longer wanted |
| **superseded** | `superseded` | replaced by other TRDD(s) (recorded in `superseded-by:`) |

A file lands here via the archival protocol (see
`~/.claude/rules/trdd-approval-tiers.md`):

1. frontmatter `column:` → `completed` | `cancelled` | `superseded`,
   bump `updated:` (set `superseded-by:` when superseding);
2. append to `## Approval log`:
   `- <ISO> — <COMPLETED|CANCELLED|SUPERSEDED> by <approver>. <reason>.`;
3. `git mv` the file here from wherever it lived.

**Never archive a `failed` TRDD.** `failed` is a *retryable* in-progress
state — it stays in `design/tasks/` and is retried until it succeeds.
Giving up on a failed TRDD is an explicit **cancel** (→ `cancelled` here).
Only never-approved proposals go to `design/refused/`; only once-approved
TRDDs land here.
