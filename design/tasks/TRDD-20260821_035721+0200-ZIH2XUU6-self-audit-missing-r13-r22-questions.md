---
trdd-id: ZIH2XUU6
title: Governance self-audit misses R13.2 no-implementation and R22 GitHub-authorship
column: todo
created: 2026-08-21T03:57:21+0200
updated: 2026-08-21T04:12:00+0200
current-owner: amama
assignee: amama
priority: 2
severity: HIGH
effort: S
task-type: bugfix
min-approval-requirement: none
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
external-refs: ["https://github.com/Emasoft/ai-maestro/issues/107"]
---

# TRDD-ZIH2XUU6 — the self-audit misses R13.2 and R22

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-21T03:57

Filed from the hub's async review of TRDD-D6H36I26 (which stays **archived and frozen**
— findings produce this new card, never an edit to that one). Hub report:
`reports/fleet-audit/20260821_034315+0200-amama-D6H36I26-governance-self-audit-review.md`
in the hub repo `Emasoft/ai-maestro`.

**NEXT ACTION:** add a 13th question (R13.2, no-implementation) and a 14th (R22,
GitHub authorship byline) to `skills/amama-governance-self-audit/SKILL.md`, citing —
never restating — each rule; then update the menu row count and the persona skills-list
entry the same way TRDD-D6H36I26 did (11→12 becomes 12→14, `RP-SKILL-MENU-01`), and
re-run the repo test scripts including `test_skill_menu_matches_shipped` and
`test_governance_citations`.

Not started. Nothing is blocked on this; the shipped skill is wrong-by-omission, not
broken.

## The finding — verified first-hand, not taken from the report

The checklist is the decision-time surface, so a governed power missing from it is
unenforced regardless of how emphatically the persona states it (`ai-maestro#107`). The
review found the persona's **single most absolute constraint** is exactly such a gap.

**A1 (PRIMARY).** The act: MANAGER authors a Tier-0 self-mandated card
(`min-approval-requirement: none`, own scope, reversible) and **implements it itself** —
edits files, commits. All 12 questions answer YES: Q2 passes (`none` ≤ `manager`), Q4
passes (born approved), Q7 passes (own session, R42.4), Q6 is vacuous (no team
contacted), Q9–Q12 pass. Twelve YES, and the act is forbidden.

**A4 (same shape).** The act: MANAGER posts a GitHub issue comment. Q12 covers the
record (Approval log, AMP) but nothing covers the R22.1 authorship byline, so a
governed GitHub write walks the 12 clean with no self-identification line.

Measured in this repo and against the hub, with the positive control that makes the
zeros results rather than a broken needle:

| Check | Result |
|---|---|
| `grep -c 'R13' skills/amama-governance-self-audit/SKILL.md` | `0` |
| `grep -c 'R22' skills/amama-governance-self-audit/SKILL.md` | `0` |
| `grep -rln 'R13' skills/` (id needle, all skills) | empty |
| `grep -rlniE 'never write code\|no implementation\|does not write code\|write the code' skills/` (CONCEPT needle) | empty |
| cited ids actually present in the 12 | R6 · R12.1 · R15.6 · R23.1–R23.5 · R26 · R28–R32 · R41 · R42/R42.8 · R49 |
| persona constraint | `agents/ai-maestro-assistant-manager-agent-main-agent.md:121` — "**NO IMPLEMENTATION — THE ONE ABSOLUTE BOUNDARY (R13.2)** … never write code and never develop software … not 'just this once because it is small or urgent'" |
| `Emasoft/ai-maestro@fork/main` — `docs/GOVERNANCE-RULES.md:581` (fetched via `gh api`) | R13.2, verdict **Explicit** — "Does **NOT** write code, does **NOT** design architecture…" |
| `Emasoft/ai-maestro@fork/main` — `docs/GOVERNANCE-RULES.md:1196` | R22.1, verdict **Explicit (USER)** — every agent writing to GitHub MUST begin the body with a one-line self-identification |

**The tree is part of the citation.** A local hub checkout reads R13.2 at `:583`, not
`:581` — that working tree is 313 commits ahead of `fork/main`, two of them above R13.2.
Both line numbers are correct *of the tree they were read from*, so a line citation with
no tree named is ambiguous by construction. The lines above name the pushed copy anyone
can fetch; prefer that form. (The 313 unpushed commits are the USER's to push — noted
here only because they explain the delta, not as work for this card.)

The concept needle matters more than the id needle: it proves the rule is **verified
absent**, not merely uncited under a different spelling.

## Not confirmed — reviewer candidates, treat as unverified

- **A2** — MANAGER doing the ORCHESTRATOR's job (R13.5) through the COS, waved through
  by Q6 because the topology question only asks *whether* the COS was the channel, not
  *what* was sent through it. Shares A1's root cause. **Not verified here.**
- **A3** — the stated decision rule is polarity-inverted for 4 of the 12, each inversion
  failing OPEN. **Not verified here.** Verify before acting; a polarity claim is cheap to
  check and expensive to get wrong.

## Negative results worth keeping

- **Citation integrity: 20/20 resolve, 0 rot**, cross-tree anchors included. The
  both-trees resolution rule that made this trustworthy is recorded at
  `.claude/project/memory/governance-self-audit-cites-hub-overlay.md`.
- **N1 — the AMP-only directive of `f7e239f` is COVERED by Q12.** Offered as the
  strongest candidate against the artifact and it held. A gap proven closed is worth as
  much as one found open, and it only counts with the catching question named.

## Notes and lessons learned

**The checklist's own "keeping this list honest" section did not save it.** The skill
already says a new MANAGER power must arrive with its question in the SAME change — but
R13.2 is not a *new* power, it is a standing prohibition that predates the checklist, so
nothing triggered the rule. A checklist built by enumerating *powers* will systematically
miss *prohibitions*, which is why the absolute one went missing while twelve narrower
rules were caught. Any fix should say so, or the next omission is the same shape.

**Q13/Q14 close the two instances; the CLASS stays open until both halves land.** The
maintenance rule must fire on a prohibition, not only on a new power — *"new or
newly-discovered PROHIBITION ⇒ its question in the same change"* — and someone must do
one sweep of the standing prohibitions that predate the checklist, because by definition
none of them ever triggered a "new power" event. Two rows fix today; the rule change plus
the sweep fix the next one.

## Acceptance (closing checklist)

- [ ] Q13 added — no-implementation, citing R13.2 (hub `docs/GOVERNANCE-RULES.md`; the
      normative text is `design/specs/governance-spec.md` on `governance-rules`), never
      restating it, and naming the "not just this once" form the persona uses.
- [ ] Q14 added — GitHub authorship byline, citing R22.1–R22.3, including the deliberate
      no-`@` form.
- [ ] Menu row count and persona skills-list entry updated in the SAME change
      (`RP-SKILL-MENU-01`).
- [ ] "Keeping this list honest" amended to fire on a prohibition too — "new or
      newly-discovered PROHIBITION ⇒ its question in the same change" — not only on a new
      power.
- [ ] ONE sweep of the standing prohibitions that predate the checklist (they trigger no
      "new power" event, so nothing else will ever surface them). Any further gap it finds
      gets its own card; this box closes when the sweep has been run, not when it comes
      back empty.
- [ ] A2 and A3 read and either confirmed (own card or folded in here) or recorded as
      refuted with what was tried.
- [ ] All repo test scripts pass, incl. `test_skill_menu_matches_shipped`,
      `test_governance_citations`, `test_skill_frontmatter_intent`, `test_r23_conformance`.
