#!/usr/bin/env python3
"""Run the report-only pytest coverage workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import subprocess
import sys


DEFAULT_BASETEMP = ".pytest-basetemp"
DEFAULT_HTML_DIR = "_coverage/html"
COVERAGE_SCOPE = ("physics_lab", "scripts")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run APL's report-only branch coverage workflow for physics_lab "
            "and Python scripts. This helper does not set a coverage threshold."
        )
    )
    parser.add_argument(
        "--basetemp",
        default=DEFAULT_BASETEMP,
        help=f"Pytest temporary directory to use. Default: {DEFAULT_BASETEMP}",
    )
    parser.add_argument(
        "--html-dir",
        default=DEFAULT_HTML_DIR,
        help=f"HTML coverage report directory. Default: {DEFAULT_HTML_DIR}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the coverage command without running pytest.",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments, usually after '--'.",
    )
    return parser


def _extra_pytest_args(raw_args: list[str]) -> list[str]:
    if raw_args and raw_args[0] == "--":
        return raw_args[1:]
    return raw_args


def coverage_command(
    *,
    basetemp: str,
    html_dir: str,
    extra_args: list[str],
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        f"--basetemp={basetemp}",
        "--cov=physics_lab",
        "--cov=scripts",
        "--cov-branch",
        "--cov-report=term-missing:skip-covered",
        f"--cov-report=html:{html_dir}",
    ]
    command.extend(extra_args)
    return command


def _render_command(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def main() -> int:
    args = build_parser().parse_args()
    extra_args = _extra_pytest_args(args.pytest_args)
    command = coverage_command(
        basetemp=args.basetemp,
        html_dir=args.html_dir,
        extra_args=extra_args,
    )

    print("APL coverage report-only helper")
    print(f"- scope: {', '.join(COVERAGE_SCOPE)}")
    print("- branch coverage: enabled")
    print("- coverage threshold: none")
    print(f"- pytest basetemp: {Path(args.basetemp)}")
    print(f"- HTML report: {Path(args.html_dir)}")
    print("Command:")
    print(_render_command(command))

    if args.dry_run:
        return 0
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
