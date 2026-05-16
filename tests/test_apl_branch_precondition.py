"""Tests for scripts/apl_branch_precondition.py (TASK-0263)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest


# ── Module loader ─────────────────────────────────────────────────────────
#
# The precondition script lives under scripts/ and is not part of the
# physics_lab package. We load it via importlib so the tests can call
# its functions directly without spawning a subprocess.

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "apl_branch_precondition.py"


@pytest.fixture(scope="module")
def precondition_module():
    spec = importlib.util.spec_from_file_location(
        "apl_branch_precondition_under_test",
        SCRIPT_PATH,
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


# ── _filter_paths ─────────────────────────────────────────────────────────


def test_filter_paths_no_patterns_passthrough(precondition_module) -> None:
    assert precondition_module._filter_paths(
        ("a.md", "b.py"), []
    ) == ("a.md", "b.py")


def test_filter_paths_glob_matches(precondition_module) -> None:
    filtered = precondition_module._filter_paths(
        ("docs/notes/draft-1.md", "docs/notes/final.md", "scripts/x.py"),
        ["docs/notes/draft-*.md", "scripts/*.py"],
    )
    assert filtered == ("docs/notes/final.md",)


def test_filter_paths_multiple_patterns(precondition_module) -> None:
    filtered = precondition_module._filter_paths(
        ("a.md", "b.md", "c.md"),
        ["a.md", "c.md"],
    )
    assert filtered == ("b.md",)


# ── run() — branch / clean-tree behaviour ─────────────────────────────────


class _Args:
    """Lightweight argparse-namespace stand-in for run()."""

    def __init__(
        self,
        expected_branch: str,
        root: str = ".",
        allow_untracked: list[str] | None = None,
        allow_modified: list[str] | None = None,
    ) -> None:
        self.expected_branch = expected_branch
        self.root = root
        self.allow_untracked = allow_untracked or []
        self.allow_modified = allow_modified or []


def _patch_paths(precondition_module, branch: str, status_stdout: str):
    """Patch current_branch and git status output in the module under test."""
    return (
        patch.object(precondition_module, "current_branch", return_value=branch),
        patch.object(
            precondition_module,
            "run_command",
            return_value=SimpleNamespace(stdout=status_stdout),
        ),
    )


def test_run_returns_zero_on_clean_match(precondition_module, capsys) -> None:
    branch_patch, dirty_patch = _patch_paths(
        precondition_module, "agent/roman/claude/task-0263-foo", ""
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(expected_branch="agent/roman/claude/task-0263-foo")
        )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Branch precondition OK" in captured.out
    assert "FAILED" not in captured.err


def test_run_fails_on_branch_mismatch(precondition_module, capsys) -> None:
    branch_patch, dirty_patch = _patch_paths(
        precondition_module, "main", ""
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(expected_branch="agent/roman/claude/task-0263-foo")
        )
    assert exit_code == 1
    assert "Branch mismatch" in capsys.readouterr().err


def test_run_fails_on_unexpected_untracked(precondition_module, capsys) -> None:
    branch_patch, dirty_patch = _patch_paths(
        precondition_module,
        "agent/roman/claude/task-0263-foo",
        "?? docs/surprise.md\n",
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(expected_branch="agent/roman/claude/task-0263-foo")
        )
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "unexpected changes" in err
    assert "docs/surprise.md" in err


def test_run_allows_untracked_glob_match(precondition_module, capsys) -> None:
    branch_patch, dirty_patch = _patch_paths(
        precondition_module,
        "agent/roman/claude/task-0263-foo",
        "?? docs/notes/draft-1.md\n?? docs/notes/draft-2.md\n",
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(
                expected_branch="agent/roman/claude/task-0263-foo",
                allow_untracked=["docs/notes/draft-*.md"],
            )
        )
    assert exit_code == 0


def test_run_allow_modified_combines_with_allow_untracked(
    precondition_module,
) -> None:
    branch_patch, dirty_patch = _patch_paths(
        precondition_module,
        "agent/roman/claude/task-0263-foo",
        "?? a.md\n M b.md\n",
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(
                expected_branch="agent/roman/claude/task-0263-foo",
                allow_untracked=["a.md"],
                allow_modified=["b.md"],
            )
        )
    assert exit_code == 0


def test_run_does_not_allow_modified_path_with_untracked_allowlist(
    precondition_module,
    capsys,
) -> None:
    branch_patch, dirty_patch = _patch_paths(
        precondition_module,
        "agent/roman/claude/task-0263-foo",
        " M docs/notes/draft-1.md\n",
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(
                expected_branch="agent/roman/claude/task-0263-foo",
                allow_untracked=["docs/notes/draft-*.md"],
            )
        )
    assert exit_code == 1
    assert "docs/notes/draft-1.md" in capsys.readouterr().err


def test_run_reports_both_failures(precondition_module, capsys) -> None:
    """Branch mismatch and dirty tree should both appear in the failure block."""
    branch_patch, dirty_patch = _patch_paths(
        precondition_module,
        "main",
        "?? scripts/extra.py\n",
    )
    with branch_patch, dirty_patch:
        exit_code = precondition_module.run(
            _Args(expected_branch="agent/roman/claude/task-0263-foo")
        )
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "Branch mismatch" in err
    assert "scripts/extra.py" in err


# ── _parse_args ───────────────────────────────────────────────────────────


def test_parse_args_requires_expected_branch(precondition_module) -> None:
    with pytest.raises(SystemExit):
        precondition_module._parse_args([])


def test_parse_args_collects_repeated_allow_patterns(precondition_module) -> None:
    ns = precondition_module._parse_args(
        [
            "--expected-branch",
            "agent/x/y/task-0001-foo",
            "--allow-untracked",
            "a/*",
            "--allow-untracked",
            "b/*",
            "--allow-modified",
            "c/*",
        ]
    )
    assert ns.expected_branch == "agent/x/y/task-0001-foo"
    assert ns.allow_untracked == ["a/*", "b/*"]
    assert ns.allow_modified == ["c/*"]


# ── main() — argparse error preserves exit code ───────────────────────────


def test_main_returns_two_on_argparse_error(precondition_module) -> None:
    exit_code = precondition_module.main([])
    assert exit_code == 2
