#!/usr/bin/env python3
"""
Check local Claude Code weekly token budget.

Reads ~/.claude/projects/ JSONL session logs, sums token usage for the
trailing 7 days, and compares against a configurable weekly limit.

The Claude Code plan exposes a weekly rolling quota (the in-app usage
panel shows "Weekly · all models" with a per-account reset date plus a
5-hour limit). This script approximates the weekly view by counting
tokens over the last 7 days; that matches the plan's reset semantics
much better than a calendar-monthly window.

Exit codes:
  0 – usage is below the threshold (safe to run more tasks)
  1 – usage is at or above the threshold

Environment variables:
  CLAUDE_PROJECTS_DIR        override ~/.claude/projects (useful for tests)
  CLAUDE_WEEKLY_TOKEN_LIMIT  total input + output + cache_creation tokens
                             allowed per trailing 7-day window
                             default: 6_000_000 (~Claude Max 5x estimate)
  CLAUDE_MONTHLY_TOKEN_LIMIT deprecated alias for CLAUDE_WEEKLY_TOKEN_LIMIT;
                             emits a stderr warning when used
  CLAUDE_BUDGET_THRESHOLD_PCT percentage of limit above which we block
                              default: 50

The gate is intentionally approximate: it counts input, output, and
cache-creation tokens from local Claude Code logs. Cache-read tokens are
reported separately for visibility but are not included in the threshold
total because they are usually discounted and can otherwise dominate
repeated-agent runs.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import sys


DEFAULT_WEEKLY_LIMIT = 6_000_000
DEFAULT_THRESHOLD_PCT = 50
ROLLING_WINDOW_DAYS = 7


def _projects_dir() -> pathlib.Path:
    override = os.environ.get("CLAUDE_PROJECTS_DIR")
    if override:
        return pathlib.Path(override)
    return pathlib.Path.home() / ".claude" / "projects"


def _week_start_rolling(now: datetime.datetime) -> datetime.datetime:
    """Return the cutoff datetime for a trailing 7-day window."""
    return now - datetime.timedelta(days=ROLLING_WINDOW_DAYS)


def compute_usage(
    projects_dir: pathlib.Path,
    now: datetime.datetime | None = None,
) -> dict:
    """Return token usage totals for the trailing 7-day window."""
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = _week_start_rolling(now)

    total_input = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    sessions_scanned = 0
    files_read = 0

    if not projects_dir.is_dir():
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_tokens": 0,
            "sessions_scanned": 0,
            "files_read": 0,
            "period_start": cutoff.isoformat(),
            "window_days": ROLLING_WINDOW_DAYS,
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
                        total_cache_creation += usage.get("cache_creation_input_tokens", 0)
                        total_cache_read += usage.get("cache_read_input_tokens", 0)
                        sessions_scanned += 1
        except OSError:
            continue

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cache_creation_tokens": total_cache_creation,
        "cache_read_tokens": total_cache_read,
        "total_tokens": total_input + total_output + total_cache_creation,
        "sessions_scanned": sessions_scanned,
        "files_read": files_read,
        "period_start": cutoff.isoformat(),
        "window_days": ROLLING_WINDOW_DAYS,
    }


def evaluate(
    usage: dict,
    weekly_limit: int | None = None,
    threshold_pct: float = DEFAULT_THRESHOLD_PCT,
    *,
    monthly_limit: int | None = None,
) -> dict:
    """Evaluate whether usage is under the budget threshold.

    Accepts either ``weekly_limit`` (preferred) or the legacy
    ``monthly_limit`` keyword argument. When both are provided,
    ``weekly_limit`` wins. The returned report includes both
    ``weekly_limit`` and a deprecated ``monthly_limit`` alias mirroring
    the same value for one release of backward compatibility.
    """
    if weekly_limit is None and monthly_limit is not None:
        weekly_limit = monthly_limit
    if weekly_limit is None:
        weekly_limit = DEFAULT_WEEKLY_LIMIT

    total = usage["total_tokens"]
    used_pct = (total / weekly_limit * 100) if weekly_limit > 0 else 0.0
    under_threshold = used_pct < threshold_pct

    return {
        **usage,
        "used_tokens": total,
        "limit_tokens": weekly_limit,
        "weekly_limit": weekly_limit,
        # Deprecated alias kept for one release; consumers should switch
        # to ``weekly_limit``.
        "monthly_limit": weekly_limit,
        "threshold_pct": threshold_pct,
        "used_pct": round(used_pct, 2),
        "remaining_pct": round(100.0 - used_pct, 2),
        "under_threshold": under_threshold,
    }


def _resolve_limit_from_env() -> int:
    """Resolve the budget limit honoring the deprecated monthly env var."""
    weekly_env = os.environ.get("CLAUDE_WEEKLY_TOKEN_LIMIT")
    monthly_env = os.environ.get("CLAUDE_MONTHLY_TOKEN_LIMIT")
    if weekly_env is not None:
        return int(weekly_env)
    if monthly_env is not None:
        print(
            "warning: CLAUDE_MONTHLY_TOKEN_LIMIT is deprecated; "
            "set CLAUDE_WEEKLY_TOKEN_LIMIT instead. "
            "Using the legacy value for this run.",
            file=sys.stderr,
        )
        return int(monthly_env)
    return DEFAULT_WEEKLY_LIMIT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report Claude Code weekly token budget usage.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON report and always exit 0",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            f"Weekly token limit "
            f"(default: ${{CLAUDE_WEEKLY_TOKEN_LIMIT:-{DEFAULT_WEEKLY_LIMIT}}}; "
            f"legacy CLAUDE_MONTHLY_TOKEN_LIMIT also honored with a warning)"
        ),
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

    limit = args.limit if args.limit is not None else _resolve_limit_from_env()

    projects_dir = args.projects_dir or _projects_dir()
    usage = compute_usage(projects_dir)
    report = evaluate(usage, weekly_limit=limit, threshold_pct=args.threshold)

    print(json.dumps(report, indent=2))

    if args.dry_run:
        return 0
    return 0 if report["under_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
