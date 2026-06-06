#!/usr/bin/env python3
"""Advisory live PR occupancy check for selected APL task ids."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.pr_capability import (  # noqa: E402
    env_with_discovered_tool_paths,
    find_gh_path,
    suspicious_proxy_env_names,
)
from physics_lab.registry.task_occupancy import classify_task_pr_occupancy  # noqa: E402


@dataclass(frozen=True)
class TaskOccupancyCheck:
    checked: bool
    source: str
    tasks: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--task", action="append", required=True, help="Task id to check.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--ignore-suspicious-proxy",
        action="store_true",
        help="Clear known loopback proxy blocker variables only for the child gh command.",
    )
    return parser


def _run_gh_pr_list(
    *,
    root: Path,
    gh_path: str,
    env: Mapping[str, str],
) -> tuple[list[dict[str, Any]] | None, str | None]:
    try:
        result = subprocess.run(
            [
                gh_path,
                "pr",
                "list",
                "--state",
                "all",
                "--limit",
                "100",
                "--json",
                "number,title,body,state,mergedAt,headRefName,url,isDraft",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
            env=dict(env),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        return None, result.stderr.strip() or result.stdout.strip()
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return None, f"gh returned invalid JSON: {exc}"
    if not isinstance(payload, list):
        return None, "gh returned a non-list JSON payload"
    return [item for item in payload if isinstance(item, dict)], None


def check_task_occupancy(
    root: Path,
    task_ids: tuple[str, ...],
    *,
    env: Mapping[str, str] | None = None,
    clear_suspicious_proxy: bool = False,
) -> TaskOccupancyCheck:
    source_env = dict(os.environ if env is None else env)
    proxy_names = suspicious_proxy_env_names(source_env)
    if proxy_names and not clear_suspicious_proxy:
        return TaskOccupancyCheck(
            checked=False,
            source="local_registry_only",
            tasks=(),
            warnings=(
                "Live PR occupancy was not checked because known local blocker "
                "proxy variables are set: "
                + ", ".join(proxy_names)
                + ". Retry with --ignore-suspicious-proxy when network access is allowed.",
            ),
        )

    child_env = env_with_discovered_tool_paths(
        source_env,
        clear_suspicious_proxy=clear_suspicious_proxy,
    )
    gh_path = find_gh_path(env=child_env)
    if gh_path is None:
        return TaskOccupancyCheck(
            checked=False,
            source="local_registry_only",
            tasks=(),
            warnings=("GitHub CLI `gh` is not installed or discoverable.",),
        )

    records, error = _run_gh_pr_list(root=root, gh_path=gh_path, env=child_env)
    if error is not None:
        return TaskOccupancyCheck(
            checked=False,
            source="local_registry_only",
            tasks=(),
            warnings=(f"Live PR occupancy lookup failed: {error}",),
        )

    return TaskOccupancyCheck(
        checked=True,
        source="github_prs",
        tasks=tuple(
            item.to_json()
            for item in classify_task_pr_occupancy(task_ids, records or [])
        ),
        warnings=(),
    )


def _print_human(report: TaskOccupancyCheck) -> None:
    print("APL task PR occupancy")
    print(f"- checked: {str(report.checked).lower()}")
    print(f"- source: {report.source}")
    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")
    if report.tasks:
        print("Tasks:")
        for item in report.tasks:
            reason = "; ".join(item["reasons"]) if item["reasons"] else "none"
            print(
                f"- {item['task_id']}: {item['classification']} "
                f"(available={str(item['available']).lower()}; reasons={reason})"
            )


def main() -> int:
    args = build_parser().parse_args()
    report = check_task_occupancy(
        Path(args.root),
        tuple(args.task),
        clear_suspicious_proxy=args.ignore_suspicious_proxy,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
