---
name: amama-presence-tracker
description: Use to compute the user's current availability state (active/monitoring/away/dnd/unknown) before any autonomous-fallback decision. Trigger before consulting amama-autonomous-fallback when an approval request arrives from a peer agent. Loaded by ai-maestro-assistant-manager-agent-main-agent.
version: 1.0.0
context: fork
agent: amama-assistant-manager-main-agent
user-invocable: false
---

# Presence Tracker Skill

## Overview

Computes the user's current availability state from a clock-anchored signal — never from self-declaration alone. The state is one of: `active`, `monitoring`, `away`, `dnd`, `unknown`, `unknown-after-compaction`. Phase 1 of the autonomous-fallback effort (TRDD-bfcedff0). Read-side only; the writer is the upcoming PRESENCE sister plugin (phase 3).

See [state-thresholds](references/state-thresholds.md) for the full state table and authority levels per state.

## Prerequisites

- AMAMA persona loaded.
- File system access to `~/.aimaestro/host-state/last-user-input.ts` (host-global) and `<project>/.claude/amama/availability-overrides.md` (project-local, optional).
- AMAMA's CozoDB (or markdown fallback `docs_dev/sessions/availability-log.md`) for the audit trail.

## Instructions

Apply this procedure **before** invoking `amama-autonomous-fallback` for any incoming approval request.

1. **Compaction guard.** If this turn is the first user-facing turn after a detected compaction event, return `("unknown-after-compaction", now, "compaction-guard")` and stop. The flag is set by the SessionStart hook (`scripts/amama_session_start.py`) when an empty in-memory marker + recent SessionStart timestamp are observed. The flag clears the moment a phase-3 PRESENCE detector emits a fresh confirmation cue (phase 3 — not implemented in phase 1).

2. **Override check.** Read `<project>/.claude/amama/availability-overrides.md` if present. The schema is documented in [state-thresholds](references/state-thresholds.md). If a non-expired override is found, return `(override.state, override.since, "override")`. Override TTL wins over the auto-clock (see "Override TTL semantics" in references).

3. **Host-global last-input read.** Read `~/.aimaestro/host-state/last-user-input.ts`. Expected format:

   ```
   # AIMAESTRO-PRESENCE v=1
   <epoch_seconds>
   ```

   If the file is absent, return `("unknown", now, "absent-and-no-presence-plugin")`. This is the expected phase-1 result until the PRESENCE plugin ships in phase 3.

4. **Schema validation (v3 hardening #1).** If the first line is missing the magic header `# AIMAESTRO-PRESENCE v=1`, OR if the second line is not a positive integer, return `("unknown", now, "corrupt-schema")` and write a one-line entry to `docs_dev/sessions/availability-log.md` with `notes='corrupt-schema'`. NEVER attempt to recover from malformed content — refuse and degrade.

5. **Idle clock.** Compute `age_seconds = max(0, now_epoch - last_input_epoch)`. The `max(0, ...)` clamp closes crisis B8 (NTP backward jump): a negative skew must NOT cause arithmetic underflow or a wrong-state classification.

6. **State classification.** Apply [state-thresholds](references/state-thresholds.md):
   - `< 30 min`           → `active`
   - `30 min – 4 h`       → `monitoring`
   - `4 h – 24 h`         → `away`
   - `≥ 24 h`             → `dnd-implied`

7. **Audit log on transition.** When the computed state differs from the last recorded state in `docs_dev/sessions/availability-log.md`, append one row: `<timestamp+offset> | <from>→<to> | <source> | <notes>`. Best-effort: if the markdown file is unwritable, log the warning to stderr and continue.

8. **Return** the tuple `(state, since, source)`. The caller (`amama-autonomous-fallback`) uses this to gate every autonomous-fallback decision.

## Phase-1 expected result

In phase 1, before the PRESENCE sister plugin ships, step 3 returns the file-absent fallback for every call. Therefore phase 1's `get_state()` always returns `("unknown", now, "absent-and-no-presence-plugin")`. This is correct — `unknown` triggers the existing escalation rules (every approval still goes to the user). The skill is **wired but dormant** until phase 3.

## What this skill does NOT do

- Does NOT write `last-user-input.ts`. That file is written by the PRESENCE plugin in phase 3.
- Does NOT parse cue lines from any source. Phase 1 has no cue parser; phase 1.5 introduces HMAC-validated cue parsing.
- Does NOT make autonomous decisions. Decision-making lives in [amama-autonomous-fallback](../amama-autonomous-fallback/SKILL.md). This skill only reports state.

## Related

- [amama-autonomous-fallback](../amama-autonomous-fallback/SKILL.md) — the consumer of this skill's output.
- [amama-session-memory](../amama-session-memory/SKILL.md) — the existing 4-state availability model in CozoDB.
- TRDD-bfcedff0: `design/tasks/TRDD-bfcedff0-21c8-439f-a3e5-b2dcc3b8ad19-amama-phase-1-presence-matrix.md`
