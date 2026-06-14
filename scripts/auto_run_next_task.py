#!/usr/bin/env python3
"""Pick and run the next available APL task with Claude Code.

This is the canonical cross-platform entrypoint. Keep this as the single
runtime path so Windows, macOS, Linux, and CI exercise the same logic.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_MAX_TURNS = 200

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_claude_budget  # noqa: E402


PRIORITY_WEIGHT = {"high": 0, "medium": 1, "low": 2}
DIFFICULTY_WEIGHT = {"low": 0, "medium": 1, "high": 2}


def _print_stderr(text: str = "") -> None:
    print(text, file=sys.stderr)


def _repo_root() -> Path:
    return Path(os.environ.get("REPO_ROOT", str(REPO_ROOT))).resolve()


def _budget_report() -> dict[str, Any]:
    projects_dir = Path(
        os.environ.get(
            "CLAUDE_PROJECTS_DIR",
            str(Path.home() / ".claude" / "projects"),
        )
    )
    if os.environ.get("CLAUDE_WEEKLY_TOKEN_LIMIT"):
        limit = int(os.environ["CLAUDE_WEEKLY_TOKEN_LIMIT"])
    elif os.environ.get("CLAUDE_MONTHLY_TOKEN_LIMIT"):
        _print_stderr(
            "warning: CLAUDE_MONTHLY_TOKEN_LIMIT is deprecated; "
            "set CLAUDE_WEEKLY_TOKEN_LIMIT instead."
        )
        limit = int(os.environ["CLAUDE_MONTHLY_TOKEN_LIMIT"])
    else:
        limit = check_claude_budget.DEFAULT_WEEKLY_LIMIT

    threshold = float(
        os.environ.get(
            "CLAUDE_BUDGET_THRESHOLD_PCT",
            check_claude_budget.DEFAULT_THRESHOLD_PCT,
        )
    )
    usage = check_claude_budget.compute_usage(projects_dir)
    return check_claude_budget.evaluate(
        usage,
        weekly_limit=limit,
        threshold_pct=threshold,
    )


def _mission_context(repo_root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "scripts/apl_mission.py", "--json"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "could not run scripts/apl_mission.py --json: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"could not parse apl_mission.py --json output: {exc}") from exc


def _rank_ready_candidates(mission: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        item
        for item in mission.get("live_task_candidates", [])
        if str(item.get("status", "")).upper() == "READY"
    ]
    return sorted(
        candidates,
        key=lambda item: (
            PRIORITY_WEIGHT.get(str(item.get("priority", "low")), 9),
            DIFFICULTY_WEIGHT.get(str(item.get("difficulty", "high")), 9),
        ),
    )


def _open_pr_items(task_id: str) -> list[dict[str, Any]]:
    if os.environ.get("APL_OPEN_PR_LIST_JSON"):
        raw = os.environ["APL_OPEN_PR_LIST_JSON"]
    elif os.environ.get("APL_OPEN_PR_LIST_CMD"):
        # Backward-compatible hook for older POSIX tests. New tests should use
        # APL_OPEN_PR_LIST_JSON to avoid platform-specific shell quoting.
        result = subprocess.run(
            os.environ["APL_OPEN_PR_LIST_CMD"],
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )
        raw = result.stdout if result.returncode == 0 else ""
    else:
        gh = shutil.which("gh")
        if gh is None:
            return []
        result = subprocess.run(
            [
                gh,
                "pr",
                "list",
                "--state",
                "open",
                "--search",
                f"{task_id} in:title",
                "--json",
                "number,title",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        raw = result.stdout if result.returncode == 0 else ""

    if not raw.strip():
        return []
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return items if isinstance(items, list) else []


def _has_open_pr(task_id: str) -> bool:
    return any(
        task_id and task_id in str(item.get("title", ""))
        for item in _open_pr_items(task_id)
    )


def _select_task(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    for candidate in candidates:
        task_id = str(candidate.get("task_id", ""))
        if _has_open_pr(task_id):
            _print_stderr(f"Skipping {task_id} - an open PR already targets this task.")
            continue
        return candidate
    return None


def _task_file(repo_root: Path, task_id: str) -> Path:
    matches = sorted((repo_root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        raise RuntimeError(f"task file for {task_id} not found in tasks/")
    return matches[0]


def _prompt(task_id: str, title: str, task_file: Path) -> str:
    return f"""Execute task {task_id} from the Autonomous Physics Lab repository.
Task file: {task_file}
Title: {title}

Follow all protocols in AGENTS.md and docs/agent-task-protocol.md exactly:
- Transition status READY -> IN_PROGRESS before editing
- Work on a branch: agent/<contributor-id>/<agent-id>/task-<number>-<slug>
- Use the lowercased GitHub username as contributor-id when available
- Run full validation: ruff, pytest, validate-repo --strict, example runs, apl_review_bundle.sh
- Transition status -> REVIEW_READY after validation passes
- Open a PR using apl_task_pr_helper.py with the full PR template body
- Do NOT push to main. Do NOT promote claims or write PRED-*.yaml files.
"""


def _stream_claude(prompt: str, *, max_turns: int, repo_root: Path) -> int:
    claude = shutil.which("claude")
    if claude is None:
        _print_stderr("ERROR: claude CLI was not found on PATH.")
        return 127

    log_path = Path(
        os.environ.get(
            "APL_AUTO_RUNNER_CHILD_LOG",
            str(
                Path(os.environ.get("TMPDIR", "/tmp"))
                / "apl-auto-runner-child-stdout.log"
            ),
        )
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    captured: list[str] = []

    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [claude, "--max-turns", str(max_turns), "-p", prompt],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log.write(line)
            captured.append(line)
        process.wait()

    child_exit = int(process.returncode or 0)
    child_output = "".join(captured)

    _print_stderr()
    if child_exit != 0 and "Reached max turns" in child_output:
        _print_stderr("=== Auto-runner: max-turns reached ===")
        return child_exit
    if child_exit != 0:
        _print_stderr("=== Auto-runner: child Claude exited non-zero ===")
        return child_exit
    return 0


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the next available APL task with Claude Code.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--max-turns",
        type=int,
        default=int(os.environ.get("CLAUDE_MAX_TURNS", DEFAULT_MAX_TURNS)),
    )
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    _print_stderr("=== Claude Code budget check ===")
    budget = _budget_report()
    _print_stderr(json.dumps(budget, indent=2))
    used_pct = budget["used_pct"]

    if not budget["under_threshold"]:
        _print_stderr()
        _print_stderr(f"Budget gate: BLOCKED - usage {used_pct}% is at or above threshold.")
        _print_stderr("Set CLAUDE_BUDGET_THRESHOLD_PCT to a higher value to override.")
        return 0

    _print_stderr()
    _print_stderr(f"Budget gate: OK - usage {used_pct}% is below threshold.")
    _print_stderr()
    _print_stderr("=== Selecting next task ===")

    try:
        ranked_ready = _rank_ready_candidates(_mission_context(repo_root))
    except RuntimeError as exc:
        _print_stderr(f"ERROR: {exc}")
        return 1

    if not ranked_ready:
        _print_stderr("No READY tasks found. Nothing to do.")
        return 0

    selected = _select_task(ranked_ready)
    if selected is None:
        _print_stderr("No READY task without an open PR is available. Nothing to do.")
        return 0

    task_id = str(selected.get("task_id", ""))
    title = str(selected.get("title", ""))
    _print_stderr(f"Selected: {task_id} - {title}")

    try:
        task_file = _task_file(repo_root, task_id)
    except RuntimeError as exc:
        _print_stderr(f"ERROR: {exc}")
        return 1

    prompt = _prompt(task_id, title, task_file)
    _print_stderr()
    if args.dry_run:
        _print_stderr("=== DRY RUN - would invoke ===")
        first_line = prompt.splitlines()[0]
        _print_stderr(f'claude --max-turns {args.max_turns} -p "{first_line}..."')
        _print_stderr()
        _print_stderr("Full prompt:")
        _print_stderr(prompt)
        return 0

    _print_stderr("=== Invoking claude CLI ===")
    _print_stderr()
    child_exit = _stream_claude(prompt, max_turns=args.max_turns, repo_root=repo_root)
    if child_exit != 0:
        if child_exit == 127:
            return child_exit
        # Re-read the child log so summary text matches the previous shell runner.
        log_path = Path(
            os.environ.get(
                "APL_AUTO_RUNNER_CHILD_LOG",
                str(
                    Path(os.environ.get("TMPDIR", "/tmp"))
                    / "apl-auto-runner-child-stdout.log"
                ),
            )
        )
        child_output = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        if "Reached max turns" in child_output:
            _print_stderr(f"Task: {task_id} - {title}")
            _print_stderr(
                f"Child Claude exit: {child_exit} (Reached max turns {args.max_turns})."
            )
            _print_stderr("Work-in-progress files may remain uncommitted in the worktree.")
            _print_stderr("Next step: inspect 'git status' inside the worktree and either rerun")
            _print_stderr(
                "  python3 scripts/auto_run_next_task.py with a higher --max-turns,"
                " or finish"
            )
            _print_stderr("  the task lifecycle (validate, commit, push, PR) by hand.")
        elif child_exit != 127:
            _print_stderr(f"Task: {task_id} - {title}")
            _print_stderr(
                f"Child Claude exit: {child_exit} (no 'Reached max turns' marker found)."
            )
            _print_stderr("Inspect the child output above and the worktree state before retrying.")
        return child_exit
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
