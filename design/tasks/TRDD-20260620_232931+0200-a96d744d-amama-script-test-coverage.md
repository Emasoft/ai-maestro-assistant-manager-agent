---
trdd-id: a96d744d-11f6-48e8-971e-09985564dcb7
title: Close AMAMA script test-coverage gap — real no-mock tests for the 11 untested scripts
column: complete
created: 2026-06-20T23:29:31+0200
updated: 2026-06-20T23:56:39+0200
current-owner: amama
assignee: amama
priority: 2
severity: MEDIUM
effort: L
task-type: infra
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: none
delivery: direct-push
test-requirements: [unit]
review-requirements: []
impacts: [ci-pipeline]
external-refs: []
---

# TRDD-a96d744d — Close AMAMA script test-coverage gap

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-20

**WHY:** `/go-on-yourself` eval (2026-06-20 night) found AMAMA ships **13 scripts but only 1 test file** (`tests/test_proposal_approvals.py`). The green CI "Test" job hides this — `pytest tests/` runs the 1 test and passes. 11 scripts are UNTESTED (`publish.py` deferred — see §Deferred). Per `~/.claude/rules/plugin-tests-are-the-plugins-job.md` every script must be tested.

**✅ DONE (2026-06-20).** All 11 scripts tested via real no-mock `python-test-writer` agents (waves 1 + 2a + 2b; wave 2's parallel spawn hit a transient server rate-limit, so the 4 affected scripts were re-run serially — the no-multiagent-during-rate-limit lesson). Result: **67 tests pass** (52 new across 11 files + 15 existing), 0 mocks, exact per-file counts (no bloat), no leaked processes (download's local `http.server` fixture closes in `finally`). 6 LOCAL commits (197c7bf TRDD · af446ca wave1 · 620e0f1 wave2a · ed2f38b report_writer · e09fd9a final3 · 0481145 README) — **NOT pushed** (per the /go-on-yourself "do not push, wait for approval" directive); they batch into the next AMAMA publish once the USER approves. `tests/README.md` updated. NO script bugs were surfaced (the scripts are sound). `publish.py` remains the only deferred script (§Deferred).

**LOAD-BEARING FACTS:**
- Style template = `tests/test_proposal_approvals.py` (353 lines): **real, no-mock** — throwaway tmp git repo, runs the ACTUAL script functions/CLI, asserts real filesystem/stdout outcomes; imports the module via `sys.path.insert(scripts/)`; standalone-runnable (`python3 tests/test_X.py`, exit 0 = pass) AND pytest-discoverable.
- CI runs `uv run pytest tests/ -v` → auto-discovers any `tests/test_*.py`. No conftest; each file self-contained.
- Real tests only — NO mocks unless a live external service is genuinely unavoidable (then test the pure/parse/path logic and note the network-gated part).
- Every test function needs a one-line docstring (feeds the result table). Mark slow tests 🐌.

## Scope — the 11 untested scripts + planned test counts (no bloat — targeted, not 30/fn)

| Script | LOC | tests | notes |
|---|---|---|---|
| amama_session_start.py | 58 | 3 | SessionStart hook — stdin JSON → behavior |
| amama_report_writer.py | 65 | 3 | report file writer |
| amama_orchestration_status.py | 127 | 4 | status CLI |
| amama_approve_plan.py | 134 | 4 | approve-plan command |
| amama_user_prompt_submit.py | 140 | 4 | UserPromptSubmit hook |
| amama_notify_agent.py | 157 | 5 | parse_frontmatter / find_agent_session / send / main |
| amama_planning_status.py | 206 | 5 | planning status CLI |
| amama_stop_check.py | 208 | 5 | Stop hook |
| amama_init_design_folders.py | 381 | 6 | design-folder scaffolder |
| amama_design_search.py | 444 | 7 | 8 pure extract/parse fns — high-value unit tests |
| amama_download.py | 640 | 6 | URL/path/error logic; network parts gated/noted |

Target ≈ 52 real tests across 11 new `tests/test_<script>.py` files.

## Requirements (every agent MUST follow)
1. **Real, no-mock.** Mirror `test_proposal_approvals.py`: tmp dirs, run the actual functions/CLI, assert real outcomes. No mocking the unit under test.
2. **Both runnable forms:** standalone `python3 tests/test_<s>.py` (exit 0 = all pass, prints a unicode-bordered result table: test fn name · status · one-line docstring desc, 🐌 for slow) AND pytest-discoverable (`def test_*`).
3. **One-line docstring per test** describing what it asserts.
4. **No bloat** — only the specified count; cover the real branches (happy path + the key edge/error cases), not permutations.
5. If a test reveals a **bug in the script**, the agent reports it (does NOT silently work around); the orchestrator fixes the script with a WHY comment (Bug-Autopsy).
6. Fail-fast respected; no swallowing errors to make a test pass.

## Execution
`python-test-writer` agents, one per script, in parallel (one turn). Each prompt: the script path, the template path, the EXACT test count, requirements 1-6, and the agent-token-budget reporting block (write the test file; return one line + report path; never dump test content).

## Verification (orchestrator, after agents return)
- `uv run pytest tests/ -v` → ALL green (incl. the existing proposal-approvals tests).
- Each new file also runs standalone (`python3 tests/test_<s>.py` exits 0 + prints its table).
- Render the consolidated result table (all test fns · status · desc).
- Re-run the exact CI command parity: `uv run pytest tests/ -v` is what CI does.
- Fix any script bug surfaced (separate commit, WHY comment).

## Derived tasks
- Update `tests/README.md` with the new files + how to run (standalone + pytest).
- CI "Test" job auto-discovers `test_*.py` — no ci.yml change needed (verify).
- These tests batch into the next AMAMA publish (release-via this TRDD = none; the version bump rides the next substantive publish, no dedicated churn).

## Deferred (NOT in this TRDD)
- `publish.py` (1513 LOC) — the publish pipeline; exercised end-to-end by the publish flow + CI gates. Unit-testing its helpers is a separate, lower-priority TRDD (its risk is already covered by every real publish + the strict pre-push hook).
