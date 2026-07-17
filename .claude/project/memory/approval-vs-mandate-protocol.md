---
name: approval-vs-mandate-protocol
description: "difference between an APPROVAL and a MANDATE / does this task need sign-off and from whom / who must sign a TRDD before I execute it / is a MANAGER or COS order binding / can an agent refuse a mandate / which authority signs which TRDD category (none / CHIEF-OF-STAFF / MANAGER / MAESTRO) / a golden-rule change needs whose approval / how does an agent verify a signature before executing"
ocd: 2026-06-21
lmd: 2026-07-17
metadata:
  node_type: memory
  type: reference
  tier: component
---

# APPROVAL vs MANDATE — the two AI-Maestro authorization protocols

^approval-vs-mandate-overview [keywords: difference between an approval and a mandate, the two AI-Maestro authorization protocols, both signed verifiable and binding, initiator and direction of authority, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]

Codified 2026-06-21 at the MAESTRO's direction, complementing the existing
approval-tier framework. Every governed action travels one of two paths. **Both
are SIGNED, agent-VERIFIABLE, and BINDING** — they differ only in the INITIATOR
and the DIRECTION of authority.

## APPROVAL protocol (bottom-up — the agent asks)

^approval-protocol [keywords: APPROVAL protocol bottom-up the agent asks, does this task need sign-off and from whom, agent authors a TRDD proposal routes to COS MANAGER MAESTRO who signs, until signed the agent must not execute, declined proposal goes to design/refused, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]

- **Initiator:** any agent (including the MANAGER, when it needs MAESTRO sign-off).
- **Artifact:** a TRDD **proposal** (`design/proposals/`, `column: proposal`) OR a
  specific written proposal.
- **Flow:** the agent authors the proposal → routes it to the authority its *tier*
  requires (COS / MANAGER / MAESTRO) → that authority **SIGNS** it (approves,
  recorded in the TRDD `## Approval log`) → the agent **VERIFIES** the signature is
  authentic → the proposal is promoted (`git mv design/proposals → design/tasks`,
  `column: planned`) and the agent is **BOUND to execute** it.
- **Until signed, the agent MUST NOT execute.** A declined proposal goes to
  `design/refused/` (`column: refused`) and must NOT be executed.
- This is the existing approval-tier flow — see [[trdd-approval-tiers-permissions]].

## MANDATE protocol (top-down — the authority orders)

^mandate-protocol [keywords: MANDATE protocol top-down the authority orders, is a MANAGER or COS order binding, can an agent refuse a mandate, a verified in-scope mandate cannot be refused, agent verifies signature then is bound to execute, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]

- **Initiator:** the MANAGER or a CHIEF-OF-STAFF (the governance authority for that
  scope).
- **Artifact:** a TRDD authored/assigned by the authority (e.g. dispatched to an
  `assignee:`) OR a specific written order.
- **Flow:** the authority issues + **SIGNS** the mandate → the receiving agent
  **VERIFIES** the signature is authentic (the MANAGER/COS really issued it) → the
  agent is **BOUND to execute** it.
- **A verified, in-scope mandate cannot be refused.** The agent MAY (and must) flag
  a genuine problem and wait, but it executes the mandate — it does not silently
  drop, ignore, or unilaterally override it.

## The symmetry (and the one difference)

^approval-mandate-symmetry [keywords: approval vs mandate symmetry comparison the one difference, both verify signature then execute both binding, approval gates own initiative mandate delivers authority initiative, an authority can only mandate within its own tier, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]

| | APPROVAL | MANDATE |
|---|---|---|
| Initiated by | an **agent** (request up) | **MANAGER / COS** (order down) |
| Signed by | the required authority (COS/MANAGER/MAESTRO) | the issuing MANAGER / COS |
| Direction | bottom-up (ask → sign → do) | top-down (order → verify → do) |
| Agent action | verify signature, then execute | verify signature, then execute |
| Binding? | yes (once approved) | yes (once verified) |

APPROVAL gates an agent's OWN initiative on an authority's sign-off; MANDATE
delivers an authority's initiative for the agent to carry out. An authority can
only MANDATE **within its own tier** (a COS cannot mandate a golden-rule change —
that is MAESTRO-only; see the criteria table).

## Verification — "the agent can verify"

^signature-verification [keywords: how does an agent verify a signature before executing, never act on an unverified or forged signature, today the signature is the git-tracked Approval log line, cryptographically verifiable signature depends on the per-agent identity layer AID, verify before executing always, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]

Neither protocol lets an agent act on an UNVERIFIED or FORGED signature. Today the
signature is the dated, git-tracked `## Approval log` line in the TRDD
(`who / when / tier / rationale`) — auditable + greppable
(`findtrdd.py --grep "APPROVED"`). The stronger form is a **cryptographically
verifiable signature** bound to the signer's identity; that depends on the
per-agent identity layer (ai-maestro#46, AMP identity / the AID signing system).
Until that lands, the audit-log line + the shared-identity self-identification
(PRRD G1.1) are the verification surface. **Verify before executing — always.**

## Approval-requirements criteria — which authority must sign which category

^approval-tier-floor [keywords: which authority must sign which TRDD category none CHIEF-OF-STAFF MANAGER MAESTRO, a golden-rule change needs whose approval, the highest-trigger objective tier-floor default none, tier 0 self-approved own-scope derived NPT EHT, tier 2 MANAGER silver-rule cross-team release baseline-deviation, tier 3 MAESTRO golden-rule shared credentials irreversible, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]

The required authority is the **highest** trigger a TRDD hits (default = none;
escalate only on a trigger). This is the objective tier-floor — see
[[trdd-approval-tiers-permissions]] and `~/.claude/rules/trdd-approval-tiers.md`
Part D for the mechanical floor + the under-classification watchdog, and
`~/.claude/rules/manager-approval-defaults.md` for the EXEMPT vs NON-EXEMPT lists.

| Required signature | TRDD categories that need it |
|---|---|
| **none** (Tier 0 — self-approved; author directly in `design/tasks/` `column: planned`) | own-scope work; **DERIVED** tasks (NPT/EHT of an already-authorized task); reversible + local; applying the ratified baseline as-is; no governance / cross-project / release / baseline-deviation touch |
| **CHIEF-OF-STAFF** (Tier 1) | team-internal coordination affecting **other members of the same team** (reprioritizing team work, creating team-internal dependencies) |
| **MANAGER** (Tier 2) | cross-**team** or cross-**project**; a **SILVER** PRRD-rule change; a **persona** change; entering the **release pipeline** (publish/deploy to production); any **baseline-ruleset deviation** (extra rule, loosened check, new bypass actor); `.github/` workflows or rulesets; touching **another project's** source; architectural / first-of-kind / high-blast-radius |
| **MAESTRO (USER)** (Tier 3) | a **GOLDEN** PRRD-rule change, or **promote/demote** between golden↔silver; **shared credentials / the owner GitHub identity**; **irreversible / owner-facing / highest-stakes** (first production deploy of a new service, breaking public-API change); anything the **MANAGER itself cannot authorize** |

**Worked example (canonical):** anything that touches a **GOLDEN** PRRD rule ALWAYS
requires **MAESTRO (USER)** approval — the MANAGER cannot sign it (golden rules are
user-only; the MANAGER may only file a proposal and wait). See
[[prrd-golden-silver-rules]].

## Governed by / see also

- Governed by [[ai-maestro-fleet-hub-governance-and-security]] (the approval-tiers glue).
- See also [[trdd-approval-tiers-permissions]] (the tier framework + the watchdog),
  [[prrd-golden-silver-rules]] (golden→MAESTRO, silver→MANAGER),
  [[assistant-role-plugin-and-15-principles]] (R36 — the chain obeys the MAESTRO).

## Notes and lessons learned

[^1]: [id:ATOM-DUPE-IS-NEWER, status:valid, keywords:"superseded_dupe_pending_deletion two_copies_of_a_memory_note which_scope_wins delete_the_duplicate_copy diverged_copies", ocd:2026-07-17, lmd:2026-07-17]
  DO NOT delete a memory page called a "superseded dupe" on the strength of that
  label, BECAUSE the copy in the WRONG scope can be the NEWER and RICHER one — this
  page's USER-scope twin was 3 days newer and carried 6 `^anchor` recall blocks the
  canonical PROJECT copy never had (~2 KB), so deleting it would have destroyed the
  recall surface and kept the thinner file. DO diff the copies first and MERGE
  (port what only the doomed copy has), then treat the source as redundant.

[^2]: [id:ATOM-TIER-ASPECT-VS-COMPONENT, status:valid, keywords:"wikimem tier aspect or component which_tier_for_this_page governed_by_vs_applies_to", ocd:2026-07-17, lmd:2026-07-17]
  DO NOT tag a page `tier: aspect` because its subject sounds like a general rule,
  BECAUSE the tier is decided by the page's LINK DIRECTION, not its topic: an aspect
  RADIATES an `## Applies to` list down; a component RECEIVES and carries `## Governed
  by` up. This page has `## Governed by` and no `## Applies to` — it is a component,
  and `aspect` was wrong. DO read the page's own link sections to classify it.
