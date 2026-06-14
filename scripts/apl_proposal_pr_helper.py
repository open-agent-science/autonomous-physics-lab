#!/usr/bin/env python3
"""Scaffold, preflight, or create a task-proposal PR.

Proposals are how agents surface bugs, friction, and new task ideas. This helper
mirrors apl_task_pr_helper.py for the proposal lane so the branch, title,
filename, and schema are correct before anything is pushed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_helper():
    from physics_lab.registry.proposal_pr_helper import (
        preflight_proposal_pr,
        proposal_branch,
        proposal_filename,
        proposal_title,
        proposal_yaml,
    )

    return (
        preflight_proposal_pr,
        proposal_branch,
        proposal_filename,
        proposal_title,
        proposal_yaml,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser(
        "scaffold", help="Print a branch, title, filename, and schema-valid proposal YAML."
    )
    scaffold.add_argument("--date", required=True, help="Proposal date as YYYYMMDD.")
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
    scaffold.add_argument("--title", required=True)
    scaffold.add_argument("--type", required=True, dest="proposal_type")
    scaffold.add_argument("--summary", required=True)
    scaffold.add_argument("--rationale", default="")
    scaffold.add_argument("--related-domain", required=True)
    scaffold.add_argument("--planning-context", required=True)
    scaffold.add_argument("--priority", default="medium")
    scaffold.add_argument("--input-mode", default="planning_only")
    scaffold.add_argument("--related-object", action="append", default=[])
    scaffold.add_argument("--strategy-alignment", action="append", default=[])
    scaffold.add_argument("--requirement", action="append", default=[])
    scaffold.add_argument("--accepted-output", action="append", default=[])
    scaffold.add_argument(
        "--write",
        action="store_true",
        help="Write the proposal YAML to tasks/proposals/<filename> instead of stdout-only.",
    )
    scaffold.add_argument("--root", default=".")

    preflight = subparsers.add_parser(
        "preflight", help="Check branch/title/filename/schema before opening a PR."
    )
    preflight.add_argument("--branch", required=True)
    preflight.add_argument("--title", required=True)
    preflight.add_argument("--proposal-path", required=True)
    preflight.add_argument("--root", default=".")

    create = subparsers.add_parser("create", help="Create a draft proposal PR using GitHub CLI.")
    create.add_argument("--branch", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--base", default="main")
    create.add_argument("--ready", action="store_true", help="Create a ready PR instead of a draft.")

    return parser


def command_scaffold(args: argparse.Namespace) -> int:
    (_, proposal_branch_fn, proposal_filename_fn, proposal_title_fn, proposal_yaml_fn) = (
        _load_helper()
    )
    branch = proposal_branch_fn(args.contributor_id, args.agent_id, args.slug)
    title = proposal_title_fn(args.title)
    filename = proposal_filename_fn(args.date, args.contributor_id, args.slug)
    document = proposal_yaml_fn(
        date_str=args.date,
        contributor_id=args.contributor_id,
        agent_id=args.agent_id,
        slug=args.slug,
        title=args.title,
        proposal_type=args.proposal_type,
        summary=args.summary,
        rationale=args.rationale,
        related_domain=args.related_domain,
        planning_context=args.planning_context,
        priority=args.priority,
        input_mode=args.input_mode,
        related_objects=tuple(args.related_object),
        strategy_alignment=tuple(args.strategy_alignment),
        requirements=tuple(args.requirement),
        accepted_outputs=tuple(args.accepted_output),
    )
    if args.write:
        target = Path(args.root) / "tasks" / "proposals" / filename
        target.write_text(document, encoding="utf-8")
    sys.stdout.write(f"Branch: {branch}\n")
    sys.stdout.write(f"Title: {title}\n")
    sys.stdout.write(f"File: tasks/proposals/{filename}\n\n")
    sys.stdout.write(document)
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    preflight_proposal_pr, _, _, _, _ = _load_helper()
    report = preflight_proposal_pr(
        Path(args.root),
        branch=args.branch,
        title=args.title,
        proposal_path=args.proposal_path,
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


def _manual_create_commands(args: argparse.Namespace) -> None:
    draft = "" if args.ready else "--draft "
    sys.stderr.write("Manual publication commands for a maintainer console:\n")
    sys.stderr.write(f"- git push origin {args.branch}\n")
    sys.stderr.write(
        f"- gh pr create {draft}--base {args.base} --head {args.branch} "
        f"--title {args.title!r} --body-file {args.body_file}\n"
    )


def command_create(args: argparse.Namespace) -> int:
    from physics_lab.registry.pr_capability import (
        env_with_discovered_tool_paths,
        find_gh_path,
        suspicious_proxy_env_names,
    )

    gh_path = find_gh_path()
    if gh_path is None:
        sys.stderr.write(
            "Cannot create PR directly: GitHub CLI `gh` is not installed or not discoverable.\n"
        )
        _manual_create_commands(args)
        return 127
    proxy_names = suspicious_proxy_env_names()
    if proxy_names:
        sys.stderr.write(
            "Warning: proxy env may block GitHub CLI calls: "
            + ", ".join(proxy_names)
            + ". Unset them for the publication command if gh reports a 127.0.0.1 connection error.\n"
        )
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
        env=env_with_discovered_tool_paths(),
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        _manual_create_commands(args)
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
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
