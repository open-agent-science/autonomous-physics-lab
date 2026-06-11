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

from physics_lab._runtime import (  # noqa: E402
    MINIMUM_PYTHON_DISPLAY,
    is_supported as _python_is_supported,
    unsupported_message as _python_unsupported_message,
)
from physics_lab.registry.pr_capability import check_pr_capability  # noqa: E402
from physics_lab.registry.review_worktree_gc import (  # noqa: E402
    review_worktree_disk_report,
)


PYTHON_MODULE_CHECKS = ("pip", "pytest", "ruff", "yaml")


@dataclass(frozen=True)
class PythonRuntimeReport:
    executable: str
    version: str
    platform: str
    modules: dict[str, bool]
    minimum_version: str
    meets_minimum: bool
    remediation: str | None


@dataclass(frozen=True)
class PytestRuntimeProbeReport:
    xdist_available: bool
    default_xdist_ok: bool
    unique_system_basetemp_xdist_ok: bool | None
    workspace_basetemp_xdist_ok: bool | None
    recommendation: str
    details: str


@dataclass(frozen=True)
class WorktreeRuntimePreflightReport:
    root: str
    git_dir: str | None
    git_common_dir: str | None
    is_git_worktree: bool
    repository_venv_python: str | None
    active_python_matches_repository_venv: bool | None
    system_temp_dir: str
    system_temp_accessible: bool
    recommended_pytest_basetemp: str
    git_index_lock_path: str | None
    git_index_parent_writable: bool | None
    git_index_lock_exists: bool | None
    recommendations: tuple[str, ...]


@dataclass(frozen=True)
class AgentDoctorReport:
    python: PythonRuntimeReport
    pr_capability: dict[str, object]
    review_worktrees: dict[str, object] | None = None
    pytest_runtime: PytestRuntimeProbeReport | None = None
    worktree_runtime: WorktreeRuntimePreflightReport | None = None


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
    parser.add_argument(
        "--worktree-runtime-preflight",
        action="store_true",
        help=(
            "Run read-only worktree/runtime diagnostics for repository venv, "
            "temp path, and git index-lock troubleshooting."
        ),
    )
    return parser


def python_runtime_report() -> PythonRuntimeReport:
    modules = {
        name: importlib.util.find_spec(name) is not None
        for name in PYTHON_MODULE_CHECKS
    }
    meets_minimum = _python_is_supported()
    return PythonRuntimeReport(
        executable=sys.executable,
        version=sys.version.split()[0],
        platform=platform.platform(),
        modules=modules,
        minimum_version=MINIMUM_PYTHON_DISPLAY,
        meets_minimum=meets_minimum,
        remediation=None if meets_minimum else _python_unsupported_message(),
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


def _git_output(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _resolve_git_path(root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def _venv_python_candidates(base: Path) -> tuple[Path, ...]:
    return (
        base / ".venv" / "Scripts" / "python.exe",
        base / ".venv" / "bin" / "python",
    )


def _find_repository_venv_python(root: Path, git_common_dir: Path | None) -> Path | None:
    search_roots: list[Path] = [root]
    if git_common_dir is not None and git_common_dir.name == ".git":
        search_roots.append(git_common_dir.parent)
    for search_root in search_roots:
        for candidate in _venv_python_candidates(search_root):
            if candidate.exists():
                return candidate.resolve()
    return None


def _path_matches(left: Path | None, right: str) -> bool | None:
    if left is None:
        return None
    try:
        return left.resolve() == Path(right).resolve()
    except OSError:
        return str(left) == right


def _default_pytest_basetemp_root(root: Path) -> Path:
    return root / ".pytest-basetemp"


def worktree_runtime_preflight(root: Path) -> WorktreeRuntimePreflightReport:
    """Collect read-only diagnostics for task worktree runtime health."""
    root = root.resolve()
    git_dir = _resolve_git_path(root, _git_output(root, "rev-parse", "--git-dir"))
    git_common_dir = _resolve_git_path(
        root,
        _git_output(root, "rev-parse", "--git-common-dir"),
    )
    is_git_worktree = (
        git_dir is not None
        and git_common_dir is not None
        and git_dir.resolve() != git_common_dir.resolve()
    )
    repository_venv_python = _find_repository_venv_python(root, git_common_dir)
    active_matches = _path_matches(repository_venv_python, sys.executable)

    system_temp_dir = Path(tempfile.gettempdir())
    system_temp_accessible = os.access(system_temp_dir, os.R_OK | os.W_OK | os.X_OK)
    recommended_basetemp_root = _default_pytest_basetemp_root(root)
    recommended_pytest_basetemp = str(
        recommended_basetemp_root / "session-<unique-id>"
        if recommended_basetemp_root.name == ".pytest-basetemp"
        else recommended_basetemp_root / "apl-pytest-<unique-id>"
    )

    git_index_lock_path = git_dir / "index.lock" if git_dir is not None else None
    git_index_parent_writable = (
        os.access(git_index_lock_path.parent, os.W_OK)
        if git_index_lock_path is not None
        else None
    )
    git_index_lock_exists = (
        git_index_lock_path.exists() if git_index_lock_path is not None else None
    )

    recommendations: list[str] = []
    if repository_venv_python is None:
        recommendations.append(
            "Repository .venv Python was not found from this checkout; use the intended "
            "Python explicitly or create the project venv before validation."
        )
    elif active_matches is False:
        recommendations.append(
            f"Run validation with repository Python: {repository_venv_python}"
        )
    if not system_temp_accessible:
        recommendations.append(
            "System temp is not fully accessible; run pytest with "
            f"`--basetemp={recommended_pytest_basetemp}` or request permission for "
            "the targeted pytest command."
        )
    if git_index_parent_writable is False:
        recommendations.append(
            "Git index metadata is not writable from this sandbox. If `git add` or "
            "`git commit` fails with index.lock permission errors, rerun the same "
            "git command with protocol-approved escalation; do not delete locks "
            "unless a stale lock is separately verified."
        )
    if git_index_lock_exists:
        recommendations.append(
            "A git index.lock file is present; verify whether a git process is active "
            "before treating it as stale."
        )
    if not recommendations:
        recommendations.append("No worktree runtime blockers detected by read-only checks.")

    return WorktreeRuntimePreflightReport(
        root=str(root),
        git_dir=str(git_dir) if git_dir is not None else None,
        git_common_dir=str(git_common_dir) if git_common_dir is not None else None,
        is_git_worktree=is_git_worktree,
        repository_venv_python=(
            str(repository_venv_python) if repository_venv_python is not None else None
        ),
        active_python_matches_repository_venv=active_matches,
        system_temp_dir=str(system_temp_dir),
        system_temp_accessible=system_temp_accessible,
        recommended_pytest_basetemp=recommended_pytest_basetemp,
        git_index_lock_path=(
            str(git_index_lock_path) if git_index_lock_path is not None else None
        ),
        git_index_parent_writable=git_index_parent_writable,
        git_index_lock_exists=git_index_lock_exists,
        recommendations=tuple(recommendations),
    )


def build_report(
    root: Path,
    *,
    require_gh_auth: bool = True,
    probe_pytest_runtime: bool = False,
    worktree_runtime_preflight_enabled: bool = False,
) -> AgentDoctorReport:
    pr_report = check_pr_capability(root, require_gh_auth=require_gh_auth)
    return AgentDoctorReport(
        python=python_runtime_report(),
        pr_capability=asdict(pr_report),
        review_worktrees=asdict(review_worktree_disk_report(root)),
        pytest_runtime=pytest_runtime_probe(root) if probe_pytest_runtime else None,
        worktree_runtime=(
            worktree_runtime_preflight(root)
            if worktree_runtime_preflight_enabled
            else None
        ),
    )


def _print_human(report: AgentDoctorReport) -> None:
    print("APL agent doctor")
    print("Python")
    print(f"- executable: {report.python.executable}")
    print(f"- version: {report.python.version}")
    print(f"- minimum required: {report.python.minimum_version}")
    print(f"- meets minimum: {report.python.meets_minimum}")
    print(f"- platform: {report.python.platform}")
    print("- modules:")
    for name, present in report.python.modules.items():
        status = "found" if present else "missing"
        print(f"  - {name}: {status}")
    if not report.python.meets_minimum and report.python.remediation:
        print("- remediation:")
        for line in report.python.remediation.splitlines():
            print(f"    {line}")

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

    if report.review_worktrees is not None:
        rw = report.review_worktrees
        free_bytes = rw.get("free_bytes")
        free_label = (
            f"{int(free_bytes) // (1024 * 1024)} MiB"
            if isinstance(free_bytes, int) and free_bytes >= 0
            else "unknown"
        )
        print("Review worktrees")
        print(f"- count under .worktrees/_reviews: {rw.get('review_worktree_count')}")
        print(f"- free disk: {free_label}")
        if rw.get("recommend_gc"):
            for reason in rw.get("reasons") or ():
                print(f"- buildup: {reason}")
            print(
                "- recommendation: run `python3 scripts/apl_worktree_gc.py` "
                "(add --dry-run first) to reclaim abandoned review worktrees."
            )
        else:
            print("- recommendation: none (no review-worktree buildup detected)")

    if report.pytest_runtime is not None:
        probe = report.pytest_runtime
        print("Pytest runtime probe")
        print(f"- xdist available: {probe.xdist_available}")
        print(f"- default xdist ok: {probe.default_xdist_ok}")
        print(f"- unique system basetemp xdist ok: {probe.unique_system_basetemp_xdist_ok}")
        print(f"- workspace basetemp xdist ok: {probe.workspace_basetemp_xdist_ok}")
        print(f"- recommendation: {probe.recommendation}")
        print(f"- details: {probe.details}")

    if report.worktree_runtime is not None:
        probe = report.worktree_runtime
        print("Worktree runtime preflight")
        print(f"- root: {probe.root}")
        print(f"- git dir: {probe.git_dir or 'not found'}")
        print(f"- git common dir: {probe.git_common_dir or 'not found'}")
        print(f"- git worktree: {probe.is_git_worktree}")
        print(f"- repository venv python: {probe.repository_venv_python or 'not found'}")
        print(
            "- active python matches repository venv: "
            f"{probe.active_python_matches_repository_venv}"
        )
        print(f"- system temp dir: {probe.system_temp_dir}")
        print(f"- system temp accessible: {probe.system_temp_accessible}")
        print(f"- recommended pytest basetemp: {probe.recommended_pytest_basetemp}")
        print(f"- git index.lock path: {probe.git_index_lock_path or 'not found'}")
        print(f"- git index parent writable: {probe.git_index_parent_writable}")
        print(f"- git index.lock exists: {probe.git_index_lock_exists}")
        print("Recommendations:")
        for item in probe.recommendations:
            print(f"- {item}")


def main() -> int:
    args = build_parser().parse_args()
    report = build_report(
        Path(args.root),
        require_gh_auth=not args.no_gh_auth_check,
        probe_pytest_runtime=args.probe_pytest_runtime,
        worktree_runtime_preflight_enabled=args.worktree_runtime_preflight,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
