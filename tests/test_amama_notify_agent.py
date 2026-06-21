#!/usr/bin/env python3
"""Real (no-mock) tests for scripts/amama_notify_agent.py.

Each test exercises the ACTUAL module functions against real temp files, real
dicts, and (for the AMP path) a real subprocess invoking a throwaway ``amp-send``
shim on a temp PATH. Nothing under test is mocked: ``parse_frontmatter`` reads a
real file, ``find_agent_session`` walks a real dict, and ``send_ai_maestro_message``
really calls ``subprocess.run`` and really reads the child's exit code — the shim
only stands in for the external AMP server (an external dependency, not the unit).

NETWORK NOTE: the production ``amp-send`` talks to a live AI Maestro server. These
tests deliberately never reach it — they prepend a temp dir holding a fake
``amp-send`` to PATH so the argv-building and exit-code branches are verified with
zero network. The live-server round-trip itself is out of scope here.

Run: python3 tests/test_amama_notify_agent.py      (exit 0 = all pass)
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import amama_notify_agent as na  # noqa: E402  # pyright: ignore[reportMissingImports]
from _harness import run_standalone  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _write_amp_shim(bindir: Path, *, exit_code: int, argv_log: Path) -> None:
    """Create an executable fake ``amp-send`` that logs its argv then exits N.

    This is the external dependency (the AMP transport), not the function under
    test. send_ai_maestro_message still runs the real subprocess against it.
    """
    shim = bindir / "amp-send"
    shim.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"open({str(argv_log)!r}, 'w', encoding='utf-8').write(chr(10).join(sys.argv[1:]))\n"
        f"sys.exit({exit_code})\n",
        encoding="utf-8",
    )
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_parse_frontmatter_valid_and_missing_file():
    """Valid frontmatter parses to (dict, body); a missing file returns ({}, '')."""
    with tempfile.TemporaryDirectory(prefix="na-fm-") as d:
        f = Path(d) / "exec.md"
        f.write_text(
            "---\n"
            "registered_agents:\n"
            "  ai_agents:\n"
            "    - agent_id: implementer-1\n"
            "      session_name: sess-impl-1\n"
            "---\n\n"
            "# Orchestration body\n\nSome prose.\n",
            encoding="utf-8",
        )
        data, body = na.parse_frontmatter(f)
        assert data["registered_agents"]["ai_agents"][0]["agent_id"] == "implementer-1"
        assert data["registered_agents"]["ai_agents"][0]["session_name"] == "sess-impl-1"
        assert body.startswith("# Orchestration body")
        # missing file → ({}, "")
        missing = Path(d) / "does-not-exist.md"
        assert na.parse_frontmatter(missing) == ({}, "")


def test_parse_frontmatter_no_delimiter_and_malformed_yaml():
    """No leading '---' returns ({}, content); malformed YAML falls back to ({}, content)."""
    with tempfile.TemporaryDirectory(prefix="na-fm2-") as d:
        # No frontmatter delimiter at all → ({}, content) with content VERBATIM.
        # (The no-delimiter branch returns the raw text; only the parsed-body
        # branch strips. We assert the script's real, correct behavior.)
        plain = Path(d) / "plain.md"
        plain_content = "just a body, no frontmatter\n"
        plain.write_text(plain_content, encoding="utf-8")
        assert na.parse_frontmatter(plain) == ({}, plain_content)

        # Opens with '---' but the YAML between the fences is malformed.
        # (Unbalanced brackets are a hard YAML parse error, not just odd data.)
        bad = Path(d) / "bad.md"
        bad_content = "---\nregistered_agents: [unterminated\n---\nbody\n"
        bad.write_text(bad_content, encoding="utf-8")
        data, body = na.parse_frontmatter(bad)
        assert data == {}
        # On YAMLError the function returns the FULL original content as body.
        assert body == bad_content


def test_find_agent_session_match_and_miss():
    """Returns the matching agent's session_name; returns None for unknown id / empty data."""
    data = {
        "registered_agents": {
            "ai_agents": [
                {"agent_id": "arch-1", "session_name": "sess-arch"},
                {"agent_id": "impl-2", "session_name": "sess-impl-2"},
            ]
        }
    }
    assert na.find_agent_session(data, "impl-2") == "sess-impl-2"
    assert na.find_agent_session(data, "arch-1") == "sess-arch"
    # unknown id → None
    assert na.find_agent_session(data, "ghost") is None
    # empty / missing structure → None (no KeyError)
    assert na.find_agent_session({}, "impl-2") is None
    assert na.find_agent_session({"registered_agents": {}}, "impl-2") is None


def test_send_message_builds_exact_argv_and_returns_true_on_success():
    """Builds the exact amp-send argv and returns True when the child exits 0 (no live server)."""
    with tempfile.TemporaryDirectory(prefix="na-amp-ok-") as d:
        bindir = Path(d)
        argv_log = bindir / "argv.txt"
        _write_amp_shim(bindir, exit_code=0, argv_log=argv_log)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{bindir}{os.pathsep}{old_path}"
        try:
            ok = na.send_ai_maestro_message(
                "sess-impl-1",
                "Subject Line",
                "Body text",
                priority="high",
                msg_type="task_assignment",
            )
        finally:
            os.environ["PATH"] = old_path
        assert ok is True
        # The real subprocess ran our shim, which logged the real argv it received.
        logged = argv_log.read_text(encoding="utf-8").split("\n")
        assert logged == [
            "sess-impl-1",
            "Subject Line",
            "Body text",
            "--priority",
            "high",
            "--type",
            "task_assignment",
        ]


def test_send_message_returns_false_on_nonzero_exit_and_missing_binary():
    """Returns False when amp-send exits non-zero, and when amp-send is absent (caught)."""
    # Branch A: amp-send exists but exits non-zero → False.
    with tempfile.TemporaryDirectory(prefix="na-amp-fail-") as d:
        bindir = Path(d)
        _write_amp_shim(bindir, exit_code=3, argv_log=bindir / "argv.txt")
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{bindir}{os.pathsep}{old_path}"
        try:
            assert na.send_ai_maestro_message("sess", "S", "M") is False
        finally:
            os.environ["PATH"] = old_path

    # Branch B: amp-send not on PATH → subprocess raises FileNotFoundError,
    # caught by the function's except → False (the error-path branch).
    with tempfile.TemporaryDirectory(prefix="na-amp-none-") as d:
        empty_bin = Path(d) / "empty"
        empty_bin.mkdir()
        old_path = os.environ.get("PATH", "")
        # PATH with ONLY an empty dir guarantees amp-send cannot be resolved.
        os.environ["PATH"] = str(empty_bin)
        try:
            assert na.send_ai_maestro_message("sess", "S", "M") is False
        finally:
            os.environ["PATH"] = old_path


if __name__ == "__main__":
    sys.exit(run_standalone(globals()))
