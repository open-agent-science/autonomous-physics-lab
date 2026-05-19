#!/usr/bin/env python3
"""
Check local Claude Code monthly token budget.

Reads ~/.claude/projects/ JSONL session logs, sums token usage for the
current billing month, and compares against a configurable limit.

Exit codes:
  0 – usage is below the threshold (safe to run more tasks)
  1 – usage is at or above the threshold

Environment variables:
  CLAUDE_PROJECTS_DIR       override ~/.claude/projects (useful for tests)
  CLAUDE_MONTHLY_TOKEN_LIMIT  total output+input tokens allowed per month
                              default: 6_000_000  (~Claude Max 5x estimate)
  CLAUDE_BUDGET_THRESHOLD_PCT percentage of limit above which we block
                              default: 50
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import sys


DEFAULT_MONTHLY_LIMIT = 6_000_000
DEFAULT_THRESHOLD_PCT = 50


def _projects_dir() -> pathlib.Path:
    override = os.environ.get("CLAUDE_PROJECTS_DIR")
    if override:
        return pathlib.Path(override)
    return pathlib.Path.home() / ".claude" / "projects"


def _month_start(now: datetime.datetime) -> datetime.datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def compute_usage(
    projects_dir: pathlib.Path,
    now: datetime.datetime | None = None,
) -> dict:
    """Return token usage totals for the current billing month."""
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = _month_start(now)

    total_input = 0
    total_output = 0
    total_cache_read = 0
    sessions_scanned = 0
    files_read = 0

    if not projects_dir.is_dir():
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "total_tokens": 0,
            "sessions_scanned": 0,
            "files_read": 0,
            "period_start": cutoff.isoformat(),
        }

    for jsonl_file in projects_dir.rglob("*.jsonl"):
        files_read += 1
        try:
            with open(jsonl_file, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    ts_str = msg.get("timestamp", "")
                    if not ts_str:
                        continue
                    try:
                        ts = datetime.datetime.fromisoformat(
                            ts_str.replace("Z", "+00:00")
                        )
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=datetime.timezone.utc)
                    except ValueError:
                        continue

                    if ts < cutoff:
                        continue

                    usage = msg.get("message", {}).get("usage") or {}
                    if usage:
                        total_input += usage.get("input_tokens", 0)
                        total_output += usage.get("output_tokens", 0)
                        total_cache_read += usage.get("cache_read_input_tokens", 0)
                        sessions_scanned += 1
        except OSError:
            continue

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cache_read_tokens": total_cache_read,
        "total_tokens": total_input + total_output,
        "sessions_scanned": sessions_scanned,
        "files_read": files_read,
        "period_start": cutoff.isoformat(),
    }


def evaluate(
    usage: dict,
    monthly_limit: int,
    threshold_pct: float,
) -> dict:
    """Evaluate whether usage is under the budget threshold."""
    total = usage["total_tokens"]
    used_pct = (total / monthly_limit * 100) if monthly_limit > 0 else 0.0
    under_threshold = used_pct < threshold_pct

    return {
        **usage,
        "monthly_limit": monthly_limit,
        "threshold_pct": threshold_pct,
        "used_pct": round(used_pct, 2),
        "remaining_pct": round(100.0 - used_pct, 2),
        "under_threshold": under_threshold,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report Claude Code monthly token budget usage.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON report and always exit 0",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.environ.get("CLAUDE_MONTHLY_TOKEN_LIMIT", DEFAULT_MONTHLY_LIMIT)),
        help=f"Monthly token limit (default: {DEFAULT_MONTHLY_LIMIT})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=float(
            os.environ.get("CLAUDE_BUDGET_THRESHOLD_PCT", DEFAULT_THRESHOLD_PCT)
        ),
        help=f"Block threshold %% of limit (default: {DEFAULT_THRESHOLD_PCT})",
    )
    parser.add_argument(
        "--projects-dir",
        type=pathlib.Path,
        default=None,
        help="Override ~/.claude/projects path",
    )
    args = parser.parse_args(argv)

    projects_dir = args.projects_dir or _projects_dir()
    usage = compute_usage(projects_dir)
    report = evaluate(usage, args.limit, args.threshold)

    print(json.dumps(report, indent=2))

    if args.dry_run:
        return 0
    return 0 if report["under_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
