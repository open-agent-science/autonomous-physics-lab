"""Tests for the Pizzocaro source-derived PSD covariance approximation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "data"
    / "atomic_clocks"
    / "source_artifacts"
    / "pizzocaro-2020-yb-sr"
    / "vlbi_source_derived_psd_covariance_approximation.yaml"
)
LEDGER = (
    ROOT
    / "data"
    / "atomic_clocks"
    / "source_artifacts"
    / "pizzocaro-2020-yb-sr"
    / "vlbi_per_window_diagnostic_ledger.yaml"
)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_covariance_artifact_has_source_derived_psd_state_and_boundaries() -> None:
    artifact = _load(ARTIFACT)

    assert artifact["task_id"] == "TASK-0666"
    assert artifact["covariance_state"] == "COV_SOURCE_DERIVED_PSD_APPROX"
    assert artifact["scope"]["sensitivity_only"] is True
    assert artifact["scope"]["benchmark_allowed"] is False
    assert artifact["scope"]["aggregates_windows"] is False
    assert artifact["promotion_boundary"]["writes_acr_benchmark_rows"] is False
    assert artifact["promotion_boundary"]["writes_benchmark_metrics"] is False
    assert artifact["promotion_boundary"]["claim_promotion_allowed"] is False


def test_covariance_row_order_matches_committed_window_ledger() -> None:
    artifact = _load(ARTIFACT)
    ledger = _load(LEDGER)

    expected_order = [window["window_id"] for window in ledger["windows"]]

    assert artifact["covariance_matrix_e_minus_34"]["row_order"] == expected_order
    assert artifact["correlation_matrix"]["row_order"] == expected_order
    assert len(expected_order) == 10


def test_covariance_matrix_is_symmetric_psd_and_uses_final_u_diagonal() -> None:
    artifact = _load(ARTIFACT)
    ledger = _load(LEDGER)
    matrix = np.array(artifact["covariance_matrix_e_minus_34"]["matrix"], dtype=float)

    assert matrix.shape == (10, 10)
    assert np.allclose(matrix, matrix.T, atol=1e-9)
    assert np.linalg.eigvalsh(matrix).min() > 0.0
    assert artifact["covariance_matrix_e_minus_34"]["positive_semidefinite_check"][
        "psd_verdict"
    ] == "PASS"

    expected_diagonal = [
        round((window["final_uncertainty"] ** 2) / 1e-34, 6)
        for window in ledger["windows"]
    ]
    assert np.allclose(np.diag(matrix), expected_diagonal, atol=1e-9)


def test_off_diagonal_recipe_uses_shared_components_and_clock_sensitivity() -> None:
    artifact = _load(ARTIFACT)
    ledger = _load(LEDGER)
    windows = ledger["windows"]
    matrix = np.array(artifact["covariance_matrix_e_minus_34"]["matrix"], dtype=float)
    shared = ["uB1_comb", "uB2", "uB4_comb", "uB1_clock", "uB4_clock"]

    first = windows[0]["systematic_components"]
    second = windows[1]["systematic_components"]
    expected = round(sum(first[name] * second[name] for name in shared) / 1e-34, 6)

    assert matrix[0, 1] == expected
    assert artifact["sensitivity_bounds"]["clock_rho_0_uncorrelated_clock_terms"][
        "psd_verdict"
    ] == "PASS"
    assert artifact["sensitivity_bounds"]["clock_rho_1_fully_correlated_clock_terms"][
        "psd_verdict"
    ] == "PASS"
