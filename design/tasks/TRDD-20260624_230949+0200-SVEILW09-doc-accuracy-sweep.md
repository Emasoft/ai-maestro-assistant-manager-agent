---
trdd-id: SVEILW09
title: AMAMA doc-accuracy sweep — stale agent name, design/reports data-hygiene, README version + missing skills
column: complete
created: 2026-06-24T23:09:49+0200
updated: 2026-06-24T23:30:19+0200
current-owner: amama
assignee: amama
priority: 2
severity: MEDIUM
effort: M
task-type: docs
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
test-requirements: [lint, typecheck]
review-requirements: [human-review]
impacts: [install-script]
external-refs: []
---

# TRDD-SVEILW09 — AMAMA doc-accuracy sweep

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-24T23:09

**✅ EXECUTED + VERIFIED 2026-06-24T23:26 — all 4 phases done; CPV --strict clean (NIT=0).**
P1 committed `ccd81fd` (README 7 fixes + publish.py `_sync_readme_version` + 5 tests; suite 93→98).
P2/P3 ran via 4 parallel spark agents: 10 skills' `agent:` field corrected, and `design/reports/`
became `reports/<component>/` across the status-reporting skill (+2 refs), 2 commands, 2 agent docs.
P4 verified: repo-wide grep shows zero stale agent names and zero `design/reports/` in source; the
CPV strict gate caught one self-inflicted MD018 (the campaign-tracker re-verification note had a
wrapped line beginning with a hash) which is now fixed; full suite 98 green; ruff and mypy clean.
Commit-not-push.

**Trigger:** USER re-invoked `/go-on-yourself`. A fresh-eyes evaluation of AMAMA's
user-facing surface (all in-control audit work from TRDD-4c388042 already done;
everything else USER/peer-gated) found genuine doc drift — accuracy + data-hygiene,
not cosmetics. All facts VERIFIED against live source before scoping.

### Verified findings (each confirmed against source this session)
1. **Stale agent NAME after a rename.** The main agent's frontmatter is
   `name: ai-maestro-assistant-manager-agent-main-agent` (verified), but
   `amama-assistant-manager-main-agent` (the OLD name) is still referenced in:
   - `README.md:183` — the `claude --agent …` install command (BROKEN — no such agent).
   - `README.md:238` — Project Structure tree (wrong filename).
   - **all 10 skills' `SKILL.md` `agent:` frontmatter** (stale cross-ref to a
     non-existent agent). CPV --strict does NOT validate this field, which is why
     it shipped green.
2. **`design/reports/` data-hygiene drift.** Scripts write to gitignored
   `reports/<script_name>/` (verified: `amama_report_writer.py` +
   `.gitignore` has only `/reports/` + `/reports_dev/`; `design/reports/` is
   git-tracked). TRDD-4c388042 A.2 fixed the SCRIPTS but left the DOCS/SKILLS
   instructing the git-tracked leak path in: `README.md:207`,
   `commands/amama-planning-status.md`, `commands/amama-orchestration-status.md`,
   `skills/amama-status-reporting/SKILL.md` (+ `references/report-formats.md`,
   `references/checklist.md`), `agents/amama-report-generator.md`,
   `agents/ai-maestro-assistant-manager-agent-main-agent.md:340`.
3. **README version badge stale.** `README.md:3` says `2.6.7`; plugin.json is
   `2.12.11`. `publish.py` never touches the README (0 refs) → it drifts every
   release (root cause).
4. **README missing 2 skills.** Skills table + Project Structure list 8 of 10 —
   missing `amama-autonomous-fallback` + `amama-presence-tracker` (both confirmed
   to have a SKILL.md).

### Plan (phased; ≤5 files/phase; commit per phase; NO push — rides next publish.py)
- **P1 (this turn):** fix `README.md` (version → 2.12.11; agent name ×2;
  `design/reports/` → `reports/<component>/`; add the 2 missing skills to the
  Skills table + Project Structure). Root-cause: teach `publish.py` to sync the
  README `**Version**:` line from plugin.json after the bump (+ a test).
- **P2:** agent-name fix across the 10 `SKILL.md` `agent:` fields → parallel
  spark agents (uniform `amama-assistant-manager-main-agent` →
  `ai-maestro-assistant-manager-agent-main-agent`).
- **P3:** `design/reports/` → `reports/<component>/` across the 2 commands, the
  status-reporting skill (+2 refs), the report-generator agent, and the main
  agent → parallel spark agents, matching the real `reports/<script_name>/`
  convention.
- **P4:** verify (repo-wide grep that zero stale refs remain; `ruff` + `mypy`
  clean; full test suite green; `publish.py --dry-run`), then commit.

### Load-bearing facts / gotchas
- Agent NAME (for `claude --agent`) = `ai-maestro-assistant-manager-agent-main-agent`
  (frontmatter `name:`), NOT the filename-vs-name confusion the OLD `amama-…` refs imply.
- Reports target = `reports/<script_name>/<script_name>_<ts>.md` (ReportWriter),
  gitignored; NEVER `design/reports/` (git-tracked = data leak).
- The `while ls design/tasks/TRDD-*-<id>-*.md` collision idiom is BROKEN under
  nullglob (unmatched glob → `ls` lists cwd → exit 0 → false "exists" → infinite
  loop / 8-min hang). Use `find design/tasks -name "*<id>*"` instead.
- MARKDOWN HYGIENE for the publish gate: never let a hard-wrapped line START with a
  markdown-special char — `#` (→ MD018 no-space-atx, hit here in the 282f61fe note),
  `+`/`* ` (→ MD004 ul-style poison, hit last session), `>` (blockquote), or `N.`
  (ordered list). CPV --strict markdownlint scans `design/tasks/*.md` too, so reword
  the line to begin with a word or a backtick.

## Why this is in-control + safe
Doc-only edits (+ a small, tested `publish.py` README-sync). No runtime logic
change. Reversible (committed, not pushed). Directly serves `/go-on-yourself`
("update the readme/docs", "fix all of it", "one source of truth", "base on
facts"). Completes the data-hygiene half of TRDD-4c388042 A.2 (scripts fixed
there; docs/skills fixed here).
