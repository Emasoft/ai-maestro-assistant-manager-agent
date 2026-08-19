---
name: approval-vs-mandate-protocol
description: "difference between an APPROVAL and a MANDATE / does this task need sign-off and from whom / who must sign a TRDD before I execute it / is a MANAGER or COS order binding / can an agent refuse a mandate / which authority signs which TRDD category (none / CHIEF-OF-STAFF / MANAGER / MAESTRO) / a golden-rule change needs whose approval / how does an agent verify a signature before executing"
ocd: 2026-06-21
lmd: 2026-08-19
publish-globally: true
metadata:
  node_type: memory
  type: reference
  tier: component
---

# APPROVAL vs MANDATE — the two AI-Maestro authorization protocols

^approval-vs-mandate-overview [desc: "Every governed action travels one of two paths — APPROVAL or MANDATE; both are signed, agent-verifiable, and binding, differing only in who initiates and which direction authority flows.", keywords: difference_between_an_approval_and_a_mandate the_two_AI-Maestro_authorization_protocols both_signed_verifiable_and_binding initiator_and_direction_of_authority, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
Codified 2026-06-21 at the MAESTRO's direction, complementing the existing
approval-tier framework. Every governed action travels one of two paths. **Both
are SIGNED, agent-VERIFIABLE, and BINDING** — they differ only in the INITIATOR
and the DIRECTION of authority. [^1] [^2]

## APPROVAL protocol (bottom-up — the agent asks)

^approval-protocol [desc: "APPROVAL protocol (bottom-up): the agent authors a TRDD proposal, routes it to the tier authority, who signs; the agent verifies the signature before executing — never before signed.", keywords: APPROVAL_protocol_bottom-up_the_agent_asks does_this_task_need_sign-off_and_from_whom agent_authors_a_TRDD_proposal_routes_to_COS_MANAGER_MAESTRO_who_signs until_signed_the_agent_must_not_execute declined_proposal_goes_to_design/refused, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
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
- This is the existing approval-tier flow — see `trdd-approval-tiers-permissions`
  (machine-LOCAL-scope page; the framework itself is in
  `~/.claude/rules/trdd-approval-tiers.md`).

## MANDATE protocol (top-down — the authority orders)

^mandate-protocol [desc: "MANDATE protocol (top-down): MANAGER/COS issues and signs an order; the agent verifies the signature and is bound to execute — a verified in-scope mandate cannot be refused.", keywords: MANDATE_protocol_top-down_the_authority_orders is_a_MANAGER_or_COS_order_binding can_an_agent_refuse_a_mandate a_verified_in-scope_mandate_cannot_be_refused agent_verifies_signature_then_is_bound_to_execute, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
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

^approval-mandate-symmetry [desc: "Comparison table: both protocols verify-then-execute and are binding; they differ only in who initiates and the direction of authority. An authority may only mandate within its own tier.", keywords: approval_vs_mandate_symmetry_comparison_the_one_difference both_verify_signature_then_execute_both_binding approval_gates_own_initiative_mandate_delivers_authority_initiative an_authority_can_only_mandate_within_its_own_tier, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
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

^signature-verification [desc: "Neither protocol allows acting on an unverified/forged signature; today the signature is the git-tracked Approval-log line, pending a cryptographic AID layer. Verify before executing — always.", keywords: how_does_an_agent_verify_a_signature_before_executing never_act_on_an_unverified_or_forged_signature today_the_signature_is_the_git-tracked_Approval_log_line cryptographically_verifiable_signature_depends_on_the_per-agent_identity_layer_AID verify_before_executing_always, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
Neither protocol lets an agent act on an UNVERIFIED or FORGED signature. Today the
signature is the dated, git-tracked `## Approval log` line in the TRDD
(`who / when / tier / rationale`) — auditable + greppable
(`findtrdd.py --grep "APPROVED"`). The stronger form is a **cryptographically
verifiable signature** bound to the signer's identity; that depends on the
per-agent identity layer (ai-maestro#46, AMP identity / the AID signing system).
Until that lands, the audit-log line + the shared-identity self-identification
(PRRD G1.1) are the verification surface. **Verify before executing — always.**

## Approval-requirements criteria — which authority must sign which category

^approval-tier-floor [desc: "The required signature is the HIGHEST trigger a TRDD hits (default: none, escalate only on a trigger) — the objective tier-floor from trdd-approval-tiers.md Part D.", keywords: which_authority_must_sign_which_TRDD_category_none_CHIEF-OF-STAFF_MANAGER_MAESTRO a_golden-rule_change_needs_whose_approval the_highest-trigger_objective_tier-floor_default_none tier_0_self-approved_own-scope_derived_NPT_EHT tier_2_MANAGER_silver-rule_cross-team_release_baseline-deviation tier_3_MAESTRO_golden-rule_shared_credentials_irreversible, type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
The required authority is the **highest** trigger a TRDD hits (default = none;
escalate only on a trigger). This is the objective tier-floor — see
`trdd-approval-tiers-permissions` (machine-LOCAL-scope page) and
`~/.claude/rules/trdd-approval-tiers.md`
Part D for the mechanical floor + the under-classification watchdog, and
`~/.claude/rules/manager-approval-defaults.md` for the EXEMPT vs NON-EXEMPT lists.

^65V0RHVA [keywords: required_signature_table_none_chief-of-staff_manager_maestro_which_TRDD_categories_need_it tier_0_self-approved_tier_1_team-internal tier_2_cross-team_silver-rule_release_baseline-deviation tier_3_golden-rule_shared_credentials_irreversible, desc: "the 4-row table mapping required signature (none/CHIEF-OF-STAFF/MANAGER/MAESTRO) to the TRDD categories that trigger it", type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
| Required signature | TRDD categories that need it |
|---|---|
| **none** (Tier 0 — self-approved; author directly in `design/tasks/` `column: planned`) | own-scope work; **DERIVED** tasks (NPT/EHT of an already-authorized task); reversible + local; applying the ratified baseline as-is; no governance / cross-project / release / baseline-deviation touch |
| **CHIEF-OF-STAFF** (Tier 1) | team-internal coordination affecting **other members of the same team** (reprioritizing team work, creating team-internal dependencies) |
| **MANAGER** (Tier 2) | cross-**team** or cross-**project**; a **SILVER** PRRD-rule change; a **persona** change; entering the **release pipeline** (publish/deploy to production); any **baseline-ruleset deviation** (extra rule, loosened check, new bypass actor); `.github/` workflows or rulesets; touching **another project's** source; architectural / first-of-kind / high-blast-radius |
| **MAESTRO (USER)** (Tier 3) | a **GOLDEN** PRRD-rule change, or **promote/demote** between golden↔silver; **shared credentials / the owner GitHub identity**; **irreversible / owner-facing / highest-stakes** (first production deploy of a new service, breaking public-API change); anything the **MANAGER itself cannot authorize** |

^MTC2O3N8 [keywords: worked_example_golden_rule_always_needs_maestro_approval MANAGER_cannot_sign_a_golden_rule_change MANAGER_may_only_file_a_proposal_and_wait, desc: "canonical worked example: any GOLDEN PRRD rule change always requires MAESTRO (USER) sign-off; the MANAGER cannot sign it and may only file a proposal", type: reference, ocd: 2026-06-21, lmd: 2026-06-21]
**Worked example (canonical):** anything that touches a **GOLDEN** PRRD rule ALWAYS
requires **MAESTRO (USER)** approval — the MANAGER cannot sign it (golden rules are
user-only; the MANAGER may only file a proposal and wait). See
[[prrd-golden-silver-rules]].

## Governed by / see also

- Governed by [[ai-maestro-fleet-hub-governance-and-security-governance]] (the approval-tiers glue).
- See also `trdd-approval-tiers-permissions` (the tier framework + the watchdog;
  machine-LOCAL-scope page, not linkable from this git-tracked page),
  [[prrd-golden-silver-rules]] (golden→MAESTRO, silver→MANAGER),
  `assistant-role-plugin-and-15-principles` (R36 — the chain obeys the MAESTRO;
  machine-LOCAL-scope page).
- See also [[verify-cross-repo-cited-sha-before-building-sha-verification-check]] —
  another agent says a commit/verb SHIPPED or is 'live on the branch' but I can't see it.


^ATOM-OV0I-V512 [desc: "MANAGER approval paths: trdd.sh approve/refuse (AID); governance.sh approve/reject = password-gated MAESTRO-only; transfers via transfer resolve", keywords: governance_approve_password_gated manager_cannot_approve_governance_request trddsh_approve_refuse transfer_resolve blocked-by_ids_only human_review_user_wait approval_call_fails_at_runtime, type: project, ocd: 2026-08-19, lmd: 2026-08-19]

Approval execution paths (hub ruling 2026-08-19, AMAMA v2.18.0): aimaestro-governance.sh approve|reject HARD-REQUIRE --password (USER authority, never passes through a model, R32) — the MANAGER never calls them; it records a verdict and surfaces the GovernanceRequest to the MAESTRO. The MANAGER's R28 path is aimaestro-trdd.sh approve <id> --approver W --rationale R / refuse <id> --reason R (AID-authorized, mints the portfolio token verify checks). Team transfers: aimaestro-governance.sh transfer resolve <id> --action approve|reject (no password). blocked-by: holds TRDD ids ONLY — USER-decision waits go to human_review; pure external waits to review-after + external-refs.

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
