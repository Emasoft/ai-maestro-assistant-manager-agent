#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_proposal_approvals.py.

Each test builds a throwaway git repo under the system temp dir, populates it
with synthetic proposal TRDDs, runs the ACTUAL script functions/CLI, and
asserts against the real filesystem outcome (files moved, frontmatter mutated,
``## Approval log`` appended, manifest resolution by stable id).

Run: python3 tests/test_proposal_approvals.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_proposal_approvals as ppa  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True,
                   capture_output=True, text=True)


def make_proposal(root: Path, slug: str, *, tier: str, created: str,
                  extra_fm: str = "") -> str:
    """Write one synthetic proposal; return its trdd-id."""
    tid = str(uuid.uuid4())
    short = tid[:8]
    pdir = ppa.proposals_dir(root)
    pdir.mkdir(parents=True, exist_ok=True)
    fname = f"TRDD-{created.replace(':', '').replace('-', '')}-{short}-{slug}.md"
    body_extra = f"{extra_fm}\n" if extra_fm else ""
    (pdir / fname).write_text(
        f"---\n"
        f"trdd-id: {tid}\n"
        f"title: Proposal {slug} — synthetic test fixture\n"
        f"column: proposal\n"
        f"created: {created}\n"
        f"updated: {created}\n"
        f"current-owner: amama\n"
        f"task-type: docs\n"
        f"approval-tier: {tier}\n"
        f"{body_extra}"
        f"---\n\n"
        f"# Proposal {slug}\n\nBody.\n\n## Approval log\n",
        encoding="utf-8",
    )
    return tid


@contextlib.contextmanager
def temp_repo(commit: bool = True):
    """Yield a fresh git repo Path with 5 synthetic proposals (P1..P5 by created)."""
    root = Path(tempfile.mkdtemp(prefix="ppa-test-"))
    try:
        _git(root, "init")
        _git(root, "config", "user.email", "test@example.com")
        _git(root, "config", "user.name", "Test")
        ids = {}
        tiers = {"p1": "2", "p2": "2", "p3": "3", "p4": "1", "p5": "2"}
        for i in range(1, 6):
            slug = f"p{i}"
            ids[slug] = make_proposal(
                root, slug, tier=tiers[slug],
                created=f"2026-06-01T10:00:0{i}+0200",
            )
        if commit:
            _git(root, "add", "-A")
            _git(root, "commit", "-m", "fixtures")
        yield root, ids
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _col(root: Path, rel: str) -> str:
    return ppa.parse_frontmatter((root / rel).read_text(encoding="utf-8")).get("column", "")


def _run(root: Path, *argv: str) -> None:
    """Invoke the CLI (suppressing stdout) with --root pinned to the temp repo."""
    with contextlib.redirect_stdout(io.StringIO()):
        rc = ppa.main(["--root", str(root), *argv])
    assert rc in (0, 1), f"unexpected rc {rc} for {argv}"


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_list_numbers_and_manifest():
    """list numbers proposals 1..N by created: and writes a stable-id manifest."""
    with temp_repo() as (root, ids):
        items = ppa.list_pending(root)
        assert [p.n for p in items] == [1, 2, 3, 4, 5]
        assert items[0].trdd_id == ids["p1"] and items[4].trdd_id == ids["p5"]
        assert items[2].tier == "3"
        ppa.write_manifest(root, items)
        man = ppa.read_manifest(root)
        assert man["items"][0]["trdd_id"] == ids["p1"]


def test_approve_subset_moves_to_tasks():
    """approved: 1,3 promotes exactly those to design/tasks/ (planned); rest stay pending."""
    with temp_repo() as (root, _ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1,3")
        tasks = {p.name for p in ppa.tasks_dir(root).glob("*.md")}
        assert sum("p1" in n for n in tasks) == 1
        assert sum("p3" in n for n in tasks) == 1
        # 2,4,5 untouched, still pending
        pend = {p.name for p in ppa.proposals_dir(root).glob("*.md")}
        assert any("p2" in n for n in pend) and any("p5" in n for n in pend)
        # frontmatter mutated + log appended on an approved one
        approved = next(ppa.tasks_dir(root).glob("*p1*.md")).read_text()
        assert "column: planned" in approved
        assert "APPROVED by USER" in approved


def test_refuse_only_complement_approves_rest():
    """refused: 2 refuses #2 AND approves every other listed proposal (complement)."""
    with temp_repo() as (root, _ids):
        _run(root, "list")
        _run(root, "decide", "--refused", "2")
        refused = list(ppa.refused_dir(root).glob("*.md"))
        assert len(refused) == 1 and "p2" in refused[0].name
        assert _col(root, refused[0].relative_to(root).as_posix()) == "refused"
        # 1,3,4,5 approved by complement
        tasks = {p.name for p in ppa.tasks_dir(root).glob("*.md")}
        assert len(tasks) == 4
        assert not any("p2" in n for n in tasks)


def test_both_lists_disable_complement():
    """approved+refused together = explicit lists; unlisted stay PENDING (no complement)."""
    with temp_repo() as (root, _ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1", "--refused", "2")
        assert len(list(ppa.tasks_dir(root).glob("*.md"))) == 1
        assert len(list(ppa.refused_dir(root).glob("*.md"))) == 1
        # 3,4,5 still pending
        pend = [p for p in ppa.proposals_dir(root).glob("*.md")]
        assert len(pend) == 3


def test_cancel_archives_approved_task_and_redirects_proposal():
    """cancel archives an APPROVED task → design/archived/; a never-approved proposal is redirected."""
    with temp_repo() as (root, ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1")          # p1 -> tasks/ (approved)
        _run(root, "cancel", "--id", ids["p1"][:8])       # approved task → archived/cancelled
        arch_file = next(ppa.archived_dir(root).glob("*p1*.md"))
        assert _col(root, arch_file.relative_to(root).as_posix()) == "cancelled"
        assert "CANCELLED by USER" in arch_file.read_text()
        # a still-pending proposal (p4, never approved) must NOT be archived — it is redirected
        _run(root, "cancel", "--id", ids["p4"][:8])
        assert any("p4" in p.name for p in ppa.proposals_dir(root).glob("*.md"))
        assert not any("p4" in p.name for p in ppa.archived_dir(root).glob("*.md"))


def test_open_lists_tasks_excludes_terminal():
    """list_open returns design/tasks/ TRDDs (incl. failed) and excludes archived ones."""
    with temp_repo() as (root, ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1,2")        # p1,p2 -> tasks/ (planned)
        # mark p2 failed (still OPEN — stays in tasks/)
        p2 = next(ppa.tasks_dir(root).glob("*p2*.md"))
        p2.write_text(ppa.set_frontmatter_field(p2.read_text(), "column", "failed"))
        _run(root, "archive", "--state", "completed", "--id", ids["p1"][:8])
        openers = ppa.list_open(root)
        assert any(p.column == "failed" for p in openers)             # failed is OPEN
        assert all(p.column not in ppa.ARCHIVE_STATES for p in openers)  # no terminal here
        assert not any("p1" in p.file for p in openers)               # completed one archived


def test_legacy_no_frontmatter_trdd_is_surfaced_not_dropped():
    """A pre-frontmatter (legacy) TRDD in design/tasks/ is surfaced as unparsed, never hidden."""
    with temp_repo() as (root, _ids):
        tdir = ppa.tasks_dir(root)
        tdir.mkdir(parents=True, exist_ok=True)
        (tdir / "TRDD-legacy-old-format.md").write_text(
            "# TRDD-legacy — old markdown-bold format\n\n**Status:** Not started\n",
            encoding="utf-8",
        )
        unparsed = ppa.list_unparsed(root, tdir)
        assert any("legacy" in f for f in unparsed)
        # it must appear in the rendered open picture
        rendered = ppa.render_open(ppa.list_open(root), 0, 0, unparsed)
        assert "UNPARSED" in rendered and "legacy" in rendered


def test_blocked_surfaces_blockers():
    """A blocked TRDD is OPEN and its blocked-by list is captured + rendered."""
    with temp_repo() as (root, _ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1")
        t = next(ppa.tasks_dir(root).glob("*p1*.md"))
        text = ppa.set_frontmatter_field(t.read_text(), "column", "blocked")
        text = ppa.set_frontmatter_field(text, "blocked-by", "[TRDD-9a8aba94]")
        t.write_text(text)
        openers = ppa.list_open(root)
        blk = [p for p in openers if p.column == "blocked"]
        assert len(blk) == 1 and blk[0].blocked_by == "[TRDD-9a8aba94]"
        rendered = ppa.render_open(openers, 0, 0)
        assert "BLOCKED" in rendered and "TRDD-9a8aba94" in rendered


def test_archive_completed_and_superseded():
    """archive --state completed|superseded on APPROVED tasks → design/archived/."""
    with temp_repo() as (root, ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1,2")          # approve first (only tasks archive)
        _run(root, "archive", "--state", "completed", "--id", ids["p1"][:8])
        _run(root, "archive", "--state", "superseded", "--id", ids["p2"][:8])
        comp = next(ppa.archived_dir(root).glob("*p1*.md"))
        sup = next(ppa.archived_dir(root).glob("*p2*.md"))
        assert _col(root, comp.relative_to(root).as_posix()) == "completed"
        assert _col(root, sup.relative_to(root).as_posix()) == "superseded"
        assert "COMPLETED by USER" in comp.read_text()


def test_archive_rejects_failed_state():
    """`archive --state failed` is rejected — failed is retryable, never archived."""
    with temp_repo() as (root, ids):
        raised = False
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                ppa.main(["--root", str(root), "archive", "--state", "failed",
                          "--id", ids["p1"][:8]])
        except SystemExit as exc:
            raised = exc.code != 0
        assert raised
        assert not list(ppa.archived_dir(root).glob("*.md"))


def test_stale_and_unknown_numbers_are_skipped():
    """Re-deciding an already-moved number is skipped; unknown numbers are reported."""
    with temp_repo() as (root, _ids):
        _run(root, "list")
        _run(root, "decide", "--approved", "1")
        # #1 already moved; #99 never existed — neither should crash or mis-target
        out = ppa.decide(root, [1, 99], [], approver="USER",
                         reason_approve="r", reason_refuse="r", dry_run=False)
        assert out["approved"] == []
        assert any(s["n"] == 1 for s in out["skipped"])
        assert out["unknown"] == [99]


def test_overlap_is_rejected():
    """A number in BOTH approved and refused raises ValueError (no partial action)."""
    with temp_repo() as (root, _ids):
        _run(root, "list")
        raised = False
        try:
            ppa.decide(root, [1], [1], approver="USER",
                       reason_approve="r", reason_refuse="r", dry_run=False)
        except ValueError:
            raised = True
        assert raised
        # nothing moved
        assert not list(ppa.tasks_dir(root).glob("*.md"))


def test_parse_numbers_ranges_and_bad_tokens():
    """parse_numbers handles commas + N-M ranges and rejects garbage tokens."""
    assert ppa.parse_numbers("1,3-5,2") == [1, 2, 3, 4, 5]
    assert ppa.parse_numbers("") == []
    bad = False
    try:
        ppa.parse_numbers("1,x")
    except ValueError:
        bad = True
    assert bad


def test_frontmatter_surgical_preservation():
    """Mutating column/updated preserves field order + flow-style lists verbatim."""
    with temp_repo() as (root, _ids):
        # add a proposal carrying flow-style lists that MUST survive untouched
        make_proposal(root, "flow", tier="2", created="2026-06-01T09:00:00+0200",
                      extra_fm="npt: [TRDD-aaaa1111, TRDD-bbbb2222]\nrelevant-rules: [3, 27]")
        _git(root, "add", "-A")
        _git(root, "commit", "-m", "flow fixture")
        _run(root, "list")  # this proposal sorts first (earliest created) → #1
        _run(root, "decide", "--approved", "1")
        moved = next(ppa.tasks_dir(root).glob("*flow*.md")).read_text()
        assert "npt: [TRDD-aaaa1111, TRDD-bbbb2222]" in moved   # flow list intact
        assert "relevant-rules: [3, 27]" in moved
        assert moved.count("\ncolumn:") == 1                    # exactly one column line
        assert "column: planned" in moved


def test_move_file_tracked_uses_git_untracked_uses_fs():
    """move_file uses `git mv` for tracked files and a filesystem rename otherwise."""
    with temp_repo() as (root, _ids):
        tracked = next(ppa.proposals_dir(root).glob("*p1*.md"))
        assert ppa.move_file(root, tracked, ppa.tasks_dir(root) / tracked.name) == "git"
        # brand-new, uncommitted proposal → fs fallback
        make_proposal(root, "fresh", tier="2", created="2026-06-02T10:00:00+0200")
        fresh = next(ppa.proposals_dir(root).glob("*fresh*.md"))
        assert ppa.move_file(root, fresh, ppa.tasks_dir(root) / fresh.name) == "fs"


def test_apply_move_rolls_back_source_on_move_failure():
    """F7: if the move fails, apply_move restores the source to its pre-mutation content."""
    with temp_repo() as (root, _ids):
        src = next(ppa.proposals_dir(root).glob("*p1*.md"))
        original = src.read_text(encoding="utf-8")
        dest_dir = ppa.tasks_dir(root)
        dest_dir.mkdir(parents=True, exist_ok=True)
        # Pre-create the destination so move_file raises FileExistsError (it refuses
        # to clobber an existing dest) — the move fails AFTER the in-place mutation.
        (dest_dir / src.name).write_text("pre-existing blocker\n", encoding="utf-8")
        raised = False
        try:
            ppa.apply_move(
                root, src, target_col="planned", dest_dir=dest_dir,
                verb="APPROVED", approver="USER", tier="2", reason="r",
            )
        except FileExistsError:
            raised = True
        assert raised, "apply_move must propagate the move failure (fail-fast)"
        # Source restored: content byte-identical to before, NOT mutated to planned.
        restored = src.read_text(encoding="utf-8")
        assert restored == original
        assert "column: proposal" in restored
        # No atomic-write temp litter left behind in the source zone.
        assert list(ppa.proposals_dir(root).glob("*.tmp.*")) == []


def test_find_in_skips_unreadable_entry():
    """F6: find_in skips an unreadable entry (a broken symlink) and still finds a readable target."""
    with temp_repo() as (root, ids):
        pdir = ppa.proposals_dir(root)
        # A broken symlink whose read_text raises OSError — find_in must skip it and
        # keep searching, not crash the whole lookup mid-scan.
        (pdir / "TRDD-broken-symlink.md").symlink_to(pdir / "nonexistent-target.md")
        found = ppa.find_in(pdir, ids["p3"][:8])
        assert found is not None and "p3" in found.name


def test_refused_only_all_unknown_does_not_mass_approve():
    """Fail-fast: `refused: N` where N is NOT in the listing must NOT mass-approve the backlog.

    Before the guard, a stale/typo refused number resolved to nothing yet the
    complement `known - {N}` still fired and silently approved EVERY proposal
    (moving the whole backlog to design/tasks/ with rc=0). The refused-only verb
    presumes the named few are real; with zero real targets there is no
    defensible "rest" to approve, so the decision must be rejected and nothing
    must move.
    """
    with temp_repo() as (root, _ids):
        _run(root, "list")
        # 99 is not in the 5-item listing → build_plan must raise (no complement).
        raised = False
        try:
            ppa.decide(root, [], [99], approver="USER",
                       reason_approve="r", reason_refuse="r", dry_run=False)
        except ValueError:
            raised = True
        assert raised, "refused-only with all-unknown numbers must raise, not mass-approve"
        # Absolutely nothing moved: all 5 still pending, tasks/ and refused/ empty.
        assert len(list(ppa.proposals_dir(root).glob("*.md"))) == 5
        assert not list(ppa.tasks_dir(root).glob("*.md"))
        assert not (ppa.refused_dir(root).is_dir() and list(ppa.refused_dir(root).glob("*.md")))
        # The CLI surfaces it as a clean rc=1 error, not a silent success.
        with contextlib.redirect_stderr(io.StringIO()):
            rc = ppa.main(["--root", str(root), "decide", "--refused", "99"])
        assert rc == 1
        assert not list(ppa.tasks_dir(root).glob("*.md"))


def test_ambiguous_short_id_does_not_misroute_archive():
    """A short id matching two distinct TRDDs must NOT archive the first one — it is rejected.

    The full trdd-id is unique, but the 8-char short form can collide across two
    distinct ids. Silently archiving the first sorted match would cancel/archive
    the WRONG TRDD. find_in must raise AmbiguousId, and `cancel --id <short>`
    must archive NEITHER file (rc=1, both left untouched in design/tasks/).
    """
    with temp_repo() as (root, _ids):
        tdir = ppa.tasks_dir(root)
        tdir.mkdir(parents=True, exist_ok=True)
        # Two APPROVED tasks whose full ids share the same first 8 chars.
        for suffix, slug in (("1111-2222-3333-444444444444", "first"),
                             ("2222-3333-4444-555555555555", "second")):
            (tdir / f"TRDD-collide-aaaaaaaa-{slug}.md").write_text(
                f"---\ntrdd-id: aaaaaaaa-{suffix}\n"
                f"title: Collide {slug}\ncolumn: dev\n"
                f"created: 2026-06-01T10:00:00+0200\n"
                f"updated: 2026-06-01T10:00:00+0200\napproval-tier: 2\n"
                f"---\n\n# Collide {slug}\n\n## Approval log\n",
                encoding="utf-8",
            )
        # find_in itself fails fast on the colliding short id.
        raised = False
        try:
            ppa.find_in(tdir, "aaaaaaaa")
        except ppa.AmbiguousId:
            raised = True
        assert raised, "find_in must raise AmbiguousId on a colliding short id"
        # The archive CLI surfaces it (rc=1) and archives NEITHER TRDD.
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            rc = ppa.main(["--root", str(root), "cancel", "--id", "aaaaaaaa"])
        assert rc == 1
        assert not (ppa.archived_dir(root).is_dir() and list(ppa.archived_dir(root).glob("*.md")))
        assert len(list(tdir.glob("*collide*.md"))) == 2   # both still in tasks/
        # An EXACT full id is still unambiguous and resolves to exactly one file.
        exact = ppa.find_in(tdir, "aaaaaaaa-1111-2222-3333-444444444444")
        assert exact is not None and "first" in exact.name


def _write_task(tdir: Path, tid: str, slug: str) -> Path:
    """Write one synthetic APPROVED task with a given trdd-id; return its path."""
    tdir.mkdir(parents=True, exist_ok=True)
    path = tdir / f"TRDD-idcase-{slug}.md"
    path.write_text(
        f"---\ntrdd-id: {tid}\n"
        f"title: Idcase {slug}\ncolumn: dev\n"
        f"created: 2026-06-01T10:00:00+0200\n"
        f"updated: 2026-06-01T10:00:00+0200\napproval-tier: 2\n"
        f"---\n\n# Idcase {slug}\n\n## Approval log\n",
        encoding="utf-8",
    )
    return path


def test_find_in_short_and_full_id_are_case_insensitive():
    """A trdd-id is written uppercase but looked up case-insensitively (UPPER/lower/MiXeD all resolve)."""
    with temp_repo() as (root, _ids):
        tdir = ppa.tasks_dir(root)
        want = _write_task(tdir, "K3QX9P2W", "canonical8")  # canonical 8-char base36 id
        for ident in ("K3QX9P2W", "k3qx9p2w", "K3qx9P2w"):
            got = ppa.find_in(tdir, ident)
            assert got == want, f"lookup {ident!r} should resolve the uppercase-stored id"


def test_case_folding_does_not_defeat_ambiguous_guard():
    """Case-insensitive lookup must still raise AmbiguousId on two distinct ids sharing a short prefix."""
    with temp_repo() as (root, _ids):
        tdir = ppa.tasks_dir(root)
        # Two DISTINCT ids sharing the same first 8 chars (case-insensitively).
        _write_task(tdir, "K3QX9P2WAAAA", "collide_a")
        _write_task(tdir, "K3QX9P2WBBBB", "collide_b")
        raised = False
        try:
            ppa.find_in(tdir, "k3qx9p2w")  # lowercase short id — collides on both
        except ppa.AmbiguousId:
            raised = True
        assert raised, "case-folding must not merge two distinct ids — AmbiguousId still fires"
        # Each full id (any case) still resolves unambiguously to its own file.
        assert (ppa.find_in(tdir, "k3qx9p2waaaa") or Path()).name.endswith("collide_a.md")
        assert (ppa.find_in(tdir, "K3QX9P2WBBBB") or Path()).name.endswith("collide_b.md")


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
