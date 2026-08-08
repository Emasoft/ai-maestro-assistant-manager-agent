---
name: governance-ssot-is-the-governance-rules-branch
description: "which ref of GOVERNANCE-RULES.md is authoritative / main says the rules end at R20 but they run to R52 / I checked the default branch and found no R42 / a rule I cited turned out unpublished / doc and CLI disagree about a permitted verb / is R42.8 ratified"
ocd: 2026-08-08
lmd: 2026-08-08
metadata:
  node_type: memory
  type: project
  tier: aspect
---

# governance-ssot-is-the-governance-rules-branch

The authoritative source for AI Maestro governance rules is **`docs/GOVERNANCE-RULES.md` on the
`governance-rules` branch** of `Emasoft/ai-maestro` — **not** the default branch. Confirmed with
the hub session (2026-08-08) as a USER decision, and verified first-hand.

**`main` is stale wholesale and actively misleading.** Measured 2026-08-08: `main` carries doc
**v4.0.2 with ZERO occurrences of `R42`**, while `governance-rules` carries **v5.3.3 with rules
through R52**. Worse than stale — `CLAUDE.md@main` `:579` calls that document *"Full governance
rules … the full **R1-R20** set"* and `:1714` repeats the range. So an agent that does the
obviously-correct thing, reads the default branch, and finds no R42 **is not being careless — it
is being correctly informed by a wrong index.** Treat `main`'s self-descriptions as historical.

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

## Notes and lessons learned

[^1]: [id:ATOM-SBT5-X3EN, status:valid, desc:"The 2026-08-07 measurement was accurate; the inference from it was not — absence of a record is not absence of the fact", keywords:"I_searched_and_found_nothing_so_it_does_not_exist concluded_absence_from_a_correct_search my_measurement_was_right_but_my_conclusion_was_wrong retracted_a_citation_that_was_actually_valid re-ran_the_measurement_and_still_got_it_wrong what_else_would_produce_this_same_empty_result unpublished_but_already_granted", ocd:2026-08-08, lmd:2026-08-08] DO NOT convert "I searched and found nothing" into "it does not exist", BECAUSE a correct search over a record that has not caught up returns exactly the same emptiness as a correct search over a fact that was never true — and re-running the search cannot tell them apart, since the measurement was already right. DO ask "what else would produce this same empty result?" before concluding absence; for a governance fact, "granted but not yet published" is always a live answer, so check the grant channel (an issue, a USER directive, a changelog) and not only the artifact.
[^2]: [id:ATOM-JX5W-FAII, status:valid, desc:"This page named GOVERNANCE-RULES.md as THE authoritative source; correct on the REF question, incomplete on the ARTIFACT one — design/specs/governance-spec.md is normative and the catalog is its emana", keywords:"which_governance_artifact_wins_spec_or_catalog GOVERNANCE-RULES_vs_governance-spec I_cited_the_doc_and_it_lost_the_conflict authority_inversion_v4.8.0 the_catalog_is_provenance_not_normative two_artifacts_describe_the_same_rule_differently", ocd:2026-08-08, lmd:2026-08-08] DO NOT treat `docs/GOVERNANCE-RULES.md` as the last word on a rule's wording just because it is the readable catalog, BECAUSE the v4.8.0 authority inversion makes `design/specs/governance-spec.md` NORMATIVE and the catalog its emanation — so a reader sent only to the catalog is sent to the copy that LOSES a conflict, and the body of this page said exactly that until 2026-08-08. DO cite the ref AND the artifact: `governance-rules` is the authoritative branch (that part stands), and within it the spec governs wording while the catalog is the paper trail. The catalog's own changelog shows the direction — R42.8 was authored in the spec first and the catalog entry called itself the emanation.
