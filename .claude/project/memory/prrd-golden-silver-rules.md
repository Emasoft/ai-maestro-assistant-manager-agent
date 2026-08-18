---
name: prrd-golden-silver-rules
description: "golden vs silver PRRD rules / what is the PRRD (Project Requirements & Rules Document) / who can change a golden rule / can the MANAGER edit a golden rule / promote or demote a rule / PRRD rule citation grammar PRRD G64.134 / rule numbering and versioning / where a project keeps its rules / which rule changes need MAESTRO vs MANAGER approval"
ocd: 2026-06-21
lmd: 2026-08-18
publish-globally: true
metadata:
  node_type: memory
  type: reference
  tier: component
---

# PRRD — golden & silver rules (the project's constitution)

## The PRRD

^prrd-what [desc:"The PRRD is a project's single authoritative rules document, at design/requirements/PRRD.md, git-tracked, one per project, overriding any general convention.", keywords: what_is_the_PRRD_Project_Requirements_and_Rules_Document where_a_project_keeps_its_rules the_single_authoritative_rules_document_one_per_project_overrides_any_convention design/requirements/PRRD.md_git-tracked tools_get-prrd_prrd-edit_findprrd, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
The **PRRD (Project Requirements & Rules Document)** is the single authoritative
rules document for a project, at `<repo-root>/design/requirements/PRRD.md`,
**git-tracked** (never gitignored). Exactly ONE per project; it overrides any
general convention. Every agent that authors a TRDD, writes code, or proposes a
decision MUST read it first and comply. Full rule:
`~/.claude/rules/prrd-design-rules.md`. Tools: `get-prrd.py` (read),
`prrd-edit.py` (mutate — authority-checked), `findprrd.py` (search). [^2]

## GOLDEN 🥇 vs SILVER 🥈

^golden-vs-silver [desc:"GOLDEN rules are set by the USER only and immutable to the MANAGER; SILVER rules are MANAGER-mutable without user approval, with other agents proposing via their COS.", keywords: golden_vs_silver_PRRD_rules who_can_change_a_golden_rule can_the_MANAGER_edit_a_golden_rule GOLDEN_set_by_USER_MAESTRO_immutable_to_MANAGER_only_USER_mutates SILVER_MANAGER-mutable_without_user_approval non-MANAGER_agents_propose_via_CHIEF-OF-STAFF, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
- **GOLDEN** — set by the **USER (= MAESTRO)**, **immutable to the MANAGER**. Only
  the USER can add / revise / delete / promote / demote a golden rule. Any agent —
  *including the MANAGER* — that thinks a golden rule needs changing files a
  **proposal** and waits for the USER (a Tier-3 / MAESTRO approval — see
  [[approval-vs-mandate-protocol]]).
- **SILVER** — **MANAGER-mutable**. The MANAGER may add / revise / delete / promote
  silver rules WITHOUT user approval (Tier-2). Non-MANAGER agents **propose** via
  their CHIEF-OF-STAFF; the MANAGER decides.

## Rule identity — `<letter><number>.<version>`

^rule-identity [desc:"A PRRD rule's identity is <letter><number>.<version>: the letter flips on promote/demote, the number is globally unique and never reused, the version bumps forward-only.", keywords: PRRD_rule_numbering_and_versioning rule_identity_letter_number_version letter_G_S_flips_on_promote_demote number_globally_unique_across_G_and_S_never_reused_even_after_deletion version_edit_counter_forward-only number_is_the_stable_machine_id, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
Three pieces joined, e.g. `G64.134`:

| Piece | Meaning | Mutable? |
|---|---|---|
| **letter** `G`/`S` | current authority (golden / silver) | YES — flips on promote/demote |
| **number** | globally-unique id across BOTH G and S; **never reused** (even after deletion) | NO |
| **version** | edit counter; bumps on every text change | forward-only |

`G7` and `S7` cannot coexist — rule 7 is golden OR silver at any moment. The
**number is the stable machine id**; the letter is a human-facing live annotation.

## Promote / demote / edit — keep the identity, flip the letter

^promote-demote [desc:"Promote/demote flips a rule's letter but keeps its number and version; a citation by number always points at the same rule regardless of the current letter.", keywords: promote_or_demote_a_rule edit_revise_text_bumps_version promote_S_to_G_demote_G_to_S_flips_letter_keeps_number_and_version delete_retires_the_number_forever load-bearing_invariant_a_citation_by_number_points_at_the_same_rule_regardless_of_current_letter lookup_tools_ignore_the_G/S, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
| Operation | Before → After | What changes |
|---|---|---|
| Edit (revise text) | `S70.3 → S70.4` | version bumps; letter unchanged |
| Promote (S→G) | `S70.3 → G70.3` | letter flips; number + version stay |
| Demote (G→S) | `G70.3 → S70.3` | letter flips; number + version stay |
| Delete | `S70.3 → —` | rule removed; number 70 **retired forever** |

**Load-bearing invariant:** a citation BY NUMBER points at the same rule
regardless of the current letter. A TRDD citing `PRRD G70.3` stays correct after
rule 70 demotes to silver (the TEXT is unchanged; only authority flipped). Lookup
tools accept the number alone and IGNORE the caller's G/S. [^1]

## Citation grammar

^citation-grammar [desc:"How to cite a PRRD rule: `PRRD G64.134` (space mandatory, greppable) — the letter is for humans, the number for machines; pinned, latest, or letter-omitted forms are all valid.", keywords: PRRD_rule_citation_grammar_PRRD_G64.134 how_to_cite_a_PRRD_rule space_mandatory_greppable_letter_for_humans_number_for_machines pinned_G64.134_vs_latest_G64_vs_letter-omitted_64.134 relevant-rules_frontmatter_plus_inline_body_citation, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
`PRRD G64.134` — **space mandatory** (greppable), **letter for humans**, **number
for machines**. Forms: `PRRD G64.134` (pinned, default), `PRRD G64` (latest
version — follows future revisions), `PRRD 64.134` (letter omitted, valid). In a
TRDD: `relevant-rules: [3, 27, 64.134]` (frontmatter) + inline `PRRD G64.134`
(body).

## Mutation authority (who can change what) — ties to the approval tiers

^mutation-authority [desc:"Mutation authority table: only the USER/MAESTRO can mutate GOLDEN rules; the MANAGER can mutate SILVER rules directly but must propose GOLDEN changes to the USER.", keywords: which_rule_changes_need_MAESTRO_vs_MANAGER_approval who_can_change_what_golden_silver USER_MAESTRO_is_the_only_one_who_mutates_golden MANAGER_mutates_silver_Tier_2_but_must_propose_golden_to_USER_Tier_3 COS_and_team_agents_only_propose golden-rule_change_is_MAESTRO_approval_silver_is_MANAGER prrd-edit_enforces_caller_is_manager, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
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

^proposal-queue [desc:"How a non-authorized agent requests a PRRD rule change: it writes a PROPOSAL file, COS forwards it to the MANAGER who decides or forwards golden changes to the USER.", keywords: PRRD_proposal_queue how_a_non-authorized_agent_requests_a_rule_change writes_a_PROPOSAL_file_proposes_revise_add_delete_promote_demote COS_forwards_to_MANAGER_who_decides_accept_reject_or_forward_golden_to_USER the_proposal_dir_is_never_purged_the_audit_trail, type: reference, ocd: 2026-06-21, lmd: 2026-06-25]
A non-authorized agent writes a proposal to
`<repo-root>/design/requirements/proposals/PROPOSAL-<ts>-<uid8>-<slug>.md`
(`proposes: revise|add|delete|promote|demote`, `target-rule:`, `status: open`).
COS forwards to MANAGER; MANAGER decides (accept → runs `prrd-edit.py`; reject →
records rationale; golden → forwards to USER). The proposal dir is NEVER purged —
it is the audit trail.

## Baseline golden rule G1.1

^baseline-g1-1 [desc:"Baseline golden rule G1.1: every agent writing to GitHub begins with a self-identification line, because it is an authorship-integrity control the MANAGER must not weaken.", keywords: baseline_golden_rule_G1.1_GitHub_authorship_self-identification every_agent_writing_to_GitHub_begins_with_a_one-line_self-identification shared_owner_identity_authorship_integrity_control_golden_so_MANAGER_cannot_weaken_it, type: reference, ocd: 2026-06-21, lmd: 2026-08-18]
Every AI-Maestro PRRD SHOULD carry, as `G1.1`, the GitHub authorship
self-identification rule: every agent that writes to GitHub begins the body with a
one-line self-identification of which agent authored it (shared owner identity).
It is GOLDEN (user-set, immutable to MANAGER) because it is an authorship-integrity
control — it stops any agent's GitHub post passing as another author's — that the
MANAGER must not be able to weaken.

## Governed by / see also

- Governed by [[ai-maestro-fleet-hub-governance-and-security-governance]] (pillar 1 — PRRD).
- See also [[approval-vs-mandate-protocol]] (golden→MAESTRO, silver→MANAGER tiers),
  `trdd-approval-tiers-permissions` and `assistant-role-plugin-and-15-principles`
  (machine-LOCAL-scope pages, not linkable from this git-tracked page).
- See also [[governance-ssot-is-the-governance-rules-branch]] — which ref of the fleet's
  GOVERNANCE-RULES.md is authoritative (the `governance-rules` branch, not main).
- See also [[claude-plugin-dependencies]] — it carries the **other direction of the same
  defect**: there, a citation pins a version that later moves and dangles; here, the text
  moves while the version does not. One root cause (the version is an unchecked claim about
  the text), two failure modes, and fixing only one still leaves you exposed — which is why
  these link rather than merely resembling each other.

## Notes and lessons learned

[^1]: [id:ATOM-VH2C-ROVA, status:valid, desc:"the_version_bump_on_edit_is_an_UNENFORCED_claim_and_skipping_it_is_worse_than_a_dangling_citation", keywords:"the_reference_still_resolves_but_the_thing_it_points_at_quietly_changed a_version_number_that_did_not_move_even_though_the_text_did I_edited_a_rule_and_forgot_to_bump_the_version citations_resolve_perfectly_to_text_that_changed_underneath_them is_the_version_bump_actually_enforced_anywhere rule_text_and_rule_version_out_of_sync", ocd:2026-08-11, lmd:2026-08-11] DO NOT treat "edit bumps the version" as a mechanism — it is an UNENFORCED CONVENTION, and skipping the bump is worse than the dangling citation it looks like the mild version of. BECAUSE a version is a machine-readable CLAIM about the text, and nothing checks the claim stayed true: two role-plugins broke this in OPPOSITE directions on the same day making the same edit — one bumped and left 14 citations pointing at a version that no longer existed, the other edited the text and did not bump, so every citation still resolved PERFECTLY to changed content. **A stale pointer announces itself on the first lookup; a pointer to silently-mutated content never does.** pytest, ruff and a `--strict` plugin validation were green through both. DO bind text to version with a checked-in hash per rule (fail on text-changed-without-bump, and print the new hash so the fix is paste-able), and cite the STABLE coordinate — the number — in living prose, reserving a pinned version for a claim genuinely about one revision.

[^2]: [id:ATOM-TIER-BY-LINK-DIRECTION, status:valid, keywords:"wikimem tier aspect or component which_tier_for_this_page governed_by_vs_applies_to", ocd:2026-07-17, lmd:2026-07-17]
  DO NOT tag a page `tier: aspect` because its subject sounds like a general rule,
  BECAUSE the tier is decided by the page's LINK DIRECTION, not its topic: an aspect
  RADIATES an `## Applies to` list down; a component RECEIVES and carries `## Governed
  by` up. This page has `## Governed by` and no `## Applies to` — it is a component,
  and `aspect` was wrong. DO read the page's own link sections to classify it. (Same
  error, same day, on [[approval-vs-mandate-protocol]] — it was a pattern, not a slip.)
