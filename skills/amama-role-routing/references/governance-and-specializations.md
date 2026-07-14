# Governance Titles vs. Agent Specializations

## Table of Contents
- [Governance Titles](#governance-titles)
- [Team Creation Authority (R29/R30/R31)](#team-creation-authority-r29r30r31)
- [Plugin Prefix Reference](#plugin-prefix-reference)
- [Communication Hierarchy](#communication-hierarchy)

## Governance Titles

AI Maestro governance titles (R26-R40, GOVERNANCE-RULES.md). The server derives a title from the AID; an agent never asserts its own title (R28):

| Governance Title | Purpose |
|------------------|---------|
| `MANAGER` | Sole authority per host. Creates/deletes teams + the COS + the 5 base members + AUTONOMOUS/MAINTAINER (R29). Obeys only the MAESTRO / active DELEGATE (R36/R37). |
| `CHIEF-OF-STAFF` | Team operations, staffing, failure recovery. Created by the MANAGER as part of team creation (R29); needs a MANAGER mandate to create further agents (R30). |
| `ARCHITECT` | Design lead — architecture, data models, requirements. |
| `ORCHESTRATOR` | Task coordinator — kanban, workflow, implementer coordination. |
| `INTEGRATOR` | Integration, code review, quality gates, deployment. |
| `MEMBER` | Core implementer. Extra project-specific agents MUST be MEMBER-titled (R30). |
| `MAINTAINER` | Governance-layer host maintenance/oversight. Reaches MANAGER + HUMAN only. |
| `AUTONOMOUS` | Independent agent outside team structure. Reaches MANAGER + peer AUTONOMOUS + HUMAN only. |
| `ASSISTANT` | A non-MAESTRO user's auto-assigned counterpart of AMAMA (R38/R39). No team; obeys only its user + the MAESTRO. |

**ARCHITECT / ORCHESTRATOR / INTEGRATOR / MEMBER are the team-internal titles** — they ARE governance titles a team agent holds (server-bound to its AID), set at creation via `--governanceTitle`. The agent's specialization is its title; its `skills` array carries the capability detail. The 5 base titles every team must contain are CHIEF-OF-STAFF + ARCHITECT + ORCHESTRATOR + INTEGRATOR + MEMBER (R31).

```bash
# CORRECT -- title bound at creation; the server enforces it from the AID (R28)
aimaestro-agent.sh create amaa-architect --client claude --team TEAM_ID --governanceTitle architect

# Extra project-specific agents MUST be MEMBER-titled on the member-agent role plugin (R30)
aimaestro-agent.sh create db-expert --client claude --team TEAM_ID --governanceTitle member
```

## Team Creation Authority (R29/R30/R31)

Before routing any work, the target team must exist and be complete. The authority model:

- **MANAGER creates AND deletes** teams, the auto-created COS, the 5 base members, and AUTONOMOUS/MAINTAINER agents — **with NO user approval** (R29). `aimaestro-teams.sh create` resolves AID auth internally; the server auto-creates the COS.
- **COS creates further agents only under a MANAGER mandate** (R30). With a team-creation mandate the COS may complete the 5-member base + add project-specific extra agents — which MUST be MEMBER-titled on the member-agent role plugin. Neither the MANAGER nor a COS may create a team lacking the 5 base members, nor create non-MEMBER agents beyond the base.
- **A team missing any of its 5 base members is FROZEN** (only the COS active, all others hibernated) until the COS completes the base (R31). Do not route work into a frozen team.

This SUPERSEDES any older text stating team/COS creation needs USER approval, a dashboard step, or that AMAMA cannot assign a COS. AMAMA creates the COS as part of team creation, on its own.

## Plugin Prefix Reference

| Role | Prefix | Role Plugin | Governance Title |
|------|--------|-------------|------------------|
| Assistant Manager | `amama-` | ai-maestro-assistant-manager-agent | `MANAGER` |
| Chief of Staff | `amcos-` | ai-maestro-chief-of-staff | `CHIEF-OF-STAFF` |
| Architect | `amaa-` | ai-maestro-architect-agent | `ARCHITECT` |
| Orchestrator | `amoa-` | ai-maestro-orchestrator-agent | `ORCHESTRATOR` |
| Integrator | `amia-` | ai-maestro-integrator-agent | `INTEGRATOR` |
| Member (programmer) | — | ai-maestro-programmer-agent | `MEMBER` |
| Maintainer | `amma-` | ai-maestro-maintainer-agent | `MAINTAINER` |
| Autonomous | `amaua-` | ai-maestro-autonomous-agent | `AUTONOMOUS` |

Every persisted agent MUST carry exactly one role plugin (R9.13). The two governance-layer
titles have a mandatory mapping: MAINTAINER → `ai-maestro-maintainer-agent`, AUTONOMOUS →
`ai-maestro-autonomous-agent`. Extra project-specific agents are MEMBER-titled on the
member-agent role plugin (R30).

## Communication Hierarchy

```
MAESTRO (active user / DELEGATE — R36/R37)
   |
AMAMA (MANAGER) — sole user interface
   |
AMCOS (CHIEF-OF-STAFF) — sole entry point into a team
   |
AMAA (ARCHITECT) · AMOA (ORCHESTRATOR) · AMIA (INTEGRATOR) · MEMBER(s)
```

**Governance titles in this hierarchy:** AMAMA `MANAGER` · AMCOS `CHIEF-OF-STAFF` · AMAA `ARCHITECT` · AMOA `ORCHESTRATOR` · AMIA `INTEGRATOR` · extras `MEMBER`.

**CRITICAL (R6 v3 / R26-R40):**
- AMAMA is the ONLY agent that communicates directly with the MAESTRO; it obeys ONLY the currently-active MAESTRO / DELEGATE (R36/R37) — every other user is subordinate.
- **AMAMA does NOT have unrestricted messaging.** Its only entry point into a team is the team's CHIEF-OF-STAFF. AMAMA NEVER messages a team-internal agent (ARCHITECT, ORCHESTRATOR, INTEGRATOR, MEMBER) directly — always route via AMCOS. (Empirical R6 v3 finding: direct MANAGER→team-member messaging left the COS/ORCHESTRATOR uninformed or contradicted, producing chaos.) AMAMA's full outbound set is HUMAN, peer MANAGERs, CHIEF-OF-STAFF, AUTONOMOUS, MAINTAINER.
- AMCOS is the SOLE gateway for delegating work to specialists — routing via AMCOS is MANDATORY, not "preferred".
- A team-internal agent reaches AMAMA only THROUGH its COS; it cannot message AMAMA directly.
- All team-internal agents hold a governance title bound to their AID (R28) — the title IS the specialization, not loose metadata.
