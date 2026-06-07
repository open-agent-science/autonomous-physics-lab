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
    return parser


def main() -> int:
    """Run the closeout sweep helper."""
    from physics_lab.registry.closeout_sweep import (
        apply_closeout_sweep_report,
        render_closeout_sweep_apply_report,
        build_closeout_sweep_report,
        render_closeout_sweep_report,
    )

    parser = build_parser()
    args = parser.parse_args()
    report = build_closeout_sweep_report(REPO_ROOT, merged_limit=args.merged_limit)
    print(render_closeout_sweep_report(report))
    if args.apply:
        print("")
        apply_report = apply_closeout_sweep_report(REPO_ROOT, report)
        print(render_closeout_sweep_apply_report(apply_report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
