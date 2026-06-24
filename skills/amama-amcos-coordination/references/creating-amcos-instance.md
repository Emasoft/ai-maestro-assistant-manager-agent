# Creating the COS (MANAGER Responsibility, R29)

## Table of Contents
- [1. Why the MANAGER Creates the COS](#1-why-the-manager-creates-the-cos)
- [2. How to Create the COS](#2-how-to-create-the-cos)
- [3. When to Create the COS](#3-when-to-create-the-cos)
- [4. Post-Creation Steps](#4-post-creation-steps)
- [5. Cross-Host COS Assignment](#5-cross-host-cos-assignment)

---

## 1. Why the MANAGER Creates the COS

You (the MANAGER) create AND delete teams on your own with NO user approval (R29), and the COS is created as part of team creation. When you run `aimaestro-teams.sh create`, the AI Maestro server auto-creates the team's CHIEF-OF-STAFF; you then wake it and grant its mandate (R30). This ensures:

1. **MANAGER authority** - You are the sole authority per host; team + COS lifecycle is yours, not the USER's (R29)
2. **Role constraint enforcement** - The server stamps the CHIEF-OF-STAFF title at creation; you do not assert it yourself, the server derives it from the AID (R28)
3. **Audit trail** - Every team/COS creation authenticates via your AID + portfolio token and is recorded in the signed ledger (R28, R33/R34)
4. **No rogue coordinators** - Only you create teams, and a team without its COS + 5 base members is FROZEN (R31), so no half-built team can coordinate

### COS creation is part of team creation

- The COS is **not** a separately-assigned role — the server auto-creates it the moment you create the team (R29)
- The COS retains its own identity but holds the CHIEF-OF-STAFF title for that team
- You wake the COS and grant its mandate (R30) so it can complete the team's 5 base members
- No dashboard step, no user approval, no governance/sudo password (R32)

---

## 2. How to Create the COS

### Prerequisites

1. AI Maestro reachable (`aimaestro-agent.sh list` — non-zero exit ⇒ server unreachable)
2. A team name not already in use (`aimaestro-teams.sh list`)
3. You are the MANAGER on this host (the frozen CLI resolves your AID auth internally)

### Creation (MANAGER, R29)

Create the team yourself; the server auto-creates the COS:

```bash
aimaestro-teams.sh create --name <team-name> [--description D] [--type closed] [--gh-owner O --gh-repo R]
```

The `--type closed` team gets a COS automatically (closed teams have exactly one COS). No `--password` is supplied by you — team creation is AID-authorized (R29). The deployed CLI's `--password` flag is a USER/UI transition residual (R32); where the deployed CLI still requires it for a genuinely password-gated sub-case, surface that operation to the MAESTRO rather than sudo-ing yourself.

**Verify**: confirm the team's `chiefOfStaff` field is set via `aimaestro-teams.sh show <team-id>`.

### Deleting / replacing a COS (MANAGER)

You delete teams (and thereby their COS) on your own (R29):

```bash
aimaestro-teams.sh delete <team-id> [--delete-agents]
```

Re-assigning an existing team's COS to a different agent uses the deployed teams CLI verb:

```bash
aimaestro-teams.sh reassign-cos <team-id> <agent-uuid>
```

(Deployed per ai-maestro#36 — confirmed by the scripts owner on ai-maestro#49. The deployed CLI's `--password <governance-password>` is a USER/UI residual, R32: AID resolves your auth for the same-host case, so you do **not** supply a password; surface any password-gated cross-host sub-case to the MAESTRO, and never fall back to a sudo path.)

### Naming Convention for the COS

The COS keeps its own session name. There is no special naming requirement; the COS role is a property of team membership, not agent identity.

For clarity in messaging and logs, you may refer to the COS as:
- `<cos-session-name> (COS for <team-name>)`

---

## 3. When to Create the COS

| Scenario | Action |
|----------|--------|
| **New team needed** | Create the team yourself (R29); the COS is auto-created with it |
| **Previous COS unresponsive** | Delete + recreate the team, or reassign the COS via the teams CLI |
| **Team restructuring** | Adjust the team via the teams CLI as composition changes |
| **Never duplicate** | Only ONE COS per closed team at any time |
| **Open teams** | Open teams have no COS; coordination is ad-hoc (closed teams only have a COS) |

---

## 4. Post-Creation Steps

After creating the team (and its auto-created COS):

1. **Verify creation** - Check `aimaestro-teams.sh show <team-id>` to confirm `chiefOfStaff` is set
2. **Wake the COS** - `aimaestro-agent.sh wake <cos-id>` so it can act
3. **Grant the COS its mandate** - Send a mandate message (R30) authorizing it to create the team's 5 base members + project MEMBERs
4. **Confirm mandate acceptance** - Wait for the COS to acknowledge its mandate and role
5. **Log the creation** - Record in the team audit log

### Mandate Message

Send a COS mandate notification using the `agent-messaging` skill:
- **Recipient**: The COS session name
- **Subject**: "COS Mandate — Team Creation"
- **Content**:
  - `type`: `cos-mandate`
  - `team_id`: The team ID
  - `team_name`: The team name
  - `expected_role`: `chief-of-staff`
  - `mandate`: `team-creation` (authorizes the 5-member base + project MEMBERs, R30)
  - `responsibilities`: "Complete the team's 5 base members, then coordinate agents. Manage task delegation and approval workflows."
- **Priority**: `high`

**Verify**: The COS should respond confirming it has accepted the role + mandate and loaded its role constraints. Until the 5 base members exist, the team stays FROZEN (R31) — only the COS active, all others hibernated.

### Verification Checklist

- [ ] You created the team via `aimaestro-teams.sh create` (R29)
- [ ] Team is type `closed`
- [ ] `aimaestro-teams.sh show <team-id>` confirms `chiefOfStaff` set (server auto-created the COS)
- [ ] COS woken via `aimaestro-agent.sh wake <cos-id>`
- [ ] Mandate message sent to the COS (R30)
- [ ] COS acknowledged role + mandate
- [ ] COS is completing the 5 base members (team FROZEN until complete, R31)

---

## 5. Cross-Host COS Assignment

When the target agent is on a different host (remote AI Maestro instance), the assignment requires a GovernanceRequest with dual-manager approval.

### When Cross-Host Assignment Is Needed

- The agent is registered on a different AI Maestro instance
- The team spans multiple hosts
- Network boundaries separate you from the target agent

### GovernanceRequest for COS Assignment

Submit a GovernanceRequest of type `assign-cos` via the frozen CLI. The `request` verb (deployed ai-maestro#36) wraps `POST /api/v1/governance/requests` — no direct `/api/` call:

```bash
aimaestro-governance.sh request \
  --type assign-cos \
  --target-host "<remote-aimaestro-url>" \
  --requested-by "<amama-session-name>" \
  --role MANAGER \
  --password "<governance-password>" \
  --payload-json '{"targetAgent":"<remote-agent-id>","targetTeam":"<team-id>","justification":"Team requires operational coordinator on remote host"}'
```

<!-- NOTE (ai-maestro#36): the submit verb (`request`) IS deployed and is used above. The deployed CLI still takes `--password` for cross-host governance, which is a USER/UI sudo residual (R32): you do NOT supply a governance/sudo password yourself — surface this cross-host approval to the MAESTRO, who actions it via the UI. The secure non-interactive env-fallback `AIMAESTRO_GOV_PASSWORD` remains a residual (see the consolidated list on ai-maestro#36). -->

See the `team-governance` skill for full CLI details.

**Expected Response:**

```json
{
  "requestId": "gov-req-<uuid>",
  "status": "pending",
  "type": "assign-cos",
  "createdAt": "2026-02-27T10:00:00Z"
}
```

### GovernanceRequest Lifecycle

1. **Pending** - Request submitted, awaiting dual-manager approval
2. **Approved** - Both managers approved; AI Maestro executes it on the remote host
3. **Rejected** - Governance policy denies the assignment; you are notified with reason
4. **Executed** - Assignment completed on remote host; you receive confirmation

**Verify**: Poll `aimaestro-governance.sh request <request-id>` until status is `approved` and then `executed`.

### Cross-Host Limitations

- Messaging latency may be higher across hosts
- ACK timeouts should be increased for cross-host COS agents
- Health check intervals should account for network latency
