from __future__ import annotations

from pathlib import Path

import yaml

from scripts.nuclear_prediction_registry_report import (
    build_registry_summary,
    write_registry_summary,
)


def _write_prediction(
    registry_dir: Path,
    prediction_id: str,
    *,
    task_id: str = "TASK-TEST",
    holdout_refs: list[str] | None = None,
    target_batch: str = "frontier-next-row",
    model_id: str = "RESULT-TEST::model_fitted_semi_empirical",
) -> None:
    payload = {
        "prediction_id": prediction_id,
        "task_id": task_id,
        "source_state": {
            "model_reference": {
                "model_id": model_id,
                "frozen_parameters_note": "Frozen test model metadata only.",
            },
            "holdout_protocol_references": holdout_refs
            if holdout_refs is not None
            else [
                "docs/blind-holdout-benchmark-protocol.md",
                "docs/prediction-registry-policy.md",
            ],
            "live_external_fetch_allowed": False,
        },
        "target_set": {
            "label": target_batch,
            "quantity": "mass_excess_mev",
            "unit": "MeV",
            "target_nuclides": [
                {
                    "nuclide_id": "Ca-55",
                    "Z": 20,
                    "N": 35,
                    "A": 55,
                    "predicted_value_mev": -8.0,
                }
            ],
        },
    }
    (registry_dir / f"{prediction_id}.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )


def _write_template(registry_dir: Path) -> None:
    payload = {"prediction_id": "PRED-XXXX", "task_id": "TASK-XXXX"}
    (registry_dir / "PRED-TEMPLATE.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )


def test_template_exclusion_and_count_semantics(tmp_path: Path) -> None:
    registry_dir = tmp_path / "prediction_registry" / "nuclear_masses"
    registry_dir.mkdir(parents=True)
    _write_template(registry_dir)
    _write_prediction(registry_dir, "PRED-0001")
    _write_prediction(registry_dir, "PRED-0003")

    summary = build_registry_summary(tmp_path)

    assert summary["actual_entry_count"] == 2
    assert summary["template_count"] == 1
    assert summary["highest_pred_id"] == "PRED-0003"
    assert summary["id_gaps"] == ["PRED-0002"]
    assert summary["target_row_count"] == 2


def test_reveal_state_grouping_blocks_scoring_until_all_gates_pass(tmp_path: Path) -> None:
    registry_dir = tmp_path / "prediction_registry" / "nuclear_masses"
    registry_dir.mkdir(parents=True)
    _write_prediction(
        registry_dir,
        "PRED-0001",
        holdout_refs=[
            "docs/blind-holdout-benchmark-protocol.md",
            "docs/nuclear-prediction-reveal-protocol.md",
            "docs/nuclear-reveal-source-readiness-checklist.md",
        ],
    )

    summary = build_registry_summary(tmp_path)
    row = summary["entries_must_not_be_scored_before_reveal_gate"][0]
    state_counts = {item["label"]: item["count"] for item in summary["reveal_state_counts"]}
    blocker_counts = {item["label"]: item["count"] for item in summary["blocker_counts"]}

    assert summary["blocked_reveal_count"] == 1
    assert summary["ready_for_reveal_count"] == 0
    assert summary["awaiting_source_count"] == 1
    assert row["reveal_state"] == "AWAITING_SOURCE_PREFLIGHT"
    assert row["blockers"] == [
        "SOURCE_PREFLIGHT_REQUIRED",
        "NO_PEEK_REVIEW_REQUIRED",
        "MAINTAINER_APPROVAL_REQUIRED",
    ]
    assert state_counts["AWAITING_SOURCE_PREFLIGHT"] == 1
    assert blocker_counts["SOURCE_PREFLIGHT_REQUIRED"] == 1


def test_model_family_grouping_uses_available_registry_metadata(tmp_path: Path) -> None:
    registry_dir = tmp_path / "prediction_registry" / "nuclear_masses"
    registry_dir.mkdir(parents=True)
    _write_prediction(
        registry_dir,
        "PRED-0001",
        task_id="TASK-0297",
        target_batch="shell-axis-balanced-001",
        model_id="RESULT-TEST::shell-axis-proton-gaussian-balanced",
    )
    _write_prediction(
        registry_dir,
        "PRED-0002",
        task_id="TASK-0265",
        target_batch="shell-magic-probe",
        model_id="RESULT-TEST::shell-n-reviewed-coefficients",
    )

    summary = build_registry_summary(tmp_path)
    families = {item["label"]: item["count"] for item in summary["model_family_counts"]}

    assert families["shell_axis"] == 1
    assert families["feature_term_selected"] == 1


def test_write_registry_summary_writes_output_without_scoring(tmp_path: Path) -> None:
    registry_dir = tmp_path / "prediction_registry" / "nuclear_masses"
    registry_dir.mkdir(parents=True)
    _write_template(registry_dir)
    _write_prediction(registry_dir, "PRED-0001")

    output_path = tmp_path / "summary.yaml"
    summary = write_registry_summary(tmp_path, output_path=output_path)
    written = yaml.safe_load(output_path.read_text(encoding="utf-8"))

    assert summary["summary_scope"]["live_external_fetch_performed"] is False
    assert summary["summary_scope"]["scoring_performed"] is False
    assert written["actual_entry_count"] == 1
