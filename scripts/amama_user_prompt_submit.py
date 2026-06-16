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

Dependencies: Python 3.8+ stdlib only (urllib.request — cross-platform, no curl).

Usage (as Claude Code hook):
    Receives JSON via stdin from UserPromptSubmit hook event.
    Output: nothing (silent fire-and-forget).

Exit codes:
    0 - Always (fail-soft, do not block prompt submission).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

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

    # The endpoint path is a fixed server-side contract (NOT user-controlled);
    # it is held in its own constant so the request target is assembled only
    # from the operator-configured api_base plus this literal path.
    # DECOUPLE-BLOCKED ai-maestro#36 (hook-split): per the frozen-CLI invariant
    # (R22) a plugin must never call /api/ directly. This direct POST must be
    # replaced by a frozen CLI (an agent-session.sh user-input verb) once that
    # verb is exposed/deployed; the plugin then carries only the non-api part
    # (the prompt-denylist filter) and shells out to the CLI for the api-part.
    path = "/api/sessions/me/user-input"
    target = f"{api_base.rstrip('/')}{path}"
    # urllib (stdlib) instead of curl: cross-platform (curl is not shipped on
    # Windows) and no shell/subprocess. The empty-bytes body yields
    # Content-Length: 0; the bearer header authenticates the session to the
    # local AI Maestro server. 2-second timeout: presence is best-effort and
    # must never block the user.
    request = urllib.request.Request(target, data=b"", method="POST")
    request.add_header("Authorization", f"Bearer {aid_auth}")
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            response.read()  # drain so the connection closes cleanly
    except (urllib.error.URLError, OSError, ValueError):
        # Any failure (HTTP error, transport failure, timeout) is non-fatal -
        # presence tracking degrades gracefully.
        pass

    # Always exit 0 - never block prompt submission on a presence-write failure.


def _main() -> None:
    """Hook entry point - fail-soft wrapper around _entry().

    Fail-soft is absolute here: even an unforeseen exception (MemoryError,
    KeyboardInterrupt mid-request, a future stdlib regression) must not
    block the user's prompt. We catch BaseException, swallow it, and let
    Python exit 0 on natural script completion.
    """
    try:
        _entry()
    except BaseException:
        pass


if __name__ == "__main__":
    _main()
