---
trdd-id: D6H36I26
title: Build a MANAGER governance self-audit checklist as a decision-time surface
column: complete
created: 2026-08-04T13:35:57+0200
updated: 2026-08-18T20:05:00+0200
current-owner: amama
assignee: amama
priority: 3
severity: MEDIUM
effort: M
task-type: feature
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
delivery: direct-push
target-branch: main
external-refs: ["https://github.com/Emasoft/ai-maestro/issues/107"]
---

# TRDD-D6H36I26 — MANAGER governance self-audit checklist

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-08-18T20:05

**✅ DONE (hub PHASE-2 GO, 2026-08-18; fable-advisor design verdict followed).**
Shipped `skills/amama-governance-self-audit/SKILL.md` — 12 MANAGER-shaped
questions (transport R23 first; tier; authorship/no-self-approval R41; mandate-vs-
proposal; team lifecycle R29/R12.1; COS-only dispatch R6; command power R42/R42.8;
PRRD golden/silver; release gate §Y; baseline deviation §F; auth R32/R28/R26;
record R15.6) + R49 refusal-form note. Each question cites, never restates.
Wiring: persona skills-list entry, menu row (11→12, RP-SKILL-MENU-01), and a
decision-time pointer in the persona intro ("walk the checklist before any
governed act; one NO ⇒ escalate one tier"). `context: inline` deliberately (a
forked walk would re-create the #107 defect — citations must land in the deciding
context); explicit `background`/`user-invocable` per the frontmatter-intent test;
canonical R23 block copied verbatim per `design/specs/r23-frozen-cli-canonical.md`.
No `references/` dir — a per-question decision-rules file would restate the cited
rules (the S8.1→S8.2 drift trap); the AUTONOMOUS layout was borrowed only for the
enumerated-list shape. Verified: ALL repo test scripts pass (incl.
test_r23_conformance, test_skill_frontmatter_intent, test_skill_menu_matches_shipped,
test_governance_citations). ai_review = fable-advisor verdict + self-recheck;
human_review escalated to the hub per the 2026-08-18 dispatch.

## The gap

This plugin has **no self-audit checklist** — no surface an agent consults at the moment it
decides *"am I allowed to do this?"*. AUTONOMOUS's finding on `#107`, which I verified against my
own plugin, is that this is the load-bearing surface:

> a rule absent from it is a rule that is not enforced regardless of how emphatically the persona
> states it

Their measured instance: an agent walked their 12-question audit to decide whether an action was
allowed, and none of the twelve covered the transport it was about to use — so the checklist
would have returned ALLOWED for the exact action the persona forbade. The persona and the
checklist disagreed, and **the checklist is what gets consulted at decision time.**

I confirmed the same shape here from the other side: R23 was stated in only 1 of 10 skills
(`11d828b` fixed it), and my plugin having zero violations was a property of the current text,
not something it enforced.

## Why not simply copy theirs

Asked directly on `#107` whether a checklist is being standardized fleet-wide. Answer: **no, and
nobody currently has the authority to decide it** — they are a solo role-plugin and explicitly
declined to have their Q13 adopted unexamined. Their reasoning, which I accept:

- The valuable property is the **shape** (a decision-time surface), not the content.
- Most of their 13 questions are AUTONOMOUS-specific (workspace isolation, teamless AMP edges,
  identity immutability). A MANAGER shares maybe a third and needs its own for the powers this
  role holds and theirs does not — **team lifecycle, approval tiers, dispatch**.
- So a copy would be wrong here even where the mechanism is right.

Their suggested split, which this TRDD adopts: **standardize the transport question's substance
as shared text; keep the checklist itself role-shaped.**

## Scope when picked up

- Draft MANAGER-shaped questions covering at minimum: approval tiers and what this role may
  self-approve, dispatch/delegation authority, team lifecycle, PRRD golden-vs-silver authority,
  the publish/deploy gate, and the transport question (no direct server API — R23).
- The transport question carries **both** reasons the CLI is mandatory and names **hooks and
  scripts**, not just skills — a hook runs with no skill loaded (agreed with AUTONOMOUS on `#107`
  and already shipped into all 10 skills in `11d828b`).
- Decide placement: its own skill, or a section of an existing one. Their layout — enumerated
  list in `SKILL.md`, one decision rule per question in `references/` — is worth borrowing as
  structure even though the content is not.

## Notes and lessons learned

**Do not restate a rule this checklist governs — cite it.** Per the `S8.1`→`S8.2` correction
(`1856101`, `ai-maestro#109`), a rule that restates another is a copy claiming to be a reference,
and a bump to the original leaves the copy asserting the old form with nothing detecting the
divergence. A checklist is exactly the artifact that invites restating; each question should
point at the rule it enforces.
