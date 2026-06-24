---
trdd-id: 282f61fe-c49b-4a35-8a85-4b9dbaeed15a
title: Overnight fleet-readiness campaign — MANAGER coordination + AMAMA in-control finish
column: dev
created: 2026-06-22T02:06:57+0200
updated: 2026-06-24T20:34:05+0200
current-owner: amama
assignee: amama
priority: 0
severity: HIGH
effort: XL
task-type: infra
labels: [fleet, coordination, overnight]
parent-trdd: null
relevant-rules: []
release-via: publish
test-requirements: [unit, lint, typecheck]
---

# Overnight fleet-readiness campaign

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-06-22T02:06

**↻ 2026-06-24T20:34 — quiet-hold re-verification (autonomous tick; nothing AMAMA-actionable).**
Re-checked each track INDEPENDENTLY (per the "one blocker ≠ all blocked" correction), not assumed:
AMAMA CI green on v2.12.11 (`baebd60`); no new inbound on tracked issues #21/#22/#42/#49 (latest
comment on each is AMAMA's OWN, confirmed via the G1.1 line); the upstream blockers #37 (R41+
decoupling+memory), #47 (APPROVAL/MANDATE), #42/#49 (core handshake) are all still OPEN →
peer/USER-gated. Decouple
residuals RE-VERIFIED still blocked: deployed `~/.local/bin/aimaestro-teams.sh` has NO `tasks` verb
and no `presence` verb → ai-maestro `governance-rules` branch NOT yet merged+deployed, so
5fc2cb0a-A.5 + the presence/team-tasks `/api/` fallbacks stay USER-gated (recalled
[[amama-12-decoupling-residuals-blocked-on-verbs]] FIRST → avoided repeating the reverted premature
repoint; #36 closing does NOT unblock these, as the memo's lesson predicted). 4c388042 in-control
work DONE (C1 CRITICAL fixed `b04ab8a`; Bucket-B fail-fast complete; D routed CPV#146; E +15 tests);
remainder = C judgment-calls + L1 dead-`thresholds.py`, both USER-surfaced. axiom reload generation
handled (/reload-plugins ran). NET: AMAMA ready; quiet hold continues.

**✅ MILESTONE 2026-06-24 (evening) — FLEET HAS NO BLOCKING CI REDS.** The orchestrator Claude
replied on orch#22 (16:51) + I verify-ack'd: its canon migration is COMPLETE (CPV ref re-pinned
`@main`→`@v2.147.1`, published v1.9.3, Release green, `cpv-remote-validate --strict` → 0/0/0/0
VALID). VERIFIED via API: its `baseline-pr-and-checks` ruleset requires ONLY `validate`, and
Validate is GREEN; the jscpd `Lint` failure is a NON-REQUIRED job, legitimately deferred to the
orchestrator's TRDD-03DYGXJW (a risky 30-file dedup needing test coverage first — gate still
runs, not gamed). CORRECTION to my earlier framing: the orchestrator was NOT a blocking red —
the workflow-level "CI failure" badge is the non-required Lint job; all REQUIRED checks + the
release are green. So #44-for-orchestrator counts DONE. Net: every fleet plugin is
canon-migrated + required-green; remaining work is all peer/USER-gated (no CI blockers).

**✅ PUBLISHED 2026-06-24 — AMAMA v2.12.11 SHIPPED + ALL CI GREEN.** Release[v2.12.11] ✅,
CI[main] ✅, Notify-Marketplace ✅, Dependency-Graph ✅; origin/main == local, clean tree.
Now live: the title-assignment doc fix (was pointing at a non-existent verb), the reassign-cos
doc fix, and the publish.py CPV-pin (local gate == CI). The dry-run-FIRST caught + fixed an
MD004 NIT (hard-wrapped prose starting with a plus-marker poisons markdownlint's ul-style
inference, issue #113) before the push — guardrail recorded in commit a5ed941. publish.py
exit codes: 1-4 (CRITICAL/MAJOR/MINOR/NIT) all block under --strict, so even a lone NIT fails
the gate — always dry-run before a real publish.

**✅ UPDATE 2026-06-24 (evening) — orchestrator @main FIXED by its Claude; new red diagnosed
and the #44 tally re-verified.**
- **orchestrator: @main re-pin LANDED** — its Claude re-pinned CPV `@main`→`@v2.147.1` in BOTH
  ci.yml+release.yml; **v1.9.3 PUBLISHED**, CPV gate green. The remaining CI-on-main red is a
  **DIFFERENT** job: Mega-Linter `COPYPASTE_JSCPD` = **9.86% dup > 5% threshold** (whole-repo
  scan of the split error-handling skill references). Diagnosed on **orch#22**: its
  `.mega-linter.yml` is byte-equivalent to AMAMA's (NOT a config gap — genuine doc dup); gave
  exemplar-grounded options (a=dedupe / b=`--ignore '**/references/**'` / c=NOT raise threshold).
  Also flagged its Release-v1.9.3 run hung ~2h (`28109731021` in_progress). **This is THEIRS to
  apply (Method-1).**
- **#44 tally re-verified (read-only):** the 4 previously-"remaining" plugins now show GREEN
  latest CI — core `v2.7.14`, integrator `v1.3.7`, janitor `v0.18.2`, amvcp `v1.4.0`. Their
  per-plugin #44 trackers still need a close-confirm, but CI-wise they're green. Net fleet red
  = **orchestrator's jscpd ONLY** (non-release-blocking; v1.9.3 is live).
- **Derived AMAMA doc fixes shipped (commit 127e6be):** title-assignment privilege row corrected
  (deployed `cmd_update` has NO title field → governance request→approve→transfer flow) +
  reassign-cos "not-deployed" residual removed. See the (later) entry below for the #49 decision.
- **Minor backlog (fold into #14, gated on #37):** AMAMA bundles NO GOVERNANCE-RULES mirror
  (good — relies on canonical), but cites rules version **v4.0.1** in `agents/…-main-agent.md:115`
  and `tests/scenarios/governance-scenarios.md:4`; #49 confirms current is **v4.0.2** (+R38.2
  user↔user-forbidden, +R39.7 ASSISTANT task-inheritance). Content already reflects R39.7;
  refresh the citation to v4.0.2 + verify R38.2 wording against the canonical text during the
  #14 propagation wave — NOT a standalone churn (content is correct; only the version# is stale).

**✅ UPDATE 2026-06-24 (later) — server #49 ground-truth received + MANAGER decisions
posted (#49 + cross-link #42).** The ai-maestro server Claude delivered point-by-point
ground truth on #49 (02:22Z) and explicitly flagged the title-assign-verb decision FOR
MANAGER. Decisions made + posted:
- **Governance ceiling = R40 (GOVERNANCE-RULES.md v4.0.2).** No rule beyond R40; AMAMA's
  R26–R40 mirror current at the number level. Sub-rule refinements to bundle if shipping
  rule TEXT: 4.0.1 (R38.1, R39.4, R39.6) + 4.0.2 (R38.2, R39.7). Still-UNLANDED governance
  additions = #37 only (frozen-CLI decoupling rule + memory-adoption rule, next free
  numbers R41+). Everything else is refinement, not a new number.
- **MANAGER-title verb — DECIDED: do NOT mint a new frozen verb.** Route MANAGER-title
  through the existing auditable `aimaestro-governance.sh request|approve|transfer`
  (title-granting belongs in the request/approve audit trail; a one-shot `assign-title`
  would set titles OUTSIDE the audit record = WEAKER governance + frozen-surface bloat for
  zero capability gain). COS-title → the now-built `aimaestro-teams.sh reassign-cos
  <teamId> <agentUUID> --password <pw>`. → **core#11/#42 fully unblocked today** (both
  `/api/` title residuals now have a frozen-CLI target). Tier-3 alternative (a dedicated
  AID-only verb for ergonomics) explicitly DEFERRED to USER (#36 items 1+7) — not required.
- **#45 verbs:** `presence` ✅ + `reassign-cos` ✅ landed; `team-tasks` + `governance-status`
  still pending under #45 (neither on core#11's critical path). New server API surfaces
  noted: `commandKey` allowlist on `PATCH /api/agents/[id]/session` (injection-proof literal
  slash-commands; matches the janitor heartbeat's reload/compact/janitor-* markers),
  `notificationType` gaining `rate_limited`+`api_error` (StopFailure classification),
  `isMarketplaceSupported(client)` graceful-degrade primitive.
- **Derived AMAMA doc fixes from the #49 ground-truth (verified vs deployed source):**
  (a) `creating-amcos-instance.md` — removed the stale `DECOUPLE-BLOCKED reassign-cos not
  yet deployed` residual → the verb IS deployed (`aimaestro-teams.sh reassign-cos`).
  (b) `agents/…-main-agent.md` privilege table — the "Change agent titles via
  `aimaestro-agent.sh update governanceTitle`" row was **factually wrong**: read the
  deployed `agent-commands.sh::cmd_update` — it accepts ONLY task/model/args/tags, has
  NO title field. Corrected to the governance request→approve→transfer flow + `reassign-cos`
  (TITLE is MAESTRO-sudo-only, R39.4). Commit pending this session.

**✅ UPDATE 2026-06-24 — orchestrator red-CI ROOT-CAUSED (was passively "monitoring"
it for ~a day; USER called that out: in /go-on-yourself there is no user gate).**
The orchestrator's `v1.9.2` Release CI is red NOT from a plugin finding — its
`ci.yml`+`release.yml` pin the CPV gate to `@main`, and **CPV removed its `main`
branch** (default is now `master`), so `uvx --from git+…claude-plugins-validation@main`
fails to resolve (`couldn't find remote ref refs/heads/main`); `uv` exits 1 and the
workflow mis-maps exit 1 → "CRITICAL findings". Verified by local repro + run 27940567560.
**Fleet blast radius (audited all 10 role plugins' workflows):** orchestrator is the
ONLY plugin still on `@main` (broken); AMAMA/autonomous/integrator pin `@v2.136.1`,
core/maintainer pin `@v2.137.0`/`@v2.143.0` (safe); 6 workflows are no-ref (float to
`master`, resolve now but unpinned). **Actions (in-bounds, Method-1):** CPV heads-up
= claude-plugins-validation#153; turnkey fix on orchestrator#22 (`@main`→`@v2.136.1`
in both workflows); fleet audit note on ai-maestro#44. **AMAMA in-yard fix:**
`publish.py` had an UNPINNED CPV ref → pinned to `@v2.136.1` via `CPV_VERSION`/`CPV_FROM`
constants (commit `31b9173`, local, not published). **ONE remaining gated step:** author
the orchestrator fork+PR (Method-2) — per the cross-project hard rule this needs an
explicit USER "author the PR" greenlight; offered on #22 + to USER. **In-bounds next
(no gate):** #24 residue A/B in AMAMA's OWN skills (G1.1 in skill templates;
memory-recall in individual skills) + #25 non-memory improvement proposals.

**USER directive (2026-06-22 ~02:00, going to sleep):** "be sure to solve all
issues, and to coordinate with the other claude via github issues. don't stop or
procrastinate. we need the fleet ready tomorrow morning." → standing autonomous
authorization for the night (RULE 1 satisfied). Pre-authorized: push/publish
AMAMA. NOT authorized: editing other plugins' repos (cross-project rule → issues
only).

**My levers (only two):**
1. AMAMA's own repo — I can edit + commit + publish (strict gate: `uv run python
   scripts/publish.py --patch`, dry-run first). v2.12.9 SHIPPED + CI green this session.
2. The rest of the fleet — coordinate via **GitHub issue comments** only. Other
   plugins' Claudes are idle overnight → my comments must be precise + actionable
   so they execute on wake.

**Constraints:** Opus-only (retry on rate-limit, never the LLM externalizer); no
parallel git/gh agents (serial); commit-often; never edit other repos; verify
before claiming; gh bodies via single-quoted heredoc (backtick hazard); every gh
post starts with the G1.1 self-id line.

### NEXT ACTION
Monitor-and-advance (campaign is peer/USER-gated). **#44 canon tally 6/10**
(autonomous·COS·programmer·architect·maintainer verified green + orchestrator
canon-green-but-head-RED). Compute each new DONE row LIVE — count #44 rows + check
the CURRENT head, not the row's claimed version. Remaining 4 #44 rows: core,
integrator, janitor, visual-communicator. Open MANAGER items: re-verify orchestrator
once its v1.9.2 CI is green (flagged orchestrator#24); the 2 #43 parity gaps are
server-routed (non-blocking). Still gated on the 3 USER actions (#35) + #46. No
AMAMA in-control code changes pending (C1/F7 await USER).

### DECISIONS RESOLVED (5 surfaced in TRDD-4c388042 bucket C) — 2026-06-22
- **C2 ✅ DONE** — approve_plan made honest (removed the GitHub-issues stub + dead
  `--skip-issues`/`--verbose` flags); committed f0cec77; 93 tests + ruff + mypy green.
- **C3 ✅ NO-OP** — `--password` is already correctly caveated everywhere as a
  USER/UI R32 residual AMAMA never supplies (verified across 6 skill refs).
- **C4 ✅ KEEP** — the 2 `model: opus` agent pins stay (USER: only Opus; guarantees
  it regardless of session model; the CPV CA-04 cache-warmth nit is non-blocking).
- **C1 ⏸ DEFER→USER** — retire the CozoDB `amama-session-memory` skill. It
  contradicts CLAUDE.md ("ships no per-plugin memory skills") BUT both agents +
  the main-agent body (L53/L544) actively depend on it for user-continuity →
  retire-vs-reconcile is a real architecture decision with live deps + product
  impact. RECOMMEND retire (continuity via janitor memory + presence-tracker), USER decides.
- **F7 ⏸ DEFER→USER** — gate the Stop-hook GitHub-issue block on `$AID_AUTH`. The
  hook ALREADY fail-softs when gh is unavailable (the common solo case), so the
  "wrongly blocked" risk is narrow; AID-gating is a low-stakes semantic refinement.
  RECOMMEND add the AID gate (fleet-only block), not urgent — USER call.

### MORNING USER-ACTIONS (verified — hand to USER)
1. **Redeploy the agent CLIs** (unblocks AMAMA #12 + makes the 4 #45 verbs + ~10
   drifted scripts live): `bash ~/ai-maestro/install-agent-cli.sh` (verified
   deployer, INSTALL_DIR=$HOME/.local/bin). 10/32 deployed aimaestro-*/amp-* are
   stale vs the governance-rules source.
2. After redeploy → ORCHESTRATOR runs the kanban round-trip (orchestrator#24) →
   MANAGER verifies + closes ai-maestro#40.
3. Nudge each idle plugin Claude to action its [fleet #44] + decoupling + gov-audit
   issue (idle agents don't poll — they need a USER nudge per memory).

### PROGRESS (2026-06-22 night)
- ✅ AMAMA v2.12.9 published + CI green (all 4 workflows).
- ✅ Kanban verb re-verify: corrected the architect's STALE #43 blocker — the
  create-task verb HAS the relationship flags (flag is `--parent`, NOT
  `--parent-task`), commit 6e1eeb57, DEPLOYED on-host (deployed==source byte-id).
  Posted #43 + nudged orchestrator#24.
- ✅ #45 verbs: verified BUILT in source (governance-rules) but NOT deployed
  (10/32 drift) → redeploy = morning user-action #1. AMAMA #12 residuals stay
  blocked-on-deploy (correctly NOT repointed to undeployed verbs). Posted #45.
- ✅ AMAMA v2.12.10 published + CI green — ships C2 (honest approve_plan: removed
  the GitHub-issues stub + dead --skip-issues/--verbose flags; doc rewritten).
- ✅ FLEET MORNING-BRIEF posted on ai-maestro#35 (per-plugin blocking-issue index
  plus the 3 USER actions). Memory + the source-vs-deployed lesson updated.
- ✅ 5 decisions: C2 done · C3 no-op · C4 keep · C1+F7 deferred→USER (recs recorded).

### PROGRESS (2026-06-23 — resume after restart)
- ✅ Heartbeat re-armed (session-only; durable→session-only downgrade, re-arms at SessionStart). Corrected the [[janitor-reload-not-agent-runnable]] memory: the janitor `janitor-reload-plugins` wrapper IS agent-runnable (keystroke injection).
- ✅ #44 canon tally re-counted LIVE = **6/10** (I'd nearly posted a stale 3/10): autonomous · COS · programmer v1.4.4 · architect v2.10.2 · maintainer v1.7.2 · orchestrator v1.9.1(canon). 5 verified green; posted the corrected tally on #44.
- ⚠️ orchestrator head **v1.9.2 RED CI** (Release+CI failed = post-canon regression) — flagged orchestrator#24 with run links; the canon row stands.
- ✅ Architect CONFIRMED #43 flags work (epic tree unblocked); verified its 2 parity gaps (`amp-kanban-create-task` no `--attachments`; `amp-kanban-list` no `--parent` filter) → acked + server-routed (non-blocking).
- ✅ Posted canon-**v2.143.0** fleet heads-up on #44: zizmor DROPPED by canon ci.yml (re-add workflow-security); the-skills-menu empty-catalog break (CPV#150, exclude); ci.yml/commitlint/publish.py defects (CPV#151); SBOM defer for post-hoc release.yml.
- ✅ Refreshed all 4 remaining #44 trackers (core#13, integrator#20, janitor#51, vc#6) with the v2.143.0 landmines + the 4 verified exemplars — each ready to run first-try (all 4 have green CI but have NOT run the canon upgrade; idle, not blocked).
- ✅ Server keystone re-checked: #40/#45/#46/#48/#49/#42/#47/#39 all OPEN + stalled (server Claude inactive 1-4 days). Critical path to "fleet ready" = the USER wakes the idle Claudes (server, the 4 plugins, orchestrator) — they don't poll; AMP unaddressable from MANAGER; PushNotify spent. Gave the USER the per-session nudge sequence.
- ⏸ USER took ownership of the janitor-wikimem ↔ harness-MEMORY.md conflict ("I will personally fix this"). PAUSING autonomous memory-maintenance passes (repair/split/harvest/consolidate/conflict) on heartbeat markers until the USER confirms — see [[user-owns-memory-md-wikimem-conflict]]. The heartbeat stub still runs (keepalive + fleet/stale nudges); recall-for-reading still used.

### WORKLIST (highest-leverage first)
- [ ] **Kanban round-trip** (#43→#40, orchestrator#24): server says deployed;
      MANAGER must run round-trip to close #40. Check deployed CLIs; attempt or
      document the exact blocker (likely #46 AMP identity).
- [ ] **Server blockers** — ensure complete specs + MANAGER ask on: #45 (4 CLI
      verbs), #46 (AMP identity), #47 (APPROVAL vs MANDATE), #48 (3-pillars
      wikimem), #49 (core alignment), #42 (core#11 handshake), #39 (assistant-role).
- [ ] **Per-plugin [fleet #44]** canon-pipeline: architect#23, autonomous#11,
      integrator#20, janitor#51, maintainer#17, orchestrator#22, amvcp#6, plugin#13
      — recipe already delivered; verify each issue is actionable, nudge if stale.
- [ ] **Governance-audit (screening)**: autonomous#12, maintainer#18, plugin#14,
      amvcp#7 — small per-plugin gaps; confirm each has the fix spec.
- [ ] **AMAMA in-control decisions** (user delegated "solve all / don't stop"):
      C1 CozoDB amama-session-memory skill (verify exists → retire/keep vs the
      global janitor memory system); C2 approve_plan stub (implement or make
      honest/fail-fast); C3 --password vs R32 example; C4 model:opus pins (KEEP);
      F7 Stop-hook $AID_AUTH gate (decide). Each = AMAMA commit → batch publish.
- [ ] **AMAMA coordination issues** (#7,#13–#22): update/close the ones now resolved.
- [ ] **AMAMA canon-drift** (non-blocking): dry-run showed RC-PIPELINE-DRIFT on
      .markdownlint.json + .mega-linter.yml (gitleaks-off is intentional, #138).
      Low-risk: declare cpv.pipeline.intentional_divergence to silence; DEFER a
      force-resync (risky unattended — can regress customizations).

### LOAD-BEARING FACTS
- AMAMA published v2.12.9 (was 2.12.8). `git push` is BLOCKED except via publish.py
  (pre-push hook, process-ancestry verified). Local commits are fine; batch-publish.
- Kanban: per memory [[kanban-pillar-no-server-backing]] the server SHIPPED the
  17-col model + CLIs; #1/#2/#36 CLOSED; #40 open only for the round-trip close gate.
- #46 (AMP identity, ~35 agents one host identity) is the documented blocker of the
  kanban round-trip #40 — verify whether it actually gates the MANAGER-side run.
- Decoupling residuals (#12) blocked on 4 undeployed verbs → ai-maestro#45.

### SUPERSEDED — do NOT carry forward
- "~25 unpushed commits await push" → SHIPPED as v2.12.9 (2026-06-22).

### Durable artifacts
- Self-audit remediation: design/tasks/TRDD-...-4c388042-amama-plugin-self-audit.md
- Memory: [[overnight-fleet-readiness-campaign]], [[amama-self-audit-remediation]],
  [[kanban-pillar-no-server-backing]], [[amama-12-decoupling-residuals-blocked-on-verbs]].

## Plan

Loop via the janitor heartbeat; each turn advance the worklist top-down. Make
AMAMA changes as local commits, batch-publish via the strict gate. Post one crisp,
current, actionable MANAGER comment per fleet issue so the owning Claude executes
on wake. Record progress in this STATE block + memory; never stop while items remain.
