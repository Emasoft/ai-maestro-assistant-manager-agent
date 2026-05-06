# State thresholds — reference

## Table of Contents

- [State table](#state-table)
- [Override TTL semantics](#override-ttl-semantics)
- [Override file format (phase 2)](#override-file-format-phase-2)
- [Server-clock anchored idle computation](#server-clock-anchored-idle-computation)
- [Crisis cross-reference](#crisis-cross-reference)

The single source of truth for availability-state boundaries used by both amama-presence-tracker and the upcoming `/amama-set-availability` slash command (phase 2). The idle clock is computed from the AI Maestro server's user-presence endpoint (`GET /api/users/me/presence`) — there is no host-local file involved.

## State table

| State | Auto-trigger (idle clock vs server) | User-explicit override | AMAMA authority while in this state |
|-------|--------------------------------------|-------------------------|--------------------------------------|
| `active` | `server_now - last_user_input < 30min` | `/amama-set-availability active [duration]` | Status quo. Escalate everything risky. Hard-floor still applies. |
| `monitoring` | `30min ≤ ... < 4h` | `/amama-set-availability monitoring [duration]` | Batch low-priority items. Escalate medium and above. Auto-approve **REVERSIBLE only**. |
| `away` | `4h ≤ ... < 24h` | `/amama-set-availability away [duration]` | Auto-approve **REVERSIBLE + COMPENSABLE**. Defer ONE-WAY-DOOR. Out-of-band ping for CRITICAL (phase 6). |
| `dnd` | `... ≥ 24h` (implied) | `/amama-set-availability dnd [duration]` | Auto-approve **REVERSIBLE only**. Defer COMPENSABLE and ONE-WAY-DOOR. Out-of-band ping for SEV-0 only (phase 6). |
| `unknown` | API unreachable, response malformed, auth-failed, or `last_user_input_epoch: null` | `/amama-set-availability unknown` (rarely useful) | **Refuse all autonomous action.** Escalate every approval to user. |
| `unknown-after-compaction` | First call after detected compaction restart, until next presence-tracker invocation | n/a | Same as `unknown`. |

## Override TTL semantics

The explicit-override TTL wins over the auto-clock. If the user runs `/amama-set-availability dnd 8h` and then types a clarifying message at hour 2, AMAMA stays in `dnd` until the 8h window expires. The user message IS processed normally — only the state machine does NOT snap back to `active`. This prevents the "user replies once but is otherwise away" failure mode.

When the override expires, the next `get_state()` call falls through to the auto-clock branch and re-classifies based on the current API response.

## Override file format (phase 2)

`<project>/.claude/amama/availability-overrides.md` is written by the phase-2 `/amama-set-availability` slash command. Phase-1's read-side handles file-absent → no-override gracefully. Schema (informative; phase-2 TRDD will formalize):

```yaml
---
state: dnd
since: 2026-05-05T18:30:00+0200
expires_at: 2026-05-06T02:30:00+0200
notes: explicit user override via /amama-set-availability
---
```

## Server-clock anchored idle computation

The `GET /api/users/me/presence` response always carries BOTH `last_user_input_epoch` and `server_now_epoch`. AMAMA computes:

```
age_seconds = max(0, response.server_now_epoch - response.last_user_input_epoch)
```

Using `server_now_epoch` from the same response means the comparison is purely intra-server-clock — no skew is possible. If the MANAGER's local host clock is 2 hours fast or slow, the classification is unaffected. The `max(0, ...)` clamp handles the case where the server's own clock briefly went backwards (NTP correction, leap second).

## Crisis cross-reference

| Crisis ID | Closure mechanism in this skill |
|-----------|--------------------------------|
| B2 (corrupted last-input.ts) | N/A — no host-local file; server is the source of truth |
| B3 (multi-host divergence) | Server aggregates by user; all MANAGERs see the same timestamp |
| B5 (dnd + 1 prompt mid-window) | Override TTL beats auto-clock |
| B6 (compaction during ritual) | Compaction guard in step 1 → `unknown-after-compaction` |
| B8 (NTP backward jump) | Both timestamps come from the same server response → no client-side clock involved |
| D4 (compaction destroys cue read) | Sticky-unknown until next presence-tracker call |
| G6 (multi-project cross-pollination) | Server aggregates by user across all sessions/projects on the host |
