# State thresholds — reference

## Table of Contents

- [State table](#state-table)
- [Override TTL semantics](#override-ttl-semantics)
- [Override file format (phase 2)](#override-file-format-phase-2)
- [Phase-1 default behavior](#phase-1-default-behavior)
- [NTP-skew clamp](#ntp-skew-clamp)
- [Crisis cross-reference](#crisis-cross-reference)

The single source of truth for availability-state boundaries used by both amama-presence-tracker (read-side, this phase) and the upcoming `/amama-set-availability` slash command (phase 2). All times are computed against `~/.aimaestro/host-state/last-user-input.ts`, the host-global epoch written by the PRESENCE sister plugin (phase 3).

## State table

| State | Auto-trigger (idle clock) | User-explicit override | AMAMA authority while in this state |
|-------|---------------------------|-------------------------|--------------------------------------|
| `active` | `now - last_user_input < 30min` | `/amama-set-availability active [duration]` | Status quo. Escalate everything risky. Hard-floor still applies. |
| `monitoring` | `30min ≤ ... < 4h` | `/amama-set-availability monitoring [duration]` | Batch low-priority items. Escalate medium and above. Auto-approve **REVERSIBLE only**. |
| `away` | `4h ≤ ... < 24h` | `/amama-set-availability away [duration]` | Auto-approve **REVERSIBLE + COMPENSABLE**. Defer ONE-WAY-DOOR. Out-of-band ping for CRITICAL (phase 6). |
| `dnd` | `... ≥ 24h` (implied) | `/amama-set-availability dnd [duration]` | Auto-approve **REVERSIBLE only**. Defer COMPENSABLE and ONE-WAY-DOOR. Out-of-band ping for SEV-0 only (phase 6). |
| `unknown` | `last-user-input.ts` missing or schema-invalid; no override; or compaction observed in this turn | `/amama-set-availability unknown` (rarely useful) | **Refuse all autonomous action.** Escalate every approval to user. |
| `unknown-after-compaction` | First call after detected compaction restart, until next phase-3 PRESENCE confirmation | n/a | Same as `unknown`. Sticky until cleared by a fresh PRESENCE cue. |

## Override TTL semantics

The explicit-override TTL wins over the auto-clock. If the user runs `/amama-set-availability dnd 8h` and then types a clarifying message at hour 2, AMAMA stays in `dnd` until the 8h window expires. The user message IS processed normally — only the state machine does NOT snap back to `active`. This prevents the "user replies once but is otherwise away" failure mode.

When the override expires, the next `get_state()` call falls through to the auto-clock branch and re-classifies based on `last-user-input.ts`.

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

## Phase-1 default behavior

In phase 1 the PRESENCE sister plugin has not shipped yet, so `~/.aimaestro/host-state/last-user-input.ts` is absent. The read-side gracefully returns `unknown` for every call, which routes every approval through the existing escalation path. No regressions.

## NTP-skew clamp

When computing `age_seconds`, always use `max(0, now_epoch - last_input_epoch)`. A negative skew (system clock jumped back) MUST NOT cause arithmetic underflow or wrong-state classification. The clamp is the single defensive guard for crisis B8.

## Crisis cross-reference

| Crisis ID | Closure mechanism in this skill |
|-----------|--------------------------------|
| B2 (corrupted last-input.ts) | Schema validation in step 4 → `unknown` |
| B5 (dnd + 1 prompt mid-window) | Override TTL beats auto-clock |
| B6 (compaction during ritual) | Compaction guard in step 1 → `unknown-after-compaction` |
| B8 (NTP backward jump) | `max(0, ...)` clamp in step 5 |
| D4 (compaction destroys cue read) | Sticky-unknown until PRESENCE re-confirms |
| G6 (multi-project cross-pollination) | Host-global file read (step 3) — same `last_user_input` for all projects on the host |
