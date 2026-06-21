#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_download.py.

Each test builds a throwaway storage tree under the system temp dir, runs the
ACTUAL module functions, and asserts against the real filesystem outcome
(files written, folder/filename derived, metadata JSON, SHA256 integrity,
read-only enforcement, error paths returning ``None``).

The network fetch is exercised WITHOUT the public internet and WITHOUT mocks:
``download_document`` shells out to ``curl``, which speaks both ``file://`` and
``http://``. The successful-download test serves a real byte stream from a
local ``http.server`` bound to 127.0.0.1 (closed in a ``finally`` — no leaks);
the failure test points ``curl`` at a genuinely non-existent ``file://`` path.

Run: python3 tests/test_amama_download.py      (exit 0 = all pass)
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import io
import json
import os
import shutil
import socketserver
import stat
import sys
import tempfile
import threading
import uuid
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_download as dl  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers — real temp dirs, a real local HTTP server, real chmod cleanup
# --------------------------------------------------------------------------- #
def _tmp() -> Path:
    """Fresh throwaway directory (a stand-in project root)."""
    return Path(tempfile.mkdtemp(prefix="amama-dl-test-"))


def _rmtree(root: Path) -> None:
    """Remove a tree even though download_document chmods files to read-only."""
    for p in root.rglob("*"):
        try:
            p.chmod(p.stat().st_mode | stat.S_IWUSR)
        except OSError:
            pass
    shutil.rmtree(root, ignore_errors=True)


def _serve_dir(directory: Path) -> tuple[socketserver.TCPServer, int]:
    """Start a real HTTP server on 127.0.0.1 serving ``directory``; return (srv, port)."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


# --------------------------------------------------------------------------- #
# Tests (exactly 7)
# --------------------------------------------------------------------------- #
def test_get_storage_root_resolution():
    """get_storage_root honours project_root, then AMAMA_STORAGE_ROOT, then cwd."""
    root = _tmp()
    saved = os.environ.pop("AMAMA_STORAGE_ROOT", None)
    try:
        # 1) explicit project_root wins over everything
        assert dl.get_storage_root(root) == root / ".aimaestro" / "received"
        # 2) env var used when no project_root
        env_dir = root / "env-store"
        os.environ["AMAMA_STORAGE_ROOT"] = str(env_dir)
        assert dl.get_storage_root(None) == env_dir
        # 3) cwd fallback when neither is set
        del os.environ["AMAMA_STORAGE_ROOT"]
        cwd = Path.cwd()
        os.chdir(root)
        try:
            assert dl.get_storage_root(None) == root.resolve() / ".aimaestro" / "received"
        finally:
            os.chdir(cwd)
    finally:
        if saved is not None:
            os.environ["AMAMA_STORAGE_ROOT"] = saved
        else:
            os.environ.pop("AMAMA_STORAGE_ROOT", None)
        _rmtree(root)


def test_download_real_file_via_local_http_server():  # 🐌 spins a real HTTP server
    """A real curl download from a local http.server writes the file, metadata, hash, and locks it."""
    root = _tmp()
    src = _tmp()
    payload = b"# AMAMA completion report\n\nReal bytes for TASK-77.\n"
    (src / "report.md").write_bytes(payload)
    srv, port = _serve_dir(src)
    try:
        result = dl.download_document(
            url=f"http://127.0.0.1:{port}/report.md",
            task_id="GH-77",
            category="reports",
            subcategory="completion",
            doc_type="completion",
            sender="amama-integrator",
            project_root=root,
        )
        assert result is not None and result.exists()
        # folder layout: <store>/reports/GH-77/completion/<ts>_completion.md
        assert result.parent == root / ".aimaestro" / "received" / "reports" / "GH-77" / "completion"
        assert result.name.endswith("_completion.md")
        assert result.read_bytes() == payload  # real content round-tripped
        # metadata sidecar exists, well-formed, and records the true hash + size
        meta_path = result.parent / f"{result.stem}_metadata.json"
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert meta["category"] == "reports" and meta["subcategory"] == "completion"
        assert meta["task_id"] == "GH-77" and meta["sender"]["agent"] == "amama-integrator"
        assert meta["source"]["type"] == "direct_url"
        import hashlib

        assert meta["download"]["sha256"] == hashlib.sha256(payload).hexdigest()
        assert meta["download"]["file_size_bytes"] == len(payload)
        # read-only enforcement: owner write bit cleared on the downloaded file
        assert not (result.stat().st_mode & stat.S_IWUSR)
    finally:
        srv.shutdown()
        srv.server_close()
        _rmtree(root)
        _rmtree(src)


def test_download_unknown_category_returns_none():
    """download_document rejects an unknown category, returns None, and writes nothing."""
    root = _tmp()
    src = _tmp()
    # A genuinely fetchable source: if the category check were bypassed, curl
    # WOULD succeed and a file would appear — so a swallowed bad category fails
    # this test rather than passing via the download-failure path.
    good = src / "real.md"
    good.write_bytes(b"# real content that would download if validation were skipped\n")
    try:
        result = dl.download_document(
            url=f"file://{good}",
            task_id="GH-1",
            category="not-a-real-category",
            project_root=root,
        )
        assert result is None
        # the bad category folder must not exist, and nothing was written anywhere
        store = root / ".aimaestro" / "received"
        assert not (store / "not-a-real-category").exists()
        assert not store.exists() or list(store.rglob("*.md")) == []
    finally:
        _rmtree(root)
        _rmtree(src)


def test_download_failure_via_bad_url_returns_none():
    """A real curl failure (missing file:// source) returns None and leaves no .md behind."""
    root = _tmp()
    missing = _tmp() / f"absent-{uuid.uuid4().hex}.md"  # guaranteed not to exist
    try:
        result = dl.download_document(
            url=f"file://{missing}",
            task_id="GH-9",
            category="tasks",
            doc_type="delegation",
            project_root=root,
        )
        assert result is None
        # curl -f writes nothing on a 404/missing source; the target folder holds no .md
        folder = root / ".aimaestro" / "received" / "tasks" / "GH-9"
        assert list(folder.glob("*.md")) == []
    finally:
        _rmtree(root)


def test_extract_attachment_url_bad_format():
    """extract_attachment_url returns None for a URL that is not an issue-comment link."""
    # Malformed (a PR comment, not an issue comment) — fails the regex before any gh call.
    assert dl.extract_attachment_url("https://github.com/owner/repo/pull/3#discussion_r1") is None
    assert dl.extract_attachment_url("not even a url") is None


def test_verify_storage_detects_integrity_violation():
    """verify_storage passes a clean store, then flags tampering as integrity + writable issues."""
    root = _tmp()
    src = _tmp()
    (src / "spec.md").write_bytes(b"# toolchain spec\nversion: 1\n")
    srv, port = _serve_dir(src)
    try:
        downloaded = dl.download_document(
            url=f"http://127.0.0.1:{port}/spec.md",
            task_id="GH-5",
            category="specs",
            subcategory="toolchains",
            doc_type="toolchain",
            project_root=root,
        )
        assert downloaded is not None

        # Healthy store: no issues reported.
        clean = dl.verify_storage(root)
        assert clean["stats"]["total_files"] == 1
        assert clean["issues"] == []

        # Tamper: make the locked file writable and change its bytes.
        downloaded.chmod(downloaded.stat().st_mode | stat.S_IWUSR)
        downloaded.write_bytes(b"# toolchain spec\nversion: 999 TAMPERED\n")

        tampered = dl.verify_storage(root)
        types = {issue["type"] for issue in tampered["issues"]}
        assert "integrity_violation" in types  # SHA256 no longer matches metadata
        assert "writable_file" in types  # write bit we restored is detected
    finally:
        srv.shutdown()
        srv.server_close()
        _rmtree(root)
        _rmtree(src)


def test_redownload_into_same_folder_succeeds():  # 🐌 spins a real HTTP server
    """H3 regression: a SECOND download into an existing task folder succeeds — the
    folder is not locked read-only (only the files are), so sibling documents can
    still be added."""
    root = _tmp()
    src = _tmp()
    (src / "a.md").write_bytes(b"# first doc\n")
    (src / "b.md").write_bytes(b"# second doc\n")
    srv, port = _serve_dir(src)
    try:
        first = dl.download_document(
            url=f"http://127.0.0.1:{port}/a.md",
            task_id="GH-77", category="reports", subcategory="completion",
            doc_type="completion", project_root=root,
        )
        assert first is not None and first.exists()
        # Second download into the SAME task/category/subcategory folder (a sibling doc).
        second = dl.download_document(
            url=f"http://127.0.0.1:{port}/b.md",
            task_id="GH-77", category="reports", subcategory="completion",
            doc_type="review", project_root=root,
        )
        assert second is not None and second.exists(), "re-download into a locked folder must not fail (H3)"
        # Both docs coexist in the one folder; both are individually read-only.
        assert first.parent == second.parent
        assert not (first.stat().st_mode & stat.S_IWUSR)
        assert not (second.stat().st_mode & stat.S_IWUSR)
    finally:
        srv.shutdown()
        srv.server_close()
        _rmtree(root)
        _rmtree(src)


def test_main_download_failure_surfaces_cause_on_stderr():
    """H4: main()'s download command writes the failure cause to stderr (not only the report)."""
    root = _tmp()
    missing_dir = _tmp()
    missing = missing_dir / f"absent-{uuid.uuid4().hex}.md"  # guaranteed not to exist
    argv = [
        "amama_download.py", "download",
        "--url", f"file://{missing}",
        "--task-id", "GH-x", "--category", "tasks",
        "--project-root", str(root),
    ]
    prev_argv, prev_env = sys.argv, os.environ.get("CLAUDE_PROJECT_DIR")
    sys.argv = argv
    os.environ["CLAUDE_PROJECT_DIR"] = str(root)  # ReportWriter writes under the temp root
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            rc = dl.main()
    finally:
        sys.argv = prev_argv
        if prev_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prev_env
        _rmtree(root)
        _rmtree(missing_dir)
    assert rc == 1
    assert "ERROR: Download failed" in err.getvalue()


def test_main_rejects_task_id_with_glob_metacharacters():
    """M2: main() rejects a --task-id with glob metachars / path separators (parse-time fail-fast)."""
    for bad in ("*", "a/b", "x?y", "[abc]"):
        prev = sys.argv
        sys.argv = ["amama_download.py", "lookup", "--task-id", bad]
        code = None
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                dl.main()
        except SystemExit as exc:
            code = exc.code
        finally:
            sys.argv = prev
        assert code not in (0, None), f"task-id {bad!r} must be rejected (got exit {code!r})"


# --------------------------------------------------------------------------- #
# Slow tests (spin a real local HTTP server) get a 🐌 marker in the result table.
# --------------------------------------------------------------------------- #
_SLOW = {"test_download_real_file_via_local_http_server", "test_redownload_into_same_folder_succeeds"}


if __name__ == "__main__":
    sys.exit(run_standalone(globals(), slow=_SLOW))
