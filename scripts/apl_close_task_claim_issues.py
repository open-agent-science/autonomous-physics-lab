#!/usr/bin/env python3
"""Close stale GitHub task-claim issues after canonical task closeout."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for task-claim issue hygiene."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Optional GitHub repo slug, e.g. owner/name.")
    parser.add_argument("--limit", type=int, default=100, help="Open issue limit to inspect.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Close issues whose canonical task is already DONE.",
    )
    return parser


def main() -> int:
    """Run task-claim issue hygiene."""
    from physics_lab.registry.task_claim_issues import (
        classify_task_claim_issues,
        close_task_claim_issue,
        load_open_github_issues,
        render_task_claim_issue_report,
    )

    args = build_parser().parse_args()
    issues = load_open_github_issues(repo=args.repo, limit=args.limit)
    report = classify_task_claim_issues(REPO_ROOT, issues)
    print(render_task_claim_issue_report(report))

    if args.apply:
        for issue in report.closeable:
            close_task_claim_issue(issue.number, repo=args.repo)
        if report.closeable:
            print("")
            print(f"Closed {len(report.closeable)} stale task-claim issue(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
