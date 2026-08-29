---
name: architecture
description: "how does the ai-maestro-assistant-manager-agent (AMAMA, the MANAGER role plugin) work / what is AMAMA architecture / overview of the MANAGER role plugin / where do the main AMAMA parts live / where are the key AMAMA components / what does the MANAGER plugin own / how does AMAMA coordinate the other role plugins / where is the 3-pillars task system TRDD PRRD Kanban wired into AMAMA / who is the sole user interface and governance authority in AI Maestro / AMAMA parts map and functionality hub"
ocd: 2026-06-14
lmd: 2026-08-29
publish-globally: false
metadata:
  node_type: memory
  type: project
  tier: hub
  functionality: architecture
  globs: ["agents/**", "skills/**", "scripts/**", "design/**"]
---
ai-maestro-assistant-manager-agent (AMAMA) is the **MANAGER** role plugin of the AI Maestro fleet: the sole user interface and governance authority. It owns the 3-pillars task system (TRDD / PRRD / Kanban), approves releases and governance changes (approval tiers), and coordinates the other role plugins via GitHub issues + AMP messaging.

## Parts map
- [[governance-ssot-is-the-governance-rules-branch]] — where the authoritative GOVERNANCE-RULES.md ref lives (the `governance-rules` branch, not main).
- (add further component/aspect pages as created — e.g. the approval-tier governance, the 3-pillars integration, the publish pipeline, the proposal-approval lifecycle)

## Applies to
- (radiates down to the component/aspect pages of this functionality — empty until the first one is written; wire the reciprocal `## Governed by` on each)

## See also
- (lateral links to other functionality hubs, once they exist)

## Notes and lessons learned
