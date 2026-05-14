#!/usr/bin/env python3
"""Scaffold, preflight, or create a canonical task PR."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_helper():
    from physics_lab.registry.task_pr_helper import (
        preflight_task_pr,
        task_branch,
        task_pr_body,
        task_title,
    )

    return preflight_task_pr, task_branch, task_pr_body, task_title


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser("scaffold", help="Print a suggested branch, title, and PR body.")
    scaffold.add_argument("--task-id", required=True)
    scaffold.add_argument("--contributor-id", required=True)
    scaffold.add_argument("--github-username", required=True)
    scaffold.add_argument("--agent-id", required=True)
    scaffold.add_argument("--agent-tool", default="Codex")
    scaffold.add_argument("--model-version")
    scaffold.add_argument("--human-reviewer", required=True)
    scaffold.add_argument("--slug", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--summary", required=True)
    scaffold.add_argument("--changed-file", action="append", default=[])
    scaffold.add_argument("--validation-command", action="append", default=[])
    scaffold.add_argument("--scientific-claim-impact", default="No claim promotion.")
    scaffold.add_argument("--result-artifact-impact", default="No committed result artifacts changed.")
    scaffold.add_argument("--body-only", action="store_true")
    scaffold.add_argument("--body-file")
    scaffold.add_argument("--root", default=".")

    preflight = subparsers.add_parser("preflight", help="Check branch/title/body before opening a PR.")
    preflight.add_argument("--branch", required=True)
    preflight.add_argument("--title", required=True)
    preflight.add_argument("--body-file", required=True)
    preflight.add_argument("--root", default=".")

    create = subparsers.add_parser("create", help="Create a draft task PR using GitHub CLI.")
    create.add_argument("--branch", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--base", default="main")
    create.add_argument("--ready", action="store_true", help="Create a ready PR instead of a draft.")

    ready = subparsers.add_parser("ready", help="Mark an existing draft task PR ready for review.")
    ready.add_argument("--pr", required=True)

    return parser


def command_scaffold(args: argparse.Namespace) -> int:
    _, task_branch_fn, task_pr_body_fn, task_title_fn = _load_helper()
    branch = task_branch_fn(args.contributor_id, args.agent_id, args.task_id, args.slug)
    title = task_title_fn(args.task_id, args.description)
    body = task_pr_body_fn(
        task_id=args.task_id,
        branch=branch,
        title=title,
        contributor_id=args.contributor_id,
        github_username=args.github_username,
        agent_tool=args.agent_tool,
        human_reviewer=args.human_reviewer,
        summary=args.summary,
        changed_files=tuple(args.changed_file),
        validation_commands=tuple(args.validation_command),
        scientific_claim_impact=args.scientific_claim_impact,
        result_artifact_impact=args.result_artifact_impact,
        model_version=args.model_version,
        root=Path(args.root),
    )
    if args.body_file:
        Path(args.body_file).write_text(body, encoding="utf-8")
    if args.body_only:
        sys.stdout.write(body)
        return 0
    sys.stdout.write(f"Branch: {branch}\n")
    sys.stdout.write(f"Title: {title}\n\n")
    sys.stdout.write(body)
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    preflight_task_pr, _, _, _ = _load_helper()
    body_text = Path(args.body_file).read_text(encoding="utf-8")
    report = preflight_task_pr(
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


def command_create(args: argparse.Namespace) -> int:
    from physics_lab.registry.pr_capability import find_gh_path

    gh_path = find_gh_path()
    if gh_path is None:
        sys.stderr.write(
            "Cannot create PR: GitHub CLI `gh` is not installed or not discoverable.\n"
        )
        return 127
    command = [
        gh_path,
        "pr",
        "create",
        "--base",
        args.base,
        "--head",
        args.branch,
        "--title",
        args.title,
        "--body-file",
        args.body_file,
    ]
    if not args.ready:
        command.insert(3, "--draft")
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        capture_output=True,
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


def command_ready(args: argparse.Namespace) -> int:
    from physics_lab.registry.pr_capability import find_gh_path

    gh_path = find_gh_path()
    if gh_path is None:
        sys.stderr.write(
            "Cannot mark PR ready: GitHub CLI `gh` is not installed or not discoverable.\n"
        )
        return 127
    completed = subprocess.run(
        [gh_path, "pr", "ready", args.pr],
        check=False,
        text=True,
        capture_output=True,
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "scaffold":
        return command_scaffold(args)
    if args.command == "preflight":
        return command_preflight(args)
    if args.command == "create":
        return command_create(args)
    if args.command == "ready":
        return command_ready(args)
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
