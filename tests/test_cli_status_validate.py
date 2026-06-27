from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_status_cli_reports_project_snapshot_fields() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["status", str(REPO_ROOT)])

    assert result.exit_code == 0, result.output
    assert "Stage: v0.2-public-alpha candidate" in result.stdout
    assert f"Repository: {REPO_ROOT}" in result.stdout
    assert "Validation: PASS" in result.stdout
    assert "Benchmarks:" in result.stdout
    assert "Latest result: results/" in result.stdout
    assert "Result id: RESULT-" in result.stdout
    assert "Verification checks:" in result.stdout


def test_validate_cli_accepts_valid_task_file() -> None:
    runner = CliRunner()
    task_path = REPO_ROOT / "tasks" / "TASK-0857-add-cli-status-validate-tests.yaml"

    result = runner.invoke(app, ["validate", str(task_path)])

    assert result.exit_code == 0, result.output
    assert f"Validated {task_path.as_posix()} as task." in result.stdout


def test_validate_cli_missing_file_exits_nonzero() -> None:
    runner = CliRunner()
    missing_path = REPO_ROOT / "tasks" / "TASK-9999-missing.yaml"

    result = runner.invoke(app, ["validate", str(missing_path)])

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
