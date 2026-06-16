---
trdd-id: 5fc2cb0a-6e89-4193-ab10-4ac5f6aa0514
title: Script↔skill sync diagnosis + the FROZEN skill-facing script-interface invariant (MANAGER ↔ ai-maestro)
column: planned
created: 2026-06-14T20:47:46+0200
updated: 2026-06-16T02:14:17+0200
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
- **🆕 USER (2026-06-16) — the SPLIT principle, explicit for HOOKS + ALL scripts, no exceptions:** every script AND every hook is divided into an **api-dependent part** and a **non-api part**. The api part lives in the **ai-maestro project, installed with it** (a CLI); the **plugin carries ONLY the non-api part**. A plugin HOOK that needs the server calls a CLI, never `/api/` directly — hooks stay in plugins, but their API logic moves out to an installed intermediary CLI the hook invokes. Named exemplar: core `ai-maestro-hook.cjs` → split so the `.cjs` calls `activity-update` CLI (`cmd_session_activity_update`, built) + `amp-inbox` (exists) — no new CLI needed, just deploy + repoint. Hook-split scope = same 4 plugins as the script bypasses (AMAMA `amama_user_prompt_submit.py`; core `.cjs`; COS/janitor hook-registered scripts); the hooks' api-parts all reuse existing/built session/inbox CLIs. Coordinated on #16 (issuecomment-4713600798). Enshrine fleet-wide: "split every script/hook; plugin carries only the non-api part; no exceptions; all plugins."
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
- ✓ **DONE — direct-API-bypass audit (2026-06-14, background agent).** USER directive: COS was forced
  to call the server API directly for agent creation; fix it + investigate similar. Result: **10 confirmed
  `/api/*` bypasses across 4 plugins** (COS 5, core 2, AMAMA 2, janitor 1; autonomous/maintainer/amvcp
  clean) collapsing to **7 distinct functionalities → canonical CLIs to add/confirm**: (1) `agent-resolve`
  name|cwd→session [COS+core+janitor], (2) `agent-list --status active` [COS], (3) `agent-command`/
  send-command POST /api/sessions/<tmux>/command [core+janitor], (4) unread-inbox list/count [AMAMA+core —
  ⚠ `amp-inbox.sh` likely already exists, may just need USING], (5) `aimaestro-session activity-update`
  [core], (6) `aimaestro-session user-input` [AMAMA], (7) `aid-governance`/`aid-whoami` + `aimaestro-teams`
  CRUD [core+COS]. Report: `reports/script-bypass-audit/20260614_210319+0200-fleet-bypass-audit.md`.
  Posted to #16. False-positives correctly excluded (amcos_spawn/wake/terminate/hibernate use
  aimaestro-agent.sh; janitor scanner-pattern files are signatures not calls). **MY OWN 2 bypasses
  (amama_stop_check.py, amama_user_prompt_submit.py) are mine to repoint once the CLIs are confirmed.**
  Open governance Q for the scripts owner: is core `ai-maestro-hook.cjs` (the AMP/AID glue) by-design
  integration-layer or a bypass to fix?
- ✓ **CLI PLAN CONFIRMED by the scripts owner (#16, 2026-06-14) — additive/frozen-safe.** Split:
  - **Already exist → REPOINT now (plugin edits, no new CLI):** #4 inbox → `amp-inbox --count`/`--unread`
    (AMAMA `amama_stop_check.py`, core hook); #2 list-active → `aimaestro-agent.sh list --status online`
    ("active"==online; COS heartbeat).
  - **Owner will EXPOSE (additive, wait):** #1 resolve → `aimaestro-agent.sh resolve <name> | --cwd <path>`;
    #3 send-command → `aimaestro-agent.sh session command <name> -- <cmd>`.
  - **Owner will ADD (new CLIs, wait):** #6 `session user-input` (AMAMA `amama_user_prompt_submit.py`);
    #7 `aimaestro-teams` CRUD + `aid-whoami`/`aid-governance` + governance-request (core `prrd_lib.py`, COS).
  - **#5 core-hook `activity-update`:** ✅ **USER DECIDED (2026-06-15) — ROUTE THROUGH A CLI; no provider-exception.**
    The core `ai-maestro-plugin` is NOT exempt from the frozen-CLI invariant: even its `ai-maestro-hook.cjs`
    must reach the server via a CLI (additive `activity-update` CLI to be added at source), end state = ZERO
    direct `/api/*` from the core hook. The `:23000`→`AIMAESTRO_API` fix still happens but is NOT sufficient
    alone. Rationale → fleet governance rule: "installed scripts frozen; ALL plugins (core included) reach the
    server only through CLIs; route every script change through the ai-maestro scripts owner." Relayed on #16
    (issuecomment-4711612291). #5 now joins #1/#3/#6/#7 as additive CLIs the owner adds → I repoint + verify-ack.
  - **Sequencing:** owner posts each CLI's exact name+args on #16 as it lands → I drive the fleet-wide repoints +
    verify each. AMAMA's two (#4 ready, #6 pending) BATCHED into AMAMA's pending memory-migration release (M5/USER publish).
- ✓ **DONE — arg-level drift audit (2026-06-14, background agent; the 2nd half of the sync audit).**
  ~24 drifts, ALL plugin-side, confined to **chief-of-staff (~21)** + **maintainer (3)**; 100% violate
  `amp-send` (positional `<recipient> <subject> <message>` + the `--type` 10-value allow-list) or
  `aimaestro-agent.sh` (phantom `messages` subcommand). Several are SILENT runtime failures (CoS
  `broadcast_notification` invalid `--type broadcast` → exit 1 every call; `amcos_failure_recovery.py:153`
  phantom `aimaestro-agent.sh messages`). **Core `ai-maestro-plugin` CLEAN** (288 invocations all valid —
  the canonical reference is internally consistent); AMAMA/autonomous/janitor/amvcp clean. Report:
  `reports/script-arg-drift-audit/20260614_221510+0200-fleet-arg-drift-audit.md`. **Fixes ROUTED (plugin-side,
  no script changes):** chief-of-staff#19 + maintainer-agent#13; recorded on #16. I verify-ack each fix.
  Confirms `amp-send` + `aimaestro-agent.sh` are the highest-blast-radius CLIs → keep frozen.
- ✓ **DONE — COMPREHENSIVE fleet-wide API-usage SEARCH (2026-06-15, per USER "search for ANY script using the api").**
  Grepped all installed plugins + shallow-cloned the 4 previously-un-audited role plugins. **Verified definitive bypass
  set = exactly 4 plugins:** AMAMA (`amama_user_prompt_submit.py` #6 only — `amama_stop_check.py` FIXED in v2.11.0),
  COS (~5, COS#20 filed), core/ai-maestro-plugin (`ai-maestro-hook.cjs` + `prrd_lib.py`, core#9), janitor
  (`terminal_trigger.py`). **CLEAN (verified):** orchestrator, integrator, programmer, architect (shallow-clone grep,
  zero `/api/` in non-test scripts), plus autonomous/maintainer/amvcp. **False positives correctly excluded:** janitor
  `tests/*_patterns.py` + `scripts/lib/*_patterns.py` + detectors = security-scanner SIGNATURES not calls; amvcp
  `cpv_skillaudit_rules.py` = audit rules. The "did we miss any?" question on #16 is now CLOSED: no missed scripts.
- ⚠ **CORRECTION (2026-06-15, COS surfaced on #16): that search was SCRIPT-ONLY and UNDERCOUNTED — the `.md` PROMPT/skill/command layer instructs direct `/api/` too, and IS in scope** (a prompt telling an agent to `curl /api/...` is a bypass — the agent runs it). So "4-plugin set / AMAMA clean" was incomplete: **AMAMA itself is NOT clean** — `amama-presence-tracker` / `amama-approval-workflows` / `amama-status-reporting` skills instruct direct calls (its scripts were repointed #4, its prompts were not; I clean them once the CLIs land). New functionalities the CLI surface must ALSO cover (gaps): **governance/transfers** (COS `amcos-transfer-agent`), **users/me/presence + sessions/me/user-input** (presence/#6), **whoami/identity** (`me`/`hosts/identity`). Full functionality→CLI map posted on #16 (issuecomment-4712406314). **Completeness criterion (all plugins, scripts+prompts):** `grep -rn '/api/'` shows no direct-call INSTRUCTIONS (descriptive "CLI wraps /api/X" docs OK). Lesson: "search for any script" must include the `.md` prompt layer — those files drive agent behavior, not just executables.

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
