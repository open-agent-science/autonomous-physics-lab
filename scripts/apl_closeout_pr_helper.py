#!/usr/bin/env python3
"""Scaffold or preflight a closeout PR without network access."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_helper():
    from physics_lab.registry.closeout_pr_helper import (
        closeout_branch,
        closeout_pr_body,
        closeout_title,
        preflight_closeout_pr,
    )

    return closeout_branch, closeout_pr_body, closeout_title, preflight_closeout_pr


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser("scaffold", help="Print a suggested branch, title, and PR body.")
    scaffold.add_argument("--task-id", action="append", required=True)
    scaffold.add_argument("--contributor-id", required=True)
    scaffold.add_argument("--github-username", required=True)
    scaffold.add_argument("--agent-id", required=True)
    scaffold.add_argument("--agent-tool", default="Codex")
    scaffold.add_argument("--model-version")
    scaffold.add_argument("--human-reviewer", required=True)
    scaffold.add_argument("--slug", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--changed-file", action="append", default=[])
    scaffold.add_argument("--include-active-board", action="store_true")
    scaffold.add_argument("--include-task-views", action="store_true")
    scaffold.add_argument("--include-context", action="store_true")
    scaffold.add_argument("--body-only", action="store_true")

    preflight = subparsers.add_parser("preflight", help="Check branch/title/body before opening a PR.")
    preflight.add_argument("--branch", required=True)
    preflight.add_argument("--title", required=True)
    preflight.add_argument("--body-file", required=True)
    preflight.add_argument("--root", default=".")

    return parser


def command_scaffold(args: argparse.Namespace) -> int:
    closeout_branch_fn, closeout_pr_body, closeout_title_fn, _ = _load_helper()
    branch = closeout_branch_fn(args.contributor_id, args.agent_id, args.slug)
    title = closeout_title_fn(args.description)
    body = closeout_pr_body(
        task_ids=tuple(args.task_id),
        branch=branch,
        title=title,
        contributor_id=args.contributor_id,
        github_username=args.github_username,
        agent_tool=args.agent_tool,
        human_reviewer=args.human_reviewer,
        changed_files=tuple(args.changed_file),
        include_active_board=args.include_active_board,
        include_task_views=args.include_task_views,
        include_context=args.include_context,
        model_version=args.model_version,
    )
    if args.body_only:
        sys.stdout.write(body)
        return 0
    sys.stdout.write(f"Branch: {branch}\n")
    sys.stdout.write(f"Title: {title}\n\n")
    sys.stdout.write(body)
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    _, _, _, preflight_closeout_pr = _load_helper()
    body_path = Path(args.body_file)
    body_text = body_path.read_text(encoding="utf-8")
    report = preflight_closeout_pr(
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


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "scaffold":
        return command_scaffold(args)
    if args.command == "preflight":
        return command_preflight(args)
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
