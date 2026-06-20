# Fleet readiness — executable finish-checklist

The remaining steps to FINISH fleet readiness, each with its owner + exact action.
Authored by the MANAGER (AMAMA). Everything an in-bounds MANAGER can do unilaterally
is done; the steps below each require a specific actor (server auth / session / owner)
the MANAGER provably cannot be. Do them in order; steps 2–6 unblock once step 1 lands.

## Step 1 — DEPLOY the CLI layer  (owner: ai-maestro Claude, or USER)
The keystone. `aimaestro-teams.sh` + `aimaestro-governance.sh` exist in
`~/ai-maestro/scripts/` (frozen) but aren't installed to PATH.
- Apply the exact installer diff: ai-maestro#36 `issuecomment-4721617777`
  (add both to `install-agent-cli.sh` `INSTALLED_FILES` + staging + install blocks).
- Run `install-agent-cli.sh` → both CLIs land on `~/.local/bin` for the whole local fleet.
- BUILD the missing verbs (server knowledge required): `kanban-config`, `presence`
  (`/api/users/{id}/presence`), expose `session user-input` in `agent-session.sh`,
  plus the cross-fleet gap candidates in ai-maestro#36 `issuecomment-4722058864`
  (team-tasks, governance status/manager/attestation/members/pubkey, hosts/identity, users, teams/stats).
  `transfer` already exists.
- Signal MANAGER springs on: `[ -e ~/.local/bin/aimaestro-teams.sh ]`.

## Step 2 — AMAMA merge + publish  (owner: MANAGER, AUTO on step 1)
Branch `decouple/api-to-frozen-cli` is ready (commit-not-publish).
- Smoke-test the repointed team/governance CLI calls (needs an AID_AUTH'd session).
- Merge `decouple/api-to-frozen-cli` → `main`; run `publish.py`.
- As each build verb lands, repoint AMAMA's 5 `DECOUPLE-BLOCKED ai-maestro#36` residuals.

## Step 3 — Each plugin's repoint slice  (owner: each plugin's Claude)
Recipe ready: AMAMA#16 `issuecomment-4721952538` (verb table + rules + marker convention
plus the "verify your agents' hallucinated verbs" warning). COS already self-decoupling
(`TRDD-…-remove-direct-api-calls`); orchestrator self-audited on #16. Most other plugins'
raw `/api/` is noise (descriptive REFERENCE docs / test fixtures / OAuth-rotator), so the
real per-plugin work is small — each Claude runs the recipe on its own source (its conventions loaded).

## Step 4 — Memory migration  (owner: integrator + amvcp Claudes)
Last 2 of 10 for the proactive-memory rollout (TRDD-d369cf76). Recall/write contract +
3 scopes per the rollout pattern the other 8 plugins already adopted.

## Step 5 — Land governance rules  (owner: governance owner / ai-maestro Claude)
Add the decoupling invariant + the memory invariant to the canonical
`ai-maestro-plugin/skills/team-governance/references/GOVERNANCE-RULES.md` (currently ends at R21).
- ASSIGN final rule numbers — note the collision: ai-maestro#33 already uses "R22" for the
  GitHub-authorship rule, so decoupling/memory need distinct numbers (R23+).
- Sync the §0 mirror list on edit (the doc has documentation + persona mirrors).
- Draft principle text is in AMAMA#16 / the api-to-cli mapping spec; the owner finalizes wording+numbers.

## Step 6 — Propagate  (owner: MANAGER, after step 5)
Once landed, cite the new rule numbers fleet-wide (replace the loose "R22" proposal label).

---
The single USER lever that starts the chain: **nudge the ai-maestro session to wake** (step 1 is
copy-paste) and the idle plugin/integrator/amvcp sessions. The MANAGER holds heartbeat-watch and
springs on step 1's signal.
