from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "run_nuclear_high_error_cluster_adversarial_audit.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("high_error_adversarial", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_adversarial_variant_composition() -> None:
    module = _load_module()
    *_, perturbed_threshold, _index = module._surface_and_index()
    variants = module._build_adversarial_variants(
        perturbed_high_error_threshold=perturbed_threshold
    )
    ids = [variant["candidate_id"] for variant in variants]

    assert ids[:3] == ["HIGHCLUSTER-001", "HIGHCLUSTER-002", "HIGHCLUSTER-003"]
    assert "HIGHCLUSTER-CONTROL-003" in ids
    assert "HIGHCLUSTER-CONTROL-004" in ids
    assert "HIGHCLUSTER-CONTROL-005" in ids
    assert "HIGHCLUSTER-CONTROL-006" in ids
    assert len([variant for variant in variants if variant["role"].endswith("_control")]) == 6


def test_build_metrics_records_required_adversarial_outputs() -> None:
    module = _load_module()
    metrics = module.build_metrics()
    summary = metrics["summary"]

    assert metrics["agent_run_id"] == "AGENT-RUN-0033"
    assert metrics["task_id"] == "TASK-0367"
    assert metrics["sandbox_only"] is True
    assert metrics["live_external_fetch_allowed"] is False
    assert summary["executed_candidate_count"] == 3
    assert summary["executed_control_count"] == 6
    assert summary["new_adversarial_control_count"] == 3
    assert summary["canonical_results_changed"] is False
    assert summary["canonical_claims_changed"] is False
    assert summary["prediction_registry_changed"] is False
    assert summary["claim_promotion_allowed"] is False
    assert summary["lane_verdict"] in {"PARTIALLY_VALID", "INCONCLUSIVE", "FALSIFIED"}

    assert "isotope_chain_transfer" in metrics
    assert "isotone_chain_transfer" in metrics
    subset_keys = metrics["baseline_metrics_by_subset"]
    for subset_id in (
        "full_known",
        "primary_holdout",
        "high_error_baseline_p75",
        "non_high_error_baseline_p75",
        "neutron_rich_local",
        "magic_region",
        "light_a_warning",
    ):
        assert subset_id in subset_keys


def test_candidate_comparison_and_stability_tables_are_complete() -> None:
    module = _load_module()
    metrics = module.build_metrics()

    comparisons = metrics["candidate_vs_strongest_control"]
    assert {row["candidate_id"] for row in comparisons} == {
        "HIGHCLUSTER-001",
        "HIGHCLUSTER-002",
        "HIGHCLUSTER-003",
    }
    for row in comparisons:
        assert row["primary_strongest_control_id"] is not None
        assert row["comparable_subset_count"] > 0
        assert 0.0 <= row["subset_win_rate"] <= 1.0
        assert isinstance(row["material_non_high_error_regression"], bool)
        assert isinstance(row["only_high_error_improvement_flag"], bool)

    stability = metrics["coefficient_stability"]
    assert stability["method"] == "deterministic_leave_one_training_row_out"
    assert stability["training_row_count"] > 1
    assert {item["candidate_id"] for item in stability["items"]} == {
        "HIGHCLUSTER-001",
        "HIGHCLUSTER-002",
        "HIGHCLUSTER-003",
    }
    for item in stability["items"]:
        assert item["fold_count"] == stability["training_row_count"]
        assert item["coefficient_summary"]
        assert len(item["full_known_delta_range_mev"]) == 2
        assert len(item["high_error_delta_range_mev"]) == 2
        assert len(item["non_high_error_delta_range_mev"]) == 2


def test_committed_metrics_match_recomputed_summary() -> None:
    module = _load_module()
    committed = json.loads(
        (Path(__file__).resolve().parents[1] / "agent_runs" / "AGENT-RUN-0033" / "metrics.json").read_text(
            encoding="utf-8"
        )
    )
    recomputed = module.build_metrics()

    assert committed["summary"] == recomputed["summary"]
    assert committed["candidate_vs_strongest_control"] == recomputed[
        "candidate_vs_strongest_control"
    ]


def test_runner_writes_only_requested_sandbox_outputs(tmp_path: Path) -> None:
    module = _load_module()
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    agent_run_path = tmp_path / "agent_run.yaml"
    limitations_path = tmp_path / "limitations.md"
    preflight_path = tmp_path / "preflight.md"
    review_summary_path = tmp_path / "review_summary.md"
    review_path = tmp_path / "review.md"

    assert (
        module.main(
            [
                "--out",
                str(metrics_path),
                "--report",
                str(report_path),
                "--agent-run",
                str(agent_run_path),
                "--limitations",
                str(limitations_path),
                "--preflight",
                str(preflight_path),
                "--review-summary",
                str(review_summary_path),
                "--review",
                str(review_path),
            ]
        )
        == 0
    )

    for path in (
        metrics_path,
        report_path,
        agent_run_path,
        limitations_path,
        preflight_path,
        review_summary_path,
        review_path,
    ):
        assert path.exists()
