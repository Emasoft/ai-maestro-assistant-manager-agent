# Team-Based Project Workflow

Governance touchpoints here follow R26-R40 (GOVERNANCE-RULES.md); rule numbers
are cited inline. The persona is the authoritative source.

## Workflow Phases

### Phase 1: Team Creation (R29-R31)

| Step | Actor | Action | CLI |
|------|-------|--------|-----|
| 1 | MANAGER | Create the team (incl. auto-created COS), NO user approval | `aimaestro-teams.sh create --name N [--type T]` |
| 2 | MANAGER | Wake the COS | `aimaestro-agent.sh wake <cos-id>` |
| 3 | MANAGER | Grant the COS its team-creation mandate — BEFORE step 4, or the COS may not create agents at all (R30) | mandate via AMP |
| 4 | COS | Create the other 4 basic members (ARCHITECT, ORCHESTRATOR, INTEGRATOR, MEMBER) under that mandate | `aimaestro-agent.sh create … --governanceTitle <title>` |
| 5 | COS | Add project-specific extra MEMBER-titled agents (under the mandate, R30) | `aimaestro-teams.sh add-agent <teamId> <agent>` |

The team stays FROZEN until all 5 base members exist — **the base is 5 INCLUDING
the COS** (R12.1), i.e. the COS plus the 4 above, not 6 agents. Completing the
base is the **COS's** duty under its mandate, not the MANAGER's (R29.1 as
corrected by the USER 2026-07-14, with R12.2 / R31.1). The base roster needs NO
GovernanceRequest. All CLIs resolve AID auth internally; AMAMA supplies no
governance/sudo password (R28/R32).

**Repo creation is NOT in this phase.** Creating the GitHub repo from template,
setting branch rules, wiring CI, and cloning are host-level maintenance — the
**MAINTAINER's** job, assigned by a mandate TRDD. The MANAGER orchestrates it; it
never runs repo bootstrap inline (`assistant-manager#32`).

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
| 19 | Members | Create PRs; task moves `dev` -> `testing` as the gates run |

### Phase 5: Review

| Step | Actor | Action |
|------|-------|--------|
| 20 | COS | Request review from integrator-skilled member; task moves `testing` -> `ai_review` once all gates PASS |
| 21 | Member | Review PR, merge or reject |
| 22 | COS | Handle failures: move to `failed`, reassign, then back to `dev` for the retry (a `failed` task is never archived) |

### Phase 6: Completion

| Step | Actor | Action |
|------|-------|--------|
| 23 | COS | Move task `ai_review` -> `complete` |
| 24 | COS | For big tasks: escalate `ai_review` -> `human_review` (manager surfaces it to the user) before `complete` |
| 25 | COS | Release per `release-via`: `publish` -> `published` (tools), or `deploy` -> `live` -> `live_auditing` (services) |
| 26 | COS | Report completion to manager |
| 27 | COS | Assign next task to available member |

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

## Task Columns (the ratified 17)

The board has exactly 17 columns, 1:1 with the TRDD `column:` field. This vocabulary is
canonical — the GitHub Project's Status options and the `status:*` labels align TO it,
never the reverse. Do not invent, rename, or collapse columns.

**14 lifecycle columns**, in order:

| # | Column | Code | Description |
|---|--------|------|-------------|
| 1 | Backburner | `backburner` | Entry point — captured, not yet prioritized |
| 2 | Todo | `todo` | Prioritized, ready to be picked up |
| 3 | Design | `design` | Being decomposed and specced |
| 4 | Dispatch | `dispatch` | Design done, awaiting assignment to a member |
| 5 | Dev | `dev` | Active implementation work |
| 6 | Testing | `testing` | Gates running (lint, types, unit/e2e, CI) |
| 7 | AI Review | `ai_review` | AI reviewer inspects the work |
| 8 | Human Review | `human_review` | Escalated to the user (via the MANAGER) |
| 9 | Complete | `complete` | Done and verified; not yet released |
| 10 | Publish | `publish` | Release pipeline running (tools) |
| 11 | Published | `published` | Released to its registry/marketplace (terminal) |
| 12 | Deploy | `deploy` | Deployment pipeline running (services) |
| 13 | Live | `live` | Running in production |
| 14 | Live Auditing | `live_auditing` | Post-deploy soak / audit window |

**3 exception columns** — orthogonal to the pipeline, not a stage in it:

| # | Column | Code | Rules |
|---|--------|------|-------|
| 15 | Blocked | `blocked` | Applies whenever `blocked-by` is non-empty. Record `pre-block-column` on entry; restore to it when the blocker clears |
| 16 | Failed | `failed` | **NOT terminal, NOT archived** — stays on the board and is retried via `dev`. Only an explicit decision to give up converts it to `cancelled` (an archival value, not a board column) |
| 17 | Superseded | `superseded` | Replaced by other work; terminal, leaves the board on the next archival pass |

## Task Routing

- **Standard**: `dev` -> `testing` -> `ai_review` -> `complete`
- **Escalated (big tasks)**: `dev` -> `testing` -> `ai_review` -> `human_review` (via the
  manager) -> `complete`
- **Gate failure**: `testing` -> `failed` -> `dev` (retry) — never archived as failed
- **After `complete`, the path is chosen by `release-via`**, never freely:
  - `publish` (tools): `complete` -> `publish` -> `published`
  - `deploy` (services): `complete` -> `deploy` -> `live` -> `live_auditing`
  - `none`: `complete` is terminal

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
