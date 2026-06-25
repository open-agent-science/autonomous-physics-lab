from __future__ import annotations

import copy
from pathlib import Path

import pytest

from physics_lab.engines.textbook_wien_firas_peak import (
    ADMISSIBLE_VERDICTS,
    REFERENCE_TEMPERATURE_K,
    WIEN_WAVELENGTH_DISPLACEMENT_M_K,
    build_spectral_points,
    evaluate_wien_firas_peak,
    load_firas_rows,
    reference_wavelength_peak_m,
)


ROOT = Path(__file__).resolve().parents[1]
FIRAS_ROWS = ROOT / "data" / "textbook_formula_audit" / "wien_firas" / "firas_monopole_rows.yaml"


@pytest.fixture(scope="module")
def dataset() -> dict:
    return load_firas_rows(FIRAS_ROWS)


def test_reference_peak_matches_frozen_constant() -> None:
    assert reference_wavelength_peak_m(REFERENCE_TEMPERATURE_K) == pytest.approx(
        WIEN_WAVELENGTH_DISPLACEMENT_M_K / REFERENCE_TEMPERATURE_K
    )


def test_verdict_is_consistent_in_scope_and_admissible(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    assert metric.verdict in ADMISSIBLE_VERDICTS
    assert metric.verdict == "CONSISTENT_IN_SCOPE"


def test_wavelength_peak_close_to_reference_after_jacobian(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    # Interpolated peak should agree tightly; raw-bin within the loose tolerance.
    assert metric.interpolated_relative_difference < 0.005
    assert metric.raw_bin_relative_difference < 0.02
    # Reference is ~1.063 mm (= 9.4 cm^-1) per the source-route note.
    assert metric.reference_wavelength_peak_m == pytest.approx(1.0632e-3, rel=1e-3)


def test_frequency_domain_peak_is_distinct_from_wavelength_peak(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    # Frequency-domain peak (~5.45 cm^-1 / ~163 GHz) differs from the
    # wavelength-domain peak (~9.5 cm^-1): Wien non-invariance via the Jacobian.
    assert metric.frequency_domain_peak_wavenumber_cm_inverse == pytest.approx(5.45)
    assert (
        metric.frequency_domain_peak_wavenumber_cm_inverse
        < metric.wavelength_domain_peak_raw_bin_wavenumber_cm_inverse
    )
    assert metric.controls["frequency_domain_peak_distinct"] is True


def test_no_jacobian_relabel_control_is_rejected(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    # Relabelling the B_nu argmax directly as a wavelength peak is badly wrong.
    assert metric.no_jacobian_relabel_relative_difference > 0.5
    assert metric.controls["no_jacobian_relabel_rejected"] is True


def test_wrong_temperature_control_is_rejected(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    assert metric.wrong_temperature_relative_difference >= 0.05
    assert metric.controls["wrong_temperature_rejected"] is True


def test_all_controls_pass(dataset: dict) -> None:
    metric = evaluate_wien_firas_peak(dataset)
    assert all(metric.controls.values())


def test_spectral_points_apply_unit_conversions(dataset: dict) -> None:
    points = build_spectral_points(dataset)
    first = points[0]
    # 2.27 cm^-1 -> 227 m^-1; lambda = 1/227 m.
    assert first.wavenumber_m_inverse == pytest.approx(227.0)
    assert first.wavelength_m == pytest.approx(1.0 / 227.0)
    assert first.frequency_hz == pytest.approx(299_792_458.0 * 227.0)


def test_residual_only_product_yields_inconclusive_semantics(dataset: dict) -> None:
    residual_like = copy.deepcopy(dataset)
    for row in residual_like["rows"]:
        row["monopole_intensity_class"] = "source_reported_residual"
    metric = evaluate_wien_firas_peak(residual_like)
    assert metric.verdict == "INCONCLUSIVE_PRODUCT_SEMANTICS"
    assert metric.controls["absolute_product_gate"] is False


def test_run_is_deterministic(dataset: dict) -> None:
    first = evaluate_wien_firas_peak(dataset)
    second = evaluate_wien_firas_peak(dataset)
    assert first == second
