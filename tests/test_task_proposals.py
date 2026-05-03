from __future__ import annotations

import textwrap
from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry import load_task_proposal
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.validation import infer_kind_from_path


def _write_task_proposal(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            """\
            proposal_id: 20260503-roman-koide-track
            title: "Add Koide particle mass relation track"
            status: PROPOSED
            type: benchmark_planning
            priority: high
            proposed_by:
              contributor_id: roman
              agent_id: codex
            strategy_alignment:
              - "Expand the planning queue without canonical task id conflicts."
            summary: "Create a proposal-first path for new task ideas."
            rationale: "Parallel contributors should not guess the next task number."
            input:
              mode: planning_only
              related_domain: task_coordination
              related_objects: []
              planning_context: "Task proposal protocol"
            requirements:
              - "Keep the proposal atomic"
            accepted_outputs:
              - "canonical task spec"
            validation:
              commands:
                - "./scripts/validate_quick.sh"
            promotion:
              canonical_task_id: null
              decision: pending
              notes: "Awaiting maintainer review"
            """
        ),
        encoding="utf-8",
    )


def test_task_proposal_registry_file_validates(tmp_path: Path) -> None:
    proposal_path = tmp_path / "tasks" / "proposals" / "20260503-roman-koide-track.yaml"
    _write_task_proposal(proposal_path)

    payload = load_task_proposal(proposal_path)

    assert payload["proposal_id"] == "20260503-roman-koide-track"
    assert payload["status"] == "PROPOSED"


def test_validate_repository_counts_task_proposals_separately(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    for directory in (
        "agents",
        "claims",
        "experiments",
        "hypotheses",
        "knowledge",
        "results",
        "tasks",
        "tasks/proposals",
        "examples",
    ):
        (repo_root / directory).mkdir(parents=True, exist_ok=True)

    _write_task_proposal(
        repo_root / "tasks" / "proposals" / "20260503-roman-koide-track.yaml"
    )

    summary = validate_repository(repo_root)

    assert summary.counts["tasks"] == 0
    assert summary.counts["task_proposals"] == 1


def test_infer_kind_from_task_proposal_path() -> None:
    assert (
        infer_kind_from_path("tasks/proposals/20260503-roman-koide-track.yaml")
        == "task_proposal"
    )


def test_cli_validate_task_proposal_smoke(tmp_path: Path) -> None:
    proposal_path = tmp_path / "tasks" / "proposals" / "20260503-roman-koide-track.yaml"
    _write_task_proposal(proposal_path)

    runner = CliRunner()
    result = runner.invoke(app, ["validate", str(proposal_path)])

    assert result.exit_code == 0
    assert "task_proposal" in result.stdout
