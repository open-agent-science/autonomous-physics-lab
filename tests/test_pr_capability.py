from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from physics_lab.registry.pr_capability import check_pr_capability


def test_pr_capability_fails_without_gh_or_token(tmp_path: Path) -> None:
    report = check_pr_capability(
        tmp_path,
        env={},
        discover_gh=False,
    )

    assert not report.ok
    assert any("Cannot create a pull request" in item for item in report.errors)


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
    fake_gh = tmp_path / "gh"
    fake_gh.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_gh.chmod(0o755)
    monkeypatch.setattr("physics_lab.registry.pr_capability.shutil.which", lambda _name: None)

    report = check_pr_capability(
        tmp_path,
        env={},
        candidate_paths=(str(fake_gh),),
        require_gh_auth=False,
    )

    assert report.ok
    assert report.gh_path == str(fake_gh)


def test_pr_capability_cli_reports_missing_tooling_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
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
        env={},
    )

    assert result.returncode == 1
    assert "PR capability check" in result.stdout
    assert (
        "Cannot create a pull request" in result.stdout
        or "not authenticated" in result.stdout
    )
