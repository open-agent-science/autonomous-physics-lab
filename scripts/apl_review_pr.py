#!/usr/bin/env python3
"""Deterministic maintainer helper for pre-merge PR review."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for PR review."""
    parser = argparse.ArgumentParser(
        description="Review a task, task-queue, proposal, closeout, or microtask PR."
    )
    parser.add_argument("--pr", type=int, help="GitHub pull request number.")
    parser.add_argument("--branch", help="Local branch to review.")
    parser.add_argument("--task", help="Task id, for example TASK-0034.")
    parser.add_argument(
        "--validation-mode",
        choices=("ci-aware", "strict"),
        default="ci-aware",
        help=(
            "Use ci-aware to avoid duplicating already-green GitHub PR checks "
            "while still running local-only validation; use strict to run every "
            "task validation command locally."
        ),
    )
    parser.add_argument(
        "--validation-timeout-seconds",
        type=int,
        default=300,
        help=(
            "Per-command local validation budget for maintainer-review task "
            "commands. Timeouts block the verdict with environment diagnostics."
        ),
    )
    return parser


def main() -> int:
    """Run the PR review helper."""
    from physics_lab.registry.maintainer_review import (
        build_review_report,
        render_review_report,
    )

    parser = build_parser()
    args = parser.parse_args()
    if args.pr is None and args.branch is None:
        parser.error("Provide at least one of --pr or --branch.")
    report = build_review_report(
        REPO_ROOT,
        pull_request=args.pr,
        branch=args.branch,
        task_id=args.task,
        validation_mode=args.validation_mode,
        validation_timeout_seconds=args.validation_timeout_seconds,
    )
    print(render_review_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
