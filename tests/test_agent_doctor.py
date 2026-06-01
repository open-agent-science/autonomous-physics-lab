from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from scripts.apl_agent_doctor import build_report


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
