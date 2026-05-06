---
name: amama-presence-tracker
description: Use when computing the user's availability state (active/monitoring/away/dnd/unknown) for autonomous-fallback gating. Trigger with availability-state checks before any decision that depends on whether the user is at the keyboard.
version: 1.1.0
context: fork
agent: amama-assistant-manager-main-agent
---

# Presence Tracker Skill

## Overview

Computes the user's availability state from a clock-anchored signal queried over REST from the AI Maestro server (`GET /api/users/me/presence`). State is one of: `active`, `monitoring`, `away`, `dnd`, `unknown`, `unknown-after-compaction`. The server records `last_user_input_epoch` on every UserPromptSubmit (via the AMAMA hook plus any other AI Maestro-managed Claude Code session that ships an equivalent hook).

## Prerequisites

- AMAMA persona loaded.
- `$AID_AUTH` and `$AIMAESTRO_API` available in the session environment.
- The AI Maestro server at `$AIMAESTRO_API` exposes the user-presence endpoints (`POST /api/sessions/me/user-input`, `GET /api/users/me/presence`).
- Append access to `docs_dev/sessions/availability-log.md` for the audit trail.

## Instructions

Apply this procedure before invoking amama-autonomous-fallback for any incoming approval request.

1. **Compaction guard.** If this is the first user-facing turn after a detected compaction, return `("unknown-after-compaction", now, "compaction-guard")` and stop.
2. **Override check.** If `<project>/.claude/amama/availability-overrides.md` carries a non-expired override, return `(override.state, override.since, "override")`.
3. **Presence read.** `GET /api/users/me/presence` with `Authorization: Bearer $AID_AUTH`. If HTTP error or transport failure, return `("unknown", now, "presence-api-unreachable")` — graceful degradation routes every approval to the user.
4. **Null check.** If response's `last_user_input_epoch` is `null` (no UserPromptSubmit has reached the server yet for this user), return `("unknown", now, "no-input-recorded")`.
5. **Idle clock — server-clock anchored.** `age_seconds = max(0, response.server_now_epoch - response.last_user_input_epoch)`. Both timestamps come from the same response, so client-server clock skew is impossible (closes crisis B8 / multi-host divergence).
6. **Classification.** Per references/state-thresholds.md: `<30min` → active, `30min-4h` → monitoring, `4h-24h` → away, `≥24h` → dnd-implied.
7. **Audit log on transition.** Append one row when computed state differs from last recorded.
8. **Return** `(state, since, source)` to the caller.

## Output

| Result | Meaning |
|--------|---------|
| `(active, ...)` | <30min idle. Status quo. |
| `(monitoring, ...)` | 30min-4h. Auto-approve REVERSIBLE only. |
| `(away, ...)` | 4h-24h. Auto-approve REVERSIBLE + COMPENSABLE. |
| `(dnd, ...)` | ≥24h or explicit override. Auto-approve REVERSIBLE only. |
| `(unknown, ..., reason)` | API unreachable, response null, malformed, auth-failed, or compaction guard. Refuse all autonomous action. |

## Error Handling

| Error | Action |
|-------|--------|
| `$AID_AUTH` empty | Return `(unknown, ..., "no-aid-auth")`. Session is not AI Maestro-managed. |
| `$AIMAESTRO_API` unreachable / timeout | Return `(unknown, ..., "presence-api-unreachable")`. Curl timeout = 2s. |
| HTTP 401 / 403 | Return `(unknown, ..., "auth-failed")`. Token is missing or revoked — escalate to user. |
| Response JSON malformed | Return `(unknown, ..., "presence-response-malformed")`. |
| Response `server_now_epoch < last_user_input_epoch` (clock skew on server) | Clamp via `max(0, ...)` — never underflow. |
| `availability-log.md` unwritable | stderr warning, continue (best-effort logging). |

## Examples

```
# Active user
GET /api/users/me/presence
→ 200 { "last_user_input_epoch": 1746543010, "server_now_epoch": 1746543310 }
age = 300 → ("active", 1746543010, "auto-clock")

# Server has no input yet
GET → 200 { "last_user_input_epoch": null, "server_now_epoch": 1746543310 }
→ ("unknown", now, "no-input-recorded")

# Override beats fresh input
override: state=dnd, expires_at=now+8h
GET → 200 (recent timestamp)
→ ("dnd", override.since, "override")

# Server unreachable
GET → curl exit 28 (timeout)
→ ("unknown", now, "presence-api-unreachable")
```

## Resources

- [references/state-thresholds.md](references/state-thresholds.md) — State table + override TTL semantics
  - State table, Override TTL semantics, Override file format (phase 2), Server-clock anchored idle computation, Crisis cross-reference

- AI Maestro server presence-API contract (handoff in repo design/handoffs/) — POST /api/sessions/me/user-input, GET /api/users/me/presence
- TRDD-bfcedff0 (design/tasks/) — Phase-1 spec, ratification gate, change log
