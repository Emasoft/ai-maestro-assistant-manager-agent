# Governance Password — USER/UI only (R32)

## Table of Contents
- [Who uses it](#who-uses-it)
- [Security Rules](#security-rules)

Under governance rule **R32, agents NEVER use a sudo/governance password.** The
governance password is a **USER/UI credential only**: the MAESTRO user (or the
currently-active MAESTRO-DELEGATE) supplies it through the dashboard UI when an
operation is sudo-gated. AMAMA — as an agent bearing the MANAGER title —
authorizes purely via its **AID + portfolio token** (R28): the server verifies
the AID identity, the MANAGER title, and the required approval/mandate token. A
GovernanceRequest is approved on that AID basis, not on an agent-supplied password.

## Who uses it

- **MAESTRO user (via UI):** sets and supplies the governance/sudo password.
- **AMAMA / any agent:** NEVER. AMAMA does not set, store, receive, or send the
  governance password. If a deployed CLI still demands `--password` for an
  operation, that is a transition residual (R32) — AMAMA surfaces the operation
  to the MAESTRO to action via the UI rather than supplying a password itself.

Setting the password is a USER/UI action with no agent CLI verb:
<!-- DECOUPLE-BLOCKED ai-maestro#36: set-governance-password — USER/UI-only (R32); no agent verb. aimaestro-governance.sh exposes requests/request/approve/reject/transfer only. -->

## Security Rules

- AMAMA NEVER stores the governance password in any file, log, or message.
- AMAMA NEVER includes the governance password in AI Maestro messages between agents.
- The password is the MAESTRO's, supplied via the UI at runtime (R32) — never held by an agent.
- UI rate limiting: 5 failed attempts trigger a 60-second cooldown (`429 Too Many Requests`).
