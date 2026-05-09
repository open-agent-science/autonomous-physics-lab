from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.validation import infer_kind_from_path
from tests.test_research_proposals import (
    _write_campaign_profile,
    _write_experiment_proposal,
    _write_hypothesis_proposal,
)


def _write_agent_run_layout(root: Path, *, metrics_path: str = "agent_runs/AGENT-RUN-0001/metrics.json") -> Path:
    _write_campaign_profile(root)
    _write_hypothesis_proposal(root / "hypothesis_proposals" / "HYP-PROPOSAL-0001.yaml")
    _write_experiment_proposal(root / "experiment_proposals" / "EXP-PROPOSAL-0001.yaml")

    run_dir = root / "agent_runs" / "AGENT-RUN-0001"
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in ("metrics.json", "report.md", "limitations.md", "preflight.md", "review_summary.md"):
        (run_dir / name).write_text("sandbox artifact\n", encoding="utf-8")

    manifest_path = run_dir / "agent_run.yaml"
    manifest_path.write_text(
        textwrap.dedent(
            f"""\
            id: AGENT-RUN-0001
            campaign_profile_id: pendulum-formula-falsification
            task_id: TASK-0152
            status: SANDBOX_COMPLETE
            sandbox_only: true
            created_by:
              contributor_id: roman
              agent_id: codex
            proposal_paths:
              hypothesis: hypothesis_proposals/HYP-PROPOSAL-0001.yaml
              experiment: experiment_proposals/EXP-PROPOSAL-0001.yaml
            artifacts:
              metrics: {metrics_path}
              report: agent_runs/AGENT-RUN-0001/report.md
              limitations: agent_runs/AGENT-RUN-0001/limitations.md
              preflight: agent_runs/AGENT-RUN-0001/preflight.md
              review_summary: agent_runs/AGENT-RUN-0001/review_summary.md
            preflight:
              passed: true
              checks:
                - name: proposal_schema
                  status: PASS
                  notes: "Both proposals passed preflight."
            limitations:
              - "Sandbox evidence only."
            verdict: REVIEW_NEEDED
            promotion_boundary:
              writes_canonical_result: false
              claim_promotion_allowed: false
              required_next_step: "Maintainer-reviewed canonical task."
            """
        ),
        encoding="utf-8",
    )
    return manifest_path


def test_agent_run_layout_validates_and_counts(tmp_path: Path) -> None:
    manifest_path = _write_agent_run_layout(tmp_path)

    payload = load_agent_run(manifest_path, root=tmp_path)
    summary = validate_repository(tmp_path)

    assert payload["id"] == "AGENT-RUN-0001"
    assert summary.counts["agent_runs"] == 1


def test_agent_run_rejects_canonical_result_artifact_path(tmp_path: Path) -> None:
    manifest_path = _write_agent_run_layout(tmp_path, metrics_path="results/EXP-0001/RUN-0001/metrics.json")

    with pytest.raises(ValueError, match="canonical memory path"):
        load_agent_run(manifest_path, root=tmp_path)


def test_cli_validate_agent_run_smoke(tmp_path: Path) -> None:
    manifest_path = _write_agent_run_layout(tmp_path)

    runner = CliRunner()
    result = runner.invoke(app, ["validate", str(manifest_path)])

    assert result.exit_code == 0
    assert "agent_run" in result.stdout


def test_infer_kind_from_agent_run_manifest_path() -> None:
    assert infer_kind_from_path("agent_runs/AGENT-RUN-0001/agent_run.yaml") == "agent_run"
