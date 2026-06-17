#!/usr/bin/env python3
"""Run the PR finish gate: maintainer review, CI, then ready transition."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", type=int, required=True, help="GitHub pull request number.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run review and CI gates but print the ready command instead of executing it.",
    )
    parser.add_argument(
        "--validation-timeout-seconds",
        type=int,
        default=300,
        help="Per-command local validation budget passed to apl_review_pr.py.",
    )
    return parser


def main() -> int:
    """Run the finish gate helper."""
    from physics_lab.registry.pr_finish_gate import finish_pr, render_finish_gate_report

    args = build_parser().parse_args()
    report = finish_pr(
        REPO_ROOT,
        args.pr,
        dry_run=args.dry_run,
        validation_timeout_seconds=args.validation_timeout_seconds,
    )
    print(render_finish_gate_report(report, pr_number=args.pr))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
