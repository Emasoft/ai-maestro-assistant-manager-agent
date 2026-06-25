#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_design_search.py.

Each test writes synthetic TRDD/design markdown to a throwaway tmp dir and runs
the ACTUAL pure extract/parse/find functions, asserting against real outcomes.
No mocks, no monkeypatching: the functions parse genuine markdown content (a
valid case plus an edge/malformed case for each), and ``parse_design_document``
/ ``find_design_directories`` operate on real files and real directories.

Run: python3 tests/test_amama_design_search.py      (exit 0 = all pass)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
_SCRIPT = _SCRIPTS / "amama_design_search.py"
sys.path.insert(0, str(_SCRIPTS))

import amama_design_search as ads  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402

# Slow tests (subprocess-spawning CLI tests) get the 🐌 marker in the standalone
# result table. Each spins a fresh interpreter, so they cost ~0.1-0.3s apiece.
_SLOW = {
    "test_main_keyword_search_writes_report_and_json",
    "test_main_no_option_errors",
    "test_main_project_dir_not_found_returns_1",
    "test_main_no_documents_branch",
}


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def _doc(uuid: str | None, title: str, status: str, *, keywords: str = "", description: str = "", body: str = "Body prose.") -> str:
    """Build a synthetic design-doc markdown string with optional frontmatter fields."""
    lines = ["---", f"title: {title}", f"status: {status}"]
    if uuid is not None:
        lines.append(f"uuid: {uuid}")
    if keywords:
        lines.append(f"keywords: [{keywords}]")
    if description:
        lines.append(f"description: {description}")
    lines += ["---", "", f"# {title}", "", body, ""]
    return "\n".join(lines)


def _make_design_tree(docs: dict[str, str]) -> Path:
    """Create a temp project root with a design/ dir holding {relpath: content} docs."""
    root = Path(tempfile.mkdtemp(prefix="amama-ds-test-"))
    design = root / "design"
    design.mkdir(parents=True, exist_ok=True)
    for rel, content in docs.items():
        target = design / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


def _run(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    """Invoke the real CLI with cwd + CLAUDE_PROJECT_DIR pinned to the temp project."""
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *argv],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
    )


def _report_text(root: Path) -> str:
    """Return the single written design-search report's content (asserts exactly one exists)."""
    reports = sorted((root / "reports" / "design-search").glob("design-search_*.md"))
    assert len(reports) == 1, f"expected exactly one report, found {len(reports)}"
    return reports[0].read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_extract_uuid_frontmatter_body_and_missing():
    """extract_uuid_from_content reads frontmatter uuid, AMAMA-UUID body tag, and returns None when absent."""
    fm = "---\ntitle: X\nuuid: a58a02c4-721d-453b-99c9-95964a33f72f\n---\n\n# X\n"
    assert ads.extract_uuid_from_content(fm) == "a58a02c4-721d-453b-99c9-95964a33f72f"

    # No frontmatter uuid, but an AMAMA-UUID: marker in the body.
    body = "# Design\n\nSome prose.\n\nAMAMA-UUID: 9a8aba94-b5d7-4d48-b05f-bdbd72295a13\n"
    assert ads.extract_uuid_from_content(body) == "9a8aba94-b5d7-4d48-b05f-bdbd72295a13"

    # Edge: a bare canonical UUID inside the first 500 chars is recognised.
    bare = "Reference TRDD 7e80e484-221a-4b2c-a252-b5820af4ea19 in the intro.\n"
    assert ads.extract_uuid_from_content(bare) == "7e80e484-221a-4b2c-a252-b5820af4ea19"

    # Malformed: no uuid anywhere -> None (not a crash).
    assert ads.extract_uuid_from_content("# Title only\n\nNo identifier here.\n") is None


def test_extract_status_frontmatter_marker_and_unknown():
    """extract_status_from_content reads frontmatter status, bracket markers, and defaults to 'unknown'."""
    fm = "---\nstatus: Approved\n---\n\n# Doc\n"
    assert ads.extract_status_from_content(fm) == "approved"  # lower-cased

    # Body bracket marker, no frontmatter.
    assert ads.extract_status_from_content("# Doc\n\n[DRAFT]\nWork in progress.\n") == "draft"

    # **Status**: bold-markdown form in the body.
    assert ads.extract_status_from_content("# Doc\n\n**Status**: Deprecated\n") == "deprecated"

    # Edge: nothing recognisable -> 'unknown'.
    assert ads.extract_status_from_content("# Doc\n\nNo status line at all.\n") == "unknown"


def test_extract_title_frontmatter_h1_and_filename_fallback():
    """extract_title_from_content prefers frontmatter title, then H1, then a humanised filename."""
    fm = "---\ntitle: \"My Quoted Title\"\n---\n\n# Different H1\n"
    assert ads.extract_title_from_content(fm, "ignored.md") == "My Quoted Title"

    # No frontmatter title -> first H1 wins.
    assert ads.extract_title_from_content("# Real Heading\n\nBody.\n", "x.md") == "Real Heading"

    # Edge: neither frontmatter nor H1 -> humanised filename (dashes/underscores -> spaces, Title Case).
    assert (
        ads.extract_title_from_content("Just body text, no heading.\n", "auth-design_spec.md")
        == "Auth Design Spec"
    )

    # Edge: a filename whose STEM contains an internal '.md' substring. Only the
    # trailing '.md' extension is stripped (removesuffix), never the inner one.
    # A naive str.replace('.md', '') would wrongly delete the middle '.md' too,
    # yielding 'V1.2 Notes' instead of the correct 'V1.2.Md Notes'.
    assert (
        ads.extract_title_from_content("Body, no heading.\n", "v1.2.md-notes.md")
        == "V1.2.Md Notes"
    )


def test_extract_keywords_merges_keywords_and_tags():
    """extract_keywords_from_content unions frontmatter keywords[] + tags[] (deduped) and is empty when absent."""
    fm = (
        "---\n"
        "keywords: [auth, oauth, 'session token']\n"
        "tags: [auth, security]\n"  # 'auth' duplicated across the two lists
        "---\n\n# Doc\n"
    )
    got = ads.extract_keywords_from_content(fm)
    # Result is built from a set -> order is non-deterministic; compare as sets.
    assert set(got) == {"auth", "oauth", "session token", "security"}
    assert len(got) == len(set(got))  # deduped: 'auth' appears once

    # Edge: no keywords/tags keys at all -> empty list.
    assert ads.extract_keywords_from_content("---\ntitle: X\n---\n\n# X\n") == []


def test_extract_summary_frontmatter_paragraph_and_truncation():
    """extract_summary_from_content uses description, else first real paragraph, with 200-char truncation rules."""
    fm = "---\ndescription: A concise design summary.\n---\n\n# Doc\n\nIgnored body para.\n"
    assert ads.extract_summary_from_content(fm) == "A concise design summary."

    # No description -> first non-heading/non-list/non-code paragraph after frontmatter.
    doc = "---\ntitle: X\n---\n\n# Heading\n\nThe first real paragraph of prose.\n\nSecond para.\n"
    assert ads.extract_summary_from_content(doc) == "The first real paragraph of prose."

    # Edge: a long body paragraph is truncated to 200 chars and gets an ellipsis appended.
    long_para = "x" * 250
    summary = ads.extract_summary_from_content(f"# H\n\n{long_para}\n")
    assert summary == "x" * 200 + "..."
    assert len(summary) == 203


def test_parse_design_document_real_file_and_unreadable():
    """parse_design_document builds a populated DesignDocument from a real file and returns None for a missing path."""
    tmp = Path(tempfile.mkdtemp(prefix="ads-test-"))
    try:
        f = tmp / "feature-x.md"
        f.write_text(
            "---\n"
            "title: Feature X Design\n"
            "uuid: a58a02c4-721d-453b-99c9-95964a33f72f\n"
            "status: approved\n"
            "keywords: [feature, x]\n"
            "description: Designing feature X end to end.\n"
            "---\n\n"
            "# Feature X Design\n\nDetails follow.\n",
            encoding="utf-8",
        )
        doc = ads.parse_design_document(f)
        assert doc is not None
        assert isinstance(doc, ads.DesignDocument)
        assert doc.uuid == "a58a02c4-721d-453b-99c9-95964a33f72f"
        assert doc.title == "Feature X Design"
        assert doc.status == "approved"
        assert set(doc.keywords) == {"feature", "x"}
        assert doc.summary == "Designing feature X end to end."
        assert doc.path == str(f)
        # Timestamps are populated ISO strings derived from the real stat().
        assert doc.created and doc.modified

        # Edge: a non-existent path is caught (OSError) and returns None, never raises.
        assert ads.parse_design_document(tmp / "does-not-exist.md") is None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_find_design_directories_detects_known_names_only():
    """find_design_directories returns existing design-pattern dirs (incl. nested docs/design) and skips unrelated/file paths."""
    tmp = Path(tempfile.mkdtemp(prefix="ads-test-"))
    try:
        (tmp / "design").mkdir()
        (tmp / "specs").mkdir()
        (tmp / "docs" / "architecture").mkdir(parents=True)
        (tmp / "src").mkdir()  # not a design pattern -> must be ignored
        # A file named like a pattern must NOT be treated as a directory.
        (tmp / "designs").write_text("not a dir\n", encoding="utf-8")

        found = ads.find_design_directories(tmp)
        names = {p.relative_to(tmp).as_posix() for p in found}
        assert "design" in names
        assert "specs" in names
        assert "docs/architecture" in names
        assert "src" not in names          # unrelated dir excluded
        assert "designs" not in names      # file (not dir) excluded
        assert all(p.is_dir() for p in found)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_get_project_dir_uses_env_then_cwd():
    """get_project_dir returns $CLAUDE_PROJECT_DIR when set, else the current working dir."""
    saved_env = os.environ.get("CLAUDE_PROJECT_DIR")
    saved_cwd = os.getcwd()
    tmp_env = Path(tempfile.mkdtemp(prefix="ads-env-"))
    tmp_cwd = Path(tempfile.mkdtemp(prefix="ads-cwd-"))
    try:
        # Env set -> that path wins (resolve() both sides: macOS /var -> /private/var symlink).
        os.environ["CLAUDE_PROJECT_DIR"] = str(tmp_env)
        assert ads.get_project_dir().resolve() == tmp_env.resolve()

        # Env cleared -> falls back to os.getcwd().
        del os.environ["CLAUDE_PROJECT_DIR"]
        os.chdir(tmp_cwd)
        assert ads.get_project_dir().resolve() == tmp_cwd.resolve()
    finally:
        os.chdir(saved_cwd)
        if saved_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = saved_env
        shutil.rmtree(tmp_env, ignore_errors=True)
        shutil.rmtree(tmp_cwd, ignore_errors=True)


def test_scan_design_documents_collects_real_docs():
    """scan_design_documents parses every *.md under the design dirs into DesignDocument objects."""
    root = _make_design_tree(
        {
            "auth.md": _doc("a58a02c4-721d-453b-99c9-95964a33f72f", "Auth Design", "approved", keywords="auth, security"),
            "nested/cache.md": _doc("11111111-2222-3333-4444-555555555555", "Cache Layer", "draft"),
            "notes.txt": "",  # non-markdown placeholder; rglob('*.md') must skip it
        }
    )
    # The .txt was written into design/ as a sibling, but only *.md is scanned.
    (root / "design" / "notes.txt").write_text("not markdown\n", encoding="utf-8")
    try:
        docs = ads.scan_design_documents(root)
        assert all(isinstance(d, ads.DesignDocument) for d in docs)
        titles = {d.title for d in docs}
        assert titles == {"Auth Design", "Cache Layer"}  # exactly the two .md docs
        by_title = {d.title: d for d in docs}
        assert by_title["Auth Design"].status == "approved"
        assert by_title["Auth Design"].uuid == "a58a02c4-721d-453b-99c9-95964a33f72f"
        assert by_title["Cache Layer"].status == "draft"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_search_by_uuid_full_and_partial():
    """search_by_uuid matches a full UUID and a case-insensitive partial substring, ignoring None-uuid docs."""
    root = _make_design_tree(
        {
            "a.md": _doc("a58a02c4-721d-453b-99c9-95964a33f72f", "Doc A", "draft"),
            "b.md": _doc("9a8aba94-b5d7-4d48-b05f-bdbd72295a13", "Doc B", "draft"),
            "c.md": _doc(None, "Doc C No UUID", "draft"),  # uuid None -> never matches
        }
    )
    try:
        docs = ads.scan_design_documents(root)
        # Full match (upper-cased query -> matched case-insensitively).
        full = ads.search_by_uuid(docs, "A58A02C4-721D-453B-99C9-95964A33F72F")
        assert [d.title for d in full] == ["Doc A"]
        # Partial-match branch: the leading 8 hex of Doc B's uuid.
        partial = ads.search_by_uuid(docs, "9a8aba94")
        assert [d.title for d in partial] == ["Doc B"]
        # A substring that no uuid contains -> empty (and the None-uuid doc never errors).
        assert ads.search_by_uuid(docs, "ffffffff") == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_search_by_keyword_all_four_branches():
    """search_by_keyword matches via title, summary, keywords list, and file path (its four branches)."""
    root = _make_design_tree(
        {
            "title-hit.md": _doc("11111111-1111-1111-1111-111111111111", "Authentication Flow", "draft"),
            "summary-hit.md": _doc("22222222-2222-2222-2222-222222222222", "Generic Doc", "draft", description="Covers the payment gateway integration."),
            "keyword-hit.md": _doc("33333333-3333-3333-3333-333333333333", "Tagged Doc", "draft", keywords="caching, redis"),
            "pathmatch-zebra.md": _doc("44444444-4444-4444-4444-444444444444", "Plain Doc", "draft"),
        }
    )
    try:
        docs = ads.scan_design_documents(root)
        # 1) title branch
        assert [d.title for d in ads.search_by_keyword(docs, "authentication")] == ["Authentication Flow"]
        # 2) summary branch (matches the frontmatter description rendered into .summary)
        assert [d.title for d in ads.search_by_keyword(docs, "payment")] == ["Generic Doc"]
        # 3) keywords-list branch
        assert [d.title for d in ads.search_by_keyword(docs, "redis")] == ["Tagged Doc"]
        # 4) file-path branch (the unique 'zebra' token only appears in the filename)
        assert [d.title for d in ads.search_by_keyword(docs, "zebra")] == ["Plain Doc"]
        # No-match -> empty list.
        assert ads.search_by_keyword(docs, "no-such-token-anywhere") == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_filter_by_status_exact_match():
    """filter_by_status returns only docs whose status equals the (case-insensitive) query."""
    root = _make_design_tree(
        {
            "a.md": _doc("11111111-1111-1111-1111-111111111111", "Approved One", "approved"),
            "b.md": _doc("22222222-2222-2222-2222-222222222222", "Approved Two", "approved"),
            "c.md": _doc("33333333-3333-3333-3333-333333333333", "Draft One", "draft"),
        }
    )
    try:
        docs = ads.scan_design_documents(root)
        approved = ads.filter_by_status(docs, "APPROVED")  # upper query -> lower-cased internally
        assert {d.title for d in approved} == {"Approved One", "Approved Two"}
        assert {d.title for d in ads.filter_by_status(docs, "draft")} == {"Draft One"}
        # A status no doc carries -> empty list.
        assert ads.filter_by_status(docs, "deprecated") == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_document_to_dict_key_set_and_values():
    """document_to_dict yields the exact 8 JSON keys with the DesignDocument's real field values."""
    root = _make_design_tree(
        {
            "feat.md": _doc(
                "a58a02c4-721d-453b-99c9-95964a33f72f",
                "Feature Spec",
                "approved",
                keywords="feature, spec",
                description="A concise feature description.",
            )
        }
    )
    try:
        (doc,) = ads.scan_design_documents(root)
        d = ads.document_to_dict(doc)
        # Exact key set used to build the --json payload.
        assert set(d.keys()) == {"path", "uuid", "title", "status", "created", "modified", "keywords", "summary"}
        assert d["uuid"] == "a58a02c4-721d-453b-99c9-95964a33f72f"
        assert d["title"] == "Feature Spec"
        assert d["status"] == "approved"
        assert set(d["keywords"]) == {"feature", "spec"}
        assert d["summary"] == "A concise feature description."
        assert d["path"] == doc.path
        # The dict must be JSON-serialisable exactly as main() emits it.
        assert json.loads(json.dumps(d))["title"] == "Feature Spec"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_keyword_search_writes_report_and_json():
    """main with --keyword runs the full pipeline: rc 0, stdout summary, and a report with matching JSON."""
    root = _make_design_tree(
        {
            "auth.md": _doc("a58a02c4-721d-453b-99c9-95964a33f72f", "Authentication Design", "approved", keywords="auth"),
            "cache.md": _doc("11111111-2222-3333-4444-555555555555", "Cache Design", "draft", keywords="cache"),
        }
    )
    try:
        cp = _run(root, "--keyword", "authentication")
        assert cp.returncode == 0, f"expected rc 0, got {cp.returncode} ({cp.stderr})"
        # Two-line stdout summary echoes the query and the match count.
        assert "Found 1 documents matching" in cp.stdout
        assert 'keyword="authentication"' in cp.stdout
        report = _report_text(root)
        assert "Design Search Report" in report
        # The matched doc is in the JSON block; the non-matching one is filtered out.
        assert "Authentication Design" in report
        assert "Cache Design" not in report
        assert '"count": 1' in report
        assert '"total_scanned": 2' in report
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_no_option_errors():
    """main with no search option -> argparse parser.error (rc 2, usage on stderr, no report dir)."""
    root = _make_design_tree({"a.md": _doc("11111111-1111-1111-1111-111111111111", "Doc", "draft")})
    try:
        cp = _run(root)  # no --uuid/--keyword/--status/--list
        assert cp.returncode == 2, f"expected argparse rc 2, got {cp.returncode} ({cp.stdout})"
        assert "At least one search option required" in cp.stderr
        # parser.error() exits before any ReportWriter instantiation -> no report dir.
        assert not (root / "reports" / "design-search").exists()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_project_dir_not_found_returns_1():
    """main with a non-existent --project-dir prints an error JSON to stdout and returns 1, writing no report."""
    root = _make_design_tree({"a.md": _doc("11111111-1111-1111-1111-111111111111", "Doc", "draft")})
    missing = root / "does-not-exist-subdir"
    try:
        cp = _run(root, "--list", "--project-dir", str(missing))
        assert cp.returncode == 1, f"expected rc 1, got {cp.returncode} ({cp.stderr})"
        payload = json.loads(cp.stdout.strip())
        assert "error" in payload
        assert "Project directory not found" in payload["error"]
        assert str(missing) in payload["error"]
        # The not-found guard returns before ReportWriter is constructed.
        assert not (root / "reports" / "design-search").exists()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_main_no_documents_branch():
    """main on a project with zero design docs hits the no-documents branch: rc 0 + a 'none' report."""
    # A valid project dir with an EMPTY design/ tree -> scan returns [] -> the
    # ReportWriter "No design documents found" branch (lines 366-375) fires.
    root = Path(tempfile.mkdtemp(prefix="amama-ds-empty-"))
    (root / "design").mkdir(parents=True, exist_ok=True)
    try:
        cp = _run(root, "--list")
        assert cp.returncode == 0, f"expected rc 0, got {cp.returncode} ({cp.stderr})"
        assert "Found 0 documents (none in project)" in cp.stdout
        report = _report_text(root)
        assert "No design documents found" in report
        assert '"count": 0' in report
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals(), slow=_SLOW))
