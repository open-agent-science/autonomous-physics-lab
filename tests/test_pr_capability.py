from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

from physics_lab.registry.pr_capability import (
    check_pr_capability,
    env_with_discovered_tool_paths,
    find_git_path,
    suspicious_proxy_env_names,
    without_suspicious_proxy_env,
)
from physics_lab.registry.pr_capability import (
    env_with_overrides as pr_capability_env_with_overrides,
)
from physics_lab.registry.subprocess_env import env_with_overrides


def _write_gh_stub(bin_dir: Path, *, exit_code: int = 0) -> Path:
    """Create a tiny cross-platform gh stub and return its executable path."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        stub = bin_dir / "gh.cmd"
        stub.write_text(f"@echo off\r\nexit /b {exit_code}\r\n", encoding="utf-8")
        return stub

    stub = bin_dir / "gh"
    stub.write_text(
        dedent(
            f"""\
            #!/bin/sh
            exit {exit_code}
            """
        ),
        encoding="utf-8",
    )
    stub.chmod(0o755)
    return stub


def test_pr_capability_is_advisory_without_gh_or_token(tmp_path: Path) -> None:
    report = check_pr_capability(
        tmp_path,
        env={},
        discover_gh=False,
    )

    assert report.ok
    assert report.errors == ()
    assert any("Direct PR creation is not available" in item for item in report.warnings)


def test_pr_capability_accepts_token_fallback_without_gh(tmp_path: Path) -> None:
    report = check_pr_capability(
        tmp_path,
        env={"GITHUB_TOKEN": "present"},
        discover_gh=False,
    )

    assert report.ok
    assert report.token_env_names == ("GITHUB_TOKEN",)
    assert any("token-based API fallback" in item for item in report.warnings)


def test_pr_capability_discovers_homebrew_style_gh_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_gh = _write_gh_stub(tmp_path)
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda _name, path=None: None,
    )

    report = check_pr_capability(
        tmp_path,
        env={},
        candidate_paths=(str(fake_gh),),
        require_gh_auth=False,
    )

    assert report.ok
    assert report.gh_path == str(fake_gh)


def test_pr_capability_discovers_windows_style_gh_path(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_gh = _write_gh_stub(tmp_path / "GitHub CLI")
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda _name, path=None: None,
    )

    report = check_pr_capability(
        tmp_path,
        env={},
        candidate_paths=(str(fake_gh),),
        require_gh_auth=False,
    )

    assert report.ok
    assert report.gh_path == str(fake_gh)


def test_pr_capability_discovers_git_from_candidate_paths(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_git = _write_gh_stub(tmp_path / "Git" / "cmd")
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda _name, path=None: None,
    )

    assert find_git_path(candidate_paths=(str(fake_git),), env={}) == str(fake_git)


def test_proxy_blocker_detection_reports_loopback_port() -> None:
    hits = suspicious_proxy_env_names(
        {
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://proxy.example.test:8080",
        }
    )

    assert hits == ("HTTPS_PROXY",)


def test_proxy_blocker_detection_deduplicates_case_variants() -> None:
    hits = suspicious_proxy_env_names(
        {
            "HTTP_PROXY": "http://127.0.0.1:9",
            "http_proxy": "http://127.0.0.1:9",
        }
    )

    assert hits == ("HTTP_PROXY",)


def test_without_suspicious_proxy_env_removes_only_known_blocker_values() -> None:
    env = without_suspicious_proxy_env(
        {
            "HTTP_PROXY": "http://127.0.0.1:9",
            "http_proxy": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://proxy.example.test:8080",
            "PATH": "test-path",
        }
    )

    assert "HTTP_PROXY" not in env
    assert "http_proxy" not in env
    assert env["HTTPS_PROXY"] == "http://proxy.example.test:8080"
    assert env["PATH"] == "test-path"


def test_env_with_discovered_tool_paths_can_clear_known_blocker_proxy(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_gh_path",
        lambda env=None: None,
    )
    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.find_git_path",
        lambda env=None: None,
    )

    env = env_with_discovered_tool_paths(
        {
            "PATH": "",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://proxy.example.test:8080",
        },
        clear_suspicious_proxy=True,
    )

    assert "HTTPS_PROXY" not in env
    assert env["HTTP_PROXY"] == "http://proxy.example.test:8080"


def test_env_with_overrides_inherits_active_environment(monkeypatch) -> None:
    monkeypatch.setenv("APL_ENV_GUARDRAIL_SENTINEL", "kept")

    env = env_with_overrides(HTTPS_PROXY="http://127.0.0.1:9")

    assert env["APL_ENV_GUARDRAIL_SENTINEL"] == "kept"
    assert env["HTTPS_PROXY"] == "http://127.0.0.1:9"


def test_env_with_overrides_can_remove_explicit_keys() -> None:
    env = env_with_overrides(
        {"PATH": "base-path", "HTTPS_PROXY": "http://127.0.0.1:9"},
        HTTPS_PROXY=None,
        HTTP_PROXY="http://proxy.example.test:8080",
    )

    assert env["PATH"] == "base-path"
    assert "HTTPS_PROXY" not in env
    assert env["HTTP_PROXY"] == "http://proxy.example.test:8080"


def test_pr_capability_keeps_backward_compatible_env_with_overrides_alias() -> None:
    assert pr_capability_env_with_overrides is env_with_overrides


def test_env_with_overrides_preserves_dependency_discovery_in_child_process() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = env_with_overrides(APL_ENV_GUARDRAIL_SENTINEL="kept")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import os, yaml; "
                "print(os.environ['APL_ENV_GUARDRAIL_SENTINEL']); "
                "print(yaml.__name__)"
            ),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert result.stdout.splitlines() == ["kept", "yaml"]


def test_env_with_discovered_tool_paths_prepends_tool_dirs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fake_gh = _write_gh_stub(tmp_path / "GitHub CLI")
    fake_git = _write_gh_stub(tmp_path / "Git" / "cmd")
    calls = {"gh": fake_gh, "git": fake_git}

    monkeypatch.setattr(
        "physics_lab.registry.pr_capability.shutil.which",
        lambda name, path=None: str(calls[name]) if path in ("", None) else None,
    )

    env = env_with_discovered_tool_paths({"PATH": ""})
    parts = [Path(part) for part in env["PATH"].split(os.pathsep)]

    assert fake_gh.parent in parts
    assert fake_git.parent in parts


def test_pr_capability_cli_reports_missing_tooling_as_warning_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env["PATH"] = ""
    # Disable the hardcoded gh discovery fallback so the test simulates
    # the "gh not installed" state deterministically. Without this
    # override, developer machines with Homebrew gh would resolve
    # /opt/homebrew/bin/gh from the fallback list and silently flip the
    # warning path off.
    env["APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"] = ""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_pr_capability_check.py",
            "--root",
            ".",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert "PR capability check" in result.stdout
    assert "git path:" in result.stdout
    assert "suspicious proxy env:" in result.stdout
    assert "Warnings:" in result.stdout
    assert "Direct PR creation" in result.stdout or "not authenticated" in result.stdout


def test_pr_capability_cli_reports_clean_state_when_gh_authenticated(
    tmp_path: Path,
) -> None:
    """Positive-path counterpart to the warning-path CLI test.

    A stub gh binary on a sandboxed PATH returns success for
    `gh auth status`. The script should report no warnings. The env-var
    override pins discovery to the stub so the registry's hardcoded
    fallback path does not silently shadow it.
    """
    repo_root = Path(__file__).resolve().parents[1]

    stub_bin = tmp_path / "stub-bin"
    stub_gh = _write_gh_stub(stub_bin)

    env = os.environ.copy()
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env["PATH"] = str(stub_bin)
    env["APL_PR_CAPABILITY_GH_CANDIDATE_PATHS"] = str(stub_gh)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/apl_pr_capability_check.py",
            "--root",
            ".",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "PR capability check" in result.stdout
    assert os.path.normcase(str(stub_gh)) in os.path.normcase(result.stdout)
    assert "Warnings: none" in result.stdout
    assert "Errors: none" in result.stdout
