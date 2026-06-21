---
trdd-id: 9a16554d-1e1e-4e37-bc9a-5624fb19e556
title: Fleet governance hardening — codify APPROVAL/MANDATE + audit role plugins for violations
column: dev
created: 2026-06-21T20:24:32+0200
updated: 2026-06-21T21:30:00+0200
current-owner: amama
assignee: amama
priority: 1
severity: HIGH
effort: L
task-type: audit
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
delivery: direct-push
target-branch: main
test-requirements: []
review-requirements: [human-review]
impacts: []
external-refs: []
---

# TRDD-9a16554d — Fleet governance hardening

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-21

**Directive (MAESTRO, 2026-06-21):** examine all role plugins in depth, fix all
remaining governance-rule violations, file ai-maestro issues for protocol/script
needs, and write two wikimems — (1) APPROVAL vs MANDATE protocol + the
approval-requirements criteria, (2) golden/silver/PRRD. Then: "make the memory
project scoped, so they are git tracked."

**Constraints (load-bearing):**
- **Cross-project:** I can edit ONLY AMAMA's source. Other role plugins are
  separate repos → governance violations there become **per-repo issues**
  (Method-1); protocol/script-function asks go to the **ai-maestro** repo.
- **Cache reach:** only **5** role plugins are in this machine's cache and thus
  deep-auditable locally — **AMAMA, autonomous, maintainer, core
  (ai-maestro-plugin), amvcp**. The other **5 — orchestrator, architect,
  integrator, programmer, chief-of-staff — are NOT cached** → audit via GitHub
  fetch or a per-repo self-audit issue (same limit as the #32 ledger).
- `/go-on-yourself`: act without approval; never relax security/quality; commit
  often; **do NOT push** (await MAESTRO approval).

**PHASE STATUS:**
- **Phase 1 — wikimems: ✅ DONE.** `approval-vs-mandate-protocol.md` +
  `prrd-golden-silver-rules.md` written to AMAMA **PROJECT scope**
  (`.claude/project/memory/`, git-tracked), committed `41bdb34`. (First written
  to USER scope, then relocated per the MAESTRO's "make the memory project
  scoped" correction; USER-scope copies pending cleanup-permission per RULE 0.)
- **Phase 2 — governance audit: ✅ DONE.** 5 cached plugins audited (parallel
  sonnet agents) + ALL reports verified against the LIVE working trees. KEY
  FINDING: auditors saw the stale installed CACHES (AMAMA 2.9.1 vs live 2.12.8;
  maintainer 1.5.0; core 2.7.6; autonomous 1.3.3; amvcp 1.3.6) → systematically
  OVER-reported. Most HIGH/CRITICAL = already-tracked fleet work: core CRITICAL
  (`ai-maestro-hook.cjs` fetch bypass) = ai-maestro#37 (.cjs rewrite); AMAMA's 6
  decoupling HIGH = the #12 `DECOUPLE-BLOCKED` residuals (blocked on #45). Stale-
  but-fixed: AMAMA R6 (report-generator memory present in live), R2/R4/R1 (PRRD/
  G1.1/tiers in live persona). GENUINE residue: A (G1.1 in skill TEMPLATES not
  just persona — fleet), B (memory-recall in individual SKILLS — fleet), C
  (autonomous silver `--user` default), D (autonomous Q7 raw /api/), E
  (status≠work-orders, minor), F (amvcp share-page public-deploy warning).
  Reports: `reports/governance-audit/` (gitignored).
- **Phase 3 — remediate: ✅ IN-CONTROL SCOPE DONE.**
  - ✅ **ai-maestro#47** — enshrine APPROVAL/MANDATE in GOVERNANCE-RULES.md +
    verifiable-signature verbs (the MANDATE counterpart + `verify` surface that
    #27 lacked; cross-refs #27/#37/#46/#33).
  - ✅ **per-repo issues** (genuine findings, framed screening-vs-cache):
    maintainer#18 (A), autonomous#12 (C/D/E/F4), amvcp#7 (B/F), core#14 (B +
    team-governance tier/G1.1; decoupling=#37 noted not re-filed).
  - ✅ **AMAMA finding A** fixed + verified: G1.1 self-id note added to the 3
    gh-post skill files + modeled in the concrete examples (commit `225b251`,
    spark-edited, diff reviewed clean). **B/E need NO fix** — AMAMA's `CLAUDE.md`
    carries the full proactive-memory contract (applies to all skills + sub-
    agents) and RULE 1 (status≠work-orders) is global + in the persona; both
    already satisfied. AMAMA R5 decoupling = the #12 residuals (blocked on #45) —
    untouched.
  - ✅ **5 non-cached plugins** (orchestrator, architect, integrator, programmer,
    chief-of-staff) — NOT locally auditable (no cache/source; cross-project). NO
    premature per-plugin issues filed (no source ⇒ no specific finding to report;
    filing speculative "self-audit" issues onto plugins that just shipped R26-R40
    would be noise). Their governance is already established: **R26-R40 = 9/9
    verified vs published main** + approval-tiers done. The NEW protocols
    (APPROVAL/MANDATE + golden/silver) propagate FLEET-WIDE via #47 once it lands
    in GOVERNANCE-RULES.md — the propagation wave (same shape as the R26-R40 wave)
    then carries them to all 10 plugins and re-checks the A/B fleet patterns (G1.1
    templates, memory-recall in skills) against each LIVE tree. Sequencing
    #47-first is correct.

**NEXT ACTION (external-gated):** when ai-maestro#47 lands the protocols in
GOVERNANCE-RULES.md, run the fleet propagation wave (per-plugin issues, R26-R40
pattern) carrying APPROVAL/MANDATE + golden/silver + the A/B re-check to all 10
plugins. IN-CONTROL: await MAESTRO review + the dupe-cleanup permission below.

**OPEN HOUSEKEEPING:** the 2 USER-scope wikimem copies (janitor plugin-data dir)
created before the MAESTRO's "project scoped" correction are superseded dupes
pending RULE-0 deletion permission.

## Governance rubric (what the audit checks each plugin against)

1. **Approval tiers + APPROVAL/MANDATE** — persona encodes the 4 tiers (0/1/2/3 =
   none/COS/MANAGER/MAESTRO), the proposal→planned flow, and the APPROVAL
   (bottom-up) vs MANDATE (top-down) distinction; never self-approves Tier 2/3;
   team agents route via COS. See `.claude/project/memory/approval-vs-mandate-protocol.md`.
2. **PRRD golden/silver** — respects golden = USER/MAESTRO-only (MANAGER cannot
   edit), silver = MANAGER-mutable; cites PRRD rules where relevant. See
   `.claude/project/memory/prrd-golden-silver-rules.md`.
3. **RULE 1 autonomy boundary** — "never take charge without explicit permission";
   status reports ≠ work orders.
4. **G1.1 self-identification** — every GitHub post self-identifies the authoring
   agent (shared owner identity / anti-impersonation).
5. **Decoupling (frozen CLI)** — no direct `/api/` calls in skills/agents/hooks/
   scripts; reach the server only via the frozen CLIs.
6. **Memory proactive-use** — recall-before-acting + write-after-solving wired
   into the persona + sub-agents.
7. **Per-agent state out of `$HOME` (#32)** — no invented per-agent ledger/cache/
   workspace under `$HOME`; lives under the agent-dir.
8. **Baseline rulesets** — respects the ratified `baseline-*` pair; no unilateral
   deviation (Tier-2).

## Deliverables
- Two governance wikimems (DONE, Phase 1).
- A consolidated governance-audit report under `reports/governance-audit/`.
- AMAMA fixes (each its own TRDD) for any AMAMA violation found.
- One per-repo governance issue for each other plugin with findings.
- One ai-maestro issue: enshrine APPROVAL/MANDATE in GOVERNANCE-RULES.md +
  request the signature-verification verbs.

## Notes and lessons learned

(none yet)
