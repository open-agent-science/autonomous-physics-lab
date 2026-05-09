from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.validation import infer_kind_from_path


def _write_campaign_profile(root: Path) -> None:
    profile_path = root / "campaign_profiles" / "pendulum-formula-falsification.yaml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(
        textwrap.dedent(
            """\
            id: pendulum-formula-falsification
            autonomy_status: WHITELISTED_PILOT
            """
        ),
        encoding="utf-8",
    )


def _write_hypothesis_proposal(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            """\
            id: HYP-PROPOSAL-0001
            title: "Sandbox pendulum candidate"
            campaign_profile_id: pendulum-formula-falsification
            proposal_kind: formula_search
            status: DRAFT
            claim_ceiling: "Sandbox-only candidate; no canonical result."
            proposed_by:
              contributor_id: roman
              agent_id: codex
              task_id: TASK-0152
            input_references:
              - docs/autonomous-research-loop.md
            hypothesis:
              statement: "A candidate formula may reduce configured-range residuals."
              variables:
                - theta in radians
              assumptions:
                - ideal pendulum exact reference is the benchmark
              expected_scope: "Configured pendulum amplitude range."
              expected_failure_modes:
                - near-separatrix breakdown
            novelty_check:
              checked_files:
                - docs/notes/pendulum-gauntlet-100.md
              possible_overlap: NONE
              notes: "No duplicate candidate recorded."
            falsification_plan:
              deterministic_check: "Compare residuals against exact reference values."
              baseline_or_reference: "exact reference baseline"
              pass_condition: "Mean residual is below the declared threshold."
              fail_condition: "Residual exceeds the declared threshold."
            overclaim_risk:
              public_claim_allowed: false
              forbidden_language:
                - "No public success framing."
              mitigations:
                - "Keep all evidence sandbox-only."
            sandbox_evidence:
              commands:
                - python3 -m physics_lab.cli preflight-research-proposal hypothesis_proposals/HYP-PROPOSAL-0001.yaml
              code_references:
                - physics_lab/registry/research_proposals.py
              metrics:
                - mean_relative_error
              output_paths:
                - agent_runs/AGENT-RUN-0001/metrics.json
            limitations:
              - "Configured range only."
            verdict: REVIEW_NEEDED
            maintainer_decision_requested: "Decide whether to request a canonical experiment task."
            promotion_boundary:
              canonical_result_allowed: false
              claim_promotion_allowed: false
              required_next_step: "Maintainer-reviewed canonical task."
            """
        ),
        encoding="utf-8",
    )


def _write_experiment_proposal(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            """\
            id: EXP-PROPOSAL-0001
            title: "Sandbox pendulum candidate check"
            campaign_profile_id: pendulum-formula-falsification
            proposal_kind: formula_search
            status: DRAFT
            claim_ceiling: "Sandbox-only experiment proposal; no canonical result."
            proposed_by:
              contributor_id: roman
              agent_id: codex
              task_id: TASK-0152
            input_references:
              - docs/research-quality-gate.md
            question: "Does the candidate beat the baseline in the configured range?"
            method:
              summary: "Run deterministic residual comparison."
              code_references:
                - physics_lab/registry/research_proposals.py
              commands:
                - python3 -m physics_lab.cli preflight-research-proposal experiment_proposals/EXP-PROPOSAL-0001.yaml
              parameters:
                sample_count: 50
            inputs:
              datasets:
                - exact pendulum reference
              constants:
                - NONE
              prior_results:
                - RESULT-0004
              assumptions:
                - ideal pendulum only
            outputs:
              sandbox_output_paths:
                - agent_runs/AGENT-RUN-0001/
              metrics:
                - mean_relative_error
              plots:
                - NONE
              notes:
                - limitations.md
            validation:
              pass_condition: "Residual beats the declared baseline."
              fail_condition: "Residual does not beat the declared baseline."
              baseline_or_reference: "exact reference baseline"
              expected_failure_modes:
                - near-separatrix breakdown
            overclaim_risk:
              public_claim_allowed: false
              forbidden_language:
                - "No public success framing."
              mitigations:
                - "Keep all evidence sandbox-only."
            limitations:
              - "Configured range only."
            verdict: REVIEW_NEEDED
            maintainer_decision_requested: "Decide whether this should become a canonical experiment task."
            promotion_boundary:
              writes_canonical_result: false
              writes_claim_update: false
              required_next_step: "Maintainer-reviewed canonical experiment task."
            """
        ),
        encoding="utf-8",
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
