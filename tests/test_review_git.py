from __future__ import annotations

from pathlib import Path

from physics_lab.registry import review_git
from physics_lab.registry.review_git import CommandResult


def test_working_tree_changed_files_handles_renames_and_arrow_literals(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        assert command == ["git", "status", "--short"]
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
        if command == ["git", "diff", "--name-only", "origin/main...feature"]:
            return CommandResult(returncode=0, stdout="docs/a.md\ndocs/b.md\n", stderr="")
        if command == ["git", "branch", "--show-current"]:
            return CommandResult(returncode=0, stdout="feature\n", stderr="")
        if command == ["git", "status", "--short"]:
            return CommandResult(returncode=0, stdout=" M docs/b.md\n?? docs/c.md\n", stderr="")
        raise AssertionError(f"Unexpected command: {command!r}")

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.changed_files_vs_main(tmp_path, "feature", base_ref="origin/main") == (
        "docs/a.md",
        "docs/b.md",
        "docs/c.md",
    )
    assert ["git", "diff", "--name-only", "origin/main...feature"] in seen_commands


def test_changed_files_vs_main_omits_worktree_for_other_branch(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        if command == ["git", "diff", "--name-only", "main...feature"]:
            return CommandResult(returncode=0, stdout="docs/a.md\n", stderr="")
        if command == ["git", "branch", "--show-current"]:
            return CommandResult(returncode=0, stdout="other\n", stderr="")
        if command == ["git", "status", "--short"]:
            raise AssertionError("status should not be read for a non-current branch")
        raise AssertionError(f"Unexpected command: {command!r}")

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.changed_files_vs_main(tmp_path, "feature") == ("docs/a.md",)


def test_branch_exists_reports_missing_ref(monkeypatch, tmp_path: Path) -> None:
    def fake_run_command(command: list[str] | str, **_: object) -> CommandResult:
        if command == ["git", "rev-parse", "--verify", "origin/main"]:
            return CommandResult(returncode=0, stdout="abc123\n", stderr="")
        if command == ["git", "rev-parse", "--verify", "missing/ref"]:
            return CommandResult(returncode=128, stdout="", stderr="fatal: Needed a single revision\n")
        raise AssertionError(f"Unexpected command: {command!r}")

    monkeypatch.setattr(review_git, "run_command", fake_run_command)

    assert review_git.branch_exists(tmp_path, "origin/main")
    assert not review_git.branch_exists(tmp_path, "missing/ref")

