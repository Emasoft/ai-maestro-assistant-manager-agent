---
trdd-id: DE33HN3J
title: Align AMAMA to the ai-maestro harness approval-record contract so the MANAGER can work in the harness
column: blocked
pre-block-column: dev
created: 2026-07-16T10:22:25+0200
updated: 2026-07-16T10:37:00+0200
current-owner: amama-manager
task-type: bugfix
scope: project
release-via: publish
mandated-by: user
approved: true
approval-judge: user
approval-datetime: 2026-07-16T10:22:25+0200
min-approval-requirement: user
relevant-rules: [1]
implementation-commits: [7edae93, 3ce3ae9, 49894b3]
---

# Align AMAMA to the ai-maestro harness approval-record contract

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-07-16

- **Mandate (USER, 2026-07-16):** "align with the ai-maestro claude (using issues opened on
  github), since some changes were made to the ai-maestro harness and governance rules. you
  must update the plugin so that the MANAGER must be able to work in the ai-maestro harness
  without issues." A mandate is approved the moment it is written.
- **DONE:** the three confirmed defects (A1–A3 below) are fixed in
  `scripts/amama_proposal_approvals.py`, with 9 new real regression tests. Full suite
  134 passed, ruff clean. Falsified against the pre-fix code: it has no resolver, never
  writes `approved:`, and renders a current-contract TRDD as `—`.
- **PUBLISHED:** v2.14.0 (2026-07-16). Both tags peel to the same commit `49894b3`
  (`v2.14.0` + `ai-maestro-assistant-manager-agent--v2.14.0`); GitHub release live.
- **NEXT ACTION:** none of mine — WAIT for the hub on ai-maestro#66, then fold the
  answers in and propagate the settled parts to the role-plugins as ONE coordinated wave.
- **BLOCKED ON (ai-maestro#66 — direction; #65 — rulings):** the MAESTRO warned
  (2026-07-16) that the fork is mid-flight and much is unimplemented, so this alignment is
  PROVISIONAL by construction. #66 asks the load-bearing question: the hub's own #59 says
  we ship TWO contradictory TRDD-transition mechanisms — (A) the `aimaestro-trdd.sh` +
  `$AID_AUTH` gate vs (B) direct file manipulation — that **B is right**, and that the §D4
  watchdog the ladder depends on **does not exist** (so the tiers are decorative today).
  **This TRDD implemented B's shape.** If B is ratified we are aligned; if the approval
  record moves into a signed token (#27/#46/#47), the frontmatter record is transitional
  and must be rebuilt. Do NOT harden further until #66 Q1/Q3 are answered.
- **DO NOT BUILD YET** (pending #66 Q5): `routed-via:`, the `amp-kanban-*.sh` board
  surface, `project-id` cross-project scoping.
- **SUPERSEDED — do NOT carry forward:** the belief that `main` has no governance layer.
  `main` DID receive governance-rules v0.28.0 on 2026-07-02 (`a6da60b`, PR #52). The
  unmerged delta is 07-02→07-14 only.

## Why

The harness overlay `rules/aimaestro/aimaestro-trdd-approval.md` (branch `governance-rules`)
names **AMAMA's own surface** as the MANAGER's batch listing/decision tool. AMAMA was built
against the pre-2026-07-10 contract and had never been migrated, so the tool the harness
points the MANAGER at was non-compliant in three ways.

## The three defects (all verified by reading the code, not grep)

- **A1 — blind to `min-approval-requirement:`.** `read_proposal` resolved only the deprecated
  `approval-tier`. The overlay states a file carries EXACTLY ONE of the two, so every TRDD
  authored under the current contract rendered as `—`: the MANAGER could not see who was
  required to approve it.
- **A2 — the approval record was never written.** `apply_move` wrote only `column:` +
  `updated:` + a prose `## Approval log` bullet — precisely the state the overlay was written
  to replace ("without them an `## Approval log` line is the only evidence — prose, not
  greppable"). The denormalized invariant was dead for every TRDD AMAMA decided, and
  `grep -l "^approved: rejected"` returned nothing.
- **A3 — the log bullet used the retired vocabulary** (`(tier N)` instead of
  `(min-approval-requirement: <title>)`).

## The fix

- `read_requirement()` resolves the canonical field first and decodes `approval-tier` ONLY as
  a legacy fallback — reading just one of the two blinds the MANAGER to the other contract.
- `write_approval_record()` writes `approved:` / `approval-judge:` / `approval-datetime:` and
  migrates the file onto `min-approval-requirement:` **on touch**, dropping `approval-tier`
  via the new `drop_frontmatter_field()` so the file ends up carrying exactly one field.
- A supersede records `approved: false` and **strips** any judge — nobody declined it, a newer
  TRDD overtook it; recording a judge would attribute a decision to someone who never made one.
- `completed`/`cancelled` archives deliberately do NOT touch the record, so archiving cannot
  overwrite the ORIGINAL approver with whoever archived it.
- `apply_move` now takes ONE `stamp` for the whole mutation (it previously called `iso_now()`
  twice, so `updated:` and the log bullet could disagree).
- `maestro` folds onto `user` on read pending the ai-maestro#65 B1 ruling, so no TRDD is lost
  whichever spelling the hub ratifies.

## Coordination

ai-maestro#65 carries the A1–A3 report (informational) and the five rulings needed from the
hub: B1 ladder contradiction, B2 skill name, B3 log-line format, B4 `routed-via:`, B5 GATE 0.

## Notes

`relevant-rules: [1]` — PRRD G1.1 (GitHub authorship self-identification) governs the issue
posts made for this task.
