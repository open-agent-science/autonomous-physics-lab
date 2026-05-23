from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

from physics_lab.registry.pr_capability import check_pr_capability


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
            #!{sys.executable}
            import sys
            sys.exit({exit_code})
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
    assert str(stub_gh) in result.stdout
    assert "Warnings: none" in result.stdout
    assert "Errors: none" in result.stdout
