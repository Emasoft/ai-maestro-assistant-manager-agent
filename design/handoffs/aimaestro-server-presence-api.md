# AI Maestro server — user-presence API enhancement (handoff spec)

**Requested by:** AMAMA plugin (`ai-maestro-assistant-manager-agent`)
**Motivation:** Replaces the proposed `ai-maestro-presence` sister plugin in the v2/v3 synthesis. Server is the natural source of truth for user activity; a separate plugin was over-engineering.
**Authoritative for AMAMA:** Yes — once these endpoints exist, AMAMA's `amama-presence-tracker` skill switches from "read host-global file" to "GET this endpoint". No host-local presence file is needed.
**Audit references in AMAMA repo:**
- TRDD `design/tasks/TRDD-bfcedff0-21c8-439f-a3e5-b2dcc3b8ad19-amama-phase-1-presence-matrix.md` — phase-1 spec (already shipped in v2.8.0)
- Audit `reports/assistant-manager-audit/20260504_023156+0200-orchestration-capability-audit.md` — Gap B (active user-presence detector)
- Synthesis `reports/assistant-manager-audit/20260504_153853+0200-crisis-stress-test-plan-v3.md` — Crises B2, B3, B4, B6, D4, G6 are closed by this server-side approach (not by a local file).

---

## 1. Goal

Give AMAMA (and any peer host's MANAGER, in multi-host deployments) a single authoritative answer to the question:

> When did the human user last type a prompt anywhere in the AI Maestro ecosystem they own?

That timestamp drives AMAMA's 4-state availability machine (`active` < 30 min, `monitoring` 30 min – 4 h, `away` 4 h – 24 h, `dnd` ≥ 24 h or explicit override). When the user is not `active`, AMAMA may take pre-classified routine reversible operations on their behalf and log them for ratification on return.

The server already tracks session lifecycles, agent registry, AMP routing, and governance requests. Adding one field per user (`last_user_input_epoch`) is a small enhancement that consolidates a missing piece into the existing source of truth.

---

## 2. Endpoint A — record user input (WRITE)

Called by Claude Code sessions whenever the human user submits a prompt. One call per `UserPromptSubmit` event. May be invoked from any AI Maestro-managed session, not only AMAMA.

### Request

```
POST /api/sessions/me/user-input
Authorization: Bearer $AID_AUTH
Content-Type: application/json
(empty body — server uses its own clock)
```

`$AID_AUTH` is the standard per-session AID secret already documented in the persona (`mst_*` token).

### Response — happy path

```
200 OK
Content-Type: application/json
{
  "recorded_at_epoch": 1746543210,
  "recorded_at_iso":   "2026-05-05T22:30:10+02:00",
  "session_id":        "<aid-resolved-from-bearer>",
  "user_id":           "<HUMAN-identity-resolved-from-aid>"
}
```

### Response — error

| Status | Body shape | Trigger |
|--------|------------|---------|
| `401`  | `{"error":"missing-or-invalid-bearer"}` | No `Authorization` header / unparseable token |
| `403`  | `{"error":"session-revoked"}`           | AID was revoked / session deleted |
| `429`  | `{"error":"rate-limited","retry_after":N}` | If you choose to rate-limit; **see §5.5** |
| `5xx`  | standard server error                    | Implementation issue |

### Behavior

1. Resolve session from `$AID_AUTH`. Reject if invalid (`401`/`403`).
2. Resolve the HUMAN user that owns the session.
3. Set `users[user_id].last_user_input_epoch = server_clock_now_epoch`.
4. Return the recorded timestamp + identifiers as JSON.

### Idempotency

Last-write-wins. Calling this endpoint twice in the same second simply leaves the field at the later second. No race-condition concern.

---

## 3. Endpoint B — read user presence (READ)

Called by AMAMA on every approval-request decision (typically once every few seconds at peak, much less when idle). Returns the user's last-input timestamp so AMAMA can compute the state locally.

### Request

```
GET /api/users/me/presence
Authorization: Bearer $AID_AUTH
```

### Response — user has at least one recorded input

```
200 OK
Content-Type: application/json
{
  "user_id":               "<HUMAN-identity>",
  "last_user_input_epoch": 1746543210,
  "last_user_input_iso":   "2026-05-05T22:30:10+02:00",
  "server_now_epoch":      1746543310,
  "server_now_iso":        "2026-05-05T22:31:50+02:00"
}
```

### Response — user has no recorded input yet (first-time setup)

```
200 OK
Content-Type: application/json
{
  "user_id":               "<HUMAN-identity>",
  "last_user_input_epoch": null,
  "last_user_input_iso":   null,
  "server_now_epoch":      1746543310,
  "server_now_iso":        "2026-05-05T22:31:50+02:00"
}
```

`null` is intentional — AMAMA treats it as `unknown` and falls back to "always escalate", which is the safe default.

### Response — error

| Status | Body shape | Trigger |
|--------|------------|---------|
| `401`  | `{"error":"missing-or-invalid-bearer"}` | No / bad bearer |
| `403`  | `{"error":"session-revoked"}`           | AID revoked |
| `5xx`  | standard error                           | Implementation issue |

### Behavior

1. Resolve session from `$AID_AUTH`.
2. Resolve owning HUMAN.
3. Read `users[user_id].last_user_input_epoch`.
4. Return both the user's timestamp and the **server's current clock**. AMAMA computes `age = server_now_epoch - last_user_input_epoch` against the server's clock to avoid client-server clock-skew (closes a residual subset of crisis B8 — NTP drift between MANAGER and server).

### Why the server returns `server_now_epoch`

AMAMA's `amama-presence-tracker` skill uses `max(0, server_now_epoch - last_user_input_epoch)` rather than `local_clock_now - last_user_input_epoch`. Returning both timestamps in the same response means the comparison is purely intra-server-clock — no skew possible. (Without this, a MANAGER on a host whose clock is 2 hours fast would compute `age = 7220 s` for a user who just typed, and incorrectly classify state as `monitoring` instead of `active`.)

---

## 4. Internal data model — minimum addition

One nullable field on the user record:

```
users:
  <user_id>:
    ...existing fields...
    last_user_input_epoch:  integer | null      # seconds since 1970-01-01 UTC
```

No schema migration concerns — the field is nullable; existing users start with `null` and become populated on first WRITE.

No new tables needed. No history tracking is required (only the most recent timestamp matters for the read).

If you want telemetry / debugging, an optional second field:

```
    last_user_input_session_id: string | null   # which session reported it last
```

— is harmless but not required.

---

## 5. Operational notes

### 5.1 Multi-host

The user may run MANAGERs on multiple hosts, each with its own `$AID_AUTH`, all owned by the same HUMAN. Endpoint B aggregates by **user**, not by session. The server stores a single `last_user_input_epoch` per user. When the user types on host A, host B's MANAGER sees the same fresh timestamp. Closes crisis B3 (multi-host divergence) "for free" — no plugin-side coordination needed.

### 5.2 Cross-session within one host

Likewise: the user typing into a PROGRAMMER session on the same host must update the same field that AMAMA reads. Endpoint A is called by **every** AI Maestro-managed Claude Code session's `UserPromptSubmit` hook — not only by AMAMA's session. The hook's payload doesn't matter (no body needed); the bearer token tells the server which user, and the server's clock gives the timestamp.

### 5.3 Hook deployment

The `UserPromptSubmit` hook that calls Endpoint A can be installed via:
- A **shared Claude Code plugin** that any AI Maestro-aware session installs (probably the cleanest — small, single-purpose).
- The **AMAMA plugin's own UserPromptSubmit hook** — but this only captures input to AMAMA's session, not other sessions on the host. Insufficient.
- The **AI Maestro CLI / session manager** that boots each session — wraps the hook config at session-start time.

I'll let the AI Maestro server team decide the rollout path. AMAMA only needs Endpoint B to be reliable.

### 5.4 Stale data / TTL

No TTL needed. The timestamp is monotonically updated and never expires. If a user is gone for a year, the field still holds their last timestamp from a year ago — and AMAMA correctly classifies them as `dnd` (≥ 24 h since last input).

### 5.5 Rate limiting

Endpoint A may be hit dozens of times per minute under heavy use (every prompt). Recommend **no application-level rate limit** — a simple field update is cheap, and rate-limiting it could distort the very signal we're trying to capture. If you must rate-limit, set the threshold high (e.g. ≥ 1 call per second per session) and return `429` with `retry_after` so the hook can backoff gracefully without losing the eventual write.

Endpoint B will be called by each AMAMA-running host roughly once per inbound approval request — typically dozens per hour, peaks of one per second during heavy periods. Trivially serveable.

### 5.6 Privacy / scope

Both endpoints are user-scoped. No cross-user leakage:
- Endpoint A can only update the requesting user's own field.
- Endpoint B can only read the requesting user's own field.
- No need for a "list all users' presence" endpoint — that'd be a privacy hole.

If a user has an admin-level MANAGER on another user's behalf (uncommon), authorization should reject the read.

### 5.7 Observability

A single new field is hard to mis-wire, but:
- Log the WRITE call at `debug` level (one line per call).
- Counter: `presence_write_total` per user.
- Counter: `presence_read_total` per user.
- Histogram: `presence_age_seconds_observed` on read (handy to check that values are sensible).

---

## 6. Test scenarios

The server team can derive a unit-test checklist from these:

| # | Scenario | Setup | Action | Expected |
|---|----------|-------|--------|----------|
| 1 | Single user, single session, write+read | Fresh DB, register one session for user A | A: write A's input. B: read A's presence. | B returns A's WRITE timestamp |
| 2 | Single user, two sessions, two writes | Two sessions for user A | Both write at different times | Read returns the newer of the two timestamps |
| 3 | Two users, no leakage | Sessions for users A and B | A writes; B reads | B sees `null` (or B's own timestamp) — never A's |
| 4 | First-time read | New user, no WRITE yet | Read | `last_user_input_epoch: null`, `server_now_epoch` populated |
| 5 | Bearer missing | No Authorization header | Either endpoint | `401` |
| 6 | Bearer revoked | AID was deleted | Either endpoint | `403` |
| 7 | Server clock returned on read | Any user with an input | Read | Response has `server_now_epoch` and `server_now_iso` set to wall-clock at read time |
| 8 | Cross-host aggregation | User A has sessions on host X and host Y | Host X writes (now-30s); host Y reads | Host Y sees the timestamp from host X |
| 9 | Multi-write idempotency | Single session writes 5 times in 1s | Read after | Latest of the 5 timestamps wins; no errors |
| 10 | Server restart durability | User A wrote yesterday; server restarted | Read today | Yesterday's timestamp still returned |

---

## 7. AMAMA-side changes (informational, not part of this PR)

For the AI Maestro server team's awareness — these will land in the AMAMA repo once the endpoints exist; **not** part of this server PR:

- `skills/amama-presence-tracker/SKILL.md` step 3 changes from "read host-global file" to "call `GET /api/users/me/presence`".
- `references/state-thresholds.md` adds `server_now_epoch` to the clock-skew clamp computation.
- The proposed `ai-maestro-presence` sister plugin is **dropped from the roadmap**.
- The proposed HMAC cue parser (phase 1.5 hardening #4) is **dropped** — there are no cues to forge when presence is queried via authenticated REST.

---

## 8. Done definition for this server PR

- [ ] Endpoint A accepts a `POST` from a valid AID and updates the user's `last_user_input_epoch`.
- [ ] Endpoint B returns the user's `last_user_input_epoch` and the `server_now_epoch` in one response.
- [ ] Both endpoints reject unauthenticated and cross-user requests.
- [ ] At least the 10 test scenarios in §6 pass.
- [ ] OpenAPI / docs updated (if the server publishes a spec).
- [ ] Changelog mentions the addition.

Once merged, AMAMA can ship a follow-up patch (~5 lines) that flips its `amama-presence-tracker` skill from file-based to REST-based — at which point phase-1 autonomy logic activates without needing a PRESENCE plugin.
