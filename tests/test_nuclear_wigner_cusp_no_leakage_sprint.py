from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_nuclear_wigner_cusp_no_leakage_sprint.py"


def load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wigner_cusp_runner", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_features_depend_only_on_z_n_a() -> None:
    runner = load_runner()
    row = {"Z": 10, "N": 12, "A": 22, "baseline_residual_mev": 999.0}
    changed = {**row, "baseline_residual_mev": -999.0, "source_status": "future"}
    assert runner.cusp_feature(row) == runner.cusp_feature(changed)
    assert runner.asymmetry_feature(row) == runner.asymmetry_feature(changed)
    assert runner.smooth_a_feature(row) == runner.smooth_a_feature(changed)


def test_cusp_is_bounded_and_peaks_at_n_equals_z() -> None:
    runner = load_runner()
    at_cusp = runner.cusp_feature({"Z": 8, "N": 8, "A": 16})
    near = runner.cusp_feature({"Z": 8, "N": 9, "A": 17})
    far = runner.cusp_feature({"Z": 8, "N": 16, "A": 24})
    assert at_cusp == 1.0
    assert 0.0 < far < near < at_cusp


def test_frozen_split_counts_and_no_overlap() -> None:
    runner = load_runner()
    rows, gate = runner.load_training_rows()
    train, validation = runner.split_nmd0003(rows)
    assert len(train) == gate["split_contract"]["train_count"]
    assert len(validation) == gate["split_contract"]["validation_holdout_count"]
    assert {row["row_id"] for row in train}.isdisjoint(
        {row["row_id"] for row in validation}
    )


def test_metrics_are_deterministic_and_keep_panels_separate() -> None:
    runner = load_runner()
    first = runner.build_metrics()
    second = runner.build_metrics()
    assert first == second
    assert set(first["baseline"]) == {
        "training",
        "validation",
        "full_known",
        "post_ame2020_holdout",
    }
    assert first["leakage_audit"]["passed"] is True
    assert first["verdict"] in {
        "NEGATIVE_RESULT",
        "DIAGNOSTIC_ONLY",
        "INCONCLUSIVE",
        "BOUNDED_FOLLOWUP_CANDIDATE",
    }


def test_decision_rejects_control_margin_failure() -> None:
    runner = load_runner()
    metrics = {
        "leakage_audit": {"passed": True},
        "candidate": {
            "panels": {
                "full_known": {"mae_mev": 1.0},
                "post_ame2020_holdout": {"mae_mev": 1.0},
            }
        },
        "baseline": {"post_ame2020_holdout": {"mae_mev": 1.1}},
        "control_asymmetry_only": {"panels": {"full_known": {"mae_mev": 1.1}}},
        "control_matched_random": {"panels": {"full_known": {"mae_mev": 1.4}}},
        "control_smooth_a": {"panels": {"full_known": {"mae_mev": 1.4}}},
        "coefficient_stability": {"stable": True},
    }
    verdict, rationale = runner.decide(metrics)
    assert verdict == "NEGATIVE_RESULT"
    assert any("does not beat every declared control" in note for note in rationale)


@pytest.mark.parametrize("seed", [777])
def test_matched_random_is_seeded(seed: int) -> None:
    runner = load_runner()
    assert runner.RANDOM_SEED == seed
