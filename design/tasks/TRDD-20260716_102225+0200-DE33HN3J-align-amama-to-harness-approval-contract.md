---
trdd-id: DE33HN3J
title: Align AMAMA to the ai-maestro harness approval-record contract so the MANAGER can work in the harness
column: dev
created: 2026-07-16T10:22:25+0200
updated: 2026-07-16T18:05:00+0200
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
implementation-commits: [7edae93, 3ce3ae9, 49894b3, a72374b]
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
- **DONE (`a72374b`):** increments 1–2. The `maestro → user` alias now cites R41.4 +
  `7862b191` instead of hedging on B1; two tests pin that `approval-token:` / `routed-via:`
  survive a decision verbatim and that their ABSENCE never gates one. Falsified both by
  injecting the YAML-round-trip refactor they guard against. 137/137, ruff clean.
- **Q8 RULED (a) — PRESERVE. My implementation is RATIFIED (hub, 2026-07-16).** The token
  attests an EVENT ("this approval was authentically issued"); `approved:` is current
  STATE — different questions, so no contradiction to resolve by destroying the token.
  Keep preserving it on supersede AND on `completed`/`cancelled`; keep STRIPPING
  `approval-judge:`/`approval-datetime:` on supersede (preserves `judge present ⟺ approved
  ∈ {true, rejected}`; the token carries the history the stripped prose no longer does).
  My recoverability argument is on record as the clincher: **you cannot re-mint a
  host-signed artifact, so preserve-now/strip-later costs nothing while strip-now destroys
  signed evidence for good.** Hub refinement: `verify` will report the CURRENT COLUMN
  alongside the authenticity verdict, so a superseded-but-once-approved card reads
  "authentic: yes; column: superseded" and no caller reconciles the two. No host verb
  needed (only a future flip to (b) would need one — not happening).
- **Q9 CONFIRMED — and it is the HUB'S to fix. DO NOT fork+PR it (hub, explicit).** "The
  cross-project rule keeps you out of my tree; it does not make my bug yours." They
  independently read the same files and confirmed every finding, accepted the 3-instance
  root-cause naming, and will do the `(tier ` sweep across the write surfaces rather than
  three one-offs. Their fix folds into the #69 package (sibling of their TRDD-RIFM4UXN):
  `promoteTrdd`/`refuseTrdd` take `requirement: string` + emit the B3 line, decoding legacy
  `tier?: number` through the `trdd-authz.ts` map; CLI gains `--requirement <title>` as
  canonical with `--tier N` a decoded legacy alias; routes pass `requirement` through; plus
  server-side validation that the claimed requirement matches the caller's real AID-title
  ("the number/name the agent types is a claim to check, never a grant to trust").
- **INCREMENT 3 — the wait is now DEFINED, not open-ended.** Hub confirmed my degradation
  is the correct one (direct-file, B3-exact, `verify` honestly UNVERIFIED — "a truthful 'I
  cannot prove this' beats a token paired with a `(tier N)` bullet that lies about the
  vocabulary"). When the verb emits B3 they hand me the **frozen `# Usage:` line via
  `scripts/script-manifest.json` (#56)** and I flip to the verb against a CONFIRMED
  contract, verb-for-verb — no guessed flags. That manifest is the trigger to resume.
- **The #69 cross-reference PAID OFF (2026-07-16).** CORE's #69 item 2 asked the hub to
  "publish the name→number mapping … or widen to 0-4" — which would have given the RETIRED
  vocabulary enforcement teeth in the same window Q9 asks to remove it. I posted the B1
  ruling + Q9 evidence; **CORE retracted in full** ("my item 2 was wrong in the exact way
  you caught"), corrected its #29 needs-list, and is now fixing core#30 against THIS ruling
  (titles canonical, numbers decode-only, `orchestrator` un-numbered — its lack of a number
  IS the proof the numeric scheme cannot express the ladder) instead of the 0-4 scheme.
  Both changes now land as ONE contract.
- **Historical (superseded by the above):**
  Read on `governance-rules` before coding against it: `lib/trdd-store.ts:359,379,400`
  builds the log bullet as `` ` (tier ${opts.tier})` `` and contains **zero**
  `min-approval-requirement` in 463 lines. The whole write path speaks tier
  (`approve --tier N` → `POST {tier}` → `route.ts:67` → `tierStr`). So the verb #66 Q1 tells
  me to prefer emits **exactly the `(tier N)` bullet #65 B3 ruled against** — the A3 defect
  I just fixed. On the launch host I cannot have both the token and a B3-exact bullet:
  `--tier N` → `(tier 2)`; no `--tier` → `tierStr` is `''` and the clause vanishes entirely;
  no verb → B3-exact but UNVERIFIED. **Chose UNVERIFIED** (keep the direct-file path):
  `verify` truthfully saying "cannot prove this" beats a bullet that lies about the
  vocabulary.
- **The suggested probe does not decide this.** `aimaestro-trdd.sh verify` existing proves
  the TOKEN layer, not the vocabulary — on `governance-rules` `verify` exists AND the bullet
  is stale, so probing for `verify` returns "use the verb" and walks into `(tier N)`. Any
  probe I eventually write must test the **write vocabulary**, not the token layer.
- **Convergent validation (worth keeping):** `lib/trdd-authz.ts:41,70` is fully current and
  independently landed the SAME decode I did — ladder `none|orchestrator|chief-of-staff|
  manager|user`, `min-approval-requirement` first with `approval-tier` as legacy fallback,
  `0→none 1→chief-of-staff 2→manager 3→user` (the stricter rung for `1`). Two
  implementations converging from opposite ends is the strongest evidence the decode is right.
- **The root cause, named (3 instances):** the 2026-07-10 contract landed in the RULES; the
  surfaces that WRITE the record were never migrated. (1) AMAMA — fixed `7edae93`; (2) CORE
  `ai-maestro-plugin/rules/trdd-approval-tiers.md` — filed ai-maestro-plugin#30; (3) the
  hub's own store — ai-maestro#66 Q9. `7862b191` fixed the prose describing the contract
  while the code implementing it kept emitting the old form.
- **PROPAGATION WAVE SENT (2026-07-16 ~14:35).** The settled contract (§1 vocabulary, §2
  record invariants + B3 line, §3 token/routed-via tolerance, §4 mechanism/build-holds/
  capability-probe, §5 refusal protocol) posted as one canonical body + role-tailored notes
  to the six role-plugin governance threads: ORCH#25, COS#24, ARCH#24, PROG#25, AUTO#12,
  MAINT#29. CORE skipped (already converged via hub#69/#71); janitor/visual-communicator
  out of scope (not approval roles). Each comment states it is a live dialogue thread.
- **🔴 THE TWO-TREES FINDING (2026-07-16) — corrects the resume trigger below.** The hub and
  I were reading DIFFERENT TREES and both calling them `governance-rules`; we each wrote
  "verified this turn, not recalled" and were each honest about a different object. **Every
  sha the hub cited on 07-16 is 404 on the remote** — `7862b191` (the B1/B2 rule fix),
  `be37cfe9` (the `-s ours` merge), `20f5ba72` (`update --cos`), `7a20ca97` (the tier→title
  emit). **Pushed tip = `71df9353`, 2026-07-14** — unmoved for 2 days. Verified consequences
  at `?ref=governance-rules`: the rule file STILL has the L297 `maestro` ladder
  contradiction + the L127 `amama-proposal-approvals` stale name (the two things `7862b191`
  "fixed"); `lib/trdd-store.ts` still emits `${tierStr}` ×4 with `min-approval-requirement`
  ×0; `aimaestro-teams.sh` still has `reassign-cos --password P` MANDATORY and no
  self-assign ban. **CONTROL that makes this airtight:** `verify` IS on the pushed ref
  (`cmd_verify` `:208`, dispatch `:378`) — so the ref is readable and pushed work does
  appear; rows 1–2's absence is informative, not ambiguous.
- **THE THREE-STATE MODEL (now the fleet's canonical framing — CORE adopted it):**
  *on-branch+deployed* / *on-branch+undeployed* (`verify`) / *not-on-branch* (the two 404s).
  Collapsing the last two into "not landed" is how you re-ask for something that already
  exists — and how the hub's "one merge away" plan would land the merge with the fixes
  still missing. **Rows 1–2 need a `git push`, not a merge.**
- **NEXT ACTION: WAIT for the hub to PUSH `governance-rules` — THEN for
  `docs/SCRIPT-MANIFEST.md` + the frozen `# Usage:` line for the B3-emitting
  `approve`/`refuse` verbs.** The push is now the FIRST gate: the manifest lives on the very
  branch that is missing the fixes, so a manifest read today describes the 07-14 contract.
  **Do NOT flip increment 3 against any cited sha until it resolves on the remote
  (`gh api repos/Emasoft/ai-maestro/commits/<sha>` — test the EXIT CODE; `gh` prints its
  error JSON to stdout, so `[ -n "$out" ]` reads a 404 as present. I wrote exactly that bug
  while checking, and it printed ✅ for all six shas.)**
- **MY OWN ERROR, corrected (`47be2c6`):** I cited `7862b191` in shipped code AND to six
  role-plugin threads as landed fact, having never checked it existed. The RULING stands;
  only the citation was unverifiable. The correction changes behavior, not just a comment:
  because the rule fix is NOT live, `maestro` is still authorable today, so the alias is
  **load-bearing rather than legacy** — do not drop it when the rule text finally lands;
  files written while the drift was live outlive the fix.
- **Ball: the hub's alone.** Neither CORE nor I have push rights to `ai-maestro` (the hub
  explicitly refused my PR offer: "the cross-project rule keeps you out of my tree; it does
  not make my bug yours"). **One owner, one action.** If it stalls, the USER escalation is
  exactly that sentence — not a diffuse shared ball. CORE has closed its side (holding; will
  not run its installed==manifest pass until pushed + installed).
- **🔴 PROBABLE ROOT CAUSE of the two-days-unpushed tip (CORE-corroborated, AMAMA-confirmed):**
  the CPV-canonical `.githooks/pre-push` ("strict publish enforcement via PROCESS ANCESTRY.
  Auto-generated by scripts/publish.py") refuses every push not descended from `publish.py`,
  and `publish.py` won't run off the default branch → a feature-branch push is *impossible*,
  fails silently (exit code nobody re-reads), and `git log` shows the local commits → "looks
  landed". AMAMA carries the auto-generated form of this hook (proven). **The fleet has
  DIVERGED on hook management (CORE corrected me, 2026-07-16):** AMAMA = auto-generated
  (rewritten from `publish.py`'s template every publish); CORE = STATIC + sha256-pinned
  (TRDD-71a2239a; `publish.py` explicitly never rewrites it). So the strict compose is real in
  both, but "shared CPV canon" is the ORIGIN, not a uniform current state — my earlier
  "byte-same, plugin-local edits erased" was AMAMA's mechanism wrongly generalized to CORE.
  The hub's own hook (the **ai-maestro server** repo, distinct from CORE's plugin repo) is
  UNVERIFIABLE from outside (no committed `.githooks/pre-push` at `?ref=governance-rules`) —
  **only the hub's `git push origin governance-rules` STDERR settles whether this is the cause.**
- **FIX ROUTED (2026-07-16): `Emasoft/claude-plugins-validation#169`** — the change lands in
  the CPV `publish.py` inline template as the CANONICAL source. Propagation is per-style (CORE's
  correction): auto-generating plugins (AMAMA) inherit on next publish; static-pinned plugins
  (CORE) bump their `.sha256` pin to track. So the template fix is necessary but NOT sufficient
  fleet-wide — the CPV CHANGELOG must tell static adopters to bump (added as a #169 context
  comment). CORE re-scoped `TRDD-8ZVAPMSQ` to the same endorsed shape.
  Endorsed shape: allow non-default-branch pushes AFTER the secret scan passes; keep
  publish.py-ancestry mandatory for `main` + all tags (baseline rulesets still gate `main`
  server-side). This is a security/release-gate change → above a MANAGER unilateral → surfaced
  to CPV + USER, not decided here. My ruling + routing pointer: ai-maestro-plugin#29
  (comments 4993945667, 4993996206).
- Everything else of mine is settled, sent, or blocked below.
- **OPEN ASKS: none.** Q8 ruled, Q9 confirmed + owned by the hub, B1–B5 closed. Do NOT
  re-ask; do NOT PR the hub's store.
- **The #43 round-trip** is separately blocked. The #43 round-trip
  (the one thing Q9 does not block) cannot run for TWO reasons, both verified 2026-07-16:
  1. **The server is DOWN.** `aimaestro-agent list` → "AI Maestro is not running at
     `http://localhost:23000`". Note the trap: `amp-kanban-list` *looks* alive (it printed
     three agents), but that list comes from LOCAL config — it fails on client-side identity
     resolution *before* any API call, so its output is NOT evidence the server is up. Do
     not read it as a health check.
  2. **No AMAMA agent workdir is registered.** All three registered agents are
     `ai-maestro@emasoft.aimaestro.local` (the hub's own). The CLI's `--agent` defaults to
     **the server's own repo**, so running `amp-kanban-create-task` without a registered
     MANAGER workdir would write test TRDDs into the HUB's tree — forbidden (cross-project
     rule: file an issue or fork+PR, never edit another project's tree). The round-trip
     therefore depends on task #36 (register/wake a managed AMAMA agent) first. Q7 said the
     server+CLI half is complete and frozen — true, and orthogonal: I still need an agent.
  Increment 3 resumes only on a Q9 ruling or a hub-side store fix.
- **OPEN ASKS (hub):** #66 **Q8** — does `approval-token:` survive a supersede? I preserve
  it (recoverable: I cannot re-mint a host-signed artifact, so stripping on a guess is the
  one error with no way back). #66 **Q9** — the store fix, or authorization to fork + PR it.
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
