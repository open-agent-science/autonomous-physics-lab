#!/usr/bin/env python3
"""Check whether this environment can create a GitHub pull request."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.pr_capability import (  # noqa: E402
    CANONICAL_GITHUB_REPOSITORY,
    check_pr_capability,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--repository",
        default=CANONICAL_GITHUB_REPOSITORY,
        help="Canonical OWNER/REPO whose authenticated viewer permission is checked.",
    )
    parser.add_argument(
        "--branch",
        help="Task branch for an exact fork command pack; defaults to the current branch.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--no-gh-auth-check",
        action="store_true",
        help="Only check for `gh` or token presence; skip `gh auth status`.",
    )
    parser.add_argument(
        "--no-repository-permission-check",
        action="store_true",
        help="Skip viewerPermission lookup and report the publication route as not_checked.",
    )
    parser.add_argument(
        "--agent-sandbox",
        action="store_true",
        help=(
            "Declare that this agent runtime may isolate the host credential store. "
            "Use for Claude or other sandboxes without an auto-detected marker."
        ),
    )
    return parser


def _render_argv(command: tuple[str, ...]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def main() -> int:
    args = build_parser().parse_args()
    report = check_pr_capability(
        Path(args.root),
        require_gh_auth=not args.no_gh_auth_check,
        check_repository_permission=not args.no_repository_permission_check,
        agent_sandbox=args.agent_sandbox,
        repository=args.repository,
        branch=args.branch,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        print("PR capability check")
        print(f"- gh path: {report.gh_path or 'not found'}")
        print(f"- git path: {report.git_path or 'not found'}")
        print(f"- gh auth state: {report.gh_auth_state}")
        print(f"- repository: {report.repository}")
        print(
            "- repository permission: "
            f"{report.repository_permission or 'unknown'}"
        )
        print(f"- publication route: {report.publication_route}")
        print(f"- authenticated login: {report.authenticated_login or 'unknown'}")
        print(f"- task branch: {report.branch or 'unknown'}")
        print(f"- agent sandbox detected: {report.sandbox_detected}")
        token_label = ", ".join(report.token_env_names) if report.token_env_names else "none"
        print(f"- token fallback: {token_label}")
        sandbox_label = (
            ", ".join(report.sandbox_env_names)
            if report.sandbox_env_names
            else "none"
        )
        print(f"- agent sandbox markers: {sandbox_label}")
        proxy_label = (
            ", ".join(report.suspicious_proxy_env_names)
            if report.suspicious_proxy_env_names
            else "none"
        )
        print(f"- suspicious proxy env: {proxy_label}")
        if report.errors:
            print("Errors:")
            for item in report.errors:
                print(f"- {item}")
        else:
            print("Errors: none")
        if report.warnings:
            print("Warnings:")
            for item in report.warnings:
                print(f"- {item}")
        else:
            print("Warnings: none")
        if report.fork_commands:
            print(
                "Fork publication commands "
                "(after preparing `.apl-pr-body.md` with the task PR helper):"
            )
            for command in report.fork_commands:
                print(f"- {_render_argv(command)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
