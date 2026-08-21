---
name: governance-self-audit-cites-hub-overlay
description: "a rule citation in the governance self-audit skill points at a file that is not in this repo / citation looks broken or rotted / audit reported missing rule files / should I repoint these citations into the plugin tree / the audit filed a batch of false rot findings / padded finding list"
ocd: 2026-08-21
lmd: 2026-08-21
metadata:
  node_type: memory
  type: project
  tier: component
publish-globally: false
---

# governance-self-audit-cites-hub-overlay


^ATOM-IEO7-ZXIE [desc: "The 12 governance self-audit questions deliberately cite HUB-repo overlay rules, so a citation that resolves outside this plugin tree is by design — resolve rot checks against BOTH trees", keywords: citation_outside_repo missing_rule_file citation_rot hub_overlay_rules governance_self-audit_skill false_rot_finding, type: project, ocd: 2026-08-21, lmd: 2026-08-21]

`skills/amama-governance-self-audit/SKILL.md` states 12 MANAGER questions that CITE the rule each
one enforces and never restate it. Some of those rules live in the **ai-maestro HUB repo's
governance overlay**, not in this plugin's tree — commit `5901f54` deliberately rewrote those
citations so they no longer look like in-plugin paths. A citation that does not resolve inside
this repo is therefore CORRECT, not rot.

Any citation-integrity check must resolve each cited id against **both** trees (this plugin AND
the hub repo) and may report rot only when the id exists in neither, or when the cited rule's
TEXT contradicts what the question implies. Same shape as [[ATOM-LL1I-6JAV]]: absence from this
tree is by design, not a defect. Resolving before believing is [[verify-cross-repo-overview]]. [^1]

## Notes and lessons learned

[^1]: [id: ATOM-AVCE-N34O, status: valid, desc: "hub review of TRDD-D6H36I26, 2026-08-21 — the guard was added before the reviewer ran", keywords: "false_rot_findings padded_finding_list repoint_citation_into_plugin_tree single-tree_citation_audit", ocd: 2026-08-21, lmd: 2026-08-21] DO NOT audit these citations against this repo alone, and DO NOT "fix" an out-of-tree citation by repointing it into the plugin tree, BECAUSE every hub-overlay citation then reads as rot: the run files a batch of false findings, and a padded list does not dilute the real ones — it arms their dismissal, and repointing re-creates the in-plugin-looking paths `5901f54` removed. DO resolve each id against both trees first, and report rot only on "exists in neither" or "text contradicts".
