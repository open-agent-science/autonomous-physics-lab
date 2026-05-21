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


def _runner_env(
    tmp_path: Path,
    fake_repo: Path,
    *,
    open_pr_task_ids: list[str] | None = None,
    use_legacy_monthly_env: bool = False,
) -> dict[str, str]:
    env = os.environ.copy()
    base_env: dict[str, str] = {
        "CLAUDE_PROJECTS_DIR": str(tmp_path / "missing-claude-projects"),
        "CLAUDE_BUDGET_THRESHOLD_PCT": "99",
        "REPO_ROOT": str(fake_repo),
    }
    # Default to the new weekly env var; flip to the deprecated alias for the
    # backward-compat regression test.
    if use_legacy_monthly_env:
        base_env["CLAUDE_MONTHLY_TOKEN_LIMIT"] = "999999999"
        env.pop("CLAUDE_WEEKLY_TOKEN_LIMIT", None)
    else:
        base_env["CLAUDE_WEEKLY_TOKEN_LIMIT"] = "999999999"
        env.pop("CLAUDE_MONTHLY_TOKEN_LIMIT", None)

    # Honor the script's APL_OPEN_PR_LIST_CMD hook so tests do not call gh
    # against the live remote. The hook prints a JSON array of objects
    # shaped like `gh pr list --json number,title` output.
    titles = [{"number": 999, "title": f"{tid}: stub"} for tid in (open_pr_task_ids or [])]
    open_pr_cmd = (
        "python3 -c "
        f"\"import json,sys;sys.stdout.write(json.dumps({titles!r}))\""
    )
    base_env["APL_OPEN_PR_LIST_CMD"] = open_pr_cmd

    env.update(base_env)
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


def test_auto_runner_skips_candidate_with_open_pr_and_picks_next(tmp_path: Path) -> None:
    """The top-ranked candidate already has an open PR; the script must
    skip it and select the next READY candidate that does not."""

    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0010",
                "title": "Already in flight via another agent",
                "status": "READY",
                "priority": "high",
                "difficulty": "low",
            },
            {
                "task_id": "TASK-0011",
                "title": "Available follow-up",
                "status": "READY",
                "priority": "high",
                "difficulty": "medium",
            },
        ],
    )

    result = subprocess.run(
        [str(RUNNER), "--dry-run"],
        cwd=REPO_ROOT,
        env=_runner_env(tmp_path, fake_repo, open_pr_task_ids=["TASK-0010"]),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Skipping TASK-0010" in result.stderr
    assert "Selected: TASK-0011" in result.stderr
    assert "Execute task TASK-0011" in result.stderr


def test_auto_runner_exits_cleanly_when_every_candidate_has_open_pr(tmp_path: Path) -> None:
    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0020",
                "title": "First in flight",
                "status": "READY",
                "priority": "high",
                "difficulty": "low",
            },
            {
                "task_id": "TASK-0021",
                "title": "Second in flight",
                "status": "READY",
                "priority": "high",
                "difficulty": "medium",
            },
        ],
    )

    result = subprocess.run(
        [str(RUNNER), "--dry-run"],
        cwd=REPO_ROOT,
        env=_runner_env(
            tmp_path,
            fake_repo,
            open_pr_task_ids=["TASK-0020", "TASK-0021"],
        ),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Skipping TASK-0020" in result.stderr
    assert "Skipping TASK-0021" in result.stderr
    assert "No READY task without an open PR" in result.stderr


def test_auto_runner_legacy_monthly_env_var_still_runs(tmp_path: Path) -> None:
    """CLAUDE_MONTHLY_TOKEN_LIMIT is deprecated but must still drive the
    budget gate for one release of backward compatibility."""

    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0030",
                "title": "Legacy env-var compatibility",
                "status": "READY",
                "priority": "high",
                "difficulty": "low",
            },
        ],
    )

    result = subprocess.run(
        [str(RUNNER), "--dry-run"],
        cwd=REPO_ROOT,
        env=_runner_env(tmp_path, fake_repo, use_legacy_monthly_env=True),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "deprecated" in result.stderr.lower()
    assert "Selected: TASK-0030" in result.stderr
