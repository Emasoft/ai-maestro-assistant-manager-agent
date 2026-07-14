#!/usr/bin/env python3
"""
amama_user_prompt_submit.py - Record user input timestamp on every UserPromptSubmit.

UserPromptSubmit hook that records the user's last-input timestamp so AMAMA's
amama-presence-tracker skill can compute idle time across sessions. Fail-soft:
never blocks prompt submission, even if the server is unreachable, the CLI is
absent, auth is missing, or any unforeseen error occurs.

The write goes through the FROZEN CLI (`aimaestro-agent.sh session user-input`),
never a direct call to the server's HTTP surface. R23 (Plugin<->Server Decoupling
via the Frozen CLI Layer) is an IRON rule: that surface changes constantly, and
the CLI is the frozen boundary that shields plugins from it. This hook carries
only the non-server part (the cron-prompt denylist filter); the server part lives
behind the CLI, which also owns auth and the endpoint.

System-injected turns (cron-fired prompts from the ai-maestro-janitor or
any other plugin that calls CronCreate) are NOT user input and must NOT
update the presence clock. Such prompts arrive on the same UserPromptSubmit
channel as human input but use a recognizable [<plugin>-<event>] prefix.
We parse the JSON payload from stdin and short-circuit on a small
denylist of known prefixes; without this filter the cron heartbeat would
reset the idle clock every time it fires.

Frozen-CLI contract (the plugin's only supported interface):
    aimaestro-agent.sh session user-input
    Auth: the CLI resolves it from $AID_AUTH itself - the plugin never
          assembles a bearer header or an endpoint URL.
    Any non-zero exit / missing CLI: ignored - fail-soft.

Dependencies: Python 3.8+ stdlib only.

Usage (as Claude Code hook):
    Receives JSON via stdin from UserPromptSubmit hook event.
    Output: nothing (silent fire-and-forget).

Exit codes:
    0 - Always (fail-soft, do not block prompt submission).
"""

from __future__ import annotations

import json
import os
import shutil
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

    if not os.environ.get("AID_AUTH", ""):
        # No AID auth means this Claude Code session isn't AI Maestro-managed.
        # Silently skip - nothing to record. (The CLI would resolve the bearer
        # itself, but spawning a process only to have it 401 is pure waste.)
        return

    # Write through the FROZEN CLI, never a direct server call (R23, IRON).
    # WHY the indirection matters and must not be "simplified" back into a POST:
    # the server's HTTP surface changes constantly; the CLI is the frozen
    # boundary. This plugin previously hand-rolled the presence POST against a
    # hardcoded endpoint path with its own bearer header, coupling it to a route
    # it does not own. The CLI also resolves auth itself, so no credential and
    # no endpoint URL is assembled here — which is why this file must stay free
    # of any endpoint literal (test_hook_never_calls_the_api_directly pins that).
    cli = shutil.which("aimaestro-agent.sh")
    if cli is None:
        # Not an AI Maestro host (or the CLI isn't installed/on PATH). Presence
        # is best-effort - degrade silently rather than block the user.
        return

    try:
        # capture_output: a UserPromptSubmit hook's stdout is INJECTED into the
        # prompt context, so this must never leak the CLI's output into the
        # user's turn. check=False + the broad except: presence is best-effort
        # and a failed write must never block prompt submission. 2s timeout for
        # the same reason - the user must not wait on a presence ping.
        subprocess.run(
            [cli, "session", "user-input"],
            capture_output=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        # Missing binary, spawn failure, or timeout - all non-fatal.
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
