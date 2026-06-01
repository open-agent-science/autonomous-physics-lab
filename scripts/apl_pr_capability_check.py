#!/usr/bin/env python3
"""Check whether this environment can create a GitHub pull request."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.pr_capability import check_pr_capability  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--no-gh-auth-check",
        action="store_true",
        help="Only check for `gh` or token presence; skip `gh auth status`.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = check_pr_capability(
        Path(args.root),
        require_gh_auth=not args.no_gh_auth_check,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        print("PR capability check")
        print(f"- gh path: {report.gh_path or 'not found'}")
        print(f"- git path: {report.git_path or 'not found'}")
        token_label = ", ".join(report.token_env_names) if report.token_env_names else "none"
        print(f"- token fallback: {token_label}")
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
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
