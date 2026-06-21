#!/usr/bin/env python3
"""Atomic file-write helper shared across AMAMA scripts.

A direct ``path.write_text(...)`` is not atomic: a crash or a concurrent run
mid-write can leave a TRUNCATED file. For a single-source-of-truth file — the
phase-state files, the download ``metadata.json`` (which carries the integrity
SHA), the design index — a partial write is a corrupted source of truth that a
later run reads as authoritative. ``atomic_write`` removes that window: it writes
the full content to a temp sibling and then ``os.replace``s it into place. Because
``os.replace`` is atomic on a single filesystem, a concurrent reader always sees
either the complete old file or the complete new file, never a partial one.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path


def atomic_write(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    """Write ``content`` to ``path`` atomically (temp sibling + ``os.replace``).

    The temp file is created in the SAME directory as ``path`` so the final
    ``os.replace`` stays on one filesystem (a cross-filesystem ``os.replace`` is
    not atomic). The temp name carries the PID so concurrent processes writing
    the same target do not clobber each other's temp. On any failure the temp
    file is removed and the original exception propagates (fail-fast — the error
    is never hidden; only the half-written temp artifact is cleaned up). ``path``'s
    parent directory must already exist (the caller owns directory creation).
    """
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    try:
        tmp.write_text(content, encoding=encoding)
        os.replace(tmp, path)
    except BaseException:
        # Remove the half-written temp so a failed write never litters a
        # ``.tmp.<pid>`` sibling; suppress only the unlink's own OSError so the
        # ORIGINAL failure is the one that propagates.
        with contextlib.suppress(OSError):
            tmp.unlink()
        raise
