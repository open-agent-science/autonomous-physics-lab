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
worktree_runtime_preflight = MODULE.worktree_runtime_preflight

RUNTIME_SPEC = importlib.util.spec_from_file_location(
    "physics_lab_runtime",
    Path(__file__).resolve().parents[1] / "physics_lab" / "_runtime.py",
)
assert RUNTIME_SPEC is not None and RUNTIME_SPEC.loader is not None
RUNTIME_MODULE = importlib.util.module_from_spec(RUNTIME_SPEC)
sys.modules[RUNTIME_SPEC.name] = RUNTIME_MODULE
RUNTIME_SPEC.loader.exec_module(RUNTIME_MODULE)


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


def test_agent_doctor_reports_python_minimum_version(tmp_path: Path) -> None:
    report = build_report(tmp_path, require_gh_auth=False)

    assert report.python.minimum_version == "3.11"
    expected_supported = RUNTIME_MODULE.is_supported(sys.version_info)
    assert report.python.meets_minimum is expected_supported
    if expected_supported:
        assert report.python.remediation is None
    else:
        assert report.python.remediation is not None


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
    assert '"worktree_runtime": null' in result.stdout


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
    assert report.worktree_runtime is None


def test_worktree_runtime_preflight_detects_repository_venv(
    tmp_path: Path,
    monkeypatch,
) -> None:
    venv_bin = tmp_path / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
    venv_bin.mkdir(parents=True)
    python_name = "python.exe" if sys.platform == "win32" else "python"
    repo_python = venv_bin / python_name
    repo_python.write_text("", encoding="utf-8")
    monkeypatch.setattr(MODULE.sys, "executable", str(repo_python))
    monkeypatch.setattr(MODULE, "_git_output", lambda root, *args: None)

    report = worktree_runtime_preflight(tmp_path)

    assert report.repository_venv_python == str(repo_python.resolve())
    assert report.active_python_matches_repository_venv is True
    assert report.git_index_lock_path is None


def test_worktree_runtime_preflight_finds_common_dir_venv_for_worktree(
    tmp_path: Path,
    monkeypatch,
) -> None:
    main = tmp_path / "main"
    worktree = tmp_path / "worktree"
    git_dir = main / ".git" / "worktrees" / "worktree"
    common_dir = main / ".git"
    venv_bin = main / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
    git_dir.mkdir(parents=True)
    common_dir.mkdir(exist_ok=True)
    worktree.mkdir()
    venv_bin.mkdir(parents=True)
    python_name = "python.exe" if sys.platform == "win32" else "python"
    repo_python = venv_bin / python_name
    repo_python.write_text("", encoding="utf-8")

    def fake_git_output(root: Path, *args: str) -> str | None:
        if args == ("rev-parse", "--git-dir"):
            return str(git_dir)
        if args == ("rev-parse", "--git-common-dir"):
            return str(common_dir)
        return None

    monkeypatch.setattr(MODULE, "_git_output", fake_git_output)
    monkeypatch.setattr(MODULE.sys, "executable", str(worktree / "python.exe"))

    report = worktree_runtime_preflight(worktree)

    assert report.is_git_worktree is True
    assert report.repository_venv_python == str(repo_python.resolve())
    assert report.active_python_matches_repository_venv is False
    assert any("Run validation with repository Python" in item for item in report.recommendations)


def test_worktree_runtime_preflight_recommends_repo_local_pytest_basetemp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(MODULE, "_git_output", lambda root, *args: None)

    report = worktree_runtime_preflight(tmp_path)

    assert report.recommended_pytest_basetemp.startswith(
        str((tmp_path / ".pytest-basetemp").resolve())
    )


def test_agent_doctor_cli_json_includes_worktree_runtime_preflight() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_agent_doctor.py",
            "--json",
            "--no-gh-auth-check",
            "--worktree-runtime-preflight",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert '"worktree_runtime"' in result.stdout
    assert '"recommended_pytest_basetemp"' in result.stdout


def test_agent_doctor_reports_review_worktree_diagnostic(tmp_path: Path) -> None:
    report = build_report(tmp_path, require_gh_auth=False)

    assert report.review_worktrees is not None
    rw = report.review_worktrees
    assert set(rw).issuperset(
        {"review_worktree_count", "free_bytes", "recommend_gc", "reasons"}
    )
    # A non-review temp dir has no review worktrees. It may still recommend GC
    # when the containing volume is below the doctor free-disk threshold.
    assert rw["review_worktree_count"] == 0
    if rw["recommend_gc"]:
        assert any("free disk" in reason for reason in rw["reasons"])
    else:
        assert rw["reasons"] == ()


def test_agent_doctor_cli_json_includes_review_worktrees() -> None:
    import json

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--json", "--no-gh-auth-check"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert "review_worktrees" in payload
    assert "review_worktree_count" in payload["review_worktrees"]
