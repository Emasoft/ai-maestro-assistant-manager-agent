---
name: prrd-golden-silver-rules
description: "golden vs silver PRRD rules / what is the PRRD (Project Requirements & Rules Document) / who can change a golden rule / can the MANAGER edit a golden rule / promote or demote a rule / PRRD rule citation grammar PRRD G64.134 / rule numbering and versioning / where a project keeps its rules / which rule changes need MAESTRO vs MANAGER approval"
ocd: 2026-06-21
lmd: 2026-07-17
metadata:
  node_type: memory
  type: reference
  tier: component
---

# PRRD — golden & silver rules (the project's constitution)

## The PRRD

^prrd-what [keywords: what is the PRRD Project Requirements and Rules Document, where a project keeps its rules, the single authoritative rules document one per project overrides any convention, design/requirements/PRRD.md git-tracked, tools get-prrd prrd-edit findprrd, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

The **PRRD (Project Requirements & Rules Document)** is the single authoritative
rules document for a project, at `<repo-root>/design/requirements/PRRD.md`,
**git-tracked** (never gitignored). Exactly ONE per project; it overrides any
general convention. Every agent that authors a TRDD, writes code, or proposes a
decision MUST read it first and comply. Full rule:
`~/.claude/rules/prrd-design-rules.md`. Tools: `get-prrd.py` (read),
`prrd-edit.py` (mutate — authority-checked), `findprrd.py` (search).

## GOLDEN 🥇 vs SILVER 🥈

^golden-vs-silver [keywords: golden vs silver PRRD rules, who can change a golden rule, can the MANAGER edit a golden rule, GOLDEN set by USER MAESTRO immutable to MANAGER only USER mutates, SILVER MANAGER-mutable without user approval, non-MANAGER agents propose via CHIEF-OF-STAFF, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

- **GOLDEN** — set by the **USER (= MAESTRO)**, **immutable to the MANAGER**. Only
  the USER can add / revise / delete / promote / demote a golden rule. Any agent —
  *including the MANAGER* — that thinks a golden rule needs changing files a
  **proposal** and waits for the USER (a Tier-3 / MAESTRO approval — see
  [[approval-vs-mandate-protocol]]).
- **SILVER** — **MANAGER-mutable**. The MANAGER may add / revise / delete / promote
  silver rules WITHOUT user approval (Tier-2). Non-MANAGER agents **propose** via
  their CHIEF-OF-STAFF; the MANAGER decides.

## Rule identity — `<letter><number>.<version>`

^rule-identity [keywords: PRRD rule numbering and versioning, rule identity letter number version, letter G S flips on promote demote, number globally unique across G and S never reused even after deletion, version edit counter forward-only, number is the stable machine id, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

Three pieces joined, e.g. `G64.134`:

| Piece | Meaning | Mutable? |
|---|---|---|
| **letter** `G`/`S` | current authority (golden / silver) | YES — flips on promote/demote |
| **number** | globally-unique id across BOTH G and S; **never reused** (even after deletion) | NO |
| **version** | edit counter; bumps on every text change | forward-only |

`G7` and `S7` cannot coexist — rule 7 is golden OR silver at any moment. The
**number is the stable machine id**; the letter is a human-facing live annotation.

## Promote / demote / edit — keep the identity, flip the letter

^promote-demote [keywords: promote or demote a rule, edit revise text bumps version, promote S to G demote G to S flips letter keeps number and version, delete retires the number forever, load-bearing invariant a citation by number points at the same rule regardless of current letter, lookup tools ignore the G/S, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

| Operation | Before → After | What changes |
|---|---|---|
| Edit (revise text) | `S70.3 → S70.4` | version bumps; letter unchanged |
| Promote (S→G) | `S70.3 → G70.3` | letter flips; number + version stay |
| Demote (G→S) | `G70.3 → S70.3` | letter flips; number + version stay |
| Delete | `S70.3 → —` | rule removed; number 70 **retired forever** |

**Load-bearing invariant:** a citation BY NUMBER points at the same rule
regardless of the current letter. A TRDD citing `PRRD G70.3` stays correct after
rule 70 demotes to silver (the TEXT is unchanged; only authority flipped). Lookup
tools accept the number alone and IGNORE the caller's G/S.

## Citation grammar

^citation-grammar [keywords: PRRD rule citation grammar PRRD G64.134, how to cite a PRRD rule, space mandatory greppable letter for humans number for machines, pinned G64.134 vs latest G64 vs letter-omitted 64.134, relevant-rules frontmatter plus inline body citation, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

`PRRD G64.134` — **space mandatory** (greppable), **letter for humans**, **number
for machines**. Forms: `PRRD G64.134` (pinned, default), `PRRD G64` (latest
version — follows future revisions), `PRRD 64.134` (letter omitted, valid). In a
TRDD: `relevant-rules: [3, 27, 64.134]` (frontmatter) + inline `PRRD G64.134`
(body).

## Mutation authority (who can change what) — ties to the approval tiers

^mutation-authority [keywords: which rule changes need MAESTRO vs MANAGER approval, who can change what golden silver, USER MAESTRO is the only one who mutates golden, MANAGER mutates silver Tier 2 but must propose golden to USER Tier 3, COS and team agents only propose, golden-rule change is MAESTRO approval silver is MANAGER, prrd-edit enforces caller_is_manager, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

| Actor | GOLDEN rules | SILVER rules |
|---|---|---|
| **USER / MAESTRO** | add/revise/delete/promote/demote (the ONLY one) | yes (directly, or demote-first) |
| **MANAGER** | **NO** — must propose to the USER (Tier 3) | add/revise/delete/promote (Tier 2, no user approval) |
| **CHIEF-OF-STAFF** | no — funnels team proposals to the MANAGER | no direct edit — proposes |
| **Team agents** (ORCH/ARCH/INT/MEMBER) | no | no — propose via their COS |

So a **golden-rule** change is always a **MAESTRO** approval; a **silver-rule**
change is a **MANAGER** approval; both flow through the
[[approval-vs-mandate-protocol]] (a proposal the authority signs). `prrd-edit.py`
enforces this (`caller_is_manager()`; golden mutations require `--user`).

## Proposal queue

^proposal-queue [keywords: PRRD proposal queue, how a non-authorized agent requests a rule change, writes a PROPOSAL file proposes revise add delete promote demote, COS forwards to MANAGER who decides accept reject or forward golden to USER, the proposal dir is never purged the audit trail, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

A non-authorized agent writes a proposal to
`<repo-root>/design/requirements/proposals/PROPOSAL-<ts>-<uid8>-<slug>.md`
(`proposes: revise|add|delete|promote|demote`, `target-rule:`, `status: open`).
COS forwards to MANAGER; MANAGER decides (accept → runs `prrd-edit.py`; reject →
records rationale; golden → forwards to USER). The proposal dir is NEVER purged —
it is the audit trail.

## Baseline golden rule G1.1

^baseline-g1-1 [keywords: baseline golden rule G1.1 GitHub authorship self-identification, every agent writing to GitHub begins with a one-line self-identification, shared owner identity anti-impersonation control golden so MANAGER cannot weaken it, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]

Every AI-Maestro PRRD SHOULD carry, as `G1.1`, the GitHub authorship
self-identification rule: every agent that writes to GitHub begins the body with a
one-line self-identification of which agent authored it (shared owner identity).
It is GOLDEN (user-set, immutable to MANAGER) because it is an anti-impersonation
control the MANAGER must not be able to weaken.

## Governed by / see also

- Governed by [[ai-maestro-fleet-hub-governance-and-security]] (pillar 1 — PRRD).
- See also [[approval-vs-mandate-protocol]] (golden→MAESTRO, silver→MANAGER tiers),
  [[trdd-approval-tiers-permissions]], [[assistant-role-plugin-and-15-principles]].

## Notes and lessons learned

[^1]: [id:ATOM-TIER-BY-LINK-DIRECTION, status:valid, keywords:"wikimem tier aspect or component which_tier_for_this_page governed_by_vs_applies_to", ocd:2026-07-17, lmd:2026-07-17]
  DO NOT tag a page `tier: aspect` because its subject sounds like a general rule,
  BECAUSE the tier is decided by the page's LINK DIRECTION, not its topic: an aspect
  RADIATES an `## Applies to` list down; a component RECEIVES and carries `## Governed
  by` up. This page has `## Governed by` and no `## Applies to` — it is a component,
  and `aspect` was wrong. DO read the page's own link sections to classify it. (Same
  error, same day, on [[approval-vs-mandate-protocol]] — it was a pattern, not a slip.)
