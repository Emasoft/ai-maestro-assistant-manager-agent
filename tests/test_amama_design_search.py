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

import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_design_search as ads  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


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


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
