---
name: amama-agent-unblock
description: Use when an agent has gone quiet, stopped answering AMP messages, or looks stuck — determine whether it is BLOCKED and why, and answer its pending question. Trigger on "agent not responding", "stalled agent", "is it blocked or idle", before escalating a silent agent to the user.
context: fork
background: false
agent: ai-maestro-assistant-manager-agent-main-agent
---

# Agent Unblock Skill

> **Never call the ai-maestro server API directly.** No skill, agent, command, hook, MCP config, bundled script, or setting may issue a request to `/api/…`, nor instruct an agent to (R23.1). Every server interaction goes through the frozen CLI layer installed with ai-maestro — `~/.local/bin/aimaestro-*.sh`, `amp-*.sh`, `aid-*.sh` (R23.2).
>
> Two independent reasons, and either alone invites a workaround:
> 1. **The CLI runs the pipeline, governance and audit gates that a raw route bypasses.** A direct call is *unaudited even when it works* — it succeeds and leaves no trace in the ledgers the fleet is governed by.
> 2. **Server routes are renameable; the CLI interface is frozen** (R23.4). Route-coupled code breaks silently on a server release, and the breakage surfaces as an agent that has quietly stopped working.
>
> There is **no element-level exception — not even for the core `ai-maestro-plugin`** (R23.5). The boundary is the script layer, not any particular plugin.
>
> **RULE 1 — this is the ONLY case where you may send a command to another agent.** The USER, verbatim: *"the case where the work is blocked must be the only case where the MANAGER or the CHIEF-OF-STAFF are allowed to directly send commands, otherwise all directives must go via normal AMP messages agent-to-agent"*. Everything else — mandates, priorities, questions, corrections — is an **AMP message** (R6 v3, through the COS). R42 locks `inject`, `slash`, `queue` and `state --pane` to **self-only for every title, MANAGER included**. If you catch yourself wanting to inject a directive, the answer is an AMP message, every time.

## Overview

An agent stopped responding. This skill decides which of two very different things is true — it is **waiting on a prompt only you can answer** (`reason` is `ask_user` or `permission`), or it is **not** — and answers the prompt in the first case only.

Note the distinction the `reason` enum draws and this skill turns on: `blocked` is not the same as *answerable*. A `rate_limited` or `api_error` agent can report `blocked=true` — it is genuinely stopped — but it has **asked nothing**, so there is no prompt to answer and injecting into it is plain injection. Read `reason`, never `blocked` alone.

Why it exists: the whole premise of AI Maestro is teams working autonomously without human supervision. An agent blocked on an `AskUserQuestion` waits **forever** — nothing times it out, and it generates no events while it waits, so it does not look broken to anything that watches for events.

## The trap this skill exists to correct

**`aimaestro-session.sh read-prompt <agent>` is NOT sufficient, and reading its `null` as "nothing is wrong" is how an agent stays stuck.** `read-prompt` returns what the plugin **hook** recorded into chat-state. Measured by the hub across 419 live chat-state files on one host:

| signal | files carrying it |
|---|---|
| `status: waiting_for_input` | 21 |
| `notificationType` | 21 |
| permission `options` | 1 |
| `question` (AskUserQuestion) | **0 — never** |

Three consequences, each of which has bitten a live agent:

1. **An `AskUserQuestion` produces no pending record at all** — `read-prompt` answers `null` for the one prompt shape that blocks forever.
2. **`status` cannot tell blocked from idle** — both read `waiting_for_input`. The discriminator is `notificationType`, not the field you would reach for.
3. **Chat-state goes stale silently** — the hook writes on events and a blocked agent generates none, so *"no recent event" is indistinguishable from "healthy."*

`block-state` reads the **terminal** instead — what is on screen now — which is why it sees what the hook missed. The two are **not alternatives**: `read-prompt` is the hook's view, `block-state` is the pane's, and when they disagree `block-state` says so via `hookDisagreed` (the hook is measured to type an `AskUserQuestion` as `permission_prompt`). **A disagreement is a fact to report, not noise to smooth over.**

## Prerequisites

- AMAMA persona loaded; you hold the `manager` title (a CHIEF-OF-STAFF may run this for **its own team only**; never an ASSISTANT).
- `$AID_AUTH` in the session environment — the CLI resolves auth from it. **Never assemble a Bearer header, an endpoint URL, or a curl command.** Agent callers need no sudo token.
- `aimaestro-session.sh` on `$PATH` and exposing `block-state`. If it reports `unknown command: block-state`, the PATH copy is stale — the repo and `~/.local/bin` are separate things. Report that to the user rather than routing around it.

## Instructions

### 1. DETECT

```bash
aimaestro-session.sh block-state <agent>
```

Returns JSON: `blocked` (bool), `reason`, `field` (`visible`/`empty`/`text` — is the input box there and clear), `choices` (option keys + labels), `excerpt` (the question verbatim), `hookDisagreed`, `sessionName`.

### 2. UNDERSTAND — only if the excerpt is not enough

```bash
aimaestro-session.sh block-state <agent> --match "MANDATE|Task B|error"
```

The regex is evaluated **server-side**, so only matching lines cross the boundary — never the whole pane. It is served **only while the agent is blocked** (409 otherwise): you search a pane to learn why work stopped, and holding a title does not entitle you to an oracle over anything the agent was ever shown.

### 3. DECIDE — the gate, before you act

| `reason` | Blocked by | Act? |
|---|---|---|
| `ask_user` | an `AskUserQuestion` it raised | **YES** — answer it |
| `permission` | a permission prompt | **YES** — answer it |
| `rate_limited` | the API window | **NO** — it clears itself. If the exhausted window is MODEL-scoped (the account still has 5h/7d headroom), the cheap remedy is the agent switching its OWN model via the curated `model-opus` / `model-sonnet` slash keys — you cannot do that for it (slash is self-only), so ask by AMP |
| `api_error` | a transport/API failure | **NO** — it asked nothing; injecting is plain injection |
| `idle` | nothing — it wants work | **NO** — work arrives by **AMP message** |
| `active` | nothing — it is working | **NO** |
| `unknown` | undetermined | **NO** — investigate, report |

**If `blocked` is false, or `reason` is anything other than `ask_user` / `permission`: do NOT inject.** A stalled agent is not automatically an answerable one — a rate-limited or erroring agent has asked no question, and answering into it is exactly the unsolicited injection the gate exists to prevent.

### 4. ACT — answer the agent's own question

```bash
aimaestro-session.sh answer <agent> --option 2
aimaestro-session.sh answer <agent> --text "hold that until I confirm"
```

Pick `--option` when `choices` is non-empty and one fits; `--text` for a free-text prompt or when no choice fits. Answer with the **user's** decision when the question needs one — this verb is a delivery mechanism, not a licence to decide on the user's behalf.

### 5. RECORD

Log the unblock in the agent's TRDD or your session memory: which agent, `reason`, the question, the answer sent, and `hookDisagreed` if true. An unblock is a cross-agent command — the one permitted kind — so it leaves a trace.

## Output

| Result | Meaning | Next |
|---|---|---|
| `blocked=true reason=ask_user` | It raised a question and is waiting | Answer it (step 4), then record |
| `blocked=true reason=permission` | Waiting on a permission prompt | Answer it (step 4), then record |
| `blocked=true reason=rate_limited\|api_error` | Stalled, but nothing was asked | Do NOT inject. Report; a rate limit self-clears |
| `blocked=false reason=idle` | Not stuck — it wants work | Send an **AMP message** (never an inject) |
| `blocked=false reason=active` | Working | Nothing to do |
| `reason=unknown` | The pane did not resolve to a known shape | Do NOT inject. Investigate and report |
| `hookDisagreed=true` | Pane and hook contradict each other | Trust the pane, and **report the disagreement** |

## Error Handling

| Error | Meaning | Action |
|---|---|---|
| `409` from `answer` | The agent is not provably waiting on a question of its own | **The system working — not a bug to route around.** Re-run `block-state`; if it now reads `ask_user`, the state changed under you |
| `409` from `--match` | The agent is not blocked | Do not retry; a pane search is only for a stopped agent |
| `403` | Title/scope refusal (COS reaching outside its team; any ASSISTANT; a self-only verb) | Do not escalate privilege, do not retry. Route the intent as an AMP message |
| `401 auth_required` | `$AID_AUTH` missing or revoked | Report to the user. Never substitute a sudo token you were not given |
| `unknown command: block-state` | The `~/.local/bin` copy is stale | Report it — the deployed CLI needs a redeploy. Do NOT fall back to `read-prompt` and conclude "fine" |
| `blocked=true` but `field.visible=false` | The pane has no input box | Do NOT type into it. Report |

## Examples

```
# The case that motivated all of this
aimaestro-session.sh block-state worker-alpha
→ { "blocked": true, "reason": "ask_user",
    "choices": [ { "key": "1", "label": "Proceed now with Task B" }, ... ],
    "hookDisagreed": true }
   (read-prompt for the same agent → null, and the hook typed it `permission_prompt`)
→ user decides option 1
aimaestro-session.sh answer worker-alpha --option 1
→ unblocked; record the unblock + the hook disagreement

# Quiet, but nothing to answer
aimaestro-session.sh block-state worker-beta
→ { "blocked": false, "reason": "idle" }
→ do NOT inject. It is waiting for work — send an AMP mandate through the COS.

# Stalled, but it asked nothing
aimaestro-session.sh block-state worker-gamma
→ { "blocked": true, "reason": "rate_limited" }
→ do NOT inject. The window clears itself; report the wait to the user.
```

## Resources

- `aimaestro-session.sh help` — the deployed verb surface and its own R42/R42.8 limits table (authoritative over any doc, including this one).

> **R42.8 is a PENDING AMENDMENT, not a ratified rule — verified 2026-08-07.** `Emasoft/ai-maestro#125` ("R42 amendment request") is **OPEN**, and the governance SSOT (`docs/GOVERNANCE-RULES.md` on the unmerged `governance-rules` branch) tops out at **R42.7** — R42.8 appears nowhere in it. What exists today is a **server-side capability** (the route ships, the CLI help cites R42.8) authorized by a **direct USER directive**, not a rule you can cite. So: keep using the procedure — the USER asked for it and the server enforces the gate — but do **not** justify it to another agent by quoting R42.8 as settled governance, and expect the numbering to change if the amendment lands differently. If the refusal you meet is a governance one rather than a 403/409, escalate rather than argue the rule.
- [ai-maestro#35](https://github.com/Emasoft/ai-maestro-assistant-manager-agent/issues/35) — the hub's spec: the 419-file measurement, the Gate 0b fix that made `answer` work for `AskUserQuestion` at all, and the caveats.
- `TRDD-U17K7AX6` (design/tasks/) — this plugin's card for the probe work; `TRDD-LT5N2JA4` (hub) — the aggregated probe that will supersede the multi-call shape.
- [amama-presence-tracker](../amama-presence-tracker/SKILL.md) — the **user's** availability, not an agent's. Different question, different CLI.
