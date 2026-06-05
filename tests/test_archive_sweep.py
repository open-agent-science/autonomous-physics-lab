"""Tests for the reusable task-archive sweep tool (TASK-0590)."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SWEEP_PATH = Path(__file__).resolve().parents[1] / "scripts" / "apl_archive_sweep.py"
_spec = importlib.util.spec_from_file_location("apl_archive_sweep", SWEEP_PATH)
assert _spec and _spec.loader
sweep = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = sweep  # required so @dataclass can resolve annotations
_spec.loader.exec_module(sweep)


def test_bucket_name_is_pure_id_function():
    assert sweep.bucket_name("TASK-0001") == "0000-0499"
    assert sweep.bucket_name("TASK-0499") == "0000-0499"
    assert sweep.bucket_name("TASK-0500") == "0500-0999"
    assert sweep.bucket_name("TASK-1234") == "1000-1499"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_plan_moves_selects_only_flat_terminal(tmp_path: Path):
    _write(tmp_path / "tasks" / "TASK-0001-done.yaml", "id: TASK-0001\nstatus: DONE\n")
    _write(tmp_path / "tasks" / "TASK-0002-active.yaml", "id: TASK-0002\nstatus: READY\n")
    _write(tmp_path / "tasks" / "archive" / "0000-0499" / "TASK-0003-old.yaml", "id: TASK-0003\nstatus: DONE\n")
    moves = sweep.plan_moves(tmp_path, sweep.TERMINAL_STATUSES, None)
    assert {m.task_id for m in moves} == {"TASK-0001"}  # active + already-archived skipped
    assert moves[0].new_rel == "tasks/archive/0000-0499/TASK-0001-done.yaml"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _init_repo(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "init")


def test_full_sweep_is_pure_move(tmp_path: Path):
    _write(tmp_path / "tasks" / "TASK-0007-done.yaml", "id: TASK-0007\nstatus: DONE\n")
    _write(tmp_path / "tasks" / "TASK-0008-active.yaml", "id: TASK-0008\nstatus: READY\n")
    # a doc that references the task by id only (the convention) — must NOT change
    _write(tmp_path / "docs" / "note.md", "History: TASK-0007 did the thing.\n")
    _init_repo(tmp_path)

    assert sweep.main(["--root", str(tmp_path)]) == 0

    assert not (tmp_path / "tasks" / "TASK-0007-done.yaml").exists()
    assert (tmp_path / "tasks" / "archive" / "0000-0499" / "TASK-0007-done.yaml").exists()
    assert (tmp_path / "tasks" / "TASK-0008-active.yaml").exists()  # active untouched
    # pure move: the id-only reference is untouched
    assert (tmp_path / "docs" / "note.md").read_text(encoding="utf-8") == "History: TASK-0007 did the thing.\n"


def test_dry_run_changes_nothing(tmp_path: Path):
    _write(tmp_path / "tasks" / "TASK-0009-done.yaml", "id: TASK-0009\nstatus: DONE\n")
    _init_repo(tmp_path)
    sweep.main(["--root", str(tmp_path), "--dry-run"])
    assert (tmp_path / "tasks" / "TASK-0009-done.yaml").exists()
