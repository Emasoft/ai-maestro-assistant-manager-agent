---
trdd-id: 9a16554d-1e1e-4e37-bc9a-5624fb19e556
title: Fleet governance hardening — codify APPROVAL/MANDATE + audit role plugins for violations
column: dev
created: 2026-06-21T20:24:32+0200
updated: 2026-06-21T20:24:32+0200
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
- **Phase 2 — governance audit: NEXT.** Parallel agents (one per cached plugin)
  read the plugin's cache against the rubric below + write a findings report to
  `reports/governance-audit/`. Non-cached 5 → gh-fetch persona audit or
  self-audit issue.
- **Phase 3 — remediate:** AMAMA violations → fix directly (own TRDDs); other
  plugins → per-repo issues; ai-maestro issue → enshrine APPROVAL/MANDATE in the
  governance SSOT (GOVERNANCE-RULES.md) + request the signature-verification
  script verbs (so "the agent can verify" a signature is real).

**NEXT ACTION:** launch the Phase-2 parallel audit of the 5 cached plugins.

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
