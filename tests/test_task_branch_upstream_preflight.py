"""Tests for the task-branch upstream tracking preflight (TASK-0624)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_branch_precondition.py"


@pytest.fixture(scope="module")
def precondition_module():
    spec = importlib.util.spec_from_file_location(
        "apl_branch_precondition_upstream_under_test",
        SCRIPT_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ── classify_branch_kind ──────────────────────────────────────────────────


def test_classify_branch_kind_recognizes_all_lifecycle_kinds(precondition_module) -> None:
    classify = precondition_module.classify_branch_kind
    assert classify("agent/roman/claude/task-0624-foo") == "task"
    assert classify("agent/roman/claude/propose-task-foo") == "proposal"
    assert classify("agent/roman/claude/task-queue-foo") == "queue"
    assert classify("agent/roman/claude/closeout-foo") == "closeout"
    assert classify("agent/roman/claude/microtask-DAV-001-foo") == "microtask"
    assert classify("agent/roman/claude/microtask-batch-DAV--foo") == "microtask"


def test_classify_branch_kind_ignores_non_task_branches(precondition_module) -> None:
    classify = precondition_module.classify_branch_kind
    assert classify("main") is None
    assert classify("") is None
    assert classify("feature/some-thing") is None
    assert classify("agent/roman/claude/random-segment") is None


# ── upstream_preflight (pure decision logic) ──────────────────────────────


def test_upstream_preflight_ok_when_tracking_own_branch(precondition_module) -> None:
    verdict = precondition_module.upstream_preflight(
        branch="agent/roman/claude/task-0624-foo",
        upstream="origin/agent/roman/claude/task-0624-foo",
    )
    assert verdict["status"] == "ok"
    assert verdict["ok"] is True
    assert verdict["safe_command"] is None


def test_upstream_preflight_flags_origin_main_tracking(precondition_module) -> None:
    verdict = precondition_module.upstream_preflight(
        branch="agent/roman/claude/task-0624-foo",
        upstream="origin/main",
    )
    assert verdict["status"] == "upstream_mismatch"
    assert verdict["ok"] is False
    assert verdict["safe_command"] == "git push origin HEAD:agent/roman/claude/task-0624-foo"


def test_upstream_preflight_flags_missing_upstream(precondition_module) -> None:
    verdict = precondition_module.upstream_preflight(
        branch="agent/roman/claude/task-0624-foo",
        upstream=None,
    )
    assert verdict["status"] == "missing_upstream"
    assert verdict["ok"] is False
    assert verdict["safe_command"] == "git push origin HEAD:agent/roman/claude/task-0624-foo"


def test_upstream_preflight_skips_detached_head(precondition_module) -> None:
    verdict = precondition_module.upstream_preflight(branch="", upstream=None)
    assert verdict["status"] == "detached_head"
    assert verdict["ok"] is True
    assert verdict["safe_command"] is None


def test_upstream_preflight_skips_non_task_branch(precondition_module) -> None:
    verdict = precondition_module.upstream_preflight(branch="main", upstream="origin/main")
    assert verdict["status"] == "not_a_task_branch"
    assert verdict["ok"] is True


def test_upstream_preflight_honors_custom_remote(precondition_module) -> None:
    verdict = precondition_module.upstream_preflight(
        branch="agent/roman/claude/task-0624-foo",
        upstream="fork/main",
        remote="fork",
    )
    assert verdict["safe_command"] == "git push fork HEAD:agent/roman/claude/task-0624-foo"


# ── run() integration (opt-in --check-upstream) ───────────────────────────


def _run_args(branch: str, **overrides) -> SimpleNamespace:
    base = {
        "expected_branch": branch,
        "root": ".",
        "allow_untracked": [],
        "allow_modified": [],
        "check_upstream": True,
        "remote": "origin",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _patch_clean_tree_and_branch(precondition_module, branch: str, upstream: str | None):
    return (
        patch.object(precondition_module, "current_branch", return_value=branch),
        patch.object(
            precondition_module, "run_command", return_value=SimpleNamespace(stdout="")
        ),
        patch.object(precondition_module, "_resolve_upstream", return_value=upstream),
    )


def test_run_passes_when_upstream_matches(precondition_module, capsys) -> None:
    branch = "agent/roman/claude/task-0624-foo"
    branch_p, tree_p, upstream_p = _patch_clean_tree_and_branch(
        precondition_module, branch, f"origin/{branch}"
    )
    with branch_p, tree_p, upstream_p:
        exit_code = precondition_module.run(_run_args(branch))
    assert exit_code == 0
    assert "Branch precondition OK" in capsys.readouterr().out


def test_run_fails_and_prints_safe_command_on_origin_main(precondition_module, capsys) -> None:
    branch = "agent/roman/claude/task-0624-foo"
    branch_p, tree_p, upstream_p = _patch_clean_tree_and_branch(
        precondition_module, branch, "origin/main"
    )
    with branch_p, tree_p, upstream_p:
        exit_code = precondition_module.run(_run_args(branch))
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "tracks 'origin/main'" in err
    assert f"git push origin HEAD:{branch}" in err


def test_run_skips_upstream_check_when_flag_absent(precondition_module) -> None:
    """Existing callers without --check-upstream must keep the old behavior."""
    branch = "agent/roman/claude/task-0624-foo"
    branch_p, tree_p, upstream_p = _patch_clean_tree_and_branch(
        precondition_module, branch, "origin/main"
    )
    # _resolve_upstream must not even be consulted when the flag is off.
    with branch_p, tree_p, patch.object(
        precondition_module, "_resolve_upstream", side_effect=AssertionError("called")
    ):
        exit_code = precondition_module.run(_run_args(branch, check_upstream=False))
    assert exit_code == 0
