#!/usr/bin/env python3
"""Scaffold, preflight, or create a canonical task PR."""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_helper():
    from physics_lab.registry.task_pr_helper import (
        prepare_current_task_pr,
        preflight_task_pr,
        task_branch,
        task_pr_body,
        task_title,
    )
    from physics_lab.registry.review_policy import infer_agent_tool

    return (
        prepare_current_task_pr,
        preflight_task_pr,
        task_branch,
        task_pr_body,
        task_title,
        infer_agent_tool,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser("scaffold", help="Print a suggested branch, title, and PR body.")
    scaffold.add_argument("--task-id", required=True)
    scaffold.add_argument(
        "--contributor-id",
        required=True,
        help=(
            "Lowercased GitHub username when available; otherwise a stable "
            "maintainer-approved short id."
        ),
    )
    scaffold.add_argument("--github-username", required=True)
    scaffold.add_argument("--agent-id", required=True)
    scaffold.add_argument(
        "--agent-tool",
        help="Human-readable agent tool label. Defaults from --agent-id when omitted.",
    )
    scaffold.add_argument("--model-version")
    scaffold.add_argument("--human-reviewer", required=True)
    scaffold.add_argument("--slug", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--summary", required=True)
    scaffold.add_argument("--changed-file", action="append", default=[])
    scaffold.add_argument("--validation-command", action="append", default=[])
    scaffold.add_argument("--scientific-claim-impact", default="No claim promotion.")
    scaffold.add_argument("--result-artifact-impact", default="No committed result artifacts changed.")
    scaffold.add_argument("--task-verdict", default="not_applicable")
    scaffold.add_argument("--canonical-destination", default="none")
    scaffold.add_argument("--review-tier", default="none")
    scaffold.add_argument("--gate-a-status", default="not_applicable")
    scaffold.add_argument("--gate-b-status", default="not_applicable")
    scaffold.add_argument("--claim-impact", default="No claim promotion.")
    scaffold.add_argument("--knowledge-impact", default="No knowledge promotion.")
    scaffold.add_argument("--limitations-blockers", default="None for this PR shape.")
    scaffold.add_argument("--branch-pushed", action="store_true")
    scaffold.add_argument("--draft-pr-opened", action="store_true")
    scaffold.add_argument("--post-pr-review-run", action="store_true")
    scaffold.add_argument("--ready-for-review", action="store_true")
    scaffold.add_argument("--body-only", action="store_true")
    scaffold.add_argument("--body-file")
    scaffold.add_argument("--root", default=".")

    preflight = subparsers.add_parser("preflight", help="Check branch/title/body before opening a PR.")
    preflight.add_argument("--branch", required=True)
    preflight.add_argument("--title", required=True)
    preflight.add_argument("--body-file", required=True)
    preflight.add_argument("--root", default=".")

    prepare_current = subparsers.add_parser(
        "prepare-current",
        help="Generate and preflight a full canonical task PR body for the current branch.",
    )
    prepare_current.add_argument("--task-id", required=True)
    prepare_current.add_argument(
        "--contributor-id",
        required=True,
        help=(
            "Lowercased GitHub username when available; otherwise a stable "
            "maintainer-approved short id."
        ),
    )
    prepare_current.add_argument("--github-username", required=True)
    prepare_current.add_argument("--agent-id", required=True)
    prepare_current.add_argument(
        "--agent-tool",
        help="Human-readable agent tool label. Defaults from --agent-id when omitted.",
    )
    prepare_current.add_argument("--model-version")
    prepare_current.add_argument("--human-reviewer", required=True)
    prepare_current.add_argument("--slug")
    prepare_current.add_argument("--description")
    prepare_current.add_argument("--summary", required=True)
    prepare_current.add_argument("--changed-file", action="append", default=[])
    prepare_current.add_argument("--validation-command", action="append", default=[])
    prepare_current.add_argument("--scientific-claim-impact", default="No claim promotion.")
    prepare_current.add_argument(
        "--result-artifact-impact",
        default="No committed result artifacts changed.",
    )
    prepare_current.add_argument("--task-verdict", default="not_applicable")
    prepare_current.add_argument("--canonical-destination", default="none")
    prepare_current.add_argument("--review-tier", default="none")
    prepare_current.add_argument("--gate-a-status", default="not_applicable")
    prepare_current.add_argument("--gate-b-status", default="not_applicable")
    prepare_current.add_argument("--claim-impact", default="No claim promotion.")
    prepare_current.add_argument("--knowledge-impact", default="No knowledge promotion.")
    prepare_current.add_argument("--limitations-blockers", default="None for this PR shape.")
    prepare_current.add_argument("--base", default="main")
    prepare_current.add_argument("--body-file")
    prepare_current.add_argument("--body-only", action="store_true")
    prepare_current.add_argument("--root", default=".")

    create = subparsers.add_parser("create", help="Create a draft task PR using GitHub CLI.")
    create.add_argument("--branch", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--base", default="main")
    create.add_argument("--ready", action="store_true", help="Create a ready PR instead of a draft.")
    create.add_argument(
        "--ignore-suspicious-proxy",
        action="store_true",
        help="Clear only known loopback blocker proxy variables for the child gh command.",
    )

    ready = subparsers.add_parser("ready", help="Mark an existing draft task PR ready for review.")
    ready.add_argument("--pr", required=True)
    ready.add_argument(
        "--ignore-suspicious-proxy",
        action="store_true",
        help="Clear only known loopback blocker proxy variables for the child gh command.",
    )

    return parser


def command_scaffold(args: argparse.Namespace) -> int:
    _, _, task_branch_fn, task_pr_body_fn, task_title_fn, infer_agent_tool = _load_helper()
    branch = task_branch_fn(args.contributor_id, args.agent_id, args.task_id, args.slug)
    title = task_title_fn(args.task_id, args.description)
    body = task_pr_body_fn(
        task_id=args.task_id,
        branch=branch,
        title=title,
        contributor_id=args.contributor_id,
        github_username=args.github_username,
        agent_tool=args.agent_tool or infer_agent_tool(args.agent_id),
        human_reviewer=args.human_reviewer,
        summary=args.summary,
        changed_files=tuple(args.changed_file),
        validation_commands=tuple(args.validation_command),
        scientific_claim_impact=args.scientific_claim_impact,
        result_artifact_impact=args.result_artifact_impact,
        task_verdict=args.task_verdict,
        canonical_destination=args.canonical_destination,
        review_tier=args.review_tier,
        gate_a_status=args.gate_a_status,
        gate_b_status=args.gate_b_status,
        claim_impact=args.claim_impact,
        knowledge_impact=args.knowledge_impact,
        limitations_blockers=args.limitations_blockers,
        branch_pushed=args.branch_pushed,
        draft_pr_opened=args.draft_pr_opened,
        post_pr_review_run=args.post_pr_review_run,
        ready_for_review=args.ready_for_review,
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
    _, preflight_task_pr, _, _, _, _ = _load_helper()
    body_text = Path(args.body_file).read_text(encoding="utf-8-sig")
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


def _print_preflight_report(errors: tuple[str, ...], warnings: tuple[str, ...]) -> None:
    if errors:
        sys.stdout.write("Errors:\n")
        for item in errors:
            sys.stdout.write(f"- {item}\n")
    else:
        sys.stdout.write("Errors: none\n")
    if warnings:
        sys.stdout.write("Warnings:\n")
        for item in warnings:
            sys.stdout.write(f"- {item}\n")
    else:
        sys.stdout.write("Warnings: none\n")


def command_prepare_current(args: argparse.Namespace) -> int:
    prepare_current_task_pr, _, _, _, _, _ = _load_helper()
    prepared = prepare_current_task_pr(
        Path(args.root),
        task_id=args.task_id,
        contributor_id=args.contributor_id,
        github_username=args.github_username,
        agent_id=args.agent_id,
        human_reviewer=args.human_reviewer,
        summary=args.summary,
        slug=args.slug,
        description=args.description,
        changed_files=tuple(args.changed_file),
        validation_commands=tuple(args.validation_command),
        scientific_claim_impact=args.scientific_claim_impact,
        result_artifact_impact=args.result_artifact_impact,
        task_verdict=args.task_verdict,
        canonical_destination=args.canonical_destination,
        review_tier=args.review_tier,
        gate_a_status=args.gate_a_status,
        gate_b_status=args.gate_b_status,
        claim_impact=args.claim_impact,
        knowledge_impact=args.knowledge_impact,
        limitations_blockers=args.limitations_blockers,
        model_version=args.model_version,
        base_ref=args.base,
        agent_tool=args.agent_tool,
        local_artifact_paths=(args.body_file,) if args.body_file else (),
    )
    if args.body_file:
        Path(args.body_file).write_text(prepared.body, encoding="utf-8")
    sys.stdout.write(f"Task: {prepared.task_id}\n")
    sys.stdout.write(f"Task file: {prepared.task_file.as_posix()}\n")
    sys.stdout.write(f"Current branch: {prepared.current_branch}\n")
    sys.stdout.write(f"Expected branch: {prepared.expected_branch}\n")
    sys.stdout.write(f"Title: {prepared.title}\n")
    if args.body_file:
        sys.stdout.write(f"Body file: {Path(args.body_file).as_posix()}\n")
    sys.stdout.write("Changed files:\n")
    if prepared.changed_files:
        for item in prepared.changed_files:
            sys.stdout.write(f"- {item}\n")
    else:
        sys.stdout.write("- <none detected>\n")
    sys.stdout.write("Validation commands:\n")
    if prepared.validation_commands:
        for command in prepared.validation_commands:
            sys.stdout.write(f"- {command}\n")
    else:
        sys.stdout.write("- <none detected>\n")
    _print_preflight_report(
        prepared.preflight.errors,
        prepared.preflight.warnings,
    )
    if args.body_only:
        sys.stdout.write("\n")
        sys.stdout.write(prepared.body)
    return 0 if prepared.preflight.ok else 1


def _quote_command(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def _print_manual_create_commands(args: argparse.Namespace) -> None:
    command = [
        "gh",
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
    sys.stderr.write("Manual publication commands for a maintainer console:\n")
    sys.stderr.write(f"- {_quote_command(['git', 'push', 'origin', args.branch])}\n")
    sys.stderr.write(f"- {_quote_command(command)}\n")
    sys.stderr.write("- python3 scripts/apl_review_pr.py --pr <number>\n")
    sys.stderr.write("- gh pr ready <number>\n")


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
        _print_manual_create_commands(args)
        return 127
    proxy_names = suspicious_proxy_env_names()
    if proxy_names:
        if args.ignore_suspicious_proxy:
            sys.stderr.write(
                "Clearing known local blocker proxy variables for child gh command: "
                + ", ".join(proxy_names)
                + ".\n"
            )
        else:
            sys.stderr.write(
                "Warning: proxy env may block GitHub CLI calls: "
                + ", ".join(proxy_names)
                + ". Retry with --ignore-suspicious-proxy if gh reports a 127.0.0.1 connection error.\n"
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
        env=env_with_discovered_tool_paths(
            clear_suspicious_proxy=args.ignore_suspicious_proxy,
        ),
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        _print_manual_create_commands(args)
    return completed.returncode


def _print_manual_ready_command(args: argparse.Namespace) -> None:
    sys.stderr.write("Manual ready-for-review command for a maintainer console:\n")
    sys.stderr.write(f"- {_quote_command(['gh', 'pr', 'ready', args.pr])}\n")


def command_ready(args: argparse.Namespace) -> int:
    from physics_lab.registry.pr_capability import (
        env_with_discovered_tool_paths,
        find_gh_path,
        suspicious_proxy_env_names,
    )

    gh_path = find_gh_path()
    if gh_path is None:
        sys.stderr.write(
            "Cannot mark PR ready directly: GitHub CLI `gh` is not installed or not discoverable.\n"
        )
        _print_manual_ready_command(args)
        return 127
    proxy_names = suspicious_proxy_env_names()
    if proxy_names:
        if args.ignore_suspicious_proxy:
            sys.stderr.write(
                "Clearing known local blocker proxy variables for child gh command: "
                + ", ".join(proxy_names)
                + ".\n"
            )
        else:
            sys.stderr.write(
                "Warning: proxy env may block GitHub CLI calls: "
                + ", ".join(proxy_names)
                + ". Retry with --ignore-suspicious-proxy if gh reports a 127.0.0.1 connection error.\n"
            )
    completed = subprocess.run(
        [gh_path, "pr", "ready", args.pr],
        check=False,
        text=True,
        capture_output=True,
        env=env_with_discovered_tool_paths(
            clear_suspicious_proxy=args.ignore_suspicious_proxy,
        ),
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        _print_manual_ready_command(args)
    return completed.returncode


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "scaffold":
        return command_scaffold(args)
    if args.command == "preflight":
        return command_preflight(args)
    if args.command == "prepare-current":
        return command_prepare_current(args)
    if args.command == "create":
        return command_create(args)
    if args.command == "ready":
        return command_ready(args)
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
