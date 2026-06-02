"""Deterministic exact-reference checks for Wien displacement fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


WIEN_WAVELENGTH_DISPLACEMENT_M_K = 0.002897771955
WAVELENGTH_DOMAIN_CONVENTION = "wavelength-domain spectral radiance peak, lambda_peak = b / T"


@dataclass(frozen=True)
class WienFixtureCheckResult:
    """Summary of deterministic fixture checks."""

    row_count: int
    max_relative_error: float
    monotonic_decreasing: bool
    scaling_check_passed: bool
    negative_controls_passed: bool

    @property
    def passed(self) -> bool:
        """Return True only when all fixture checks pass."""
        return (
            self.monotonic_decreasing
            and self.scaling_check_passed
            and self.negative_controls_passed
        )


def lambda_peak_m(temperature_k: float, constant_m_k: float = WIEN_WAVELENGTH_DISPLACEMENT_M_K) -> float:
    """Return wavelength-domain Wien peak in meters for a Kelvin temperature."""
    if temperature_k <= 0:
        raise ValueError("temperature_k must be positive Kelvin")
    return constant_m_k / temperature_k


def load_wien_fixture(path: str | Path) -> dict[str, Any]:
    """Load a Wien exact-reference fixture from YAML."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("fixture must be a YAML mapping")
    return data


def check_wien_fixture(fixture: dict[str, Any]) -> WienFixtureCheckResult:
    """Validate deterministic Wien fixture rows and declared negative controls."""
    source = fixture["source_convention"]
    constant = float(source["value_m_k"])
    if source.get("convention") != WAVELENGTH_DOMAIN_CONVENTION:
        raise ValueError("fixture must declare the wavelength-domain spectral-radiance convention")

    temperatures = [float(value) for value in fixture["temperature_grid_k"]]
    expected = [float(value) for value in fixture["expected_lambda_peak_m"]]
    tolerance = float(fixture["checks"]["relative_tolerance"])
    if len(temperatures) != len(expected):
        raise ValueError("temperature and expected lambda arrays must have equal length")

    calculated = [lambda_peak_m(temperature, constant) for temperature in temperatures]
    relative_errors = [
        abs(calculated_value - expected_value) / expected_value
        for calculated_value, expected_value in zip(calculated, expected, strict=True)
    ]
    max_relative_error = max(relative_errors, default=0.0)
    monotonic_decreasing = all(
        left > right for left, right in zip(expected, expected[1:], strict=False)
    )
    scaling_check_passed = all(
        abs((temperature * wavelength) - constant) / constant <= tolerance
        for temperature, wavelength in zip(temperatures, expected, strict=True)
    ) and max_relative_error <= tolerance

    negative_controls_passed = _check_negative_controls(fixture, temperatures, tolerance)
    return WienFixtureCheckResult(
        row_count=len(temperatures),
        max_relative_error=max_relative_error,
        monotonic_decreasing=monotonic_decreasing,
        scaling_check_passed=scaling_check_passed,
        negative_controls_passed=negative_controls_passed,
    )


def _check_negative_controls(
    fixture: dict[str, Any], temperatures: list[float], tolerance: float
) -> bool:
    """Return True when declared negative controls fail for the intended reason."""
    controls = fixture["negative_controls"]
    expected = [float(value) for value in fixture["expected_lambda_peak_m"]]

    wrong_constant = float(controls["wrong_constant"]["value_m_k"])
    wrong_constant_lambdas = [lambda_peak_m(temperature, wrong_constant) for temperature in temperatures]
    wrong_constant_fails = any(
        abs(control - expected_value) / expected_value > tolerance
        for control, expected_value in zip(wrong_constant_lambdas, expected, strict=True)
    )

    wrong_temperature_unit_fails = controls["wrong_temperature_unit"].get("input_unit") != "kelvin"
    wrong_peak_domain_fails = (
        controls["wrong_peak_domain"].get("convention") != WAVELENGTH_DOMAIN_CONVENTION
    )
    return wrong_constant_fails and wrong_temperature_unit_fails and wrong_peak_domain_fails
