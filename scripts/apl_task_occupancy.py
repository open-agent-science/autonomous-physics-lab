#!/usr/bin/env python3
"""Advisory live PR occupancy check for selected APL task ids."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.github_readonly import GitHubReadOnlyClient  # noqa: E402
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


def check_task_occupancy(
    root: Path,
    task_ids: tuple[str, ...],
    *,
    env: Mapping[str, str] | None = None,
    clear_suspicious_proxy: bool = False,
) -> TaskOccupancyCheck:
    client = GitHubReadOnlyClient(
        root,
        env=env,
        clear_suspicious_proxy=clear_suspicious_proxy,
    )
    result = client.list_pull_requests()
    if not isinstance(result.payload, list):
        return TaskOccupancyCheck(
            checked=False,
            source="local_registry_only",
            tasks=(),
            warnings=result.diagnostics,
        )

    return TaskOccupancyCheck(
        checked=True,
        source="github_prs" if result.source == "gh" else "public_rest_prs",
        tasks=tuple(
            item.to_json()
            for item in classify_task_pr_occupancy(task_ids, result.payload)
        ),
        warnings=result.diagnostics,
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
