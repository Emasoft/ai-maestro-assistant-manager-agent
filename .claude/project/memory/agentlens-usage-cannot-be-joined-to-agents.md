---
name: agentlens-usage-cannot-be-joined-to-agents
description: "why is the agent-state probe's usage field null / why does sources.usage report unavailable / how do I get per-agent token cost or usage figures / can agentlens usage be joined to an ai-maestro agent / is there a session-id to agent-id join key / why not just match agentlens workspace to the agent workingDirectory / where do per-agent cost numbers come from / does AgentSession record the Claude Code session id / does agentlens record the agent id / how do I attribute token spend to a specific agent / why does the probe not report cost per agent / can I use the workspace path as a join key / two agents share one working directory / agentlens shows sessions but not agents / what unblocks TRDD-2EUC9O2S / why was the usage join left unbuilt / per-agent usage attribution is missing"
ocd: 2026-08-29
lmd: 2026-08-29
publish-globally: false
metadata:
  node_type: memory
  type: project
  tier: component
---

# agentlens-usage-cannot-be-joined-to-agents


^ATOM-HKTN-KU6S [desc: "Neither agentlens nor ai-maestro records the other's id, so per-agent usage cannot be joined; the probe's usage stays null by design.", keywords: usage_is_null sources.usage_unavailable per-agent_token_cost per-agent_usage_attribution session-id_to_agent-id_join agentlens_workspace_join_key AgentSession_has_no_session_id agentlens_has_no_agent_id workspace_equals_workingDirectory two_agents_one_working_directory probe_usage_returns_null why_no_cost_per_agent agentlens_sessions_view_keys_on_session_id TRDD-2EUC9O2S ai-maestro_issue_155, type: project, trdd: TRDD-2EUC9O2S, ocd: 2026-08-29, lmd: 2026-08-29]
The agent-state probe reports `usage: null` and `sources.usage: unavailable`
**by design**, because no join key exists between the two data sources.

Measured 2026-08-29, both directions:

- ai-maestro's `AgentSession` (`types/agent.ts`) carries `index`, `status`,
  `workingDirectory`, `createdAt`, `lastActive` — and **no Claude Code session
  id**.
- agentlens session records carry `sessionId`, `workspace`, `accountId`,
  `model`, `title` — and **no agent id**.

The only overlapping field is a filesystem path (`workingDirectory` ↔
`workspace`), and it is the wrong-but-natural guess. It fails **uniqueness** —
one workdir was observed claimed by two different agents — and it fails
**coverage**: 6 of 244 agentlens workspaces match an agent workdir, so 97.5% are
orphaned and only 1.5% of 26,855 session records are attributable. One of the six
matches is itself degenerate: an agent registered with `workingDirectory: /`
matches the workspace `/`, sweeping every root-cwd session into one agent.

So a path join misattributes cost while silently dropping most of the data — and
a wrong number is worse than a visible null, because a null is legible as missing
and a wrong figure is not.

The id itself is not missing from the system: a live Claude Code hook payload
carries `session_id` and `cwd` as adjacent keys. The gap is only that nothing
persists it onto the agent record. `Emasoft/ai-maestro#155` asks for exactly
that; until it lands, the null stands.

## Notes and lessons learned
