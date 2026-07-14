#!/usr/bin/env python3
"""Atomic single-entry append for AMAMA session-memory logs.

The session-memory skill previously grew a log by re-Writing the ENTIRE file via
the Write tool, so every new entry re-emitted the whole (ever-growing) log through
the model's context — the K9 token blowup. This appends ONE entry with a single
``O_APPEND`` write and prints only a short confirmation, so the log's existing
content NEVER flows through the model again.

Why ``O_APPEND`` and not the temp-file+rename of ``amama_atomic_write``: a
copy-to-temp-then-rename append would have to READ the whole log back to
reconstruct it (O(n) per call, O(n^2) total) — the exact cost we are avoiding. A
lone ``O_APPEND`` write lands at end-of-file atomically w.r.t. concurrent
appenders (POSIX), never truncates, and never reads the log at all.

Usage:
    amama_append_log.py <path> <entry> [--id ID]
    amama_append_log.py <path> --stdin [--id ID]   # entry read from stdin
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def append_entry(path: Path, entry: str) -> None:
    """Append ``entry`` (one record) to ``path`` via a single ``O_APPEND`` write.

    The parent dir is created if missing; a trailing newline is ensured so records
    stay line-delimited. The existing log is NEVER read — only the new bytes are
    written, at end-of-file, atomically.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = entry if entry.endswith("\n") else entry + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data.encode("utf-8"))
    finally:
        os.close(fd)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Atomically append ONE entry to an AMAMA log.")
    ap.add_argument("path", help="log file to append to")
    ap.add_argument("entry", nargs="?", help="the entry text (omit when using --stdin)")
    ap.add_argument("--stdin", action="store_true", help="read the entry from stdin")
    ap.add_argument("--id", default="entry", help="short id echoed in the confirmation")
    args = ap.parse_args(argv)
    entry = sys.stdin.read() if args.stdin else args.entry
    if entry is None:
        ap.error("provide an entry argument or --stdin")
    path = Path(args.path)
    append_entry(path, entry)
    print(f"wrote {args.id} to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
