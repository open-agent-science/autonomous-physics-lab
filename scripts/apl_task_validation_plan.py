#!/usr/bin/env python3
"""Print an advisory local-validation plan for a canonical task."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.task_validation_plan import build_task_validation_plan  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Canonical task id, for example TASK-0522.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--changed-file", action="append", default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def _print_human(plan) -> None:
    print("APL task validation plan")
    print(f"- task: {plan.task_id}")
    print(f"- task file: {plan.task_file}")
    print("- changed files:")
    for path in plan.changed_files:
        print(f"  - {path}")
    if not plan.changed_files:
        print("  - none")
    print("- canonical task commands:")
    for command in plan.task_commands:
        print(f"  - {command}")
    if not plan.task_commands:
        print("  - none")
    fast_lane = "recommended" if plan.fast_lane_recommended else "not required for this narrow diff"
    print(f"- parallel fast lane: {fast_lane}")
    if plan.fast_lane_recommended:
        print("  - python3 scripts/validate_fast.py")
    probe = "recommended before fallback decisions" if plan.windows_runtime_probe_recommended else "optional"
    print(f"- pytest runtime probe: {probe}")
    if plan.windows_runtime_probe_recommended:
        print("  - python3 scripts/apl_agent_doctor.py --probe-pytest-runtime --no-gh-auth-check")
    print("- validation layers:")
    for layer in plan.validation_layers:
        print(f"  - {layer}")
    print("- notes:")
    for note in plan.notes:
        print(f"  - {note}")


def main() -> int:
    args = build_parser().parse_args()
    plan = build_task_validation_plan(
        Path(args.root),
        args.task,
        changed_files=None if args.changed_file is None else tuple(args.changed_file),
    )
    if args.json:
        print(json.dumps(asdict(plan), indent=2, sort_keys=True))
    else:
        _print_human(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
