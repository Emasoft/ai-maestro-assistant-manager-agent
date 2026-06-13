---
name: amama-proposal-approvals
description: "Batch-review the TRDD proposals in design/proposals/ and approve, refuse, or cancel them fast. Use when the USER/MANAGER says 'list proposals', 'review proposals', 'show pending TRDDs', or replies with 'approved: 4,6,22', 'refused: 7,8', or asks to cancel/archive a TRDD."
allowed-tools: "Bash(python3:*), Bash(git:*), Read, Grep, Glob"
metadata:
  author: "Emasoft"
---

## Overview

The user-facing fast path for deciding proposals (`column: proposal`) in
`design/proposals/`. It lists them numbered, then lets the approver act in
one short line. Canonical rules: `~/.claude/rules/trdd-approval-tiers.md`
Part A (Creation / Promotion / Refusal / Cancellation / Batch-approval).

This skill is the **proposal-folder** approval surface. It is distinct from:
- `amama-approval-workflows` — GovernanceRequest API (teams / agent lifecycle).
- `amama-prrd-trdd-kanban` — the per-`column:` v2 pipeline transitions.

All three coexist; this one only moves files between
`design/proposals/` ↔ `design/tasks/` / `refused/` / `archived/`.

## Prerequisites

- `design/proposals/` exists in the target project (the script resolves the
  project via `CLAUDE_PROJECT_DIR` → git top → cwd).
- Git identity set as Emasoft for the commit step (per global rules).
- Script: `$CLAUDE_PLUGIN_ROOT/scripts/amama_proposal_approvals.py` (stdlib only).

## Instructions

Let `PPA="$CLAUDE_PLUGIN_ROOT/scripts/amama_proposal_approvals.py"`.

1. **List** (triggers: "list proposals", "review proposals", "show pending
   TRDDs"). Run and show the table verbatim:
   ```bash
   python3 "$PPA" list
   ```
   This also writes the number→`trdd-id` manifest the next step resolves
   against. Always list before deciding if the listing is stale or absent.

2. **Decide** (triggers: the user replies `approved: …` and/or `refused: …`).
   Extract the numbers and run ONE command:
   ```bash
   # approve-only: approve listed, REST STAY PENDING
   python3 "$PPA" decide --approved "4,6,22"
   # refuse-only: refuse listed, APPROVE EVERY OTHER listed proposal (complement)
   python3 "$PPA" decide --refused "7,8"
   # both: explicit lists, rest stay PENDING (no complement)
   python3 "$PPA" decide --approved "1,2" --refused "9"
   ```
   For the bulk `refused:` form, run with `--dry-run` first and show the user
   exactly which proposals will be approved-by-complement before executing.
   Pass `--approver MANAGER` (or `USER`) to record who decided.

3. **Archive** (triggers: "cancel / complete / supersede / withdraw / archive a
   TRDD"). Moves a proposal OR an already-planned task to `design/archived/`
   in a terminal-DONE state, by id:
   ```bash
   python3 "$PPA" archive --state completed  --id dd9a3026   # finished/shipped
   python3 "$PPA" archive --state cancelled  --id dd9a3026   # withdrawn (alias: `cancel`)
   python3 "$PPA" archive --state superseded --id dd9a3026   # replaced by other TRDD(s)
   ```
   **Never archive a `failed` TRDD.** `failed` is retryable — it stays OPEN in
   `design/tasks/` and is retried until it succeeds. Giving up on a failed
   TRDD is an explicit `archive --state cancelled`.

4. **Commit the moves.** The script performs `git mv` + frontmatter edits but
   does NOT commit. Review `git status`, then commit the specific moved files
   (never `git add -A`). A design/ change should then be synced to the repo
   per the design-folder-sync rule.

## Decision semantics (the asymmetry — say it back to the user)

| Reply | Listed numbers | Every OTHER pending proposal |
|---|---|---|
| `approved: …` | → approved (`design/tasks/`) | stay **PENDING** |
| `refused: …` | → refused (`refused/`) | **approved** (complement) |
| both lines | approved / refused as listed | stay **PENDING** |

`approved:` is the safe explicit verb (omission never refuses). `refused:`
is the bulk verb (use only after reviewing the whole list — it approves the
rest). Numbers resolve against the most recent `list` manifest by stable
`trdd-id`; an already-decided number is skipped and reported, never
mis-targeted.

## Output

| Outcome | Action |
|---|---|
| Approved | `column: planned`, `## Approval log` line, `git mv` → `design/tasks/` |
| Refused | `column: refused`, log line, `git mv` → `design/refused/` |
| Archived | `column: completed`/`cancelled`/`superseded`, log line, `git mv` → `design/archived/` |
| Skipped | number already decided / not pending — reported, no change |
| Unknown | number not in the manifest — reported, no change |

A timestamped decision report is written under
`reports/proposal-approvals/` (gitignored).

## Error Handling

| Error | Fix |
|---|---|
| "no proposal listing manifest" | run `list` first |
| number in BOTH approved and refused | the script refuses (ValueError); fix the lists |
| "destination already exists" | a same-named file is already in the target folder; investigate |
| `git mv` not possible (untracked file) | the script falls back to a filesystem move automatically |

## Examples

```text
User: list proposals
→ python3 "$PPA" list   (show the numbered table)

User: approved: 1,3,5
→ python3 "$PPA" decide --approved "1,3,5" --approver USER

User: refused: 2
→ python3 "$PPA" decide --refused "2" --dry-run   (show plan: #2 refused, rest approved)
→ python3 "$PPA" decide --refused "2" --approver USER

User: cancel the orchestrator proposal
→ python3 "$PPA" cancel --id dd9a3026
```

## Scope

ONLY moves proposal/task TRDD files between the four design/ folders with the
correct `column:` + log line. Does NOT author proposals (that is the
Creation procedure / `amama-prrd-trdd-kanban`), does NOT touch the PRRD, and
does NOT push to GitHub (that is the design-folder-sync layer).
