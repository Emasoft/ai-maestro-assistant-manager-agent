#!/usr/bin/env python3
"""Shared report writer for AMAMA scripts.

All AMAMA scripts use this module to write verbose output to timestamped
report files and print only concise summaries to stdout. This reduces
token consumption when script output is captured into agent context.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path


class ReportWriter:
    """Writes verbose output to timestamped report files in design/reports/."""

    def __init__(self, script_name: str) -> None:
        self.script_name = script_name
        self._report_dir = self._resolve_report_dir()
        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _resolve_report_dir(self) -> Path:
        """Resolve report directory from CLAUDE_PROJECT_DIR, fallback to /tmp."""
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if project_dir:
            report_dir = Path(project_dir) / "design" / "reports"
        else:
            report_dir = Path("/tmp") / "amama-reports"
        try:
            report_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            report_dir = Path("/tmp") / "amama-reports"
            report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir

    def get_report_path(self) -> Path:
        """Return the timestamped report file path."""
        filename = f"{self.script_name}_{self._timestamp}.md"
        return self._report_dir / filename

    def write_report(self, content: str) -> Path:
        """Write full content to report file. Returns the file path."""
        report_path = self.get_report_path()
        report_path.write_text(content, encoding="utf-8")
        return report_path

    def print_summary(self, summary: str, report_path: Path | None = None) -> None:
        """Print 2-3 line summary to stdout.

        Format:
            [DONE] script_name - summary_line
            Report: /absolute/path/to/report.md
        """
        print(f"[DONE] {self.script_name} - {summary}")
        if report_path:
            print(f"Report: {report_path}")

    def print_failure(self, summary: str, report_path: Path | None = None) -> None:
        """Print failure summary to stderr."""
        print(f"[FAILED] {self.script_name} - {summary}", file=sys.stderr)
        if report_path:
            print(f"Report: {report_path}", file=sys.stderr)
