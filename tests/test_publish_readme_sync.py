#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/publish.py::_sync_readme_version.

Each test builds a throwaway temp project, runs the ACTUAL
``_sync_readme_version`` against a real ``README.md`` on disk, and asserts the
real filesystem outcome: the ``**Version**:`` badge is mirrored from plugin.json
on a bump, the op is idempotent, only the FIRST (leading) badge line is touched
(prose mentioning "**Version**:" further down is left alone), and a missing
README / missing badge is a no-op skip rather than a failure (the badge is
documentation, never a release gate). Nothing is mocked.

Regression guard for TRDD-SVEILW09: the badge had drifted 6 minors (2.6.7 vs
plugin.json 2.12.11) because nothing synced it — this test pins the sync so it
cannot silently rot again.

Second regression guard (TRDD-DE33HN3J, 2026-07-16): the sync above was correct
and these tests passed, yet the badge STILL drifted a release behind — because
``README.md`` was missing from the release commit's staged file list, so the
rewrite was made on disk and then thrown away, leaving the tree dirty after
every publish. Testing the sync in isolation proved the claim while the pipeline
was inert; ``test_synced_files_are_staged_by_the_release_commit`` closes that
gap by asserting the OTHER half of the contract.

Run: python3 tests/test_publish_readme_sync.py      (exit 0 = all pass)
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import publish  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


def test_synced_files_are_staged_by_the_release_commit():
    """Every file a bump rewrites is in RELEASE_STAGED_FILES — an unstaged sync is inert."""
    staged = publish.RELEASE_STAGED_FILES
    # README.md is the one this test exists for: _sync_readme_version() rewrote it
    # on every publish, but it was absent here, so the change was never committed.
    assert "README.md" in staged
    # uv.lock has the same shape (rewritten by _sync_uv_lock).
    assert "uv.lock" in staged
    # the version SSOT itself must obviously land
    assert ".claude-plugin/plugin.json" in staged
    # the list is the single source of truth for Step 11 — no duplicates
    assert len(staged) == len(set(staged))


def test_sync_updates_stale_badge():
    """_sync_readme_version mirrors plugin.json onto a stale README **Version** badge."""
    d = Path(tempfile.mkdtemp(prefix="readme-sync-"))
    try:
        readme = d / "README.md"
        readme.write_text("# Plugin\n\n**Version**: 2.6.7\n\nBody.\n", encoding="utf-8")
        ok, msg = publish._sync_readme_version(d, "2.12.11")
        assert ok, msg
        assert "**Version**: 2.12.11" in readme.read_text(encoding="utf-8")
        assert "2.6.7" not in readme.read_text(encoding="utf-8")
        assert "2.12.11" in msg
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_sync_is_idempotent():
    """A README already at the target version is reported 'already' and not rewritten."""
    d = Path(tempfile.mkdtemp(prefix="readme-sync-"))
    try:
        readme = d / "README.md"
        readme.write_text("**Version**: 2.12.11\n", encoding="utf-8")
        before = readme.read_text(encoding="utf-8")
        ok, msg = publish._sync_readme_version(d, "2.12.11")
        assert ok, msg
        assert "already" in msg.lower()
        assert readme.read_text(encoding="utf-8") == before
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_sync_touches_only_leading_badge_not_prose():
    """Only the first **Version** line is changed; a later prose mention is left intact."""
    d = Path(tempfile.mkdtemp(prefix="readme-sync-"))
    try:
        readme = d / "README.md"
        readme.write_text(
            "**Version**: 2.6.7\n\n## History\n**Version**: 1.0.0 was the first release.\n",
            encoding="utf-8",
        )
        ok, msg = publish._sync_readme_version(d, "2.12.11")
        assert ok, msg
        text = readme.read_text(encoding="utf-8")
        assert text.startswith("**Version**: 2.12.11\n")
        # The prose line further down is untouched (count=1).
        assert "**Version**: 1.0.0 was the first release." in text
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_sync_skips_readme_without_badge():
    """A README with no **Version** badge is a no-op skip (ok=True), content unchanged."""
    d = Path(tempfile.mkdtemp(prefix="readme-sync-"))
    try:
        readme = d / "README.md"
        readme.write_text("# Plugin\n\nNo badge here.\n", encoding="utf-8")
        before = readme.read_text(encoding="utf-8")
        ok, msg = publish._sync_readme_version(d, "2.12.11")
        assert ok, msg
        assert "no **Version** badge" in msg
        assert readme.read_text(encoding="utf-8") == before
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_sync_skips_missing_readme():
    """A project with no README.md is a no-op skip (ok=True), not a failure."""
    d = Path(tempfile.mkdtemp(prefix="readme-sync-"))
    try:
        ok, msg = publish._sync_readme_version(d, "2.12.11")
        assert ok, msg
        assert "not found" in msg
        assert not (d / "README.md").exists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
