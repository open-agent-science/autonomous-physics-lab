"""Synthetic reveal dry-run tests for the shell-axis-balanced-001 mini-wave.

These tests exercise the partial-reveal, paired-control, and baseline-relative
scoring shape that a future real reveal of PRED-0063..PRED-0068 will need.
Every value loaded into the dry-run is a fabricated toy. No real nuclear mass
measurement is referenced, fetched, or scored here.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pytest

from physics_lab.engines.nuclear_prediction_reveal import (
    ELIGIBLE_STATUS,
    NON_MEASURED_VALUE_ONLY,
    SOURCE_PREDATES_REGISTRATION,
    TARGET_NOT_REVEALED,
    run_synthetic_reveal_dry_run,
)
from physics_lab.registry.examples import load_example_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "examples" / "nuclear_shell_axis_mini_wave_synthetic_reveal.yaml"

MINI_WAVE_PREDICTION_IDS = (
    "PRED-0063",  # candidate primary (proton-axis Gaussian)
    "PRED-0064",  # candidate companion (proton x neutron product)
    "PRED-0065",  # candidate diagnostic (neutron-axis Gaussian)
    "PRED-0066",  # negative control (sign-inverted proton-axis Gaussian)
    "PRED-0067",  # negative control (near-null shell-axis correction)
    "PRED-0068",  # reference control (frozen baseline)
)

CANDIDATE_PRIMARY = "PRED-0063"
SIGN_INVERTED_CONTROL = "PRED-0066"
NEAR_NULL_CONTROL = "PRED-0067"
BASELINE_REFERENCE = "PRED-0068"


def _result() -> dict[str, Any]:
    return run_synthetic_reveal_dry_run(ROOT, CONFIG)


def _rows_by_pred(result: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in result["comparison_rows"]:
        grouped[str(row["prediction_id"])].append(row)
    return grouped


def _per_pred_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    eligible = [row for row in rows if row["eligible_for_synthetic_scoring"]]
    if not eligible:
        return {"eligible_count": 0, "mae_mev": 0.0, "rmse_mev": 0.0}
    signed_errors = [float(row["signed_error_mev"]) for row in eligible]
    abs_errors = [abs(error) for error in signed_errors]
    return {
        "eligible_count": len(eligible),
        "mae_mev": sum(abs_errors) / len(abs_errors),
        "rmse_mev": math.sqrt(
            sum(error * error for error in signed_errors) / len(signed_errors)
        ),
    }


# ---------------------------------------------------------------------------
# Source labelling and configuration discipline
# ---------------------------------------------------------------------------


def test_shell_axis_mini_wave_source_is_labeled_synthetic() -> None:
    result = _result()

    assert result["mode"] == "synthetic_reveal_dry_run"
    assert result["source"]["synthetic_source"] is True
    assert result["source"]["real_measurement_source"] is False
    assert result["source"]["source_kind"] == "synthetic_toy_measurement"
    assert result["source"]["source_id"].startswith("SYNTH-")
    assert result["verdict"] == "INCONCLUSIVE_SYNTHETIC_DRY_RUN"


def test_shell_axis_mini_wave_example_loads_through_repository_examples() -> None:
    payload = load_example_config(CONFIG)

    assert payload["config_kind"] == "nuclear_prediction_synthetic_reveal"
    assert payload["synthetic_source"]["source_kind"] == "synthetic_toy_measurement"
    assert payload["synthetic_source"]["real_measurement_source"] is False
    assert tuple(payload["registry_snapshot"]["prediction_ids"]) == MINI_WAVE_PREDICTION_IDS


# ---------------------------------------------------------------------------
# Registry-snapshot coverage and partial-reveal shape
# ---------------------------------------------------------------------------


def test_shell_axis_mini_wave_covers_all_six_pred_entries() -> None:
    result = _result()

    assert tuple(result["registry_snapshot"]["prediction_ids"]) == MINI_WAVE_PREDICTION_IDS
    assert result["registry_snapshot"]["entry_count"] == 6
    assert result["registry_snapshot"]["target_row_count"] == 48

    seen = {str(row["prediction_id"]) for row in result["comparison_rows"]}
    assert seen == set(MINI_WAVE_PREDICTION_IDS)


def test_shell_axis_mini_wave_reports_partial_coverage_and_exclusions() -> None:
    result = _result()
    coverage = result["coverage"]

    # Per fixture: 4 eligible measured-synthetic rows, 2 omitted nuclides
    # (Cu-81, Cs-139), 1 extrapolated row (Co-77), 1 predates row (Cd-130)
    # — all × 6 PRED entries.
    assert coverage["target_rows"] == 48
    assert coverage["eligible_rows"] == 24
    assert coverage["unrevealed_rows"] == 12
    assert coverage["ineligible_rows"] == 12

    counts = coverage["eligibility_status_counts"]
    assert counts[ELIGIBLE_STATUS] == 24
    assert counts[TARGET_NOT_REVEALED] == 12
    assert counts[NON_MEASURED_VALUE_ONLY] == 6
    assert counts[SOURCE_PREDATES_REGISTRATION] == 6


def test_shell_axis_mini_wave_per_target_exclusions_are_uniform_across_preds() -> None:
    """The same synthetic row should produce the same eligibility status across
    every PRED entry — partial-reveal must not silently shift labels per entry."""

    result = _result()
    by_pred = _rows_by_pred(result)

    for prediction_id in MINI_WAVE_PREDICTION_IDS:
        rows = {row["nuclide_id"]: row for row in by_pred[prediction_id]}

        assert rows["V-70"]["eligibility_status"] == ELIGIBLE_STATUS
        assert rows["Mn-75"]["eligibility_status"] == ELIGIBLE_STATUS
        assert rows["Ag-129"]["eligibility_status"] == ELIGIBLE_STATUS
        assert rows["Sb-135"]["eligibility_status"] == ELIGIBLE_STATUS
        assert rows["Co-77"]["eligibility_status"] == NON_MEASURED_VALUE_ONLY
        assert rows["Cd-130"]["eligibility_status"] == SOURCE_PREDATES_REGISTRATION
        assert rows["Cu-81"]["eligibility_status"] == TARGET_NOT_REVEALED
        assert rows["Cs-139"]["eligibility_status"] == TARGET_NOT_REVEALED


# ---------------------------------------------------------------------------
# Paired controls and candidate-vs-baseline scoring shape
# ---------------------------------------------------------------------------


def test_shell_axis_mini_wave_keeps_paired_controls_visible() -> None:
    """A reveal artifact that drops the paired controls or the baseline
    reference must not be accepted; verify all three are present alongside
    the candidates."""

    result = _result()
    by_pred = _rows_by_pred(result)

    for prediction_id in (
        SIGN_INVERTED_CONTROL,
        NEAR_NULL_CONTROL,
        BASELINE_REFERENCE,
    ):
        rows = by_pred[prediction_id]
        assert len(rows) == 8, (
            f"{prediction_id} should appear as 8 target rows alongside the candidates"
        )

        statuses = Counter(str(row["eligibility_status"]) for row in rows)
        assert statuses[ELIGIBLE_STATUS] == 4
        assert statuses[TARGET_NOT_REVEALED] == 2
        assert statuses[NON_MEASURED_VALUE_ONLY] == 1
        assert statuses[SOURCE_PREDATES_REGISTRATION] == 1


def test_shell_axis_mini_wave_primary_candidate_mae_matches_expected_toy_offsets() -> None:
    """Synthetic offsets in the fixture are designed so the primary candidate
    PRED-0063 has small, deterministic absolute errors against the toy
    source. Confirm the MAE matches arithmetic on those offsets."""

    result = _result()
    metrics = _per_pred_metrics(_rows_by_pred(result)[CANDIDATE_PRIMARY])

    # Per fixture: predicted - synthetic for the four eligible rows is
    # -0.5, -0.3, -0.4, -0.6 (V-70, Mn-75, Ag-129, Sb-135).
    expected_mae = (0.5 + 0.3 + 0.4 + 0.6) / 4.0
    expected_rmse = math.sqrt((0.25 + 0.09 + 0.16 + 0.36) / 4.0)

    assert metrics["eligible_count"] == 4
    assert metrics["mae_mev"] == pytest.approx(expected_mae, abs=1e-6)
    assert metrics["rmse_mev"] == pytest.approx(expected_rmse, abs=1e-6)


def test_shell_axis_mini_wave_negative_control_mae_is_larger_than_primary_candidate() -> None:
    """Synthetic values are placed near PRED-0063's predictions, so the
    sign-inverted control PRED-0066 must register a *larger* MAE than the
    primary candidate. This is the candidate-vs-negative-control shape the
    review note documents."""

    result = _result()
    by_pred = _rows_by_pred(result)

    primary = _per_pred_metrics(by_pred[CANDIDATE_PRIMARY])
    sign_inverted = _per_pred_metrics(by_pred[SIGN_INVERTED_CONTROL])

    assert primary["eligible_count"] == 4
    assert sign_inverted["eligible_count"] == 4
    assert sign_inverted["mae_mev"] > primary["mae_mev"], (
        "Sign-inverted control must have larger MAE than primary candidate "
        "when synthetic source is placed near the candidate predictions"
    )


def test_shell_axis_mini_wave_baseline_reference_and_near_null_control_have_eligible_metrics() -> None:
    """Baseline reference PRED-0068 and near-null control PRED-0067 are not
    candidates, but their metrics must be reported alongside candidates so
    a reviewer can compare candidate uplift against the no-correction
    baseline shape."""

    result = _result()
    by_pred = _rows_by_pred(result)

    baseline = _per_pred_metrics(by_pred[BASELINE_REFERENCE])
    near_null = _per_pred_metrics(by_pred[NEAR_NULL_CONTROL])

    assert baseline["eligible_count"] == 4
    assert near_null["eligible_count"] == 4
    # PRED-0067 and PRED-0068 have identical predicted values per the
    # mini-wave registration (both are baseline reference shape), so their
    # MAE against the same synthetic source must match.
    assert near_null["mae_mev"] == pytest.approx(baseline["mae_mev"], abs=1e-9)
    assert near_null["rmse_mev"] == pytest.approx(baseline["rmse_mev"], abs=1e-9)


# ---------------------------------------------------------------------------
# Registry immutability and forbidden states
# ---------------------------------------------------------------------------


def test_shell_axis_mini_wave_dry_run_does_not_mutate_frozen_registry_entries() -> None:
    """Frozen prediction registry entries must be read-only inputs to the
    dry-run. Verify that running the dry-run does not change any PRED file."""

    before = {
        prediction_id: (
            ROOT / "prediction_registry" / "nuclear_masses" / f"{prediction_id}.yaml"
        ).read_bytes()
        for prediction_id in MINI_WAVE_PREDICTION_IDS
    }

    _result()

    for prediction_id, original in before.items():
        path = ROOT / "prediction_registry" / "nuclear_masses" / f"{prediction_id}.yaml"
        assert path.read_bytes() == original, (
            f"Frozen registry entry {prediction_id} must not be mutated by the dry-run"
        )


def test_shell_axis_mini_wave_metrics_aggregate_across_eligible_rows_only() -> None:
    """Top-level engine metrics aggregate across every eligible row in every
    PRED entry. Confirm that the engine's reported eligible_count matches
    the 24 measured-synthetic rows from the fixture."""

    result = _result()
    metrics = result["metrics"]

    assert metrics["eligible_count"] == 24
    assert metrics["mae_mev"] is not None
    assert metrics["rmse_mev"] is not None
    assert metrics["mae_mev"] > 0.0
    assert metrics["rmse_mev"] >= metrics["mae_mev"] - 1e-9, (
        "RMSE must be at least as large as MAE for any non-empty error set"
    )
