---
trdd-id: 5fc2cb0a-6e89-4193-ab10-4ac5f6aa0514
title: Script↔skill sync diagnosis + the FROZEN skill-facing script-interface invariant (MANAGER ↔ ai-maestro)
column: planned
created: 2026-06-14T20:47:46+0200
updated: 2026-06-14T20:47:46+0200
current-owner: amama
assignee: amama
priority: 1
severity: HIGH
effort: L
task-type: infra
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
review-requirements: [human-review]
impacts: [install-script, public-api]
external-refs: ["github.com/Emasoft/ai-maestro/issues/35", "github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/16", "github.com/Emasoft/ai-maestro/issues/34", "github.com/Emasoft/ai-maestro/issues/27"]
---

# TRDD-5fc2cb0a — Script↔skill sync + the FROZEN script-interface invariant

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-06-14

**USER directive (2026-06-14).** A new coordination partner exists: the **ai-maestro core
repo's Claude** (Emasoft/ai-maestro — server + unified-installer + the **scripts layer**). The
USER connected us. There are **script↔skill SYNC issues** between the installer-deployed scripts
and the skills/agents that call them (all role plugins, **specifically the core ai-maestro-plugin's
skills**) → **fleet readiness is still incomplete**. The scripts owner is the ai-maestro Claude;
any script change routes through it.

### 🔒 THE LOAD-BEARING INVARIANT (USER, verbatim intent) — protect this forever
The scripts are a **stability buffer**: skills call a **FIXED script CLI**; the scripts translate
that stable surface to the **ever-changing ai-maestro server API**. The whole point: **when the API
changes, only the scripts change — never the plugins.** Therefore:
- **The skill-facing interface of every existing script (name + args + output shape) is FROZEN —
  forever.** Changing one breaks ~a dozen plugins.
- New capability = **ADD new scripts + new skills**, never modify an existing script's interface.
- The ONLY exception is a serious security vulnerability in a script's syntax.
The ai-maestro Claude **independently affirmed** this same invariant on assistant-manager#16 ✅.
This must be carried into the fleet governance-rules ("installed scripts are frozen; route all
script changes through the ai-maestro scripts owner; never patch installed scripts in a plugin").

### Coordination channel (OPEN)
- I opened **Emasoft/ai-maestro#35**; the ai-maestro Claude opened **assistant-manager#16** (it's
  HOLDING its `governance-rules` push pending my answers — I gave the readiness snapshot + cleared
  it conditionally: clear to push iff the branch doesn't change any script's skill-facing interface).
- Overlapping ai-maestro issues to align: **#34** (memory recall wiring), **#27** (AMP
  approval-request/answer — my approval-tier flow), **#1/#2** (kanban/task model — the Kanban pillar).

### Diagnosis findings so far (confidence-marked — recheck discipline)
- ✓ **VERIFIED — the core plugin already SHIPS the pillars/memory skills:** `ai-maestro-plugin`
  v2.7.6 has `prrd-trdd-kanban`, `team-kanban`, `team-governance`, `memory-recall/search/write`,
  `agent-messaging/identity`, `docs-search`, `graph-query`, `ai-maestro-agents-management`,
  `planning`, `network-security`, `mcp-discovery`. → **TRDD-f5883dcc (#8) must EXTEND these, not add
  a parallel `ama-*` set; the core `memory-*` skills overlap janitor global `janitor-memory-*` →
  reconcile in the memory rollout (TRDD-d369cf76).**
- ✓ **VERIFIED — source↔installed inventory gap:** `~/.local/bin` has the installed CLIs (56 amp-,
  10 graph-, 8 docs-, 7 aid-, 6 agent-, 2 memory-, 4 aimaestro-, all `.sh`-suffixed) but the
  `~/ai-maestro/scripts` checkout (70 files) contains **no `docs-*`/`graph-*`/`memory-*`**. So the
  canonical source for the installed docs/graph/memory CLIs is NOT in that checkout (stale checkout
  or sourced elsewhere) — **OPEN question for the ai-maestro Claude (#16).**
- ✗ **REFUTED would-be-FP:** `command -v docs-search/graph-describe/memory-search/aid-status` failed,
  but the installed CLIs are `.sh`-suffixed (`docs-search.sh` etc. EXIST) and the skills call the
  `.sh` forms → those calls DO resolve. NOT a drift. (Caught before claiming — verify-before-fixing.)
- ? **NOT YET DONE:** arg-level interface drift (a skill passing flags an installed script rejects) —
  the deeper per-call comparison pass. Awaiting USER decision: run it now, or take the source-gap
  question to the ai-maestro Claude on #16 first.

## Plan
1. Resolve the source-of-truth gap with the ai-maestro Claude on #16 (where do installed
   docs/graph/memory CLIs come from; is the checkout stale).
2. (If directed) run the arg-level drift pass: per core-plugin skill, compare each script call's
   args against the installed script's accepted args; hand the ai-maestro Claude a precise drift list.
3. Re-scope TRDD-f5883dcc (#8) to EXTEND the existing `prrd-trdd-kanban`/`team-*` skills, not add `ama-*`.
4. Carry the frozen-interface rule + "route script changes through the ai-maestro owner" into the
   fleet governance-rules rollout.

## Acceptance criteria
- Script↔skill drift enumerated + fixed at the source (ai-maestro repo), installed CLIs match what
  skills call (name + args + output), no plugin-local script patches.
- The frozen-interface invariant enshrined in the fleet governance rules + honored by core #8.
- #8 re-scoped to extend existing core skills; core memory-* vs janitor global reconciled.
