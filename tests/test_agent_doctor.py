from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "apl_agent_doctor.py"
SPEC = importlib.util.spec_from_file_location("apl_agent_doctor", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
build_report = MODULE.build_report
pytest_runtime_probe = MODULE.pytest_runtime_probe


def _write_probe_target(root: Path) -> None:
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_agent_doctor.py").write_text(
        "def test_agent_doctor_builds_report_without_network_auth_check(tmp_path):\n"
        "    assert tmp_path.exists()\n",
        encoding="utf-8",
    )


def test_agent_doctor_builds_report_without_network_auth_check(tmp_path: Path) -> None:
    report = build_report(tmp_path, require_gh_auth=False)

    assert report.python.executable
    assert report.python.modules["pip"] in (True, False)
    assert "errors" in report.pr_capability
    assert "warnings" in report.pr_capability
    assert "gh_path" in report.pr_capability
    assert "git_path" in report.pr_capability


def test_agent_doctor_cli_json_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_agent_doctor.py",
            "--json",
            "--no-gh-auth-check",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert '"python"' in result.stdout
    assert '"pr_capability"' in result.stdout
    assert '"pytest_runtime": null' in result.stdout


def test_pytest_runtime_probe_reports_workspace_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_probe_target(tmp_path)
    calls: list[Path | None] = []

    def fake_run(root: Path, probe_test: Path, *, basetemp: Path | None):
        calls.append(basetemp)
        return subprocess.CompletedProcess(
            args=[],
            returncode=0 if len(calls) == 3 else 1,
            stdout="workspace fallback passed" if len(calls) == 3 else "probe failed",
            stderr="",
        )

    monkeypatch.setattr(MODULE, "_run_pytest_probe", fake_run)

    report = pytest_runtime_probe(tmp_path)

    assert report.xdist_available is True
    assert report.default_xdist_ok is False
    assert report.unique_system_basetemp_xdist_ok is False
    assert report.workspace_basetemp_xdist_ok is True
    assert "--basetemp=.pytest-basetemp" in report.recommendation


def test_pytest_runtime_probe_prefers_unique_system_temp_fallback(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_probe_target(tmp_path)
    calls: list[Path | None] = []

    def fake_run(root: Path, probe_test: Path, *, basetemp: Path | None):
        calls.append(basetemp)
        return subprocess.CompletedProcess(
            args=[],
            returncode=0 if len(calls) == 2 else 1,
            stdout="unique system temp passed" if len(calls) == 2 else "default failed",
            stderr="",
        )

    monkeypatch.setattr(MODULE, "_run_pytest_probe", fake_run)

    report = pytest_runtime_probe(tmp_path)

    assert report.default_xdist_ok is False
    assert report.unique_system_basetemp_xdist_ok is True
    assert report.workspace_basetemp_xdist_ok is None
    assert "<short-temp>/apl-pytest-<unique-id>" in report.recommendation


def test_agent_doctor_build_report_skips_runtime_probe_by_default(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def unexpected_probe(root: Path):
        raise AssertionError("runtime probe should stay opt-in")

    monkeypatch.setattr(MODULE, "pytest_runtime_probe", unexpected_probe)

    report = build_report(tmp_path, require_gh_auth=False)

    assert report.pytest_runtime is None
