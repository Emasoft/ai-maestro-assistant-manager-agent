#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_atomic_write.py.

Each test runs the ACTUAL ``atomic_write`` against a throwaway temp dir and
asserts the real filesystem outcome: content written, an existing file
overwritten, no ``.tmp`` sibling left behind on success, and — on a write that
cannot complete — the error propagates (fail-fast) with no temp litter and no
partially-created destination.

Run: python3 tests/test_amama_atomic_write.py      (exit 0 = all pass)
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_atomic_write as aw  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


def test_atomic_write_creates_overwrites_and_leaves_no_temp():
    """atomic_write writes content, overwrites an existing file, and leaves no .tmp sibling."""
    d = Path(tempfile.mkdtemp(prefix="aw-test-"))
    try:
        target = d / "state.md"
        aw.atomic_write(target, "first\n")
        assert target.read_text(encoding="utf-8") == "first\n"
        # Overwrite in place — the reader sees the complete new content.
        aw.atomic_write(target, "second body\nwith two lines\n")
        assert target.read_text(encoding="utf-8") == "second body\nwith two lines\n"
        # No leftover temp siblings after a successful write.
        assert list(d.glob("*.tmp.*")) == []
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_atomic_write_propagates_and_cleans_temp_on_failure():
    """A write whose parent dir is missing raises (fail-fast), creates no dest, and leaves no temp."""
    d = Path(tempfile.mkdtemp(prefix="aw-test-"))
    try:
        missing = d / "no-such-subdir" / "state.md"  # parent directory does not exist
        raised = False
        try:
            aw.atomic_write(missing, "x\n")
        except OSError:
            raised = True
        assert raised, "atomic_write must propagate the write error (fail-fast), not swallow it"
        # The destination was never created, and no .tmp litter exists anywhere under d.
        assert not missing.exists()
        assert list(d.rglob("*.tmp.*")) == []
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
