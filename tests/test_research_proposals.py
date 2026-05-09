from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry import load_hypothesis_proposal
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


def _write_hypothesis_proposal(path: Path, *, baseline: str = "exact reference baseline") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            f"""\
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
              baseline_or_reference: "{baseline}"
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


def test_hypothesis_proposal_preflight_validates_campaign_and_baseline(tmp_path: Path) -> None:
    _write_campaign_profile(tmp_path)
    proposal_path = tmp_path / "hypothesis_proposals" / "HYP-PROPOSAL-0001.yaml"
    _write_hypothesis_proposal(proposal_path)

    payload = load_hypothesis_proposal(proposal_path, root=tmp_path)

    assert payload["id"] == "HYP-PROPOSAL-0001"
    assert payload["campaign_profile_id"] == "pendulum-formula-falsification"


def test_formula_search_hypothesis_requires_baseline_plan(tmp_path: Path) -> None:
    _write_campaign_profile(tmp_path)
    proposal_path = tmp_path / "hypothesis_proposals" / "HYP-PROPOSAL-0001.yaml"
    _write_hypothesis_proposal(proposal_path, baseline="compare residuals only")

    with pytest.raises(ValueError, match="baseline"):
        load_hypothesis_proposal(proposal_path, root=tmp_path)


def test_experiment_proposal_cli_preflight_smoke(tmp_path: Path) -> None:
    _write_campaign_profile(tmp_path)
    proposal_path = tmp_path / "experiment_proposals" / "EXP-PROPOSAL-0001.yaml"
    _write_experiment_proposal(proposal_path)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "preflight-research-proposal",
            str(proposal_path),
            "--root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Preflight PASS" in result.stdout
    assert "pendulum-formula-falsification" in result.stdout


def test_validate_repository_counts_research_proposals(tmp_path: Path) -> None:
    _write_campaign_profile(tmp_path)
    _write_hypothesis_proposal(tmp_path / "hypothesis_proposals" / "HYP-PROPOSAL-0001.yaml")
    _write_experiment_proposal(tmp_path / "experiment_proposals" / "EXP-PROPOSAL-0001.yaml")

    summary = validate_repository(tmp_path)

    assert summary.counts["hypothesis_proposals"] == 1
    assert summary.counts["experiment_proposals"] == 1


def test_infer_kind_from_research_proposal_paths() -> None:
    assert infer_kind_from_path("hypothesis_proposals/HYP-PROPOSAL-0001.yaml") == "hypothesis_proposal"
    assert infer_kind_from_path("experiment_proposals/EXP-PROPOSAL-0001.yaml") == "experiment_proposal"
