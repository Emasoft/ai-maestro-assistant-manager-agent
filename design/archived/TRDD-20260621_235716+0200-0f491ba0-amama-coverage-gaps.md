---
trdd-id: 0f491ba0-9fa0-49f4-933b-b938d7a7d4d9
title: AMAMA test-coverage gaps — close the HIGH-value function/branch gaps (bucket E)
column: complete
created: 2026-06-21T23:57:16+0200
updated: 2026-06-22T00:06:17+0200
current-owner: amama
assignee: amama
priority: 3
severity: LOW
effort: M
task-type: feature
parent-trdd: TRDD-4c388042
relevant-rules: []
test-requirements: [unit]
---

# TRDD-0f491ba0 — AMAMA test-coverage gaps (bucket E of the self-audit)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-22

**✅ COMPLETE (HIGH-value scope).** Both Opus agents landed: design_search +10 (file
7→17), download +5 (file 9→14); full suite **78→93 pass**, ruff + mypy clean, both
scripts byte-identical to HEAD (agents reverted their mutation-test edits). Committed
`79cb1ca` — LOCAL, NOT pushed (awaiting USER approval per /go-on-yourself). design_search
tests read + confirmed real; download set mutation-tested. LOW/NIT gaps remain DEFERRED
(below) — out of this TRDD's scope.

**Origin:** bucket E of the self-audit (TRDD-4c388042). The audit's tests report
(`reports/plugin-audit/20260621_221741+0200-tests.md`) found the suite is
genuinely high-quality (no fake/mocked tests) with **22 function/branch coverage
gaps**. File-level coverage is already complete (every AMAMA script has a test
file, from TRDD-a96d744d's 67 tests + this session's bucket-B additions → 78
tests). The gaps are finer-grained.

**Plan — close only the HIGH-value gaps via two parallel `python-test-writer`
agents (Opus), real no-mock, matching the existing patterns; LOW/NIT deferred.**

- **Agent 1 — `amama_design_search.py`** (biggest gap: CLI + search layer
  untested; the test file only covers the 8 pure helpers). Cover: `get_project_dir`
  (env set/clear), `scan_design_documents` (tmp design/ tree), `search_by_uuid`
  (full + partial), `search_by_keyword` (title/summary/keywords/path),
  `filter_by_status`, `document_to_dict` (JSON shape), `main` CLI (arg parse,
  no-option `parser.error`, project-dir-not-found, no-documents ReportWriter
  branch). Target ~8–10 tests.
- **Agent 2 — `amama_download.py`** — cover `lookup_documents` (download→lookup +
  metadata JSON read), `extract_attachment_url` happy path (PATH-injected `gh`
  shim returning a URL), `init_storage` (category dirs), `main` CLI smoke
  (download/lookup/verify). Target ~5–6 tests.

**MOOT — do NOT test:** `set_readonly` recursive/dir branch — REMOVED this session
(bucket-F M5, commit `08f5221`); the branch no longer exists.

**DEFERRED (LOW/NIT, not in this TRDD):** `amama_stop_check` error/empty branches;
`amama_init_design_folders` write_*_file `False`-return branch; proposal
render/`cmd_open` helpers; thin `_entry`/`_main` wrappers (effectively covered via
subprocess). The audit itself rated these LOW/NIT.

**NEXT ACTION:** dispatch the two agents (no-commit; report to
`reports/python-test-writer/`); on return run the CI-equivalent trio
(`ruff check` · `mypy scripts` · `pytest -q`) and commit the new tests.

**Gotchas:** real no-mock only (build tmp `design/` trees, PATH-inject `gh`,
local `http.server` for download — the suite's own substitutions of genuinely
external deps); each test needs a one-line docstring (the table renderer reads
it); mark slow tests `_SLOW` → 🐌; restore `cwd`/`argv`/`PATH`/`CLAUDE_PROJECT_DIR`
in `finally`; keep both standalone (`run_standalone`) AND pytest-compatible.

## Durable artifacts to read before acting
- `reports/plugin-audit/20260621_221741+0200-tests.md` — the gap inventory + per-function fix notes.
- `tests/test_amama_design_search.py`, `tests/test_amama_download.py` — extend these.
- `tests/_harness.py` — `run_standalone`; `tests/test_amama_orchestration_status.py` / `test_amama_planning_status.py` — the CLI-subprocess test pattern to mirror.
