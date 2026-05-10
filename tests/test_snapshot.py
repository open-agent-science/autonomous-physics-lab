from pathlib import Path

from physics_lab.registry.snapshot import (
    build_snapshot_context,
    render_authority_notes,
    render_current_state_summary,
)


def test_build_snapshot_context_uses_canonical_repo_root() -> None:
    root = Path(".").resolve()
    context = build_snapshot_context(root)

    assert context.invocation_root == root
    assert context.canonical_root.exists()
    assert (context.canonical_root / "pyproject.toml").exists()
    assert context.repo_name == context.canonical_root.name
    assert context.default_base_ref


def test_render_authority_notes_mentions_canonical_layers() -> None:
    rendered = render_authority_notes(Path("."))

    assert "canonical_repo_root" in rendered
    assert "Authoritative current-state sections" in rendered
    assert "archive context" in rendered


def test_render_current_state_summary_uses_structured_repository_state() -> None:
    rendered = render_current_state_summary(Path("."))

    assert "### Current Task State" in rendered
    assert "### Current Experiment State" in rendered
    assert "### Recent Result Surface" in rendered
    assert "### REVIEW_READY now" in rendered
    assert "- REVIEW_READY:" in rendered
    assert "`TASK-0138`" in rendered
    assert "`TASK-0171`" in rendered
    assert "`EXP-0008`" in rendered


def test_snapshot_script_open_pr_section_uses_pr_list_result() -> None:
    script = Path("scripts/apl_snapshot.sh").read_text(encoding="utf-8")

    assert "gh auth status" not in script
    assert "git remote get-url origin" in script
    assert 'gh pr list --repo "$repo_slug" --state open --limit 30' in script
    assert 'echo "No open pull requests."' in script
