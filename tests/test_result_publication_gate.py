"""Tests for the Gate A agent-publication checker."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys

import yaml

from physics_lab.registry.result_publication_gate import check_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_TEMPLATE = REPO_ROOT / "results" / "RESULT-TEMPLATE.agent-published.yaml"
PRED_TEMPLATE = REPO_ROOT / "prediction_registry" / "PRED-TEMPLATE.agent-published.yaml"


def _result_payload() -> dict:
    payload = yaml.safe_load(RESULT_TEMPLATE.read_text(encoding="utf-8"))
    payload = deepcopy(payload)
    payload["result_id"] = "RESULT-9998"
    payload["engine_version"] = "0.2-test"
    payload["git_commit"] = "deadbeefcafebabe"
    payload["verification"]["passed"] = True
    payload["verification"]["checks"][0] = {
        "name": "deterministic_replay",
        "status": "PASS",
        "details": "Replay command completed and metrics matched the stored payload.",
        "metrics": {"max_abs_delta": 0.0},
    }
    payload["agent_proposal_evaluation"]["evidence_summary"] = (
        "Deterministic test fixture with populated Gate A metadata."
    )
    for key in payload["agent_proposal_evaluation"]["gates_checked"]:
        payload["agent_proposal_evaluation"]["gates_checked"][key] = True
    return payload


def _prediction_payload() -> dict:
    payload = yaml.safe_load(PRED_TEMPLATE.read_text(encoding="utf-8"))
    payload = deepcopy(payload)
    payload.update(
        {
            "prediction_id": "PRED-9998",
            "title": "Agent-published test prediction",
            "campaign_profile_id": "test-campaign",
        }
    )
    payload["registered_by"] = {"contributor_id": "test", "agent_id": "test-agent"}
    payload["source_state"]["git_commit"] = "deadbeefcafebabe"
    payload["source_state"]["model_reference"] = {
        "model_id": "TEST-MODEL-001",
        "source_path": "results/EXP-9999/RUN-9999/result.yaml",
        "frozen_parameters_note": "All fixture parameters are frozen.",
    }
    payload["source_state"]["baseline_reference"] = {
        "source_path": "results/EXP-9999/RUN-9999/baseline.json"
    }
    payload["source_state"]["training_data_references"] = [
        "data/test/training-source.yaml"
    ]
    payload["source_state"]["source_data_state_note"] = (
        "No reveal-relevant future measurement was read for this fixture."
    )
    payload["target_set"] = {
        "label": "test-targets",
        "quantity": "test_quantity",
        "unit": "test_unit",
        "targets": [
            {
                "target_id": "test-1",
                "predicted_value": 1.0,
                "uncertainty": None,
                "confidence_note": "Point estimate fixture.",
            }
        ],
    }
    payload["reveal_conditions"] = {
        "comparison_source_class": "future_reviewed_source",
        "reveal_controlled_by": "maintainer",
        "no_peek_rule": "Do not read reveal data before registration.",
        "partial_reveal_allowed": False,
        "expected_reveal_window": "unknown",
    }
    payload["agent_proposal_evaluation"]["evidence_summary"] = (
        "Frozen prediction fixture with populated Gate A metadata."
    )
    for key in payload["agent_proposal_evaluation"]["gates_checked"]:
        payload["agent_proposal_evaluation"]["gates_checked"][key] = True
    return payload


def _codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_valid_agent_published_result_passes_gate_a() -> None:
    report = check_payload(_result_payload(), root=REPO_ROOT)

    assert report.ok, report.issues
    assert report.artifact_kind == "result"


def test_result_missing_deterministic_command_fails() -> None:
    payload = _result_payload()
    payload["command"] = ""

    report = check_payload(payload, root=REPO_ROOT)

    assert not report.ok
    assert "result-command" in _codes(report)


def test_result_missing_verification_check_fails() -> None:
    payload = _result_payload()
    payload["verification"]["checks"] = []

    report = check_payload(payload, root=REPO_ROOT)

    assert not report.ok
    assert "result-verification" in _codes(report)


def test_result_protected_id_fails(tmp_path: Path) -> None:
    protected_dir = tmp_path / "results"
    protected_dir.mkdir()
    (protected_dir / "golden-results.yaml").write_text(
        "golden_results:\n  - result_id: RESULT-9998\n",
        encoding="utf-8",
    )

    report = check_payload(_result_payload(), root=tmp_path)

    assert not report.ok
    assert "protected-result" in _codes(report)


def test_overclaim_positive_context_fails_but_guardrail_context_passes() -> None:
    payload = _result_payload()
    overclaim_term = "sol" + "ved"
    payload["title"] = f"This result {overclaim_term} the problem"

    report = check_payload(payload, root=REPO_ROOT)

    assert not report.ok
    assert "overclaim-wording" in _codes(report)

    guarded = _result_payload()
    guarded["limitations"].append(f"Do not say this {overclaim_term} the problem.")
    guarded_report = check_payload(guarded, root=REPO_ROOT)

    assert guarded_report.ok, guarded_report.issues


def test_valid_agent_published_prediction_passes_gate_a() -> None:
    report = check_payload(_prediction_payload(), root=REPO_ROOT)

    assert report.ok, report.issues
    assert report.artifact_kind == "prediction"


def test_prediction_live_external_fetch_fails() -> None:
    payload = _prediction_payload()
    payload["source_state"]["live_external_fetch_allowed"] = True

    report = check_payload(payload, root=REPO_ROOT)

    assert not report.ok
    assert "pred-live-fetch" in _codes(report)


def test_prediction_claim_ceiling_must_remain_non_claim() -> None:
    payload = _prediction_payload()
    payload["claim_ceiling"] = "This prediction confirms the model."

    report = check_payload(payload, root=REPO_ROOT)

    assert not report.ok
    assert "pred-claim-ceiling" in _codes(report)


def test_cli_returns_success_for_valid_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "result.yaml"
    artifact.write_text(yaml.safe_dump(_result_payload()), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/apl_check_result_publication.py",
            str(artifact),
            "--root",
            str(REPO_ROOT),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS" in completed.stdout
