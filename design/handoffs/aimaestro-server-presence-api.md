# AI Maestro server — user-presence API (small enhancement)

AMAMA needs to compute the user's idle time. Two endpoints + one new field on the user record.

---

## `POST /api/sessions/me/user-input`

**Auth:** `Authorization: Bearer $AID_AUTH` (existing per-session token).
**Body:** empty.
**Effect:** server sets `users[<owner-of-session>].last_user_input_epoch = server_clock_now`.
**Response 200:**
```json
{ "recorded_at_epoch": 1746543210 }
```
**Errors:** `401` (missing/invalid bearer), `403` (session revoked).

Called from `UserPromptSubmit` hooks installed in AI Maestro-managed Claude Code sessions.

---

## `GET /api/users/me/presence`

**Auth:** `Authorization: Bearer $AID_AUTH`.
**Response 200:**
```json
{
  "last_user_input_epoch": 1746543210,
  "server_now_epoch":      1746543310
}
```
`last_user_input_epoch` is `null` if no `POST` has ever happened for this user.

**Errors:** `401`, `403`.

`server_now_epoch` is included so the client computes `age = server_now_epoch - last_user_input_epoch` against the server's clock — eliminates client-server clock skew.

Called by AMAMA on each approval-request decision.

---

## Data model

One nullable field on the user record:

```
users[<user_id>].last_user_input_epoch : integer (seconds since epoch) | null
```

Both endpoints are user-scoped (no cross-user reads or writes).
