#!/usr/bin/env python3
"""Run the always-on CI gates locally before pushing a PR (TASK-0726).

A task's declared validation is often narrower than what CI runs, so a PR can
pass locally and then fail the CI "fast tests" job — costing a 3-6 minute
round-trip. This command runs the CI-parity gates first: ruff, the targeted
docs/task tests CI runs, and strict repository validation. Use --full to run the
whole fast suite instead.

All checks run with the repository venv interpreter, so launching with a bare
system python does not produce false failures.

Examples:
    python3 scripts/apl_prepush_check.py
    python3 scripts/apl_prepush_check.py --full
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the pre-push check."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the always-on CI gates locally before pushing: ruff, the "
            "targeted docs/task tests, and strict repository validation. Use "
            "--full to run the whole fast suite."
        )
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the whole fast suite (validate_fast.py) instead of the targeted gates.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to check (default: this checkout).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the pre-push CI-parity check and return its exit code."""
    from physics_lab.registry.prepush_check import (
        render_prepush_report,
        run_prepush_checks,
    )

    parser = build_parser()
    args = parser.parse_args(argv)
    report = run_prepush_checks(Path(args.root), full=args.full)
    print(render_prepush_report(report))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
