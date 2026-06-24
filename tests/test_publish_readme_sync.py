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
