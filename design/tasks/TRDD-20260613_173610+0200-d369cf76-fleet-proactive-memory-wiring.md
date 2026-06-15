---
trdd-id: d369cf76-4192-4137-b4d1-86cd8b345b99
title: Fleet-wide — wire every plugin's agents (main AND sub) to proactively use the memory system
column: planned
created: 2026-06-13T17:36:10+0200
updated: 2026-06-15T21:27:51+0200
current-owner: amama
assignee: amama
priority: 2
severity: HIGH
effort: L
task-type: infra
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
test-requirements: []
review-requirements: [human-review]
impacts: [public-api]
external-refs: ["github.com/Emasoft/ai-maestro-janitor/issues/18"]
---

# TRDD-d369cf76 — Fleet proactive-memory wiring (main + sub agents)

## ⏵ STATE — READ THIS FIRST ON RESUME — 2026-06-14

**✅ AMAMA MIGRATION PUBLISHED — v2.11.0 (2026-06-15).** USER authorized the publish (M5 satisfied
by explicit USER approval); `publish.py --minor` ran all gates green (pytest 15-passed, CPV --strict
0/0/0/0, version-consistency OK) → tagged + pushed + GitHub release
(github.com/Emasoft/ai-maestro-assistant-manager-agent/releases/tag/v2.11.0). Shipped: the full memory
migration + the AMAMA bypass-#4 repoint + a `.gitignore .janitor/` housekeeping fix (runtime state was
untracked-but-not-ignored — corrected before publish; the prior STATE's "gitignored" claim was wrong).
AMAMA is now the published MANAGER exemplar of the global-memory shape. Fleet rollout continues: 7
plugins still to verify-ack (COS done). Historical file-work record below.

**⚠ ROLLOUT CAVEAT (verified 2026-06-15, tracked janitor#37): recall via the SKILL, not the rule's bash
snippet.** The installed `~/.claude/rules/markdown-memory-recall.md` can be STALE on a given machine —
PROJECT shown as `<git-root>/memory/` (old) vs the correct `<git-root>/.claude/project/memory/` in cached
0.8.10. Cause: a session that loaded an OLDER janitor (e.g. 0.7.5 hooks) re-installs the old-path rule at
SessionStart, actively re-staling it. The `/janitor-memory-recall` SKILL uses the correct root regardless,
so **skill-based recall WORKS** — only someone hand-running the rule's inline `PROJECT_MEM=…` bash would
miss PROJECT notes. Fleet sweep (2026-06-15): only AMAMA + COS have `.claude/project/memory/` committed;
8 plugins pending (each has an open `feat(memory): adopt…` tracking issue). Mitigation until janitor#37
lands: recall skill-first; `/reload-plugins` after bootstrap syncs the rule snippet.

**🟢 AMAMA MIGRATION FILE-WORK COMPLETE (2026-06-14, committed, NOT yet published).** Done
manually (the bootstrap skill wasn't loaded in-session — replicated from the v0.8.8 cache +
COS v2.16.0 reference): (1) PROJECT scope `.claude/project/memory/` + gitignore exception
(`.claude/`→`.claude/**` + `!.claude/project/memory/**`; verified trackable via `git add
--dry-run`) + arch hub + MEMORY.md; (2) main agent + `amama-report-generator` sub-agent rewired
to global `janitor-memory-*` + the proactive contract (recall/write/PROPAGATE/zsh-safe form);
(3) new `CLAUDE.md` folds the MANAGER-role recall emphasis (Caveat 1) + the janitor-coupling
(Caveat 2); (4) removed `skills/amama-memory-recall`+`-write`, `rules/memory-protocol.md`, + their
tests (`test_memory_system.py`, `memory_ops.py`); README + tests/README repointed. **Test gate
GREEN (15 passed); CPV `--strict` = 0 CRITICAL/0 MAJOR/0 MINOR/0 NIT (17 non-blocking WARNINGs:
13 cache CA-01..06 + 1 markdownlint-config) — VALIDATED PUBLISH-READY.** Also folded in the AMAMA
bypass #4 repoint (`amama_stop_check.py` → `amp-inbox --count`). Commits on `main` (unpushed).
REMAINING = the publish ONLY — **M5-gated
(MANAGER can't self-approve AMAMA's own release) → USER runs `publish.py` on return** (a `/reload-plugins`
then makes the global skills live in-session, but the file-work is already done). AMAMA now matches
COS v2.16.0's shape = the MANAGER exemplar. Fleet rollout: 8 plugins nudged with the GO (COS done).

---
_(historical STATE below — 2026-06-13)_

**🟢 FINAL SPEC RECEIVED (janitor, via assistant-manager#15 — supersedes the per-plugin
`<plugin>-memory-*` model in the body below).** Memory skills are **GLOBAL, from the
user-level janitor plugin** — names **CONFIRMED UNCHANGED**: `janitor-memory-recall` /
`janitor-memory-write` / `janitor-memory-update` (no rename). Role plugins **USE the global
skills; they do NOT ship their own**. The locked config:
- **3-scope storage:** LOCAL `~/.claude/projects/<slug>/memory/` (harness, unchanged) ·
  **PROJECT `<repo>/.claude/project/memory/`** (tracked+pushed; needs gitignore exception:
  `.claude/**` ignored then `!.claude/project/memory/**`) · USER `${CLAUDE_PLUGIN_DATA}/memory/`.
- **Rollout mechanism = the NEW `/janitor-memory-bootstrap` skill** — each plugin's own main
  agent runs it once (creates `.claude/project/memory/` + gitignore exception, seeds the
  arch-hub page + MEMORY.md, points the agent at the recall rule + skills + proactive contract).
- **Proactive contract** (now in the skills + `markdown-memory-recall` rule): recall-before-acting
  · write/update-after-solving · maintain-project-wikimem · scope-routing. **MY DELTA:** also
  propagate the contract into SUB-AGENT prompts (sub-agents inherit nothing — USER's must-have).
- **REMOVE the fleet's redundant per-plugin skills** — AMAMA strips `amama-memory-recall`/`-write`
  + reconciles `rules/memory-protocol.md` (confirming removal with janitor on #15).
- **EXECUTE ON JANITOR PUBLISH** — the janitor's skills/bootstrap are committed but UNPUSHED
  (pending USER review). Align now (design locked); run `/janitor-memory-bootstrap` + the rework
  once it ships. No `column:` collision — memory lives under `.claude/project/memory/`, the
  3-pillars under `design/` (orthogonal).
- **✅ SECOND BLOCKER CLEARED — CPV #120 fixed in CPV v2.126.15 (2026-06-14T02:37).** `validate_gitignore`
  previously raised an UNSATISFIABLE `[MINOR] missing coverage for .claude/` for any plugin tracking
  content under `.claude/` (the PROJECT-memory pattern `.claude/project/memory/**`) — its old
  `git check-ignore -q -- .claude` test could never pass once a subtree under `.claude/` was tracked.
  CPV's Claude fixed it: the `.claude/` coverage category is now satisfied when the plugin TRACKS
  content under `.claude/` (decided git-authoritatively via `git ls-files -- .claude/`), FN-safe
  two-sided (a real un-ignored+un-tracked `.claude/` cache leak still gets the MINOR). So the
  `.claude/**` + `!.claude/project/memory/**` pattern now passes `--strict`. **Min CPV version for
  the memory rework = v2.126.15** (the `uvx --from git+…` runner pulls latest, so it's covered).
  TO VERIFY first-hand during the AMAMA rework (run `cpv-remote-validate --strict` on the tracked
  `.claude/project/memory/` layout). The memory rollout is now gated on ONLY the janitor's memory publish.
- **🟢 JANITOR #15 CONFIRMATIONS (2026-06-14) — design LOCKED; cleared to align now + execute on publish.**
  The janitor's Claude confirmed on `assistant-manager#15` (the publish-ping channel):
  - **REMOVE AMAMA's per-plugin memory artifacts:** `skills/amama-memory-recall/`,
    `skills/amama-memory-write/`, `rules/memory-protocol.md` (133 lines). NOTE: `skills/amama-session-memory/`
    is a SEPARATE concern (the deferred reconciliation item in the v2.10 follow-up TRDD) — NOT part of this removal.
  - **CAVEAT 1 — RESOLVED (scanned 2026-06-14):** `rules/memory-protocol.md` (133 lines) is explicitly
    "the AMAMA-parameterized MIRROR of the canonical `~/.claude/rules/markdown-memory-recall.md`" (its line 3),
    which v0.8.0 refreshes. The ONLY plugin-UNIQUE content to FOLD into AMAMA's CLAUDE.md before deleting:
    the **MANAGER-role recall emphasis** — for AMAMA the highest-value recalls are **confirmed user
    preferences** + **prior approval/governance decisions**; AMAMA's workhorse note `type` is `feedback`
    (e.g. merge-strategy, escalate-all-prod-deploys, don't-over-flag-ToS-on-own-accounts). Everything else
    is generic mirror content (index-by-symptom, recall-before-acting, note schema, memgrep, dual-test) =
    covered by the canonical rule. Its refs to `amama-memory-write/recall` are obsolete (those skills are removed).
  - **CAVEAT 2:** document the janitor-dependency coupling explicitly — now a USER-ratified invariant
    (the janitor is the ONLY USER-scope plugin, "above claude code itself," guardian of the oauth;
    janitor-always-present is what makes relying on the global memory system safe by construction).
  - **🔴 ZSH RECALL-BUG FIX — FLEET-CRITICAL.** The documented recall snippet built `ROOTS` as a space-joined
    string passed UNQUOTED (`memgrep recall "$SYMPTOM" $ROOTS`). bash word-splits it; **zsh (macOS default)
    does NOT** → the whole string reaches memgrep as ONE bogus path → **0 results, exit 0, SILENTLY** (every
    zsh agent got an empty memory). Fixed to the array form (`ROOTS+=("$d")` built, `"${ROOTS[@]}"` expanded);
    janitor commit `df2e563` + regression test. The global `markdown-memory-recall` rule reinstalls the fixed
    form automatically on publish, BUT the fleet-rollout directive MUST instruct every plugin to ADOPT THE FIXED
    ARRAY-FORM recall command (the old string form is a silent footgun on zsh). My own
    `~/.claude/rules/markdown-memory-recall.md` still has the OLD buggy form today — the janitor publish overwrites
    it; until then, use the array form if I recall.
  - **REFERENCES TO UPDATE when removing amama-memory-* (grep hits):** README.md, tests/README.md,
    `agents/…-main-agent.md` (rewire to global `janitor-memory-*`); the 2 TRDDs reference it intentionally — leave.
  - **TRIGGER:** execute on the janitor's publish (a janitor release > v0.7.5). The janitor will PING
    `assistant-manager#15` when it ships. Sequence: AMAMA exemplar FIRST, then the fleet. CPV/PSS out of scope.

**AMAMA IS IN SCOPE (USER emphasized — it's the MANAGER, the most important role).** AMAMA's
own agents MUST be updated as the exemplar, not just the fleet's:
- `agents/…-main-agent.md` — currently references the per-plugin `amama-memory-recall/write`
  (lines 37-38, 48-54). REWIRE to the global `janitor-memory-*` + ADD the PROPAGATE-to-sub-agents
  clause.
- `agents/amama-report-generator.md` (sub-agent) — ADD the proactive-memory block (recall + propagate).
- REMOVE the `amama-memory-recall`/`-write` skills + reconcile `rules/memory-protocol.md`
  (keep as a thin pointer to the global rule, or drop) — per #31's answer.
- Execute bundled with the memory-path follow-up release (one coherent AMAMA memory-rework publish).

**USER directive (2026-06-13).** Adopting the memory *skills* is NOT enough — every role
plugin's agent `.md` files must be **wired to PROACTIVELY invoke** the memory system
(recall-before-acting + write-after-learning), and **critically that wiring must apply to
SUB-AGENTS too**, not only the main agent. "This is one important task you have in preparing
the fleet." Coordinate with each plugin to update their agent `.md` files.

**SEQUENCING.** The janitor is finalizing the new memory skill + a PROJECT-memory path change
(incoming "in the next few hours"). The new memory skill "will certainly contain the
instructions" (the HOW). So: WAIT for the janitor's memory skill to land, then coordinate the
wiring referencing the final skill — and bundle AMAMA's own wiring with the memory-path
follow-up release (avoid double-publishing AMAMA).

**AMAMA's own state (scoped 2026-06-13):**
- `agents/…-main-agent.md` — ✅ ALREADY wired (lines 48-54: "Recall before acting" + capture via amama-memory-write).
- `agents/amama-report-generator.md` (SUB-AGENT) — ❓ needs review/wiring (the user's "even sub-agents" gap). Add at least recall-where-relevant + the propagation principle.

## The requirement (what every plugin must add to its agent `.md` files)

Every `agents/*.md` (main AND each sub-agent) gets a proactive-memory block. Canonical text
(adapt `<plugin>-memory-*` to the plugin's skill names):

```
## Memory — proactive (applies to YOU and every sub-agent you spawn)
- RECALL before acting: before debugging a recurring problem, making/repeating a decision,
  recommending, or acting on a recurring alert, invoke `<plugin>-memory-recall` with the
  SYMPTOM (the user's words / the error text) — "have we hit this before?". Cheap; do it first.
- WRITE after learning: when something durable + non-obvious is confirmed (a preference, a
  gotcha + its why, a decision), invoke `<plugin>-memory-write` — `description:` indexed by
  the SYMPTOM (the question), NOT the answer's jargon.
- PROPAGATE: when you spawn a sub-agent, include this same memory directive in its prompt so
  it recalls + writes too. Memory discipline is inherited, not assumed.
```

## Plan
1. **Wait** for the janitor's new memory skill + PROJECT-path change to land (TRDD tracks it via task #9). Reference its final instructions.
2. **AMAMA (lead by example):** wire `amama-report-generator.md` (sub-agent) with the recall + propagation block; confirm the main agent's block matches the canonical text + adds the PROPAGATE clause. Bundle into the memory-path follow-up release.
3. **Fleet coordination:** message every role plugin (orchestrator, integrator, programmer, architect, autonomous, chief-of-staff, maintainer, integrator, code-auditor, amvcp, + base) to add the proactive-memory block to ALL their `agents/*.md` (main + sub). Verify-and-ack each against its live tree.
4. **Verify:** for each plugin, grep its `agents/*.md` for the recall/write/propagate directive; a plugin is done only when EVERY agent file (not just the main) carries it.

## Why
Skills that are never invoked are dead weight. The fleet adopted memory-recall/write skills,
but without an explicit agent-level "recall before acting / write after learning / propagate
to sub-agents" instruction, agents won't use them — and sub-agents (which inherit nothing by
default) definitely won't. This wiring is what makes the memory system actually function
across the fleet. It is a restart-readiness item.

## Acceptance criteria
- Every role plugin's `agents/*.md` (main + every sub-agent) carries the proactive-memory block.
- Sub-agent SPAWN sites instruct propagation of the memory directive.
- AMAMA exemplifies it (main + amama-report-generator).
- Verified against each plugin's live tree + acked.
