---
trdd-id: EQULXUH8
title: Self-audit sweep found two more uncovered prohibitions — AMP URL-only and role-plugin-at-creation
column: complete
created: 2026-08-25T14:08:48+0200
updated: 2026-08-25T14:12:00+0200
current-owner: amama
assignee: amama
priority: 3
severity: MEDIUM
effort: S
task-type: bugfix
min-approval-requirement: none
parent-trdd: null
created-by: ZIH2XUU6
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
external-refs: ["https://github.com/Emasoft/ai-maestro/issues/107"]
---

# TRDD-EQULXUH8 — self-audit sweep findings: R15.4 and agent-creation constraints

Filed by TRDD-ZIH2XUU6's standing-prohibitions sweep (its acceptance says any
further gap gets its own card). Both candidates verified absent from
`skills/amama-governance-self-audit/SKILL.md` by full-file read plus id-needle
grep (0 hits for `R15.4`, `R9.13`, `R11.12`, `R12.3`, `role-plugin`, `URL`);
both rules verified present verbatim in the hub spec
(`design/specs/governance-spec.md` on `governance-rules`, lines 562 / 463 / 491
/ 508 as of 2026-08-25).

## The two gaps

1. **R15.4 amp-carries-url-only** — AMP messages carry only the GitHub
   issue/comment URL of an attachment, never the file content. Q12 covers
   *leaving* a record via AMP but nothing covers the payload constraint, so a
   MANAGER AMP send with inlined content walks the 14 clean.
2. **R9.13 / R11.12 role-plugin-mandatory + R12.3 one-role-per-agent** — the
   MANAGER creates teams and AUTONOMOUS/MAINTAINER agents; creation-time
   plugin/role constraints are uncited (Q5 cites R29/R12.1/R30/R31 only), so a
   plugin-less or dual-role creation walks the 14 clean.

## Acceptance

- [x] Q15 added — AMP attachment payload, citing R15.4, never restating it.
- [x] Q16 added — agent/team creation constraints, citing R9.13/R11.12/R12.3.
- [x] Menu row count (14→16), skill description, and safe-side enumeration
      updated in the SAME change (`RP-SKILL-MENU-01`).
- [x] `test_skill_menu_matches_shipped`, `test_governance_citations`,
      `test_skill_frontmatter_intent`, `test_r23_conformance`: 15 passed.

## Approval log

- 2026-08-25T14:12:00+0200 — `todo → complete` under the USER's blanket session
  directive. Implemented in the same session it was filed; all boxes verified.
