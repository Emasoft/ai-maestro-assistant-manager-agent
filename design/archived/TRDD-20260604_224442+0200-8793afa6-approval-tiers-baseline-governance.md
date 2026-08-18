---
trdd-id: 8793AFA6
title: TRDD approval tiers, proposal→planned lifecycle, and baseline-ruleset governance across all role plugins
column: complete
created: 2026-06-04T22:44:42+0200
updated: 2026-08-18T20:55:00+0200
current-owner: amama
assignee: amama
priority: 2
severity: MEDIUM
effort: M
labels: [governance, trdd, baseline, personas]
task-type: docs
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
delivery: direct-push
target-branch: main
impacts: [config-schema]
test-requirements: []
review-requirements: [human-review]
runtime-targets: [macos]
external-refs: []
---

# TRDD-8793afa6 — Approval tiers, proposal→planned lifecycle, and baseline-ruleset governance

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-04

**User directive (verbatim intent), 2026-06-04:**
1. All AI Maestro agents must be aware there are **standard baselines
   for GitHub rulesets**, that the **janitor auto-enforces** them if an
   agent forgets, and that any **special exception / added rule /
   deviation** from the baseline requires **MANAGER permission**. Make
   this clear in all role-plugin main-agent files.
2. TRDDs with status `proposal` live in `design/proposals/`; once
   approved (by USER, MANAGER, or COS) and promoted to `planned`, the
   `.md` is **moved** to `design/tasks/`.
3. Agents may still author TRDDs **directly** in `design/tasks/` as
   `planned` (DERIVED TASKS, or independent in-scope tasks) — they must
   continuously plan+execute their own work.
4. The deliverable the user delegated to MANAGER: **make clear the
   classification and criteria** for when a TRDD needs USER / MANAGER /
   COS / no approval (agent-independent default).

**Current state:**
- ✅ Phase 1 (foundational, local/global, additive) — DONE:
  - Canonical rule written: `~/.claude/rules/trdd-approval-tiers.md`
    (Part A folder lifecycle, Part B 4-tier classification, Part C
    baseline governance). Auto-loads into EVERY agent's context, so it
    is in force ecosystem-wide WITHOUT editing the other repos.
  - `design/proposals/` staging folder + `README.md` created in the
    MANAGER project.
  - This TRDD authored as the plan-of-record.
- ✅ Part B classification CONFIRMED by USER ("yes") 2026-06-04.
- ✅ Phase 2 (cross-boundary) — COMPLETE 2026-06-04:
  - VERIFY-FIRST: pervasive local↔upstream DRIFT found → studied UPSTREAM
    per plugin via gh (never the drifted/dirty local clones).
  - 7 detailed, self-contained TRDDs drafted (1 exemplar + 6 swarm),
    QA-passed (per-repo verification tooling confirmed to exist).
  - POSTED as GitHub issues (USER-authorized "post them"):
    orchestrator-agent#11, chief-of-staff#15, architect-agent#12,
    integrator-agent#11, programmer-agent#11, autonomous-agent#4,
    maintainer-agent#8.
  - MANAGER's OWN main-agent file edited locally — new
    `### Task Approval Tiers` section after `### GovernanceRequest
    Approval (C4)`, disambiguating the two approval axes.

**✅ CARD COMPLETE 2026-08-18.** Each receiving plugin implements its issue on
its OWN pipeline (cross-project; out of MANAGER's hands). The last pending item —
push authorization for the local MANAGER changes — was delivered by the hub's
publish GO (recorded USER delegation, TRDD-BRRJK57P): everything shipped in
release v2.17.2 via publish.py. The optional fold of Part A into
trdd-design-tasks.md is superseded by the aimaestro-trdd-approval overlay
(min-approval-requirement title ladder), which now governs.

**Load-bearing facts / gotchas:**
- `~/.claude/` is **NOT** a git repo → only ADDITIVE new rule files
  there (no rewrites of existing global rules without care).
- Each role plugin is its **own git repo** under `~/Code/*` (verified):
  EMASOFT-ORCHESTRATOR/ARCHITECT/INTEGRATOR/CHIEF-OF-STAFF/PROGRAMMER-AGENT,
  AI-MAESTRO-AUTONOMOUS/MAINTAINER/WEBDESIGN-AGENT, and this one
  (ASSISTANT-MANAGER). **Do not edit the other 8 trees directly.**
- Global `~/.claude/rules/*.md` auto-load into every session's context
  → that is the cross-project-safe mechanism for an ecosystem rule.
- Existing `design/tasks/` TRDDs (cos-delegation-authority,
  amama-phase-1) are **grandfathered** as `planned`; do NOT move them.

**SUPERSEDED — do NOT carry forward:** none yet.

**Durable artifacts to read before acting:**
- `~/.claude/rules/trdd-approval-tiers.md` (the rule this TRDD ships)
- `~/.claude/rules/manager-approval-defaults.md` (EXEMPT/NON-EXEMPT — the
  tiers map onto this)
- `~/.claude/rules/prrd-design-rules.md` (GOLDEN/SILVER + proposal queue)
- `~/.claude/rules/trdd-design-tasks.md` (v2 columns)

## The classification (summary — full text in the rule file)

| Tier | Approver | Fires when |
|---|---|---|
| **0** | none (agent-independent, DEFAULT) | DERIVED TASK or in-own-scope; no baseline deviation; no cross-team/project/release; reversible+local. = the EXEMPT list. |
| **1** | CHIEF-OF-STAFF | affects other same-team members / beyond own slice but in-team. Routes via COS (R6 v3). |
| **2** | MANAGER | baseline deviation; cross-team/project; release/deploy; SILVER PRRD / persona change; architectural/first-of-kind. = the NON-EXEMPT list minus USER-only. |
| **3** | USER | GOLDEN PRRD change / promote-demote; anything MANAGER can't authorize; irreversible/public/owner-identity. |

Default Tier 0. Escalate one tier when unsure.

## Folder workflow

- `proposal` → `design/proposals/` (awaiting approval).
- approve → `status: planned`, log in `## Approval log`, `git mv` to
  `design/tasks/`, enter v2 pipeline.
- Tier-0 work → authored directly in `design/tasks/` as `planned`.

## Baseline governance

Standard pair `baseline-history-protect` + `baseline-pr-and-checks`;
janitor auto-enforces; apply-as-is = Tier 0; ANY deviation = Tier 2
(MANAGER). Canonical def in `manager-approval-defaults.md` §F.

## Phase 2 plan (cross-project — refined per USER 2026-06-04)

**SCOPE (authoritative, verified 2026-06-04):** ONLY **role plugins in
the `Emasoft/ai-maestro-plugins` marketplace**, where a *role plugin* is
DEFINED (per USER) as a marketplace plugin that contains a
`*-main-agent.md` file. Verified against the live marketplace manifest
(11 plugins) + a per-repo tree check — exactly **8** qualify:
assistant-manager (MANAGER), chief-of-staff, architect, orchestrator,
integrator, programmer (MEMBER), maintainer, autonomous.
NOT role plugins (no `*-main-agent.md` → excluded): `ai-maestro-plugin`
(base), `ai-maestro-janitor` (daemon, no persona),
`ai-maestro-visual-communicator-plugin`. Also out of scope: the
`emasoft-*` marketplace (different product line) and
`ai-maestro-webdesign-agent` (WIP, no repo, absent from the manifest).
NB: `ai-maestro-maintainer-agent` is both a role-plugin issue target AND
the baseline-coordination peer — the approval-tiers issue is distinct
from the baseline thread (maintainer#7 / janitor#14).

**Target ai-maestro role plugins (study UPSTREAM → detailed TRDD → issue):**

| role | repo (Emasoft/…) | upstream HEAD |
|---|---|---|
| ORCHESTRATOR | ai-maestro-orchestrator-agent | a3301a5 |
| ARCHITECT | ai-maestro-architect-agent | 6557fa3 |
| INTEGRATOR | ai-maestro-integrator-agent | 36f24c4 |
| MEMBER | ai-maestro-programmer-agent | 4090149 |
| CHIEF-OF-STAFF | ai-maestro-chief-of-staff | 6117ce6 |
| AUTONOMOUS | ai-maestro-autonomous-agent | 71553af |
| MAINTAINER | ai-maestro-maintainer-agent | (feat branch unpushed; study `main`) |
| MANAGER (mine) | ai-maestro-assistant-manager-agent | LOCAL edit, not an issue |

**VERIFY-FIRST done** — pervasive local↔upstream DRIFT (see STATE). Study
the UPSTREAM (GitHub) state per plugin via `gh`, NEVER the local clones.

**Per-plugin loop (7 issue targets):**
1. Deep-study the plugin's UPSTREAM main-agent file + relevant skills via
   `gh` (read from GitHub, never the local clone).
2. Draft a DETAILED, SELF-CONTAINED TRDD in `design/proposals/`: full WHY,
   exact main-agent text to add, integration point, reconciliation with
   existing persona, acceptance + verification. Self-contained — the
   receiving agent shares none of our context.
3. MANAGER reviews the draft.
4. Post the TRDD as a GitHub ISSUE on that plugin's repo (cross-project
   method — issue, never a direct edit).

Exemplar-first: ORCHESTRATOR drafted as the template → validate → swarm
the remaining 6.

**MANAGER's own main-agent file** = LOCAL edit (in scope), done alongside.

Optional follow-up: fold Part A into `trdd-design-tasks.md` (deferred —
significant edit to a non-git global file).

## Approval log

- 2026-06-04T22:44:42+0200 — Authored as `planned` directly in
  `design/tasks/` per USER directive (a user-directed task is approved
  by definition — Tier 3 author is the USER). Phase 1 implemented;
  Phase 2 gated on USER confirmation of the Part B classification.

## Acceptance (closing checklist)

- [x] Canonical rule `~/.claude/rules/trdd-approval-tiers.md` authored (Part A folder lifecycle, Part B 4-tier classification, Part C baseline governance).
- [x] Part B classification confirmed by USER ("yes") 2026-06-04.
- [x] 7 detailed, self-contained TRDDs drafted and posted as GitHub issues on the 7 receiving role-plugin repos (orchestrator#11, chief-of-staff#15, architect#12, integrator#11, programmer#11, autonomous#4, maintainer#8).
- [x] MANAGER's own main-agent file updated locally with the `### Task Approval Tiers` section.
- [x] Local MANAGER changes shipped in release v2.17.2 via publish.py (push authorization recorded, TRDD-BRRJK57P).
- [x] Optional Part A fold into `trdd-design-tasks.md` explicitly superseded by the aimaestro-trdd-approval overlay.

Closed complete on 2026-08-19 per TRDD-QX6VFAXS corpus hygiene pass.
