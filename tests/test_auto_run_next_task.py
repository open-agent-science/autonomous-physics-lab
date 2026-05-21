"""Smoke tests for scripts/auto_run_next_task.sh."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "auto_run_next_task.sh"


def _write_fake_repo(tmp_path: Path, *, candidates: list[dict[str, object]]) -> Path:
    repo = tmp_path / "fake-repo"
    scripts_dir = repo / "scripts"
    tasks_dir = repo / "tasks"
    scripts_dir.mkdir(parents=True)
    tasks_dir.mkdir()
    mission_payload = {
        "live_task_candidates": candidates,
    }
    (scripts_dir / "apl_mission.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                f"print(json.dumps({mission_payload!r}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for candidate in candidates:
        task_id = str(candidate.get("task_id", "TASK-0000"))
        if task_id.startswith("TASK-"):
            (tasks_dir / f"{task_id}-fake.yaml").write_text(
                f'id: {task_id}\ntitle: "{candidate.get("title", "Fake task")}"\n',
                encoding="utf-8",
            )
    return repo


def _runner_env(tmp_path: Path, fake_repo: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_PROJECTS_DIR": str(tmp_path / "missing-claude-projects"),
            "CLAUDE_MONTHLY_TOKEN_LIMIT": "999999999",
            "CLAUDE_BUDGET_THRESHOLD_PCT": "99",
            "REPO_ROOT": str(fake_repo),
        }
    )
    return env


def test_auto_runner_dry_run_selects_ready_task(tmp_path: Path) -> None:
    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0001",
                "title": "Already in review",
                "status": "REVIEW_READY",
                "priority": "high",
                "difficulty": "low",
            },
            {
                "task_id": "TASK-0002",
                "title": "Run small science audit",
                "status": "READY",
                "priority": "high",
                "difficulty": "medium",
            },
        ],
    )

    result = subprocess.run(
        [str(RUNNER), "--dry-run", "--max-turns", "12"],
        cwd=REPO_ROOT,
        env=_runner_env(tmp_path, fake_repo),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Budget gate: OK" in result.stderr
    assert "Selected: TASK-0002" in result.stderr
    assert "claude --max-turns 12" in result.stderr
    assert "Execute task TASK-0002" in result.stderr
    assert "TASK-0001" not in result.stderr


def test_auto_runner_dry_run_exits_cleanly_without_ready_tasks(tmp_path: Path) -> None:
    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0003",
                "title": "Blocked task",
                "status": "BLOCKED",
                "priority": "high",
                "difficulty": "low",
            },
        ],
    )

    result = subprocess.run(
        [str(RUNNER), "--dry-run"],
        cwd=REPO_ROOT,
        env=_runner_env(tmp_path, fake_repo),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "No READY tasks found. Nothing to do." in result.stderr
