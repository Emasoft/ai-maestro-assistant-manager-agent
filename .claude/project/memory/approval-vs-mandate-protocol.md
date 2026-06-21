---
name: approval-vs-mandate-protocol
description: "difference between an APPROVAL and a MANDATE / does this task need sign-off and from whom / who must sign a TRDD before I execute it / is a MANAGER or COS order binding / can an agent refuse a mandate / which authority signs which TRDD category (none / CHIEF-OF-STAFF / MANAGER / MAESTRO) / a golden-rule change needs whose approval / how does an agent verify a signature before executing"
ocd: 2026-06-21
lmd: 2026-06-21
metadata:
  node_type: memory
  type: reference
  tier: aspect
---

# APPROVAL vs MANDATE — the two AI-Maestro authorization protocols

Codified 2026-06-21 at the MAESTRO's direction, complementing the existing
approval-tier framework. Every governed action travels one of two paths. **Both
are SIGNED, agent-VERIFIABLE, and BINDING** — they differ only in the INITIATOR
and the DIRECTION of authority.

## APPROVAL protocol (bottom-up — the agent asks)

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

Neither protocol lets an agent act on an UNVERIFIED or FORGED signature. Today the
signature is the dated, git-tracked `## Approval log` line in the TRDD
(`who / when / tier / rationale`) — auditable + greppable
(`findtrdd.py --grep "APPROVED"`). The stronger form is a **cryptographically
verifiable signature** bound to the signer's identity; that depends on the
per-agent identity layer (ai-maestro#46, AMP identity / the AID signing system).
Until that lands, the audit-log line + the shared-identity self-identification
(PRRD G1.1) are the verification surface. **Verify before executing — always.**

## Approval-requirements criteria — which authority must sign which category

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

(none yet)
