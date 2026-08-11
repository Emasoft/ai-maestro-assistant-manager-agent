---
name: governance-ssot-is-the-governance-rules-branch
description: "which ref of GOVERNANCE-RULES.md is authoritative / is main still stale or did the branch get merged / main said the rules end at R20 but they run to R52 / I checked the default branch and found no R42 / a rule I cited turned out unpublished / doc and CLI disagree about a permitted verb / is R42.8 ratified"
ocd: 2026-08-08
lmd: 2026-08-11
metadata:
  node_type: memory
  type: project
  tier: aspect
---

# governance-ssot-is-the-governance-rules-branch

The authoritative source for AI Maestro governance rules is **`docs/GOVERNANCE-RULES.md` in
`Emasoft/ai-maestro`**, and **as of 2026-08-11 `main` and the `governance-rules` branch serve the
byte-identical file** (v5.3.3, sha256 `e9f2a863…`) — so either ref is safe to read today. See
`^ATOM-9DXQ-K15X` for the measurement.

**For three days that was NOT true, and the divergence is why this page exists.** Measured
2026-08-08: `main` carried doc **v4.0.2 with ZERO occurrences of `R42`** while `governance-rules`
carried **v5.3.3 through R52**, and `CLAUDE.md@main` compounded it by calling the stale copy
*"Full governance rules … the full **R1-R20** set"*. An agent that did the obviously-correct
thing — read the default branch, find no R42 — **was not being careless; it was being correctly
informed by a wrong index.** Both defects are now gone (`CLAUDE.md@main` no longer mentions the
R1-R20 range at all).

**So the standing instruction is the METHOD, not the ref**: measure the ref you are about to
cite, with a control, at the moment you cite it. This divergence opened and closed without
announcement, and neither event was visible from inside this repo. [^3]

**How to read it (no clone needed):**

```bash
gh api "repos/Emasoft/ai-maestro/contents/docs/GOVERNANCE-RULES.md?ref=governance-rules" \
  --jq .content | base64 -d > /tmp/GOV.md
```

**Cite the VERSION, fetch the TIP.** This branch advances several times a day — three different
tip shas were current within one working session — so a cited sha ages out almost immediately
while `version:` in the frontmatter stays meaningful.

**Rules do not all bind this plugin.** `R7`, `R8`, `R21`, `R47`, `R50`, `R51` govern how the
ai-maestro **server and UI must be built**, not the MANAGER's conduct. That classification is
enforced by `tests/test_governance_citations.py`, which also fails when a rule is neither cited
nor classified — so an upstream rule addition surfaces here instead of sitting unnoticed.

See also [[architecture]], [[prrd-golden-silver-rules]].


^ATOM-N5HI-C5C0 [desc:"R42.8 was USER-granted 2026-08-05 but published 2026-08-08; measuring in that window showed absence and two agents wrongly concluded non-ratification", keywords: R42.8_ratified_or_not a_rule_I_cited_was_unpublished grep_found_no_R42_on_main the_rule_exists_but_I_cannot_find_it published_later_than_it_was_granted doc_and_CLI_disagree_on_a_permitted_verb block-state_missing_from_the_rule_text, ocd: 2026-08-08, lmd: 2026-08-08]

The R42.8 episode is the worked example of why this page exists. The rule was granted by the
USER on 2026-08-05, but only reached a readable ref on 2026-08-08 ~05:51Z. Two agents measured
inside that window, both correctly found nothing, and both concluded the rule was not ratified —
one of them (this plugin) shipped a release demoting a citation that had been right all along.

Separately, cross-checking the ratified text against the deployed `aimaestro-session.sh` found
they disagreed: the rule named `read-prompt` and `answer` only, while the CLI also permitted
`block-state` cross-agent — and the server had always granted it. The TEXT was wrong, not the
code. Reported upstream and corrected in doc v5.3.3. [^1] [^2]


^ATOM-9DXQ-K15X [desc:"main and governance-rules converged to byte-identical v5.3.3 on 2026-08-11; the divergence this page was written about is OVER", keywords: is_main_still_stale which_ref_should_I_read_now main_vs_governance-rules_branch the_branch_was_merged_to_main I_read_main_and_found_R42_after_all ref_divergence_that_has_since_closed do_I_still_need_the_branch_ref, type: reference, ocd: 2026-08-11, lmd: 2026-08-11]

**As of 2026-08-11 the two refs are the SAME FILE.** Re-measured first-hand: `main` and
`governance-rules` both serve `docs/GOVERNANCE-RULES.md` at **v5.3.3, 1953 lines, sha256
`e9f2a863d713b8601961952c077b0fcb640de1043213e987c9048977933db03c`** — byte-identical, both
carrying `R39.8/9/10` and rules through `R52`. `CLAUDE.md@main` no longer claims the "R1-R20"
range either (0 hits, down from 2). The branch was merged.

So the *operational* advice on this page is now moot: reading `main` today gets the same bytes.
What survives is the METHOD — measure the ref you are about to cite, with a control, at the
moment you cite it. The divergence was real for at least three days and closed without
announcement; neither its opening nor its closing was visible from inside this repo. [^3]

## Notes and lessons learned

[^1]: [id:ATOM-SBT5-X3EN, status:valid, desc:"The 2026-08-07 measurement was accurate; the inference from it was not — absence of a record is not absence of the fact", keywords:"I_searched_and_found_nothing_so_it_does_not_exist concluded_absence_from_a_correct_search my_measurement_was_right_but_my_conclusion_was_wrong retracted_a_citation_that_was_actually_valid re-ran_the_measurement_and_still_got_it_wrong what_else_would_produce_this_same_empty_result unpublished_but_already_granted", ocd:2026-08-08, lmd:2026-08-08] DO NOT convert "I searched and found nothing" into "it does not exist", BECAUSE a correct search over a record that has not caught up returns exactly the same emptiness as a correct search over a fact that was never true — and re-running the search cannot tell them apart, since the measurement was already right. DO ask "what else would produce this same empty result?" before concluding absence; for a governance fact, "granted but not yet published" is always a live answer, so check the grant channel (an issue, a USER directive, a changelog) and not only the artifact.
[^2]: [id:ATOM-JX5W-FAII, status:valid, desc:"This page named GOVERNANCE-RULES.md as THE authoritative source; correct on the REF question, incomplete on the ARTIFACT one — design/specs/governance-spec.md is normative and the catalog is its emana", keywords:"which_governance_artifact_wins_spec_or_catalog GOVERNANCE-RULES_vs_governance-spec I_cited_the_doc_and_it_lost_the_conflict authority_inversion_v4.8.0 the_catalog_is_provenance_not_normative two_artifacts_describe_the_same_rule_differently", ocd:2026-08-08, lmd:2026-08-08] DO NOT treat `docs/GOVERNANCE-RULES.md` as the last word on a rule's wording just because it is the readable catalog, BECAUSE the v4.8.0 authority inversion makes `design/specs/governance-spec.md` NORMATIVE and the catalog its emanation — so a reader sent only to the catalog is sent to the copy that LOSES a conflict, and the body of this page said exactly that until 2026-08-08. DO cite the ref AND the artifact: `governance-rules` is the authoritative branch (that part stands), and within it the spec governs wording while the catalog is the paper trail. The catalog's own changelog shows the direction — R42.8 was authored in the spec first and the catalog entry called itself the emanation.
[^3]: [id:ATOM-TP6X-R0RD, status:valid, desc:"This page recorded a ref divergence as a standing property; a divergence is a dated STATE that closes silently, so it must be re-measured at citation time", keywords:"I_cited_a_stale_fact_from_my_own_memory my_note_said_main_was_stale_but_it_is_not a_divergence_that_closed_without_telling_me memory_was_right_when_written_and_wrong_now do_not_trust_a_dated_measurement_as_current recheck_before_citing_your_own_note drift_between_two_refs_is_a_state_not_a_property", ocd:2026-08-11, lmd:2026-08-11] DO NOT record a measured difference between two refs (or two artifacts) as a standing PROPERTY of either one, BECAUSE a divergence is a dated STATE with a shelf life — it opens and closes on someone else's schedule, silently, and a note that says "main is stale wholesale" keeps asserting that in full confidence long after a merge made it false; this page did exactly that for three days and I was about to answer another agent's question from it. DO write the measurement WITH its date and method attached, and RE-RUN it before citing — one `shasum` of the two refs, with a control that proves the comparison can still see a difference, costs a single command and is the only thing that distinguishes "still true" from "was true".
