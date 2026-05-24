"""Smoke tests for the cross-platform autonomous task runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parents[1]
PY_RUNNER = REPO_ROOT / "scripts" / "auto_run_next_task.py"


def _run_runner(
    args: list[str],
    *,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """Run the cross-platform Python auto-runner entrypoint."""
    return subprocess.run(
        [sys.executable, str(PY_RUNNER), *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


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
    # against the live remote. The JSON hook is preferred because it avoids
    # shell quoting differences across Windows, macOS, and Linux.
    titles = [{"number": 999, "title": f"{tid}: stub"} for tid in (open_pr_task_ids or [])]
    base_env["APL_OPEN_PR_LIST_JSON"] = json.dumps(titles)

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

    result = _run_runner(
        ["--dry-run", "--max-turns", "12"],
        env=_runner_env(tmp_path, fake_repo),
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

    result = _run_runner(["--dry-run"], env=_runner_env(tmp_path, fake_repo))

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

    result = _run_runner(
        ["--dry-run"],
        env=_runner_env(tmp_path, fake_repo, open_pr_task_ids=["TASK-0010"]),
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

    result = _run_runner(
        ["--dry-run"],
        env=_runner_env(
            tmp_path,
            fake_repo,
            open_pr_task_ids=["TASK-0020", "TASK-0021"],
        ),
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

    result = _run_runner(
        ["--dry-run"],
        env=_runner_env(tmp_path, fake_repo, use_legacy_monthly_env=True),
    )

    assert result.returncode == 0, result.stderr
    assert "deprecated" in result.stderr.lower()
    assert "Selected: TASK-0030" in result.stderr


def _make_stub_claude_bin(
    bin_dir: Path,
    *,
    stdout_text: str,
    exit_code: int,
) -> str:
    """Write a stub `claude` executable that emits the given stdout and
    exits with the given exit code. Returns a PATH value with this bin
    directory at the front."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        stub = bin_dir / "claude.cmd"
        stub.write_text(
            "\r\n".join(
                [
                    "@echo off",
                    f'"{sys.executable}" "%~dp0claude_stub.py"',
                    f"exit /b {exit_code}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        stub = bin_dir / "claude"
        stub.write_text(
            dedent(
                f"""\
                #!{sys.executable}
                import sys

                sys.stdout.write({stdout_text!r})
                if not {stdout_text!r}.endswith("\\n"):
                    sys.stdout.write("\\n")
                sys.exit({exit_code})
                """
            ),
            encoding="utf-8",
        )
        stub.chmod(0o755)

    if os.name == "nt":
        (bin_dir / "claude_stub.py").write_text(
            dedent(
                f"""\
                import sys

                sys.stdout.write({stdout_text!r})
                if not {stdout_text!r}.endswith("\\n"):
                    sys.stdout.write("\\n")
                """
            ),
            encoding="utf-8",
        )
    return os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")])


def test_auto_runner_detects_max_turns_exit_and_reports_clearly(tmp_path: Path) -> None:
    """When the child Claude exits non-zero with 'Reached max turns' on
    stdout, the runner must report the work-in-progress state and exit
    with the child's exit code instead of silently dropping the failure."""

    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0040",
                "title": "Max-turns exit detection",
                "status": "READY",
                "priority": "high",
                "difficulty": "low",
            },
        ],
    )

    bin_dir = tmp_path / "stub-bin"
    path_value = _make_stub_claude_bin(
        bin_dir,
        stdout_text="Doing work...\nError: Reached max turns (60)",
        exit_code=1,
    )

    env = _runner_env(tmp_path, fake_repo)
    env["PATH"] = path_value
    env["APL_AUTO_RUNNER_CHILD_LOG"] = str(tmp_path / "child-stdout.log")

    result = _run_runner(["--max-turns", "60"], env=env)

    assert result.returncode == 1, (result.stdout, result.stderr)
    # Child's stdout still surfaces (we tee'd it).
    assert "Reached max turns (60)" in result.stdout
    # Runner's post-run summary names the task and suggests a next step.
    assert "max-turns reached" in result.stderr.lower()
    assert "TASK-0040" in result.stderr
    assert "Work-in-progress" in result.stderr or "work-in-progress" in result.stderr.lower()
    assert "higher --max-turns" in result.stderr or "finish" in result.stderr.lower()


def test_auto_runner_reports_non_max_turns_failure_distinctly(tmp_path: Path) -> None:
    """A non-zero exit without the 'Reached max turns' marker should still
    surface a runner summary, but distinct from the max-turns path."""

    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0041",
                "title": "Generic child failure",
                "status": "READY",
                "priority": "high",
                "difficulty": "low",
            },
        ],
    )

    bin_dir = tmp_path / "stub-bin"
    path_value = _make_stub_claude_bin(
        bin_dir,
        stdout_text="Some unrelated failure",
        exit_code=2,
    )

    env = _runner_env(tmp_path, fake_repo)
    env["PATH"] = path_value
    env["APL_AUTO_RUNNER_CHILD_LOG"] = str(tmp_path / "child-stdout.log")

    result = _run_runner(["--max-turns", "60"], env=env)

    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "no 'reached max turns' marker" in result.stderr.lower()
    assert "TASK-0041" in result.stderr


def test_auto_runner_default_max_turns_is_200(tmp_path: Path) -> None:
    """Default --max-turns is 200 so review/audit tasks have headroom to
    finish commit/push/PR after a substantial write. A live TASK-0312 run
    showed 60 was far too low; 80 (the original default) was still too
    low; 200 gives comfortable margin without enabling runaway behavior."""

    fake_repo = _write_fake_repo(
        tmp_path,
        candidates=[
            {
                "task_id": "TASK-0050",
                "title": "Default max-turns sanity",
                "status": "READY",
                "priority": "high",
                "difficulty": "low",
            },
        ],
    )

    # Strip CLAUDE_MAX_TURNS from the env so the script's own default applies.
    env = _runner_env(tmp_path, fake_repo)
    env.pop("CLAUDE_MAX_TURNS", None)

    result = _run_runner(["--dry-run"], env=env)

    assert result.returncode == 0, result.stderr
    # The dry-run summary line names the chosen --max-turns value.
    assert "claude --max-turns 200" in result.stderr, result.stderr
