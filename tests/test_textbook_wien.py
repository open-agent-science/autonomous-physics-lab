from __future__ import annotations

from pathlib import Path

import pytest

from physics_lab.engines.textbook_wien import (
    WIEN_WAVELENGTH_DISPLACEMENT_M_K,
    check_wien_fixture,
    lambda_peak_m,
    load_wien_fixture,
)


FIXTURE_PATH = Path("data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml")


def test_lambda_peak_scaling_uses_kelvin_temperature() -> None:
    assert lambda_peak_m(5000.0) == pytest.approx(
        WIEN_WAVELENGTH_DISPLACEMENT_M_K / 5000.0
    )


@pytest.mark.parametrize("temperature", [0.0, -1.0])
def test_lambda_peak_rejects_non_positive_kelvin_temperature(temperature: float) -> None:
    with pytest.raises(ValueError, match="positive Kelvin"):
        lambda_peak_m(temperature)


def test_wien_fixture_exact_reference_checks_pass() -> None:
    fixture = load_wien_fixture(FIXTURE_PATH)
    result = check_wien_fixture(fixture)

    assert result.passed
    assert result.row_count == 8
    assert result.max_relative_error <= 1.0e-12


def test_wien_fixture_expected_peaks_are_strictly_monotonic() -> None:
    fixture = load_wien_fixture(FIXTURE_PATH)
    expected = [float(value) for value in fixture["expected_lambda_peak_m"]]

    assert all(left > right for left, right in zip(expected, expected[1:]))


def test_wien_fixture_negative_controls_fail_as_controls() -> None:
    fixture = load_wien_fixture(FIXTURE_PATH)
    controls = fixture["negative_controls"]

    assert controls["wrong_constant"]["expected"] == "fail_scaling_check"
    assert controls["wrong_temperature_unit"]["expected"] == "fail_temperature_unit_check"
    assert controls["wrong_peak_domain"]["expected"] == "fail_wavelength_domain_constant_check"
    assert check_wien_fixture(fixture).negative_controls_passed


def test_wien_fixture_rejects_frequency_domain_convention() -> None:
    fixture = load_wien_fixture(FIXTURE_PATH)
    fixture["source_convention"]["convention"] = "frequency-domain spectral radiance peak"

    with pytest.raises(ValueError, match="wavelength-domain"):
        check_wien_fixture(fixture)
