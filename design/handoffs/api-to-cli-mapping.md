# AMAMA decoupling — authoritative `/api/` → frozen-CLI mapping

Single source of truth for repointing AMAMA off direct `/api/` calls onto the
immutable CLI layer (R22). Syntax below is **verified** — deployed CLIs read
from `~/.local/bin`, source-only CLIs read from `~/ai-maestro/scripts/` (frozen
by design: their headers state "Plugins call THIS script, never the HTTP API
directly; new capability = new subcommand/flag only").

Tracked by TRDD-5fc2cb0a. Keystone deploy gap = ai-maestro#36.

## Repoint rules (for every editor / sub-agent)

1. Change only **direct `/api/` INSTRUCTION calls** — `curl …/api/…` examples,
   operation tables whose cells are `/api/…`, prose telling the agent to hit an
   endpoint. Pure architecture description may stay but prefer citing the CLI.
2. The CLIs resolve AID auth internally — **drop manual `-H "Authorization:
   Bearer $AID_AUTH"` curl scaffolding**; that coupling goes away.
3. For a **BLOCKED** op (no CLI verb yet), do NOT invent syntax and do NOT leave
   a bare `/api/`. Replace with a greppable marker:
   `<!-- DECOUPLE-BLOCKED ai-maestro#36: <op> — CLI verb not yet deployed -->`
   and keep the current behavior described as fallback. Never break a working hook.
4. Behavior must not otherwise change. Re-read the file before editing; verify after.

## MESSAGING — `amp-*` (DEPLOYED, frozen) ✓ repoint now

| Direct call | Frozen CLI |
|---|---|
| `GET /api/messages?agent=…&status=unread` (check inbox) | `amp-inbox` |
| `GET /api/messages` (read one) | `amp-read <id>` |
| `POST /api/messages` (send) | `amp-send …` |
| (reply to a message) | `amp-reply …` |

## AGENTS — `aimaestro-agent.sh` (DEPLOYED, frozen) ✓ repoint now

| Direct call | Frozen CLI |
|---|---|
| `GET /api/sessions` (connectivity probe) | `aimaestro-agent.sh list` (non-zero exit ⇒ server unreachable) |
| `GET /api/agents` | `aimaestro-agent.sh list` |
| `GET /api/agents/{id}` | `aimaestro-agent.sh show <id>` |
| `POST /api/agents` | `aimaestro-agent.sh create <name> [opts]` |
| `PATCH /api/agents/{id}` (e.g. `governanceTitle`) | `aimaestro-agent.sh update <id> [opts]` |
| `DELETE /api/agents/{id}` | `aimaestro-agent.sh delete <id>` |
| `POST /api/agents/{id}/wake` | `aimaestro-agent.sh wake <id>` |
| `POST /api/agents/{id}/hibernate` | `aimaestro-agent.sh hibernate <id>` |

## TEAMS — `aimaestro-teams.sh` (SOURCE-frozen; deploy pending #36) ✓ repoint now (works on deploy)

| Direct call | Frozen CLI |
|---|---|
| `GET /api/teams` | `aimaestro-teams.sh list` |
| `GET /api/teams/{id}` | `aimaestro-teams.sh show <teamId>` |
| `POST /api/teams` | `aimaestro-teams.sh create --name N [--description D] [--agents u1,u2] [--type T] [--cos UUID] [--password P] [--gh-owner O --gh-repo R]` |
| `PATCH /api/teams/{id}` | `aimaestro-teams.sh update <teamId> [opts]` |
| `DELETE /api/teams/{id}` | `aimaestro-teams.sh delete <teamId> [--password P] [--delete-agents]` |
| (add/remove agent ↔ team) | `aimaestro-teams.sh add-agent …` / `remove-agent …` |
| `PATCH /api/teams/{id}/chief-of-staff` | **NOT a CLI verb** — COS assignment is **USER-only via the dashboard**. Keep prose: "USER assigns COS via dashboard; MANAGER only recommends." |

## GOVERNANCE — `aimaestro-governance.sh` (SOURCE-frozen; deploy pending #36) ✓ repoint now (works on deploy)

| Direct call | Frozen CLI |
|---|---|
| `GET /api/v1/governance/requests?status=pending` | `aimaestro-governance.sh requests [--status pending]` |
| (get one request) | `aimaestro-governance.sh request <id>` |
| `POST /api/v1/governance/requests/{id}/approve` | `aimaestro-governance.sh approve <id> --password P [--approver UUID]` |
| `POST /api/v1/governance/requests/{id}/reject` | `aimaestro-governance.sh reject <id> --password P [--rejector UUID] [--reason R]` |
| (cross-host transfer) | `aimaestro-governance.sh transfer …` |
| `GET /api/governance` (flat status: `hasManager`…) | **Possible gap** — no dedicated verb confirmed. If a status probe is needed, use `aimaestro-governance.sh requests` as the connectivity signal; otherwise mark `<!-- DECOUPLE-BLOCKED ai-maestro#36: governance status verb -->`. |

## BLOCKED on keystone (#36) — mark, do NOT guess, do NOT break

| Direct call | Owner | Action |
|---|---|---|
| `GET /api/users/me/presence` (`amama-presence-tracker`) | presence verb not built | marker + keep current behavior described |
| `POST /api/sessions/me/user-input` (`scripts/amama_user_prompt_submit.py` hook) | session user-input verb not exposed as callable subcommand | marker; **leave the working hook untouched** until the verb lands, then split (hook → CLI) |

## File worklist

- `agents/ai-maestro-assistant-manager-agent-main-agent.md` — primary; agent + team + governance + messaging tables and curl examples. (orchestrator handles personally)
- `skills/amama-approval-workflows/**` — governance approve/reject/requests ✓
- `skills/amama-status-reporting/**` — agents/teams/sessions reads ✓
- `skills/amama-amcos-coordination/**` — teams + agents ✓
- `skills/amama-presence-tracker/**` — BLOCKED (presence) → markers only
- `skills/amama-autonomous-fallback/references/reversibility-matrix.md` — verify descriptive vs instruction
- `docs/AGENT_OPERATIONS.md`, `docs/TEAM_REGISTRY_SPECIFICATION.md`, `docs/FULL_PROJECT_WORKFLOW.md` — operation tables
- `README.md` — one COS-assignment line (dashboard prose)
- `hooks/hooks.json` + `scripts/amama_user_prompt_submit.py` — BLOCKED (hook-split) → marker only
