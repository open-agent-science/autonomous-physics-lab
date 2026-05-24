from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_help(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script, "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_maintainer_review_script_help_smoke() -> None:
    result = _run_help("scripts/apl_review_pr.py")

    assert result.returncode == 0
    assert "Review a task" in result.stdout
    assert "--pr" in result.stdout
    assert "--branch" in result.stdout


def test_closeout_task_script_help_smoke() -> None:
    result = _run_help("scripts/apl_closeout_task.py")

    assert result.returncode == 0
    assert "Check or apply maintainer task closeout" in result.stdout
    assert "--task" in result.stdout
    assert "--pr" in result.stdout


def test_closeout_sweep_script_help_smoke() -> None:
    result = _run_help("scripts/apl_closeout_sweep.py")

    assert result.returncode == 0
    assert "Scan REVIEW_READY tasks" in result.stdout
    assert "--merged-limit" in result.stdout


def test_coverage_report_script_help_smoke() -> None:
    result = _run_help("scripts/apl_coverage_report.py")

    assert result.returncode == 0
    assert "report-only branch coverage" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--html-dir" in result.stdout
