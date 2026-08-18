---
trdd-id: MCP7W45G
title: Apply hub-review patches to the governance self-audit checklist
column: complete
created: 2026-08-18T20:13:13+0200
updated: 2026-08-18T20:13:13+0200
current-owner: amama
assignee: amama
priority: 2
severity: MEDIUM
effort: XS
task-type: bugfix
parent-trdd: TRDD-D6H36I26
npt: []
eht: []
blocked-by: []
min-approval-requirement: none
release-via: none
delivery: direct-push
target-branch: main
---

# TRDD-MCP7W45G — hub-review patches to amama-governance-self-audit

Derived (Tier-0) card for the two REQUIRED patches from the hub's D6H36I26
review (2026-08-18, cross-session dispatch; verdict PASS WITH TWO REQUIRED
PATCHES). Both defects verified first-hand before patching:

1. **Q2 cited superseded vocabulary.** `approval-tier:` is deprecated,
   decode-only, never written on a new TRDD (overlay
   `rules/aimaestro/aimaestro-trdd-approval.md`, §"min-approval-requirement
   supersedes approval-tier", USER 2026-07-10); the machine-global
   `trdd-approval-tiers.md` is the stale predecessor. Q2 now keys on
   `min-approval-requirement:` (title ladder) and cites the overlay.
2. **Q10 called the ratified baseline a "pair".** It is a TRIO —
   `baseline-history-protect` + `baseline-pr-and-checks` +
   `baseline-tag-protect` (verified: `aimaestro-manager-approval-defaults.md`
   L152/L159 "Applying this baseline-* TRIO as-is is EXEMPT"). Q10 now names
   the trio, so re-applying the tag ruleset is not misread as a deviation.

## Approval log

- 2026-08-18T20:13:13+0200 — Tier-0 derived card (parent D6H36I26); patches
  mandated by the hub review message (ai-maestro MANAGER under recorded USER
  delegation, hub record TRDD-BRRJK57P). Hub: "No re-review needed if the diff
  matches the two patches." Diff matches; card closes complete.

## Acceptance (closing checklist)

- [x] Q2 patched to key on `min-approval-requirement:` (title ladder) and cite the `aimaestro-trdd-approval.md` overlay instead of the deprecated `approval-tier:` vocabulary.
- [x] Q10 patched to name the ratified baseline as the TRIO (`baseline-history-protect` + `baseline-pr-and-checks` + `baseline-tag-protect`), not a pair.
- [x] Both defects verified first-hand before patching.
- [x] Hub review confirmed diff matches the two mandated patches — no re-review needed.

Closed complete on 2026-08-19 per TRDD-QX6VFAXS corpus hygiene pass.
