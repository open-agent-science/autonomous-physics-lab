#!/usr/bin/env python3
"""Run the opt-in PR auto-ready gate for a GitHub Actions event."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    from physics_lab.registry.pr_auto_ready import AUTO_READY_LABEL

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event-path",
        default=os.environ.get("GITHUB_EVENT_PATH"),
        help="Path to the GitHub event JSON payload. Defaults to GITHUB_EVENT_PATH.",
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="Explicit pull request number; overrides event payload discovery.",
    )
    parser.add_argument(
        "--label",
        default=AUTO_READY_LABEL,
        help="Opt-in label required before the finish gate may mark a draft PR ready.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run review and CI gates but print the ready command instead of executing it.",
    )
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Exit non-zero when the PR opted in but review or CI blocks the ready transition.",
    )
    parser.add_argument(
        "--validation-timeout-seconds",
        type=int,
        default=300,
        help="Per-command local validation budget passed to apl_review_pr.py.",
    )
    parser.add_argument(
        "--ignore-check-name",
        action="append",
        default=[],
        help="Additional check name to ignore while classifying CI status; may be repeated.",
    )
    parser.add_argument(
        "--ignore-workflow",
        action="append",
        default=[],
        help="Additional workflow name to ignore while classifying CI status; may be repeated.",
    )
    return parser


def _load_event_payload(event_path: str | None) -> dict[str, object]:
    if not event_path:
        return {}
    path = Path(event_path)
    if not path.exists():
        raise FileNotFoundError(f"GitHub event payload not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping JSON event payload: {path}")
    return payload


def main() -> int:
    """Run the auto-ready helper."""
    from physics_lab.registry.pr_auto_ready import render_auto_ready_result, run_auto_ready

    args = build_parser().parse_args()
    try:
        event_payload = _load_event_payload(args.event_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Auto-ready status: error\nReason: {exc}", file=sys.stderr)
        return 1

    result = run_auto_ready(
        REPO_ROOT,
        event_payload,
        pr_number=args.pr,
        label=args.label,
        dry_run=args.dry_run,
        ignored_check_names=tuple(args.ignore_check_name),
        ignored_workflows=tuple(args.ignore_workflow),
        validation_timeout_seconds=args.validation_timeout_seconds,
    )
    print(render_auto_ready_result(result))
    if result.status == "error":
        return 1
    if args.fail_on_blocked and result.status == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
