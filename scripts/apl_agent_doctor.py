#!/usr/bin/env python3
"""Diagnose local agent runtime and PR-publication readiness."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid

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
class PytestRuntimeProbeReport:
    xdist_available: bool
    default_xdist_ok: bool
    unique_system_basetemp_xdist_ok: bool | None
    workspace_basetemp_xdist_ok: bool | None
    recommendation: str
    details: str


@dataclass(frozen=True)
class AgentDoctorReport:
    python: PythonRuntimeReport
    pr_capability: dict[str, object]
    pytest_runtime: PytestRuntimeProbeReport | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--no-gh-auth-check",
        action="store_true",
        help="Skip `gh auth status`; useful before logging in or in offline environments.",
    )
    parser.add_argument(
        "--probe-pytest-runtime",
        action="store_true",
        help=(
            "Run a disposable xdist/tmp_path probe with unique system-temp and "
            "workspace-local fallback paths."
        ),
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


def _run_pytest_probe(
    root: Path,
    probe_target: str,
    *,
    basetemp: Path | None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-n",
        "2",
        "--dist",
        "loadfile",
        "-q",
    ]
    if basetemp is not None:
        command.extend(["--basetemp", str(basetemp)])
    command.append(probe_target)
    return subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _probe_details(result: subprocess.CompletedProcess[str]) -> str:
    lines = [line.strip() for line in (result.stdout + result.stderr).splitlines() if line.strip()]
    return lines[-1] if lines else f"pytest exited with status {result.returncode}"


def pytest_runtime_probe(root: Path) -> PytestRuntimeProbeReport:
    """Check default Windows-like xdist execution and a local basetemp fallback."""
    root = root.resolve()
    xdist_available = importlib.util.find_spec("xdist") is not None
    if not xdist_available:
        return PytestRuntimeProbeReport(
            xdist_available=False,
            default_xdist_ok=False,
            unique_system_basetemp_xdist_ok=None,
            workspace_basetemp_xdist_ok=None,
            recommendation="Install the development extras before running parallel pytest.",
            details="pytest-xdist is not importable.",
        )

    probe_target = (
        "tests/test_agent_doctor.py::"
        "test_agent_doctor_builds_report_without_network_auth_check"
    )
    if not (root / "tests" / "test_agent_doctor.py").is_file():
        return PytestRuntimeProbeReport(
            xdist_available=True,
            default_xdist_ok=False,
            unique_system_basetemp_xdist_ok=None,
            workspace_basetemp_xdist_ok=None,
            recommendation="Run the probe from an APL repository checkout.",
            details="tests/test_agent_doctor.py was not found.",
        )

    try:
        default_result = _run_pytest_probe(root, probe_target, basetemp=None)
        if default_result.returncode == 0:
            return PytestRuntimeProbeReport(
                xdist_available=True,
                default_xdist_ok=True,
                unique_system_basetemp_xdist_ok=None,
                workspace_basetemp_xdist_ok=None,
                recommendation="Use the default parallel pytest path.",
                details=_probe_details(default_result),
            )

        default_short_root = "C:/tmp" if platform.system() == "Windows" else tempfile.gettempdir()
        short_root = Path(os.environ.get("APL_PYTEST_BASETEMP_ROOT", default_short_root))
        short_root.mkdir(parents=True, exist_ok=True)
        unique_system_basetemp = short_root / f"apl-pytest-{uuid.uuid4().hex[:12]}"
        system_result = _run_pytest_probe(
            root,
            probe_target,
            basetemp=unique_system_basetemp,
        )
        system_ok = system_result.returncode == 0
        shutil.rmtree(unique_system_basetemp, ignore_errors=True)
        if system_ok:
            return PytestRuntimeProbeReport(
                xdist_available=True,
                default_xdist_ok=False,
                unique_system_basetemp_xdist_ok=True,
                workspace_basetemp_xdist_ok=None,
                recommendation=(
                    "Use parallel pytest with a unique short system-temp "
                    "`--basetemp=<short-temp>/apl-pytest-<unique-id>` for this session."
                ),
                details=(
                    f"default: {_probe_details(default_result)}; "
                    f"unique system temp: {_probe_details(system_result)}"
                ),
            )

        workspace_basetemp = root / ".pytest-basetemp" / f"session-{uuid.uuid4().hex[:12]}"
        workspace_result = _run_pytest_probe(
            root,
            probe_target,
            basetemp=workspace_basetemp,
        )
        workspace_ok = workspace_result.returncode == 0
        shutil.rmtree(workspace_basetemp, ignore_errors=True)
        recommendation = (
            "Use parallel pytest with a unique "
            "`--basetemp=.pytest-basetemp/session-<unique-id>` for this session."
            if workspace_ok
            else "Use targeted `-n0` debugging and delegate broad validation to CI."
        )
        return PytestRuntimeProbeReport(
            xdist_available=True,
            default_xdist_ok=False,
            unique_system_basetemp_xdist_ok=False,
            workspace_basetemp_xdist_ok=workspace_ok,
            recommendation=recommendation,
            details=(
                f"default: {_probe_details(default_result)}; "
                f"unique system temp: {_probe_details(system_result)}; "
                f"workspace fallback: {_probe_details(workspace_result)}"
            ),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return PytestRuntimeProbeReport(
            xdist_available=True,
            default_xdist_ok=False,
            unique_system_basetemp_xdist_ok=False,
            workspace_basetemp_xdist_ok=False,
            recommendation="Use targeted `-n0` debugging and delegate broad validation to CI.",
            details=f"{type(exc).__name__}: {exc}",
        )


def build_report(
    root: Path,
    *,
    require_gh_auth: bool = True,
    probe_pytest_runtime: bool = False,
) -> AgentDoctorReport:
    pr_report = check_pr_capability(root, require_gh_auth=require_gh_auth)
    return AgentDoctorReport(
        python=python_runtime_report(),
        pr_capability=asdict(pr_report),
        pytest_runtime=pytest_runtime_probe(root) if probe_pytest_runtime else None,
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

    if report.pytest_runtime is not None:
        probe = report.pytest_runtime
        print("Pytest runtime probe")
        print(f"- xdist available: {probe.xdist_available}")
        print(f"- default xdist ok: {probe.default_xdist_ok}")
        print(f"- unique system basetemp xdist ok: {probe.unique_system_basetemp_xdist_ok}")
        print(f"- workspace basetemp xdist ok: {probe.workspace_basetemp_xdist_ok}")
        print(f"- recommendation: {probe.recommendation}")
        print(f"- details: {probe.details}")


def main() -> int:
    args = build_parser().parse_args()
    report = build_report(
        Path(args.root),
        require_gh_auth=not args.no_gh_auth_check,
        probe_pytest_runtime=args.probe_pytest_runtime,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
