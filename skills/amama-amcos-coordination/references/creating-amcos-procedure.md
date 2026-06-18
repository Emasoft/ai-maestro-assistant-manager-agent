# Team Creation and Agent Registration Procedure

## Contents

- [Overview](#overview)
- [Key Principles](#key-principles)
- [Agent Registration](#agent-registration)
- [Team Creation](#team-creation)
- [COS Creation](#cos-creation)
- [Step-by-Step Procedure](#step-by-step-procedure)
- [Success Criteria](#success-criteria)
- [Troubleshooting](#troubleshooting)
- [Related Documents](#related-documents)

## Overview

This document describes the step-by-step procedure for creating a team and its agents. You (the MANAGER) create AND delete teams on your own with NO user approval (R29); the server auto-creates the team's COS as part of team creation, and you grant the COS a team-creation mandate (R30) to build out the 5 base members.

## Key Principles

1. **MANAGER creates teams + COS** - You create teams via `aimaestro-teams.sh create` (R29); the server auto-creates the COS. No user approval, no dashboard step (R29)
2. **5 base members are mandatory** - A team missing any of its 5 base members is FROZEN (only the COS active, all others hibernated) until the COS completes the base (R31)
3. **COS needs a mandate to create agents** - The COS needs your approval/mandate to create agents, unless you granted a team-creation mandate (the 5-member base + project-specific extra MEMBER agents, which must be MEMBER-titled on the member-agent role plugin). Neither you nor the COS may create a team lacking the 5 base members, nor create non-MEMBER agents (R30)
4. **One COS per closed team** - Each closed team has exactly one COS (auto-created with the team)
5. **Team registry is persistent** - Teams are stored in `~/.aimaestro/teams/registry.json`
6. **AID-authorized, never sudo** - Team + agent lifecycle authenticates via your AID + portfolio token (R28); you NEVER supply a governance/sudo password (R32). A deployed CLI that still demands `--password` is a transition residual — surface such an op to the MAESTRO instead

---

## Agent Registration

### Registration Call

Register a new agent using `aimaestro-agent.sh create <name>` or the `ai-maestro-agents-management` skill. The CLI resolves your AID auth internally (R28).

### Agent Required Parameters

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `name` | Agent session name and registry identifier | `coordinator-alpha` |
| `workingDirectory` | Agent's working directory | `~/agents/coordinator-alpha/` |
| `role` | Default role in the system | `member` |

Additional optional fields may include:
- `description` - Human-readable description of the agent's purpose
- `capabilities` - Array of capability tags
- `metadata` - Key-value metadata for the agent

### Verify Registration

```
aimaestro-agent.sh list
```

Filter for the specific agent by name.


---

## Team Creation

### Team Creation (MANAGER, R29)

You create the team yourself; the server auto-creates its COS:

```bash
aimaestro-teams.sh create --name N [--description D] [--type closed] [--agents u1,u2] [--gh-owner O --gh-repo R]
```

No `--password` is supplied by you — team creation is AID-authorized (R29). The deployed CLI's `--password` flag is a USER/UI residual (R32).

### Team Required Parameters

| Parameter | Purpose | Example Value |
|-----------|---------|---------------|
| `name` | Team name (unique) | `svgbbox-development` |
| `description` | Team purpose | `"SVG bounding box library development team"` |
| `type` | Access model | `open` or `closed` |
| `agentIds` | Initial member agents | `["coordinator-alpha", "dev-agent-1"]` |

### Team Types

| Type | Description | COS Allowed |
|------|-------------|-------------|
| `open` | Any registered agent can join | No |
| `closed` | Invite-only, managed membership | Yes (one COS, auto-created) |

**Only closed teams have a COS.** Open teams use ad-hoc coordination without a designated coordinator.

### Verify Team Creation

After you create the team, verify it exists and its COS is set:

```
aimaestro-teams.sh list
aimaestro-teams.sh show <team-id>
```


---

## COS Creation (MANAGER, R29 + R30)

The COS is auto-created by the server when you create a closed team (R29). You then wake it and grant it a team-creation mandate (R30) so it can complete the team's 5 base members.

See [creating-amcos-instance.md](creating-amcos-instance.md) for COS creation details including cross-host scenarios.

---

## Step-by-Step Procedure

### Step 1: Register Agent (if needed)

If a specific agent must exist before team membership, register it using `aimaestro-agent.sh create <name>` or the `ai-maestro-agents-management` skill.

**Verify**: `aimaestro-agent.sh list` lists the agent.


### Step 2: Create the Team (MANAGER, R29)

You create the team yourself — no user approval, no dashboard:

```bash
aimaestro-teams.sh create --name project-alpha-team --description "Development team for project alpha" --type closed
```

**Verify**: `aimaestro-teams.sh list` lists the team. Note the returned `teamId`. The server auto-creates the team's COS.


### Step 3: Wake the COS and Grant Its Mandate (R30)

The COS was auto-created with the team. Wake it and grant its team-creation mandate:

```bash
aimaestro-agent.sh wake <cos-id>
```

Then send the mandate (R30) authorizing the 5 base members + project MEMBERs.

**Verify**: `aimaestro-teams.sh show <teamId>` confirms `chiefOfStaff` is set; the COS responds confirming its mandate.

### Step 4: Send Mandate Message

Notify the COS of its mandate using the `agent-messaging` skill:

- **Recipient**: `<cos-session-name>`
- **Subject**: "COS Mandate — Team Creation"
- **Content**:
  - `type`: `cos-mandate`
  - `team_id`: `team-id`
  - `team_name`: `project-alpha-team`
  - `expected_role`: `chief-of-staff`
  - `mandate`: `team-creation`
- **Priority**: `high`

See the `agent-messaging` skill for full messaging details.

### Step 5: Verify COS Acknowledgment

Check inbox using the `agent-messaging` skill for a response from the COS within 30 seconds.

Expected response content:
```json
{
  "type": "cos-mandate-accepted",
  "team_id": "<team-id>",
  "status": "active",
  "constraints_loaded": true
}
```


**Handling `constraints_loaded: false`**: If the COS responds with `constraints_loaded: false`, it accepted the mandate but failed to load its governance constraints. In this case:
1. Send a `cos-reload-constraints` message to the COS
2. Wait 15 seconds and re-send the health ping
3. If the response still shows `constraints_loaded: false`, delete + recreate the team (R29) so a fresh COS is auto-created
4. Report to user if no COS can load constraints

**Handling no response**: If no `cos-mandate-accepted` response arrives within 30 seconds, the wake/mandate may have failed silently. Verify via `aimaestro-teams.sh show <team-id>` that `chiefOfStaff` is set. If set but no response, send a health ping. If not set, the team creation did not complete — recreate the team via `aimaestro-teams.sh create` (R29).

### Step 6: Verify the 5 Base Members (R31)

A team missing any of its 5 base members is FROZEN (R31) — only the COS active, all others hibernated. Confirm the COS is completing the base under its mandate (R30):

```bash
aimaestro-teams.sh show <team-id>
```

The team unfreezes once the COS completes all 5 base members. Until then, do NOT delegate work into the team.

### Step 7: Log the Setup

Record the team and COS in the active sessions log:

File: `docs_dev/sessions/active-teams.md`

```markdown
## Team: project-alpha-team
- **Created**: 2026-02-27 10:00:00 (by MANAGER, R29)
- **Type**: closed
- **COS**: coordinator-alpha (auto-created)
- **Mandate granted**: 2026-02-27 10:00:05 (team-creation, R30)
- **Base members**: completing (team FROZEN until 5/5, R31)
- **Last Health Check**: 2026-02-27 10:00:10 (ALIVE)
- **Current Tasks**: Awaiting base completion
```

### Step 8: Report to User

Notify the user that the team and COS are ready:

```
Team and COS ready!

Team: project-alpha-team (closed) — created by MANAGER (R29)
COS: coordinator-alpha (mandate granted, R30)
Base members: completing (team unfreezes at 5/5, R31)
Status: Active and responding

The COS is completing the team's 5 base members and will coordinate specialist agents within this team.
```

## Success Criteria

A successful team setup with COS meets ALL of the following:

- [ ] Any pre-required agent registered (`aimaestro-agent.sh list` lists it)
- [ ] You created the team via `aimaestro-teams.sh create` (R29) — team ID available via `aimaestro-teams.sh list`
- [ ] Team stored in `~/.aimaestro/teams/registry.json`
- [ ] Server auto-created the COS — `aimaestro-teams.sh show <teamId>` confirms `chiefOfStaff` set
- [ ] COS woken and granted its team-creation mandate (R30)
- [ ] COS acknowledged role + mandate
- [ ] COS completing the 5 base members (team FROZEN until 5/5, R31)
- [ ] Team and COS logged in `docs_dev/sessions/active-teams.md`

## Troubleshooting

### Agent Registration Fails

**Cause**: AI Maestro service may be down or agent name collision

**Solution**:
1. Check AI Maestro connectivity: `aimaestro-agent.sh list` (non-zero exit ⇒ server unreachable)
2. Check for name collisions: `aimaestro-agent.sh list` (filter by name client-side)
3. If collision, choose a different agent name with a suffix

### Team Creation Fails

**Cause**: Invalid agent IDs, duplicate team name, or service issue

**Solution**:
1. Verify all `agentIds` exist in the registry
2. Check for team name collisions: `aimaestro-teams.sh list` (filter by name client-side)
3. Verify AI Maestro service is healthy
4. Re-run `aimaestro-teams.sh create` (R29) — never fall back to a sudo/password path (R32)

### COS Mandate Fails

**Cause**: COS not woken, team not type `closed`, or constraints failed to load

**Solution**:
1. Verify the team is type `closed` (open teams have no COS)
2. Wake the COS: `aimaestro-agent.sh wake <cos-id>`
3. Confirm `aimaestro-teams.sh show <teamId>` shows `chiefOfStaff` set
4. Re-send the mandate message; if constraints still fail to load, delete + recreate the team (R29)

### No Response to Mandate Message

**Cause**: COS may not be running or not processing messages

**Solution**:
1. Wait additional 10 seconds
2. Retry the mandate message
3. Check COS session status via `aimaestro-agent.sh show <cos-id>`
4. If the COS is unresponsive, delete + recreate the team so a fresh COS is auto-created (R29)

## Related Documents

- [creating-amcos-instance.md](creating-amcos-instance.md) - COS creation details and cross-host scenarios
- [approval-response-workflow.md](approval-response-workflow.md) - COS approval workflow
- [delegation-rules.md](delegation-rules.md) - COS delegation rules
- [workflow-checklists.md](workflow-checklists.md) - Coordination checklists
