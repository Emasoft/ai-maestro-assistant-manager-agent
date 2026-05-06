#!/usr/bin/env python3
"""
amama_user_prompt_submit.py - Record user input timestamp on every UserPromptSubmit.

UserPromptSubmit hook that POSTs to the AI Maestro server's user-presence
endpoint so AMAMA's amama-presence-tracker skill can compute idle time
across sessions. Fail-soft: never blocks prompt submission, even if the
server is unreachable or auth is missing.

Endpoint contract (server-side):
    POST /api/sessions/me/user-input
    Authorization: Bearer $AID_AUTH
    Body: empty
    Response 200: { "recorded_at_epoch": <int> }
    Errors 401/403: ignored — fail-soft

Dependencies: Python 3.8+ stdlib only (uses curl via subprocess).

Usage (as Claude Code hook):
    Receives JSON via stdin from UserPromptSubmit hook event.
    Output: nothing (silent fire-and-forget).

Exit codes:
    0 - Always (fail-soft, do not block prompt submission).
"""

from __future__ import annotations

import os
import subprocess
import sys


def _entry() -> None:
    # Drain stdin so Claude Code's hook pipe doesn't block. We don't need
    # the payload — the server reads "now" from its own clock, identifies
    # the user via the bearer token.
    try:
        sys.stdin.read()
    except OSError:
        pass

    api_base = os.environ.get("AIMAESTRO_API", "http://localhost:23000")
    aid_auth = os.environ.get("AID_AUTH", "")

    if not aid_auth:
        # No AID auth means this Claude Code session isn't AI Maestro-managed.
        # Silently skip — nothing to record.
        return

    url = f"{api_base.rstrip('/')}/api/sessions/me/user-input"
    try:
        # 2-second timeout: presence is best-effort, never block the user.
        # -X POST with empty body. -fsS: fail silently on HTTP errors but
        # show errors on stderr (which is discarded below by suppressing
        # stderr capture failures).
        subprocess.run(
            [
                "curl",
                "-fsS",
                "-X", "POST",
                "-H", f"Authorization: Bearer {aid_auth}",
                "-H", "Content-Length: 0",
                "--max-time", "2",
                url,
            ],
            capture_output=True,
            timeout=3,
            check=False,
        )
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, OSError):
        # Any failure is non-fatal — presence tracking degrades gracefully.
        pass

    # Always exit 0 — never block prompt submission on a presence-write failure.


if __name__ == "__main__":
    _entry()
