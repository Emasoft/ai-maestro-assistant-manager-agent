---
name: amama-presence-tracker
description: Use when computing the user's availability state (active/monitoring/away/dnd/unknown) for autonomous-fallback gating. Trigger with availability-state checks before any decision that depends on whether the user is at the keyboard.
context: fork
agent: ai-maestro-assistant-manager-agent-main-agent
---

# Presence Tracker Skill

## Overview

Computes the user's availability state from a clock-anchored signal read through the frozen AI Maestro CLI (`aimaestro-agent.sh presence`). State is one of: `active`, `monitoring`, `away`, `dnd`, `unknown`, `unknown-after-compaction`. The server records `last_user_input_epoch` on every UserPromptSubmit (via the AMAMA hook plus any other AI Maestro-managed Claude Code session that ships an equivalent hook).

## Prerequisites

- AMAMA persona loaded.
- `$AID_AUTH` available in the session environment — the CLI resolves auth from it. **Never assemble a Bearer header, an endpoint URL, or a curl command.**
- The frozen CLI `aimaestro-agent.sh` is on `$PATH` and exposes the user-presence verbs: `aimaestro-agent.sh session user-input` (write, called by the AMAMA UserPromptSubmit hook) and `aimaestro-agent.sh presence` (read, used here).
- Append access to `docs_dev/sessions/availability-log.md` for the audit trail.

## Instructions

Apply this procedure before invoking amama-autonomous-fallback for any incoming approval request.

1. **Compaction guard.** If this is the first user-facing turn after a detected compaction, return `("unknown-after-compaction", now, "compaction-guard")` and stop.
2. **Override check.** If `<project>/.claude/amama/availability-overrides.md` carries a non-expired override, return `(override.state, override.since, "override")`.
3. **Presence read (authoritative).** Run `aimaestro-agent.sh presence` with a 2s timeout. The CLI resolves auth itself from `$AID_AUTH` and prints JSON on stdout. On non-zero exit / transport failure / timeout, go to step 3b (do NOT immediately return `unknown`).
3b. **Janitor-breadcrumb fallback (degraded).** If the server is unreachable, read `~/.aimaestro/state/user-presence.json` (`{last_user_input_epoch, source, written_at_epoch}`, written by the janitor's on-prompt-submit hook + refreshed each heartbeat). If present and `written_at_epoch` is recent (< 30min stale), use its `last_user_input_epoch` with `source="janitor-breadcrumb"`. If absent or stale, return `("unknown", now, "presence-unreachable")` — graceful degradation routes every approval to the user. (The janitor writing this breadcrumb is a coordination follow-up; until it lands, server-unreachable → `unknown`.)
4. **Null check.** If the chosen source's `last_user_input_epoch` is `null` (no UserPromptSubmit recorded yet), return `("unknown", now, "no-input-recorded")`.
5. **Idle clock — server-clock anchored.** `age_seconds = max(0, response.server_now_epoch - response.last_user_input_epoch)`, where `response` is the JSON printed by `aimaestro-agent.sh presence`. Both timestamps come from the same response, so client-server clock skew is impossible (closes crisis B8 / multi-host divergence).
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
| `(unknown, ..., reason)` | Presence read failed (CLI error / unreachable), response null, malformed, auth-failed, or compaction guard. Refuse all autonomous action. |

## Error Handling

| Error | Action |
|-------|--------|
| `$AID_AUTH` empty | Return `(unknown, ..., "no-aid-auth")`. Session is not AI Maestro-managed. |
| `aimaestro-agent.sh presence` not on `$PATH` | Return `(unknown, ..., "presence-api-unreachable")`. AI Maestro CLI is not installed. |
| Server unreachable / CLI timeout (non-zero exit) | Return `(unknown, ..., "presence-api-unreachable")`. CLI timeout = 2s. |
| CLI reports an auth failure (token missing or revoked) | Return `(unknown, ..., "auth-failed")`. Escalate to user. |
| CLI stdout is not valid JSON | Return `(unknown, ..., "presence-response-malformed")`. |
| Response `server_now_epoch < last_user_input_epoch` (clock skew on server) | Clamp via `max(0, ...)` — never underflow. |
| `availability-log.md` unwritable | stderr warning, continue (best-effort logging). |

## Examples

```
# Active user
aimaestro-agent.sh presence
→ { "last_user_input_epoch": 1746543010, "server_now_epoch": 1746543310 }
age = 300 → ("active", 1746543010, "auto-clock")

# Server has no input yet
aimaestro-agent.sh presence
→ { "last_user_input_epoch": null, "server_now_epoch": 1746543310 }
→ ("unknown", now, "no-input-recorded")

# Override beats fresh input
override: state=dnd, expires_at=now+8h
aimaestro-agent.sh presence → recent timestamp
→ ("dnd", override.since, "override")

# Server unreachable
aimaestro-agent.sh presence → non-zero exit (timeout)
→ ("unknown", now, "presence-api-unreachable")
```

## Resources

- [references/state-thresholds.md](references/state-thresholds.md) — State table + override TTL semantics
  - State table, Override TTL semantics, Override file format (phase 2), Server-clock anchored idle computation, Crisis cross-reference

- AI Maestro frozen-CLI presence contract (handoff in repo design/handoffs/) — `aimaestro-agent.sh session user-input` (write), `aimaestro-agent.sh presence` (read)
- TRDD-bfcedff0 (design/tasks/) — Phase-1 spec, ratification gate, change log
