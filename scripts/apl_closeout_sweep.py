#!/usr/bin/env python3
"""Deterministic maintainer helper for closeout-sweep candidate discovery."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for closeout sweep runs."""
    parser = argparse.ArgumentParser(
        description="Scan REVIEW_READY tasks and find merged-task closeout candidates."
    )
    parser.add_argument(
        "--merged-limit",
        type=int,
        default=200,
        help="How many merged PRs to inspect via gh.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Apply all READY closeout candidates by updating task statuses from "
            "REVIEW_READY to DONE. Requires clean main."
        ),
    )
    parser.add_argument(
        "--auto-safe",
        action="store_true",
        help=(
            "Apply only the auto-safe subset of READY candidates: tasks not opted "
            "out via `closeout: review`, whose merged PR touched no protected "
            "scientific artifact, and that do not unblock another task. Requires "
            "clean main. Used by the post-merge board-sync automation."
        ),
    )
    return parser


def main() -> int:
    """Run the closeout sweep helper."""
    from physics_lab.registry.closeout_sweep import (
        apply_auto_safe_closeouts,
        apply_closeout_sweep_report,
        full_repo_signal_status,
        render_closeout_sweep_apply_report,
        build_closeout_sweep_report,
        render_closeout_sweep_report,
    )

    parser = build_parser()
    args = parser.parse_args()
    report = build_closeout_sweep_report(REPO_ROOT, merged_limit=args.merged_limit)
    print(render_closeout_sweep_report(report))
    if args.auto_safe:
        print("")
        signal = full_repo_signal_status(REPO_ROOT)
        if signal != "ok":
            print(
                f"full_repo signal is `{signal}` (red/stale/unknown) -> report-only; "
                "committing no auto-closeouts. The main full_repo status must be a "
                "fresh success before safe tasks are auto-closed."
            )
        else:
            apply_report = apply_auto_safe_closeouts(REPO_ROOT, report)
            print(render_closeout_sweep_apply_report(apply_report))
    elif args.apply:
        print("")
        apply_report = apply_closeout_sweep_report(REPO_ROOT, report)
        print(render_closeout_sweep_apply_report(apply_report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
