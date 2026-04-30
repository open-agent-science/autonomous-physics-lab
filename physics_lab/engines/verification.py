"""Verification checks for pendulum formula discovery evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from physics_lab.engines.formula_discovery import FittedModel
from physics_lab.engines.simulation import exact_pendulum_period_ratio
from physics_lab.engines.symbolic import validate_pendulum_model_dimensions


THETA2_EXPECTED = 1.0 / 16.0
THETA4_EXPECTED = 11.0 / 3072.0
SIN2_EXPECTED = 0.25
X2_EXPECTED = 9.0 / 64.0
SECOND_DERIVATIVE_EXPECTED = 1.0 / 8.0


@dataclass(frozen=True)
class VerificationCheck:
    """A single verification check outcome."""

    name: str
    status: str
    details: str
    metrics: dict[str, float | str]


@dataclass(frozen=True)
class VerificationSummary:
    """Verification summary for a candidate model."""

    checks: list[VerificationCheck]

    @property
    def passed(self) -> bool:
        return all(check.status == "PASS" for check in self.checks if check.status != "PLACEHOLDER")


def _small_angle_limit_check(model: FittedModel) -> VerificationCheck:
    theta = np.array([1.0e-6], dtype=float)
    predicted = float(model.predict(theta)[0])
    deviation = abs(predicted - 1.0)
    status = "PASS" if deviation <= 1.0e-10 else "FAIL"
    return VerificationCheck(
        name="small_angle_limit",
        status=status,
        details="Checks whether the candidate returns T/T0 ~= 1 near zero amplitude.",
        metrics={"predicted": predicted, "deviation": deviation},
    )


def _small_angle_window_accuracy_check(
    model: FittedModel,
    theta_range: tuple[float, float],
) -> VerificationCheck:
    theta_end = min(theta_range[1], 0.2)
    theta_start = min(theta_range[0], theta_end / 2.0, 1.0e-3)
    theta = np.linspace(max(theta_start, 1.0e-4), theta_end, 50, dtype=float)
    predicted = model.predict(theta)
    exact = exact_pendulum_period_ratio(theta)
    relative_error = np.abs(predicted - exact) / exact
    mean_relative_error = float(np.mean(relative_error))
    max_relative_error = float(np.max(relative_error))
    status = "PASS" if max_relative_error <= 1.0e-5 else "FAIL"
    return VerificationCheck(
        name="small_angle_window_accuracy",
        status=status,
        details=(
            "Compares candidate predictions to the exact elliptic-integral solution "
            "on a small-angle window."
        ),
        metrics={
            "theta_window_start": float(theta[0]),
            "theta_window_end": float(theta[-1]),
            "mean_relative_error": mean_relative_error,
            "max_relative_error": max_relative_error,
        },
    )


def _small_angle_curvature_check(model: FittedModel) -> VerificationCheck:
    step = 1.0e-4
    theta = np.array([step], dtype=float)
    origin = np.array([0.0], dtype=float)
    positive = float(model.predict(theta)[0])
    center = float(model.predict(origin)[0])
    negative = float(model.predict(-theta)[0])
    estimated_second_derivative = (positive - 2.0 * center + negative) / (step**2)
    abs_error = abs(estimated_second_derivative - SECOND_DERIVATIVE_EXPECTED)
    status = "PASS" if abs_error <= 0.01 else "FAIL"
    return VerificationCheck(
        name="small_angle_curvature",
        status=status,
        details=(
            "Checks whether the local second derivative near zero matches the exact "
            "pendulum small-angle curvature."
        ),
        metrics={
            "step": step,
            "expected_second_derivative": SECOND_DERIVATIVE_EXPECTED,
            "estimated_second_derivative": estimated_second_derivative,
            "abs_error": abs_error,
        },
    )


def _large_angle_window_accuracy_check(
    model: FittedModel,
    theta_range: tuple[float, float],
) -> VerificationCheck:
    theta_end = theta_range[1]
    theta_start = max(theta_range[0], theta_end - 0.2)
    theta = np.linspace(theta_start, theta_end, 50, dtype=float)
    predicted = model.predict(theta)
    exact = exact_pendulum_period_ratio(theta)
    relative_error = np.abs(predicted - exact) / exact
    mean_relative_error = float(np.mean(relative_error))
    max_relative_error = float(np.max(relative_error))
    status = "PASS" if max_relative_error <= 0.005 else "FAIL"
    return VerificationCheck(
        name="large_angle_window_accuracy",
        status=status,
        details=(
            "Compares candidate predictions to the exact elliptic-integral solution "
            "on the upper end of the configured amplitude range."
        ),
        metrics={
            "theta_window_start": float(theta[0]),
            "theta_window_end": float(theta[-1]),
            "mean_relative_error": mean_relative_error,
            "max_relative_error": max_relative_error,
        },
    )


def _evenness_check(model: FittedModel, theta_range: tuple[float, float]) -> VerificationCheck:
    theta = np.linspace(theta_range[0], theta_range[1], 25, dtype=float)
    positive = model.predict(theta)
    negative = model.predict(-theta)
    max_difference = float(np.max(np.abs(positive - negative)))
    status = "PASS" if max_difference <= 1.0e-10 else "FAIL"
    return VerificationCheck(
        name="evenness",
        status=status,
        details="Checks whether the candidate model is even in theta.",
        metrics={"max_difference": max_difference},
    )


def _monotonicity_check(model: FittedModel, theta_range: tuple[float, float]) -> VerificationCheck:
    theta = np.linspace(theta_range[0], theta_range[1], 100, dtype=float)
    predicted = model.predict(theta)
    diffs = np.diff(predicted)
    min_step = float(np.min(diffs))
    status = "PASS" if np.all(diffs >= -1.0e-10) else "FAIL"
    return VerificationCheck(
        name="monotonicity",
        status=status,
        details="Checks whether the candidate is non-decreasing on the configured theta range.",
        metrics={"min_step": min_step},
    )


def _dimensional_consistency_check(model: FittedModel) -> VerificationCheck:
    result = validate_pendulum_model_dimensions(model.candidate.model_id)
    return VerificationCheck(
        name="dimensional_consistency",
        status=result.status,
        details=result.details,
        metrics=result.metrics,
    )


def _known_small_angle_coefficients_check(model: FittedModel) -> VerificationCheck:
    expected: dict[str, float] | None = None
    if model.candidate.model_id == "model_theta2":
        expected = {"a": THETA2_EXPECTED}
    elif model.candidate.model_id == "model_theta2_theta4":
        expected = {"a": THETA2_EXPECTED, "b": THETA4_EXPECTED}
    elif model.candidate.model_id == "model_sin2":
        expected = {"a": SIN2_EXPECTED}
    elif model.candidate.model_id == "model_x_x2":
        expected = {"a": SIN2_EXPECTED, "b": X2_EXPECTED}

    if expected is None:
        return VerificationCheck(
            name="known_small_angle_coefficients",
            status="PLACEHOLDER",
            details="No expected coefficient mapping for this model family.",
            metrics={},
        )

    errors = {
        name: abs(model.coefficients[name] - expected_value)
        for name, expected_value in expected.items()
    }
    status = "PASS" if all(error <= 0.05 for error in errors.values()) else "FAIL"
    metrics: dict[str, float | str] = {}
    for name, expected_value in expected.items():
        metrics[f"expected_{name}"] = expected_value
        metrics[f"actual_{name}"] = model.coefficients[name]
        metrics[f"abs_error_{name}"] = errors[name]
    return VerificationCheck(
        name="known_small_angle_coefficients",
        status=status,
        details="Compares fitted low-order coefficients to the known small-angle series.",
        metrics=metrics,
    )


def verify_candidate_model(
    model: FittedModel,
    theta_range: tuple[float, float],
) -> VerificationSummary:
    """Run the pendulum evidence checks for a candidate model."""
    checks = [
        _small_angle_limit_check(model),
        _small_angle_window_accuracy_check(model, theta_range=theta_range),
        _small_angle_curvature_check(model),
        _large_angle_window_accuracy_check(model, theta_range=theta_range),
        _evenness_check(model, theta_range=theta_range),
        _monotonicity_check(model, theta_range=theta_range),
        _dimensional_consistency_check(model),
        _known_small_angle_coefficients_check(model),
    ]
    return VerificationSummary(checks=checks)


def serialize_verification_summary(summary: VerificationSummary) -> dict[str, Any]:
    """Convert verification results into a JSON/YAML-safe structure."""
    return {
        "passed": summary.passed,
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "details": check.details,
                "metrics": check.metrics,
            }
            for check in summary.checks
        ],
    }
