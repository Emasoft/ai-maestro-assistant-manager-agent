---
prrd-version: 1.3
updated: 2026-06-14T07:31:03+0200
project: ai-maestro-assistant-manager-agent
project-id: autonomous
canonical-source: design/requirements/PRRD.md
mirrors: []
---

# Project Requirements & Rules — ai-maestro-assistant-manager-agent

MANAGER role plugin (AMAMA) — sole user interface, governance authority, approvals.

## §0. Canonical source + copies

| Path | Role | Update strategy |
|---|---|---|
| `design/requirements/PRRD.md` | **CANONICAL** for this project | Edit first. Bump `prrd-version:`. Update `updated:`. |

## §I. How to read this document

Rule citation form: `PRRD G<n>.<v>` (golden, user-set) or `PRRD S<n>.<v>`
(silver, manager-mutable). Rule numbers are globally unique across G/S;
promote/demote flips the letter without changing the number. The
`get-prrd.py <n>` script returns a rule's text by bare number. Full
spec: `~/.claude/rules/prrd-design-rules.md`.

## 🥇 GOLDEN — set by the USER (immutable to MANAGER)

- **G1.1** — Every agent that writes to GitHub (issue, issue comment, PR, PR comment, PR review, discussion, release note) MUST begin the body with a one-line self-identification of which agent/role/plugin authored it, because all AI Maestro agents share the single human-owner GitHub identity (the owner's gh CLI auth). Recommended leading line: _Posted by the Claude developing **<plugin-or-role>** (via the shared @owner gh auth)._ Commit messages SHOULD carry an `Agent: <role>` trailer.

## 🥈 SILVER — MANAGER-mutable (agents propose via COS)

- **S2.1** — Validate this plugin only via the remote CPV plugin (`uvx --from git+https://github.com/Emasoft/claude-plugins-validation cpv-remote-validate plugin . --strict`). Never ship vendored validation/setup/lint scripts in this repo; CI's exit-0-only `--strict` gate is the release blocker. Report CPV false-positives/errors as upstream issues — never request rule suppression or exemption (the exempt-list was an exploitable attack surface; devitalize or remove flagged content instead).
- **S3.3** — Declare the inter-plugin dependency on `ai-maestro-plugin` in `plugin.json` as the pinned **object** form `[{"name": "ai-maestro-plugin", "version": "^X.Y.0"}]` — verified to pass CPV `--strict` (0 MAJOR) and to clear the un-exemptable version-constraint WARNING. In `marketplace.json`, the bare string form `["ai-maestro-plugin"]` is the safe default (valid on every CPV version); as of **CPV v2.126.19** (#106 resolved — `validate_plugin` and `validate_marketplace` now share one dependency schema) the object form is ALSO accepted there, so either validates and existing string entries need not change.
- **S4.1** — Every agent/skill/tool report is written to `<main-repo-root>/reports/<component>/<YYYYMMDD_HHMMSS±HHMM>-<slug>.md` (local time + GMT offset). Both `reports/` and `reports_dev/` stay gitignored — reports may carry private paths/tokens/PII.
- **S5.1** — The TRDD `column:` pipeline in `design/tasks/` is the authoritative task lifecycle. Any GitHub-Projects board or the AI Maestro server kanban is a visual projection of it, never the source of truth.
- **S6.1** — Session memory uses the janitor's three-scope markdown-notes system (LOCAL `~/.claude/projects/<slug>/memory/`, PROJECT `<git-root>/memory/`, USER `~/.claude/memory/`), recall via memgrep-or-grep-fallback. The legacy `activeContext`/`progress`/`patterns` hook-bank is retired (TRDD-8707e849).
- **S7.1** — This repo is solo-operated: `project-id: autonomous`, PRRD mutations via `prrd-edit.py --user` (the human owner is the manager). When the fleet goes live and a team takes ownership, re-scope `project-id:` to the registered AI Maestro project id and activate the approval chain — a Tier-2 transition the MANAGER coordinates.
- **S8.1** — Every GitHub post (issue, comment, PR, review, discussion, release note) leads with the line "This is the Claude responsible for the ai-maestro-assistant-manager-agent project." — the concrete instance of `PRRD G1.1` for this repo.
- **S9.1** — The MANAGER cannot self-approve its OWN releases: the `complete → publish` / `complete → deploy` transitions and any release/deploy of this plugin require USER approval. Routine mechanical column transitions remain exempt per `manager-approval-defaults.md`.
- **S10.1** — The standard GitHub baseline rulesets (`baseline-history-protect` + `baseline-pr-and-checks`) apply to this repo as-is; any deviation (extra rule, loosened check, new bypass actor, disabled ruleset) is a Tier-2 change requiring MANAGER approval.
