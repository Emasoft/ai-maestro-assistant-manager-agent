---
trdd-id: DE33HN3J
title: Align AMAMA to the ai-maestro harness approval-record contract so the MANAGER can work in the harness
column: dev
created: 2026-07-16T10:22:25+0200
updated: 2026-07-16T10:22:25+0200
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
implementation-commits: []
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
- **NEXT ACTION:** publish AMAMA (`uv run scripts/publish.py --minor`), then answer
  ai-maestro#65 B1–B5 when the hub replies.
- **BLOCKED ON (ai-maestro#65):** B1 the self-contradicting authority ladder (`user` vs
  `maestro`); B2 the skill-name mismatch; B5 GATE 0 — these overlays live ONLY on the
  unmerged `governance-rules` branch, so the contract is not on any provisioned host yet.
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
