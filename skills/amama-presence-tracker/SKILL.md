---
name: amama-presence-tracker
description: Use when computing the user's availability state (active/monitoring/away/dnd/unknown) for autonomous-fallback gating. Trigger with availability-state checks before any decision that depends on whether the user is at the keyboard.
version: 1.0.0
context: fork
agent: amama-assistant-manager-main-agent
---

# Presence Tracker Skill

## Overview

Computes the user's availability state from a clock-anchored signal (the host-global file `~/.aimaestro/host-state/last-user-input.ts`) — never from self-declaration alone. State is one of: `active`, `monitoring`, `away`, `dnd`, `unknown`, `unknown-after-compaction`. Phase 1 of TRDD-bfcedff0. Read-side only — the writer is the upcoming PRESENCE sister plugin (phase 3). Until phase 3 ships, this skill always returns `unknown`, which routes every approval through the existing escalation path. **No regressions in production until phase 3.**

## Prerequisites

- AMAMA persona loaded.
- Read access to `~/.aimaestro/host-state/last-user-input.ts` (host-global) and `<project>/.claude/amama/availability-overrides.md` (project-local, optional).
- Append access to `docs_dev/sessions/availability-log.md` for the audit trail.

## Instructions

Apply this procedure before invoking amama-autonomous-fallback for any incoming approval.

1. **Compaction guard.** If this is the first user-facing turn after a detected compaction, return `("unknown-after-compaction", now, "compaction-guard")` and stop.
2. **Override check.** If `<project>/.claude/amama/availability-overrides.md` carries a non-expired override, return `(override.state, override.since, "override")`.
3. **Host-global read.** Read `~/.aimaestro/host-state/last-user-input.ts`. If absent, return `("unknown", now, "absent-and-no-presence-plugin")` — the expected phase-1 result.
4. **Schema validation (v3 hardening #1).** First line MUST be `# AIMAESTRO-PRESENCE v=1`; second line MUST be a positive integer epoch. Otherwise return `("unknown", now, "corrupt-schema")` and log to availability-log.
5. **Idle clock.** `age_seconds = max(0, now_epoch - last_input_epoch)` — the `max(0, ...)` clamp closes crisis B8 (NTP backward jump).
6. **Classification.** Per references/state-thresholds.md: `<30min` → active, `30min-4h` → monitoring, `4h-24h` → away, `≥24h` → dnd-implied.
7. **Audit log on transition.** Append one row when computed state differs from last recorded.
8. **Return** `(state, since, source)` to the caller.

Phase-1 expected behavior: file is absent (PRESENCE plugin not yet shipped), so step 3 returns `unknown`. The skill is wired but dormant until phase 3.

## Output

| Result | Meaning |
|--------|---------|
| `(active, since, ...)` | User is at the keyboard (<30min idle). Status quo. |
| `(monitoring, since, ...)` | 30min-4h idle. Auto-approve REVERSIBLE only. |
| `(away, since, ...)` | 4h-24h idle. Auto-approve REVERSIBLE + COMPENSABLE. |
| `(dnd, since, ...)` | >24h idle or explicit override. Auto-approve REVERSIBLE only. |
| `(unknown, now, ...)` | File absent / corrupt / no override. Refuse all autonomous action. |
| `(unknown-after-compaction, now, ...)` | First turn after detected compaction. Sticky until next PRESENCE confirmation. |

## Error Handling

| Error | Action |
|-------|--------|
| `last-user-input.ts` missing | Return `(unknown, ..., "absent-and-no-presence-plugin")` |
| Magic header missing or `v != 1` | Return `(unknown, ..., "corrupt-schema")` + log |
| Second line not a positive integer | Return `(unknown, ..., "corrupt-schema")` + log |
| `availability-log.md` unwritable | stderr warning, continue (best-effort logging) |
| `now < last_input_epoch` (clock skew) | Clamp via `max(0, ...)` — never underflow |

## Examples

**Phase-1 default (file absent):**
```
get_state() → ("unknown", 1746543210, "absent-and-no-presence-plugin")
```

**Active user (post-phase-3, file present):**
```
# AIMAESTRO-PRESENCE v=1
1746543010
get_state() at 1746543210 → ("active", 1746543010, "auto-clock")
```

**Override holds over recent input:**
```
override:  state=dnd, expires_at=now+8h
last-user-input.ts:  recent (now-30s)
get_state() → ("dnd", override.since, "override")
```

**Corrupt schema:**
```
last-user-input.ts:  "not_a_number\nlol\n"
get_state() → ("unknown", now, "corrupt-schema")
audit-log: schema-mismatch on line 1
```

## Resources

- [references/state-thresholds.md](references/state-thresholds.md) — State table + override TTL semantics
  - State table, Override TTL semantics, Override file format (phase 2), Phase-1 default behavior, NTP-skew clamp, Crisis cross-reference

- TRDD-bfcedff0: design/tasks/TRDD-bfcedff0-21c8-439f-a3e5-b2dcc3b8ad19-amama-phase-1-presence-matrix.md — Spec
  - Sections: User request, Why phase 1 first, Files, Test scenarios, Reversibility, Security, DoD, Open questions, Ratification gate
