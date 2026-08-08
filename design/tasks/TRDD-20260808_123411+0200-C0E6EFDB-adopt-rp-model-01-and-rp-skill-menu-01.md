---
trdd-id: C0E6EFDB
title: Adopt RP-MODEL-01 and RP-SKILL-MENU-01 from role-plugins-spec 1.1.0
column: complete
created: 2026-08-08T12:34:11+0200
updated: 2026-08-08T12:34:11+0200
current-owner: amama-session
task-type: infra
approval-tier: 0
relevant-rules: []
external-refs: ["https://github.com/Emasoft/ai-maestro/issues/136"]
---

# Adopt RP-MODEL-01 + RP-SKILL-MENU-01 (role-plugins-spec 1.1.0)

Tier 0: applying a ratified upstream spec clause to this plugin's own tree, no
deviation, no other team affected.

## Source, verified first-hand

`design/specs/role-plugins-spec.md` **spec-version 1.1.0** on `governance-rules`,
tip **`eaf609ad`** — fetched and read, not taken from the routing note.

## What the clauses require, and what this repo did

**RP-MODEL-01** (RULED 2026-08-08, ai-maestro#136, closes TRDD-TYB3Q1NJ): role-plugin
MAIN agents omit `model:`, same as subagents. Migration is on-next-release; carrying
a key past that publish is a conformance failure.

- `ai-maestro-assistant-manager-agent-main-agent.md` pinned `model: opus` -> **key dropped**.
- `amama-report-generator.md` (a SUBAGENT) also pinned `model: opus` -> **key dropped**.

The subagent is the finding worth reporting: the spec's rationale asserts subagents
"already omit `model:` everywhere", and this file was a live counterexample. A
universal disproved by one file is exactly the shape of error RP-MODEL-01 was itself
correcting, so it goes upstream rather than being quietly fixed.

**RP-SKILL-MENU-01** (new): the main agent MUST carry a compact skill menu, one line
per shipped skill, updated in the SAME change that touches any skill.

- Measured before: all 11 skill names appeared in the persona, but scattered through
  prose with **no menu section** — coverage, not a menu. The upstream survey listed
  AMAMA as "menu present", which was generous.
- Added: an 11-row table (name + when to reach for it) ahead of the Memory Protocol.

## Guardrail

`tests/test_skill_menu_matches_shipped.py` fails when the menu and `skills/*/SKILL.md`
disagree in EITHER direction, and when any agent file carries a `model:` key. Teeth
confirmed by simulating the pre-change state in memory: the model check fires.
Non-vacuity guards included — an empty parsed menu fails loudly rather than reporting
a clean sync over nothing.

## Acceptance criteria

- [x] Both agent files carry no `model:` key
- [x] Skill menu present with exactly the shipped skills (11)
- [x] Conformance test added and green
- [x] Published, and the release reported upstream with tag + tip sha
