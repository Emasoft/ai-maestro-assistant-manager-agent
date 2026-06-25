---
trdd-id: G290DKHM
title: AMAMA script correctness review — fix CRITICAL mass-approve + HIGH id-collision + HIGH sidecar-orphan bugs
column: complete
created: 2026-06-25T06:24:48+0200
updated: 2026-06-25T06:24:48+0200
current-owner: amama
assignee: amama
priority: 1
severity: CRITICAL
effort: M
task-type: bugfix
parent-trdd: null
npt: []
eht: []
blocked-by: []
relevant-rules: []
release-via: publish
delivery: direct-push
target-branch: main
test-requirements: [unit, lint, typecheck]
review-requirements: [human-review]
impacts: []
external-refs: []
---

# TRDD-G290DKHM — AMAMA script correctness review (GOLDEN-RULE deep read)

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative) — 2026-06-25T06:24

**✅ EXECUTED + VERIFIED — 3 real bugs fixed, full suite green (101 passed), ruff + mypy clean.**
Trigger: USER challenge "why are you not working??" → `/go-on-yourself` in-control improvement.
A fresh-eyes correctness review of AMAMA's two most complex AMAMA-specific scripts (delegated to
two parallel Opus reviewers, GOLDEN-RULE whole-file read; findings verified by me against the
actual diffs before landing). NOT cosmetic — all three are real correctness/governance/data-integrity
bugs that the existing test suite did not catch.

### Fixed (each: real bug, fail-before/pass-after regression test, WHY comment at the change site)
1. **CRITICAL — `amama_proposal_approvals.py::build_plan` mass-approve via phantom complement.**
   In `refused:`-only batch mode, a stale/typo'd number whose id resolves to nothing
   (`decide --refused 99`) made `refuse_set & known` empty, so the complement `known - refuse_set`
   became the ENTIRE listing → every pending proposal silently APPROVED + moved to `design/tasks/`
   at rc=0. Fix: fail-fast — if not one refused number resolves, raise (rc=1, nothing moves). A mix
   of valid+unknown still proceeds (user named ≥1 real target). Test:
   `test_refused_only_all_unknown_does_not_mass_approve`.
2. **HIGH — `amama_proposal_approvals.py::find_in` short-id collision mis-route.** The 8-char short
   id is only a "casual" reference and CAN collide; `find_in` returned the first sorted match, so
   `cancel/archive --id <short>` could silently archive the WRONG TRDD. Fix: exact full-id wins;
   unique short resolves; >1 short raises `AmbiguousId` → `cmd_archive` surfaces it per-ident
   (rc=1, the rest of the batch still proceeds). Test:
   `test_ambiguous_short_id_does_not_misroute_archive`.
3. **HIGH — `amama_download.py` metadata sidecar orphaned on inner-`.md` filename.** Write side
   used `filename.replace('.md','')` (strips EVERY `.md`); read side uses `md_file.stem` (final
   suffix only). For a filename with `.md` mid-string (e.g. `--doc-type spec.md`) they disagreed →
   metadata orphaned → `lookup` silently returned `{}` AND `verify_storage` SKIPPED the SHA256
   integrity check (it lives in the `else` of the missing-metadata guard), so a tampered file passed
   verification undetected. Fix: write side uses `Path(filename).stem` (single source of truth with
   the read side). Test: `test_metadata_sidecar_name_matches_read_side_when_filename_has_inner_md`.

### Flagged for MANAGER decision (real, NOT auto-fixed — design-level) — see download report
- **[HIGH] `lookup_documents` can't find docs in no-task-id categories (`specs`, `sync`).** It
  searches for a folder literally named `{task_id}`, but those categories store the task_id only in
  the metadata JSON, never in the path → docs are unfindable by `lookup --task-id`.
- **[MEDIUM] `lookup_documents` misses subcategory subfolders.** It globs `*.md` non-recursively;
  docs downloaded with `--subcategory` sit in a subfolder → unfindable by `lookup`, though `verify`
  (rglob) counts them — the two read paths disagree.
- **[LOW]** empty task folder left behind on download failure (cosmetic litter).
- **[NIT]** `init_storage` `.gitignore` "already present?" check is a coarse substring match.

**DECISION (next in-control step):** fix the two `lookup_documents` gaps together as ONE coherent
design change (recursive search + consult `metadata["task_id"]` for the no-task-id categories) with
its own regression tests — they are real functional gaps in a MANAGER tool. The LOW/NIT items are
deferred (negligible impact; fixing them now would be churn against `/go-on-yourself` "write only
what is strictly necessary"). Tracked as the follow-up to this TRDD.

### Verification
`uv run --with pytest pytest tests/ -q` → **101 passed** (98 prior + 3 new). `ruff check scripts/
tests/` → all passed. `mypy scripts/` → no issues (15 files). Reviewer reports:
`reports/amama-code-review/20260625_06*-{proposal-approvals,amama-download}.md` (gitignored).

### Gotcha re-encountered (and the lesson held)
The `while ls design/tasks/TRDD-*-$ID-*.md` collision idiom hung 8 min AGAIN (nullglob → `ls`
lists cwd → exit 0 → infinite loop) — the exact SVEILW09 gotcha. Re-confirmed: use
`while [ -n "$(find design/tasks -name "TRDD-*-$ID-*.md")" ]` for the create-time collision check.

## Why this is in-control + safe
Pure correctness fixes to AMAMA's OWN scripts (no external dependency, no peer/USER gate). Each is a
real bug the suite missed, fixed fail-fast with a proven regression test and a WHY comment. Directly
serves `/go-on-yourself` ("identify shortcomings, base on facts, improve on real ground"). Reversible
(committed, not pushed — rides the next publish.py with the doc-sweep commits, pending USER approval).
