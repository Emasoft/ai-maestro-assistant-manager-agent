# Team-Based Project Workflow

Governance touchpoints here follow R26-R40 (GOVERNANCE-RULES.md); rule numbers
are cited inline. The persona is the authoritative source.

## Workflow Phases

### Phase 1: Team Creation (R29-R31)

| Step | Actor | Action | CLI |
|------|-------|--------|-----|
| 1 | MANAGER | Create GitHub repo + team (incl. auto-created COS), NO user approval | `aimaestro-teams.sh create --name N [--type T]` |
| 2 | MANAGER | Create the 4 remaining base members (ARCHITECT, ORCHESTRATOR, INTEGRATOR, MEMBER), NO user approval | `aimaestro-agent.sh create … --governanceTitle <title>` |
| 3 | MANAGER | Wake the COS | `aimaestro-agent.sh wake <cos-id>` |
| 4 | MANAGER | Grant the COS its mandate | mandate via AMP |
| 5 | COS | Add project-specific extra MEMBER-titled agents (under the mandate, R30) | `aimaestro-teams.sh add-agent <teamId> <agent>` |

The team stays FROZEN until the COS + all 5 base members exist (R31). The base
roster needs NO GovernanceRequest — it is a MANAGER action (R29). All CLIs
resolve AID auth internally; AMAMA supplies no governance/sudo password (R28/R32).

### Phase 2: Design

| Step | Actor | Action |
|------|-------|--------|
| 6 | Manager | Send requirements to COS |
| 7 | COS | Assign design task to architect-skilled member |
| 8 | Member | Create design document |
| 9 | COS | Forward design to manager |
| 10 | Manager | Get user approval; send approved design to COS |

### Phase 3: Task Planning

| Step | Actor | Action |
|------|-------|--------|
| 11 | COS | Decompose design into tasks |
| 12 | COS | Create task issues on GitHub kanban |
| 13 | COS | Assign tasks to members |
| 14 | Members | Request clarifications if needed |

### Phase 4: Implementation

| Step | Actor | Action |
|------|-------|--------|
| 15 | Members | Work on assigned tasks |
| 16 | COS | Move tasks: `dispatch` -> `dev` |
| 17 | Members | Complete work, notify COS |
| 18 | COS | Approve PR creation |
| 19 | Members | Create PRs |

### Phase 5: Review

| Step | Actor | Action |
|------|-------|--------|
| 20 | COS | Request review from integrator-skilled member |
| 21 | Member | Review PR, merge or reject |
| 22 | COS | Handle failures: reassign, move back to `dev` |

### Phase 6: Completion

| Step | Actor | Action |
|------|-------|--------|
| 23 | COS | Move task to `ai_review` then `complete` |
| 24 | COS | For big tasks: escalate to `human_review` (via manager) before completing |
| 25 | COS | Report completion to manager |
| 26 | COS | Assign next task to available member |

## Governance Touchpoints

| Event | Requires GovernanceRequest |
|-------|---------------------------|
| Team creation / deletion | No (MANAGER action, no user approval, R29) |
| COS creation | No (auto-created with the team, R29) |
| 5 base members | No (MANAGER action, R29) |
| Extra MEMBER-titled agents | No — COS creates them under its MANAGER mandate (R30) |
| Agent replacement | Yes |
| Design approval | Yes (user via MANAGER) |
| Big task human review | Yes (user via MANAGER) |

## Task Statuses

Task status is the **ratified 17-column kanban vocabulary**, 1:1 with the TRDD `column:`
field — 14 lifecycle + 3 exception columns. Consumers align TO it, never the reverse
(ai-maestro R25 / TRDD-YUGDER9D):

```
backburner → todo → design → dispatch → dev → testing → ai_review → human_review → complete
  → publish → published   (tools)
  → deploy → live → live_auditing   (services)
exception (orthogonal): blocked · failed · superseded
```

See `skills/amama-github-routing/references/task-system-sync.md` for the full column table
and the GitHub-Project mapping.

## Task Routing

- **Small**: `dev` -> `testing` -> `ai_review` -> `complete`
- **Big**: `dev` -> `testing` -> `ai_review` -> `human_review` (escalate to manager) -> `complete`

## Communication

All inter-agent communication via the AI Maestro messaging CLI (`amp-send …`).
GitHub used for: repos, issues, PRs, project boards.

## Non-MAESTRO users and the ASSISTANT agent (R36-R39)

- The MANAGER obeys ONLY the MAESTRO user, or the single active MAESTRO-DELEGATE
  while one is appointed (R36/R37). Every other user — native or foreign — is
  subordinate to the MANAGER like any agent.
- Each non-MAESTRO user is auto-assigned ONE ASSISTANT agent (role plugin
  `ai-maestro-assistant-role-agent` = MANAGER planning ∪ AUTONOMOUS programming,
  minus all agent/team creation). The ASSISTANT has no team, obeys only its user
  and the MAESTRO, is invisible to other agents (but receives every task/permission
  sent to its user), and is non-deletable except by deleting the user (R38/R39).
- A normal (non-ASSISTANT) user-agent messages ONLY its own ASSISTANT, its team's
  COS, and the MANAGER; it receives kanban tasks and opens a PR on completion, and
  is subordinate (task clarifications only). The MANAGER is aware of ASSISTANT
  agents but does not manage them beyond ordinary MANAGER authority.
