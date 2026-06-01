#!/usr/bin/env python3
"""Diagnose local agent runtime and PR-publication readiness."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import importlib.util
import json
from pathlib import Path
import platform
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.registry.pr_capability import check_pr_capability  # noqa: E402


PYTHON_MODULE_CHECKS = ("pip", "pytest", "ruff", "yaml")


@dataclass(frozen=True)
class PythonRuntimeReport:
    executable: str
    version: str
    platform: str
    modules: dict[str, bool]


@dataclass(frozen=True)
class AgentDoctorReport:
    python: PythonRuntimeReport
    pr_capability: dict[str, object]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--no-gh-auth-check",
        action="store_true",
        help="Skip `gh auth status`; useful before logging in or in offline environments.",
    )
    return parser


def python_runtime_report() -> PythonRuntimeReport:
    modules = {
        name: importlib.util.find_spec(name) is not None
        for name in PYTHON_MODULE_CHECKS
    }
    return PythonRuntimeReport(
        executable=sys.executable,
        version=sys.version.split()[0],
        platform=platform.platform(),
        modules=modules,
    )


def build_report(root: Path, *, require_gh_auth: bool = True) -> AgentDoctorReport:
    pr_report = check_pr_capability(root, require_gh_auth=require_gh_auth)
    return AgentDoctorReport(
        python=python_runtime_report(),
        pr_capability=asdict(pr_report),
    )


def _print_human(report: AgentDoctorReport) -> None:
    print("APL agent doctor")
    print("Python")
    print(f"- executable: {report.python.executable}")
    print(f"- version: {report.python.version}")
    print(f"- platform: {report.python.platform}")
    print("- modules:")
    for name, present in report.python.modules.items():
        status = "found" if present else "missing"
        print(f"  - {name}: {status}")

    pr = report.pr_capability
    print("PR publication")
    print(f"- gh path: {pr.get('gh_path') or 'not found'}")
    print(f"- git path: {pr.get('git_path') or 'not found'}")
    tokens = pr.get("token_env_names") or ()
    token_label = ", ".join(tokens) if tokens else "none"
    print(f"- token fallback: {token_label}")
    proxy_names = pr.get("suspicious_proxy_env_names") or ()
    proxy_label = ", ".join(proxy_names) if proxy_names else "none"
    print(f"- suspicious proxy env: {proxy_label}")

    warnings = pr.get("warnings") or ()
    errors = pr.get("errors") or ()
    if errors:
        print("Errors:")
        for item in errors:
            print(f"- {item}")
    else:
        print("Errors: none")
    if warnings:
        print("Warnings:")
        for item in warnings:
            print(f"- {item}")
    else:
        print("Warnings: none")


def main() -> int:
    args = build_parser().parse_args()
    report = build_report(
        Path(args.root),
        require_gh_auth=not args.no_gh_auth_check,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
