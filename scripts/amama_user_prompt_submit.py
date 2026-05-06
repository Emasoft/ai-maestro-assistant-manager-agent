#!/usr/bin/env python3
"""
amama_user_prompt_submit.py - Record user input timestamp on every UserPromptSubmit.

UserPromptSubmit hook that POSTs to the AI Maestro server's user-presence
endpoint so AMAMA's amama-presence-tracker skill can compute idle time
across sessions. Fail-soft: never blocks prompt submission, even if the
server is unreachable, auth is missing, or any unforeseen error occurs.

System-injected turns (cron-fired prompts from the ai-maestro-janitor or
any other plugin that calls CronCreate) are NOT user input and must NOT
update the presence clock. Such prompts arrive on the same UserPromptSubmit
channel as human input but use a recognizable [<plugin>-<event>] prefix.
We parse the JSON payload from stdin and short-circuit on a small
denylist of known prefixes; without this filter the cron heartbeat would
reset the idle clock every time it fires.

Endpoint contract (server-side):
    POST /api/sessions/me/user-input
    Authorization: Bearer $AID_AUTH
    Body: empty
    Response 200: { "recorded_at_epoch": <int> }
    Errors 401/403: ignored - fail-soft

Dependencies: Python 3.8+ stdlib only (uses curl via subprocess).

Usage (as Claude Code hook):
    Receives JSON via stdin from UserPromptSubmit hook event.
    Output: nothing (silent fire-and-forget).

Exit codes:
    0 - Always (fail-soft, do not block prompt submission).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Prompts that look like user input on the UserPromptSubmit channel but
# are actually fired by CronCreate-driven plugins. Adding a new entry here
# is the canonical way to teach the presence WRITE side to ignore another
# scheduled-prompt source. Match is `prompt.lstrip().startswith(prefix)`.
SYSTEM_PROMPT_PREFIXES = (
    "[janitor-heartbeat]",
    "[janitor-renew]",
    "[janitor-resume]",
)


def _is_system_injected(payload_raw: str) -> bool:
    """Return True if the hook payload describes a cron-injected prompt.

    The Claude Code UserPromptSubmit payload is a JSON object containing
    at least a `prompt` field. Anything we cannot parse is treated as
    "not system-injected" so a malformed payload still results in a POST
    (the alternative — silently dropping the WRITE — would be the worse
    failure mode here, because it makes the user look idle when they are
    not).
    """
    try:
        payload = json.loads(payload_raw)
    except (ValueError, TypeError):
        return False
    if not isinstance(payload, dict):
        return False
    prompt = payload.get("prompt")
    if not isinstance(prompt, str):
        return False
    head = prompt.lstrip()
    return any(head.startswith(p) for p in SYSTEM_PROMPT_PREFIXES)


def _entry() -> None:
    # Read the full hook payload. We need the prompt text to filter out
    # cron-injected turns; draining without parsing was the v2.9.0 bug.
    try:
        raw = sys.stdin.read()
    except OSError:
        raw = ""

    if _is_system_injected(raw):
        # Cron heartbeat or other system-fired turn - not user input.
        return

    api_base = os.environ.get("AIMAESTRO_API", "http://localhost:23000")
    aid_auth = os.environ.get("AID_AUTH", "")

    if not aid_auth:
        # No AID auth means this Claude Code session isn't AI Maestro-managed.
        # Silently skip - nothing to record.
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
                "-X",
                "POST",
                "-H",
                f"Authorization: Bearer {aid_auth}",
                "-H",
                "Content-Length: 0",
                "--max-time",
                "2",
                url,
            ],
            capture_output=True,
            timeout=3,
            check=False,
        )
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, OSError):
        # Any failure is non-fatal - presence tracking degrades gracefully.
        pass

    # Always exit 0 - never block prompt submission on a presence-write failure.


if __name__ == "__main__":
    # Fail-soft is absolute: even an unforeseen exception (MemoryError,
    # KeyboardInterrupt mid-curl, a future stdlib regression) must not
    # block the user's prompt. Catch BaseException, swallow it, and exit 0.
    try:
        _entry()
    except BaseException:
        pass
    sys.exit(0)
