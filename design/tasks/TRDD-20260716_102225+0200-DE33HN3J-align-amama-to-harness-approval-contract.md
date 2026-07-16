---
trdd-id: DE33HN3J
title: Align AMAMA to the ai-maestro harness approval-record contract so the MANAGER can work in the harness
column: dev
created: 2026-07-16T10:22:25+0200
updated: 2026-07-16T11:34:00+0200
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
- **UNBLOCKED 2026-07-16:** the hub answered #66 (all 7 direction questions) and #65 (all
  5 rulings). The verdict on the shipped work is **"the right shape — keep it"**. What
  remains is additive, not a rebuild.

### The hub's direction, as it binds AMAMA

| Ask | Ruling | What AMAMA owes |
|---|---|---|
| Q1 mechanism | **B ratified** — files are the SSOT for state; `7edae93` is the right shape | keep it; **prefer the script verb for approve/refuse WHEN the host offers it** (it mints the token), else direct-file |
| Q2 watchdog | **not ours** — the ladder's enforcer must not be a party the ladder authorizes (my argument, on record) | **zero implementation** |
| Q3 record vs token | **(a)** — frontmatter stays the durable, greppable record; the token *authenticates* it | harden toward (a); tolerate `approval-token:` on read |
| Q4 / B1 ladder | **`user`** canonical; `maestro` = deprecated READ-alias | my accept-both/normalize map is ratified — make it permanent |
| B3 log line | confirmed **verbatim** | already matches |
| B4 `routed-via:` | COS-authored; **read-only**, and nothing stamps it yet | read-tolerance only; **never gate on its presence** |
| Q5 `amp-kanban-*.sh` | **BUILD** — 6 verbs deployed + frozen (R23), 17 columns | the #43 round-trip |
| Q5 `project-id` | **HOLD** — `findtrdd.py` is not deployed; cross-project ids are rule prose only | nothing |
| Q5 R43–R48 / ASSISTANT | **DO NOT build** (my #28) | nothing |
| Q6 / B5 SSOT | `governance-rules` is canonical; `main` is stale for governance; **merge NOT soon** (USER: off the active list — launching the server comes first) | **gate new behavior on a CAPABILITY probe, not a version** |

- **The token layer (new since my audit; shipped hub-side 2026-07-14, `d7531e53` /
  TRDD-K2WJH7RF):** `aimaestro-trdd.sh approve` mints a host-signed portfolio token pinned
  to the card id, recorded as `approval-token:`; `aimaestro-trdd.sh verify <id>` answers
  **from the token, never from the prose** — because `approval-judge:` and the log bullet
  are exactly what a forger rewrites. The write verbs are **correctness wrappers + the
  minting surface, NOT an authorization boundary** (a gate you can walk around with `Edit`
  is a suggestion with extra steps). Walking around them stays legal; the cost is that the
  approval reports **UNVERIFIED**. `OPERATIONS_REQUIRING_TOKEN` is OFF deliberately.
- **THIS host is PRE-token (verified, not assumed):** `~/.local/bin/aimaestro-trdd.sh` has
  **no `verify` verb** and its `approve` still takes `--tier N`. So the capability probe
  returns false here today — which is precisely why the probe, not a version check, is the
  right gate: the launch host runs the `governance-rules` working tree directly (pm2 from
  the checkout), so the contract IS live exactly where the fleet will run.
- **NEXT ACTION:** land the three additive increments (ratify the `maestro` alias with its
  ruling cite; add `approval-token:` + `routed-via:` read-tolerance; add the capability
  probe that prefers the token-minting verb), then run the #43 round-trip.
- **SUPERSEDED — do NOT carry forward:**
  - the belief that `main` has no governance layer. `main` DID receive governance-rules
    v0.28.0 on 2026-07-02 (`a6da60b`, PR #52), and `governance-rules` now **incorporates**
    that tip (merge `be37cfe9`, `-s ours`, tree-verified — it was the squash of this
    branch's own #52). The delta is one-directional; nothing on `main` is missing.
  - "the §D4 watchdog is missing, so the tiers are decorative, so AMAMA might have to
    build it" — Q2 closed that: it is neutral infrastructure (janitor idle-sweep or
    server-side), decided inside the watchdog build design. Not mine either way.
  - "`maestro` might be the top rung" — ruled `user`, and the drift was fixed hub-side in
    `7862b191`.

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
