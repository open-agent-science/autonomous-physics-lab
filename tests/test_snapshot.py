import re
from pathlib import Path

from physics_lab.registry.snapshot import (
    build_snapshot_context,
    render_authority_notes,
    render_current_state_summary,
    render_strategic_context_map,
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
    canonical_experiment_count = len(list(Path("experiments").glob("EXP-*.yaml")))
    canonical_section = rendered.split("### Canonical Experiments", maxsplit=1)[1].split(
        "### Recent Result Surface",
        maxsplit=1,
    )[0]
    experiment_lines = [
        line for line in canonical_section.splitlines() if line.startswith("- `EXP-")
    ]

    assert "### Current Task State" in rendered
    assert "### Current Experiment State" in rendered
    assert "### Recent Result Surface" in rendered
    assert "### REVIEW_READY now" in rendered
    assert re.search(r"^- REVIEW_READY: \d+$", rendered, re.MULTILINE)
    assert "### Recently DONE" in rendered
    assert re.search(r"^- `TASK-\d{4}`", rendered, re.MULTILINE)
    assert len(experiment_lines) == canonical_experiment_count
    assert "`EXP-0012`" in rendered


def test_render_strategic_context_map_explains_current_project_stage() -> None:
    rendered = render_strategic_context_map(Path("."))

    assert "### Strategic Snapshot Front Page" in rendered
    assert "Current Architecture Stage" in rendered
    assert "Campaign Motion" in rendered
    assert "Scientific Memory Conveyor" in rendered
    assert "Critical Files And Directories" in rendered
    assert "`missions/current.yaml`" in rendered
    assert "`docs/result-promotion-protocol.md`" in rendered
    assert "`agent_runs/`" in rendered
    assert "`results/`" in rendered
    assert "nuclear-mass-surface" in rendered
    assert "AGENT_PUBLISHED" in rendered or "AGENT_VALIDATED" in rendered


def test_snapshot_script_open_pr_section_uses_pr_list_result() -> None:
    script = Path("scripts/apl_snapshot.sh").read_text(encoding="utf-8")

    assert 'SNAPSHOT_DIR="${APL_SNAPSHOT_DIR:-${CANONICAL_REPO_ROOT}/_snapshots}"' in script
    assert 'OUT="${SNAPSHOT_DIR}/apl_snapshot_${TS}.md"' in script
    assert "gh auth status" not in script
    assert "git remote get-url origin" in script
    assert 'gh pr list --repo "$repo_slug" --state open --limit 30' in script
    assert 'echo "No open pull requests."' in script


def test_snapshot_script_does_not_run_validation_commands() -> None:
    script = Path("scripts/apl_snapshot.sh").read_text(encoding="utf-8")

    assert "python3 -m pytest" not in script
    assert "ruff check" not in script
    assert "validate-repo" not in script
    assert "examples/pendulum.yaml" not in script


def test_snapshot_script_includes_strategic_context_and_current_mission_docs() -> None:
    script = Path("scripts/apl_snapshot.sh").read_text(encoding="utf-8")

    assert 'section "Strategic Context For Agents"' in script
    assert "render_strategic_context_map" in script
    assert "docs/current-missions.md" in script
    assert "docs/result-promotion-protocol.md" in script
    assert "docs/scientific-memory-review-tiers.md" in script
