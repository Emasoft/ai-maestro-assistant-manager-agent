---
trdd-id: 6fc2c762-6c80-4adb-9241-209834425ecb
title: Dedupe test scaffolding to clear the Mega-Linter jscpd CI gate
column: complete
created: 2026-06-21T16:38:10+0200
updated: 2026-06-21T18:05:00+0200
published-version: 2.12.7
published-at: 2026-06-21T16:57:00+0200
current-owner: amama
assignee: cpv-plugin-fixer
priority: 1
severity: HIGH
effort: M
task-type: refactor
parent-trdd: TRDD-a96d744d
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
test-requirements: [unit]
review-requirements: []
impacts: [ci-pipeline]
external-refs: ["github.com/Emasoft/claude-plugins-validation/issues/143", "github.com/Emasoft/ai-maestro-assistant-manager-agent/actions/runs/27907343369"]
---

# TRDD-6fc2c762 — Dedupe test scaffolding to clear the Mega-Linter jscpd CI gate

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-21

**WHY:** The test-coverage campaign (parent [[TRDD-a96d744d]]) added 11 new
`tests/test_amama_*.py` files. Each writer-agent copied the template's shared
scaffolding (the `_table()` unicode result-table renderer, the `main()`
standalone runner, and per-pair fixtures) from `tests/test_proposal_approvals.py`.
That pushed the repo's jscpd copy-paste ratio to **7.36% > 5%**, so CI's
Mega-Linter **Lint** job FAILS on jscpd (15 clones) — even though `publish.py`
exits 0 (its local gate has no jscpd check; that gate-parity gap is filed
upstream as CPV **#143**). v2.12.6 shipped (tagged + released) with red CI.

**THE FIX (the only acceptable one — never relax the gate):** genuine DRY
extraction. Move the shared scaffolding into a single `tests/_harness.py` (the
`_table()` renderer + a `run_standalone(module_globals)` runner; and any
genuinely-common fixtures), and refactor all 12 test files (the 11 new + the
`test_proposal_approvals.py` template) to import + call it instead of carrying
their own copy. **Forbidden:** raising the jscpd `--threshold`, adding
`.jscpd.json` ignore globs, or `jscpd:ignore` markers — those relax the gate
(USER rule: never relax quality gates).

**NEXT ACTION:** the `cpv-plugin-fixer` agent (dispatched per the USER's "execute
the cpv fixer agent" directive) performs the refactor, verifies locally (pytest
67 still green + each file still standalone-runnable + `npx jscpd` under 5% +
ruff + CPV-lint), then publishes via `publish.py --patch` (→ v2.12.7; the strict
pre-push hook mandates publish.py), then **watches CI to GREEN** (publish.py exit
0 does NOT imply green CI — that is the whole #143 gap; the Lint job must pass).

**LOAD-BEARING FACTS:**
- The cloned block is `tests/test_proposal_approvals.py [315:353]` (the
  `# Runner + result table` section: `_table()` + `main()` + `if __name__`) plus
  per-pair fixtures. The `_table`/`main` body is byte-identical across files.
- `main()` collects `[v for k,v in sorted(globals().items()) if k.startswith("test_")]`
  — so the harness runner must take the caller's `globals()` to find its tests.
- Strict hook: a plain `git push` is REFUSED (process-ancestry check) — only
  `publish.py --patch|--minor|--major` may push.
- CI Lint = Mega-Linter; the failing linter is jscpd (`.jscpd.json`,
  `--threshold 5`). Reproduce locally before re-publishing.

## Acceptance criteria
1. `tests/_harness.py` holds the single copy of the result-table renderer +
   standalone runner; all 12 test files import it (no copied `_table`/`main`).
2. `uv run --with pytest pytest tests/ -q` → 67 passed (unchanged behavior).
3. Each `tests/test_*.py` still runs standalone (`python3 tests/test_x.py`,
   exit 0, prints its table).
4. jscpd over the repo is **< 5%** (reproduce CI's check locally).
5. `ruff check .` + `ruff check --select I .` + CPV `cpv-remote-validate lint` all clean.
6. `publish.py --patch` → v2.12.7 published, AND CI run is **fully green**
   (Lint included), confirmed via `gh run watch --exit-status`.

## Progress — 2026-06-21 (cpv-plugin-fixer)

DRY extraction applied. `tests/_harness.py` now holds the single copy of the
result-table renderer (`_table`) + the standalone runner (`run_standalone`).
All 12 test files (11 new + `test_proposal_approvals.py`) import it and replace
their copied runner block with `if __name__ == "__main__": sys.exit(run_standalone(globals()))`.
Per-file slow-test 🐌 markers preserved via `run_standalone(globals(), slow=_SLOW)`
(download: 1 slow, user_prompt_submit: 4 slow); empty-`_SLOW` placeholders removed.

Local verification (faithful CI repro = `npx jscpd@4.0.5 --reporters console --threshold 5 --format python tests scripts shared`):
- jscpd: **7.36% (15 clones) → 0.32% (1 clone)**, exit 0. The 1 residual clone is the
  `_run()` subprocess helper between orchestration_status/planning_status (18 lines,
  169 tokens) — far under 5%, no further extraction needed.
- pytest: 67 passed (unchanged). Each test file standalone: exit 0 + unicode table.
- ruff (E,F,W,I) clean (isort auto-fixed the 2 added imports); mypy clean;
  `cpv-remote-validate lint` → CRITICAL/MAJOR/MINOR/WARNING all 0.

## DONE — 2026-06-21 — v2.12.7 published, CI FULLY GREEN

Published **v2.12.7** via `publish.py --patch` (bump → commit → tag → push → release).
CI run [27908058062](https://github.com/Emasoft/ai-maestro-assistant-manager-agent/actions/runs/27908058062)
= **completed success** (3m32s): **Lint ✓** (Mega-Linter / jscpd now 0.32% < 5% — the
fix is confirmed in CI, not just locally), Validate ✓, Test matrix ubuntu ✓ + macos ✓,
Test gate ✓. Release + Notify-Marketplace workflows also `success`. Acceptance criteria
1-6 all met. `column: complete`.

## Notes and lessons learned

[^1]: [ocd:2026-06-21 lmd:2026-06-21] The local `npx jscpd` resolved to an
  UNRELATED Rust tool (`cpd` v5) with different flags — to reproduce CI faithfully
  you MUST pin the exact CI tool `jscpd@4.0.5` (the node MegaLinter linter) AND scope
  it to the git-tracked python dirs (`tests scripts shared`), because a bare `.`
  scan pulled in gitignored `.venv/`/`scripts_dev/` and diluted the % to a wrong 2%.
  Lesson: reproduce a CI linter with the linter's EXACT version + the EXACT file set
  CI sees (gitignore-filtered), or the local number is meaningless.
