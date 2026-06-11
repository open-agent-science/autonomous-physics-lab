from __future__ import annotations

from pathlib import Path

from physics_lab.registry import review_git
from physics_lab.registry.review_git import CommandResult


def _assert_git_command(command: list[str] | str, *tail: str) -> None:
    assert isinstance(command, list)
    assert command[0] == "git"
    assert command[-len(tail) :] == list(tail)


def test_working_tree_changed_files_handles_renames_and_arrow_literals(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        _assert_git_command(command, "status", "--short")
        return CommandResult(
            returncode=0,
            stdout="\n".join(
                [
                    " M physics_lab/registry/review_git.py",
                    "R  docs/old-name.md -> docs/new-name.md",
                    "C  templates/base.md -> templates/copy.md",
                    "?? docs/a -> b.md",
                    " D docs/removed.md",
                ]
            ),
            stderr="",
        )

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.working_tree_changed_files(tmp_path) == (
        "physics_lab/registry/review_git.py",
        "docs/new-name.md",
        "templates/copy.md",
        "docs/a -> b.md",
        "docs/removed.md",
    )


def test_changed_files_vs_main_uses_merge_base_ref_and_current_worktree(
    monkeypatch,
    tmp_path: Path,
) -> None:
    seen_commands: list[list[str] | str] = []

    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        seen_commands.append(command)
        if isinstance(command, list) and command[-3:] == [
            "diff",
            "--name-only",
            "origin/main...feature",
        ]:
            return CommandResult(returncode=0, stdout="docs/a.md\ndocs/b.md\n", stderr="")
        if isinstance(command, list) and command[-2:] == ["branch", "--show-current"]:
            return CommandResult(returncode=0, stdout="feature\n", stderr="")
        if isinstance(command, list) and command[-2:] == ["status", "--short"]:
            return CommandResult(returncode=0, stdout=" M docs/b.md\n?? docs/c.md\n", stderr="")
        raise AssertionError(f"Unexpected command: {command!r}")

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.changed_files_vs_main(tmp_path, "feature", base_ref="origin/main") == (
        "docs/a.md",
        "docs/b.md",
        "docs/c.md",
    )
    assert any(
        isinstance(command, list) and command[-3:] == ["diff", "--name-only", "origin/main...feature"]
        for command in seen_commands
    )


def test_changed_files_vs_main_omits_worktree_for_other_branch(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        if isinstance(command, list) and command[-3:] == ["diff", "--name-only", "main...feature"]:
            return CommandResult(returncode=0, stdout="docs/a.md\n", stderr="")
        if isinstance(command, list) and command[-2:] == ["branch", "--show-current"]:
            return CommandResult(returncode=0, stdout="other\n", stderr="")
        if isinstance(command, list) and command[-2:] == ["status", "--short"]:
            raise AssertionError("status should not be read for a non-current branch")
        raise AssertionError(f"Unexpected command: {command!r}")

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.changed_files_vs_main(tmp_path, "feature") == ("docs/a.md",)


def test_branch_exists_reports_missing_ref(monkeypatch, tmp_path: Path) -> None:
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        if isinstance(command, list) and command[-3:] == ["rev-parse", "--verify", "origin/main"]:
            return CommandResult(returncode=0, stdout="abc123\n", stderr="")
        if isinstance(command, list) and command[-3:] == ["rev-parse", "--verify", "missing/ref"]:
            return CommandResult(returncode=128, stdout="", stderr="fatal: Needed a single revision\n")
        raise AssertionError(f"Unexpected command: {command!r}")

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.branch_exists(tmp_path, "origin/main")
    assert not review_git.branch_exists(tmp_path, "missing/ref")


# ── Ignore-paths behaviour (TASK-0261) ─────────────────────────────────────


def _fake_status(stdout: str):
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        _assert_git_command(command, "status", "--short")
        return CommandResult(returncode=0, stdout=stdout, stderr="")

    return fake_run_command


def test_working_tree_filters_default_harness_ignore(
    monkeypatch, tmp_path: Path
) -> None:
    """Untracked harness lockfile must be filtered by the default ignore list."""
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status("?? .claude/scheduled_tasks.lock\n"),
    )
    assert review_git.working_tree_changed_files(tmp_path) == ()


def test_working_tree_keeps_normal_untracked_with_default_ignore(
    monkeypatch, tmp_path: Path
) -> None:
    """A non-harness untracked file must still be reported."""
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status(
            "?? .claude/scheduled_tasks.lock\n?? docs/notes/draft.md\n"
        ),
    )
    assert review_git.working_tree_changed_files(tmp_path) == (
        "docs/notes/draft.md",
    )


def test_working_tree_respects_custom_ignore_tuple(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status(" M docs/a.md\n?? docs/b.md\n"),
    )
    filtered = review_git.working_tree_changed_files(
        tmp_path, ignore_paths=("docs/b.md",)
    )
    assert filtered == ("docs/a.md",)


def test_working_tree_strict_mode_returns_everything(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status("?? .claude/scheduled_tasks.lock\n M docs/a.md\n"),
    )
    strict = review_git.working_tree_changed_files(tmp_path, ignore_paths=())
    assert strict == (".claude/scheduled_tasks.lock", "docs/a.md")


def test_git_status_clean_true_when_only_harness_lock_is_present(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status("?? .claude/scheduled_tasks.lock\n"),
    )
    assert review_git.git_status_clean(tmp_path)


def test_git_status_clean_ignores_generated_context_and_task_views(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status(" M CONTEXT.md\n M docs/task-views/support.md\n"),
    )
    assert review_git.git_status_clean(tmp_path)


def test_git_status_clean_false_for_real_modifications(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status(" M docs/a.md\n"),
    )
    assert not review_git.git_status_clean(tmp_path)


def test_git_status_clean_strict_mode_blocks_on_harness_lock(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        review_git,
        "run_command",
        _fake_status("?? .claude/scheduled_tasks.lock\n"),
    )
    assert not review_git.git_status_clean(tmp_path, ignore_paths=())


def test_harness_ignore_paths_is_a_tuple() -> None:
    """Defense-in-depth: the constant is exported and must be a tuple of strings."""
    assert isinstance(review_git.HARNESS_IGNORE_PATHS, tuple)
    assert ".claude/scheduled_tasks.lock" in review_git.HARNESS_IGNORE_PATHS
    assert all(isinstance(p, str) for p in review_git.HARNESS_IGNORE_PATHS)
