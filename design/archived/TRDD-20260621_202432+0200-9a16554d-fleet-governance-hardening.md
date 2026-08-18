---
trdd-id: 9A16554D
title: Fleet governance hardening — codify APPROVAL/MANDATE + audit role plugins for violations
column: complete
created: 2026-06-21T20:24:32+0200
updated: 2026-08-18T20:35:00+0200
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

**✅ #47's CONTENT LANDED (verified 2026-07-17):** the protocols are codified as
**R41. APPROVAL vs MANDATE** in `GOVERNANCE-RULES.md` v4.5.0 @ `?ref=governance-rules`
(L1443), bodied and readable — even though the *issue* ai-maestro#47 is still OPEN.
Issue-state ≠ content-state; judge from the rule BODY on the readable ref, never
from the tracker. So the propagation wave's precondition is MET.

**✅ PROPAGATION WAVE FIRED 2026-08-18 (hub GO under recorded USER delegation,
hub record TRDD-BRRJK57P) — CARD COMPLETE.** 10 per-plugin issues posted, R41
cited as canonical (never restated), G1.1 self-ID on each, zero bare handles:
orchestrator#34, architect#27, integrator#25, programmer#29, chief-of-staff#30,
autonomous#19 (folds their #12), maintainer#41 (folds #18), core ai-maestro-plugin#63
(folds #14), amvcp#10 (folds #7), AMAMA#37 (verified-compliant ledger, closed).
All deliverables of this card are now done; per-plugin follow-through happens on
each repo's own pipeline.

**✅ HOUSEKEEPING RESOLVED — by MERGE, not deletion (`4094cd8`).** The two
USER-scope wikimem copies were recorded above as "superseded dupes pending RULE-0
deletion permission". **That framing was WRONG and is retracted.** Diffing them
before proposing any delete (RULE 0) showed the copies in the *wrong scope* were
the **newer, richer** ones: 3-4 days ahead and carrying **14 `^anchor` recall
blocks (~4.7 KB)** the canonical PROJECT copies never had. Deleting them would have
destroyed the symptom-indexed recall surface and kept the thinner files. All 14
anchors are now ported into the PROJECT copies and the merge is verified lossless
(nothing remains only in the USER copies but a stale `lmd:` and an empty
placeholder). The USER-scope originals are UNTOUCHED and stay that way absent an
explicit USER decision — nothing about them is pending on the USER's desk, because
their content is now safe in the canonical scope. See the `[^1]` lesson atom
`ATOM-DUPE-IS-NEWER` on `.claude/project/memory/approval-vs-mandate-protocol.md`.

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

## Acceptance (closing checklist)

- [x] Two governance wikimems written (Phase 1): `approval-vs-mandate-protocol.md`, `prrd-golden-silver-rules.md`, in AMAMA PROJECT scope, git-tracked.
- [x] Governance audit of all 5 locally-cached plugins completed and verified against live working trees; reports under `reports/governance-audit/`.
- [x] ai-maestro#47 landed as R41 (APPROVAL vs MANDATE) in GOVERNANCE-RULES.md v4.5.0.
- [x] Propagation wave fired 2026-08-18 (hub GO, TRDD-BRRJK57P): 10 per-plugin issues posted citing R41, all with G1.1 self-ID, zero bare handles.
- [x] AMAMA finding A fixed and verified (G1.1 self-id note added to 3 gh-post skill files, commit `225b251`).
- [x] USER-scope vs PROJECT-scope wikimem duplication resolved by lossless merge (`4094cd8`), not deletion — 14 recall anchors ported into the canonical PROJECT copies.

Closed complete on 2026-08-19 per TRDD-QX6VFAXS corpus hygiene pass.
