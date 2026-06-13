#!/usr/bin/env python3
"""
amama_session_start.py - AI Maestro Assistant Manager SessionStart hook.

The old activeContext/progress/patterns memory-bank that this hook used to load
at session start has been retired (TRDD-8707e849). Session memory is now the
markdown-notes + memgrep system, recalled on demand via the `amama-memory-recall`
skill — NOT auto-loaded at session start. This hook therefore loads nothing; it
remains registered so the SessionStart wiring is intact and so subagent runs are
explicitly short-circuited.

Dependencies: Python 3.8+ stdlib only

Usage (as Claude Code hook):
    Receives JSON via stdin from SessionStart hook event.

Exit codes:
    0 - Success
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    """Main entry point for SessionStart hook.

    Reads (and discards) the hook payload from stdin. No session memory is loaded
    here anymore — recall is on-demand via the `amama-memory-recall` skill.

    Returns:
        Exit code: 0 for success
    """
    # Read hook input from stdin (may be empty for SessionStart).
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
        else:
            hook_input = {}
    except json.JSONDecodeError:
        hook_input = {}

    # Subagent runs carry agent_id (2.1.69+); nothing to do for them either.
    if hook_input.get("agent_id"):
        return 0

    return 0


def _entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _entry()
