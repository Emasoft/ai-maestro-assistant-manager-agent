---
trdd-id: 282f61fe-c49b-4a35-8a85-4b9dbaeed15a
title: Overnight fleet-readiness campaign — MANAGER coordination + AMAMA in-control finish
column: dev
created: 2026-06-22T02:06:57+0200
updated: 2026-06-22T10:19:35+0200
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
AMAMA fully shipped + coordinated for the morning. Remaining is monitor-and-advance:
watch for peer responses on #43 / orchestrator#24 / #45 / #35, run MANAGER
verify-acks if a peer reports ready, and loop via the heartbeat. No AMAMA in-control
code changes pending (C1/F7 await USER). Awaiting the USER's morning (3 USER actions on #35).

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
  + the 3 USER actions). Memory + the source-vs-deployed lesson updated.
- ✅ 5 decisions: C2 done · C3 no-op · C4 keep · C1+F7 deferred→USER (recs recorded).

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
