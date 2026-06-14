#!/usr/bin/env python3
"""Scaffold or preflight a microtask PR without network access."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_helper():
    from physics_lab.registry.microtask_pr_helper import (
        microtask_branch,
        microtask_pr_body,
        microtask_title,
        preflight_microtask_pr,
    )

    return (
        microtask_branch,
        microtask_pr_body,
        microtask_title,
        preflight_microtask_pr,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser("scaffold", help="Print a suggested branch, title, and PR body.")
    scaffold.add_argument("--queue-id", required=True)
    scaffold.add_argument(
        "--contributor-id",
        required=True,
        help=(
            "Lowercased GitHub username when available; otherwise a stable "
            "maintainer-approved short id."
        ),
    )
    scaffold.add_argument("--agent-id", required=True)
    scaffold.add_argument("--slug", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--microtask-id")
    scaffold.add_argument("--microtask-ids", nargs="*", default=[])

    preflight = subparsers.add_parser("preflight", help="Check branch/title/body before opening a PR.")
    preflight.add_argument("--branch", required=True)
    preflight.add_argument("--title", required=True)
    preflight.add_argument("--body-file", required=True)
    preflight.add_argument("--root", default=".")

    status = subparsers.add_parser("status", help="Show effective microtask availability.")
    status.add_argument("--queue-id")
    status.add_argument("--include-unavailable", action="store_true")
    status.add_argument("--json", action="store_true")
    status.add_argument("--root", default=".")

    return parser


def command_scaffold(args: argparse.Namespace) -> int:
    microtask_branch, microtask_pr_body, microtask_title, _ = _load_helper()
    branch = microtask_branch(
        args.contributor_id,
        args.agent_id,
        args.slug,
        queue_id=None if args.microtask_id else args.queue_id,
        microtask_id=args.microtask_id,
    )
    title = microtask_title(args.queue_id, args.description)
    body = microtask_pr_body(
        queue_id=args.queue_id,
        branch=branch,
        title=title,
        microtask_ids=tuple(args.microtask_ids),
    )
    sys.stdout.write(f"Branch: {branch}\n")
    sys.stdout.write(f"Title: {title}\n\n")
    sys.stdout.write(body)
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    _, _, _, preflight_microtask_pr = _load_helper()
    body_path = Path(args.body_file)
    body_text = body_path.read_text(encoding="utf-8")
    report = preflight_microtask_pr(
        Path(args.root),
        branch=args.branch,
        title=args.title,
        body_text=body_text,
    )
    if report.errors:
        sys.stdout.write("Errors:\n")
        for item in report.errors:
            sys.stdout.write(f"- {item}\n")
    else:
        sys.stdout.write("Errors: none\n")
    if report.warnings:
        sys.stdout.write("Warnings:\n")
        for item in report.warnings:
            sys.stdout.write(f"- {item}\n")
    else:
        sys.stdout.write("Warnings: none\n")
    return 0 if report.ok else 1


def command_status(args: argparse.Namespace) -> int:
    from physics_lab.registry.microtask_queue_summary import load_microtask_availability

    items = load_microtask_availability(Path(args.root), queue_id=args.queue_id)
    if not args.include_unavailable:
        items = tuple(item for item in items if item.status == "available")

    if args.json:
        sys.stdout.write(json.dumps([asdict(item) for item in items], indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.queue_id:
        sys.stdout.write(f"Microtask availability for {args.queue_id}\n")
    else:
        sys.stdout.write("Microtask availability\n")
    sys.stdout.write(
        "| Queue | Microtask | Status | Repeatable | Completed Runs | Active Runs | Risk | Title |\n"
    )
    sys.stdout.write("| --- | --- | --- | --- | ---: | ---: | --- | --- |\n")
    for item in items:
        escaped_title = item.title.replace("|", "\\|")
        sys.stdout.write(
            "| "
            f"`{item.queue_id}` | "
            f"`{item.microtask_id}` | "
            f"`{item.status}` | "
            f"`{str(item.repeatable).lower()}` | "
            f"{item.completed_runs} | "
            f"{item.active_runs} | "
            f"`{item.risk_level}` | "
            f"{escaped_title} |\n"
        )
    if not items:
        sys.stdout.write("\nNo matching microtasks.\n")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "scaffold":
        return command_scaffold(args)
    if args.command == "preflight":
        return command_preflight(args)
    if args.command == "status":
        return command_status(args)
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
