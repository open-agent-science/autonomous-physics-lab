"""Scoring helpers for pendulum formula discovery."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_lab.engines.formula_discovery import FittedModel


@dataclass(frozen=True)
class ErrorMetrics:
    """Relative error metrics for a model evaluation."""

    mean_relative_error: float
    max_relative_error: float


@dataclass(frozen=True)
class ModelScore:
    """Complete evaluation data for a fitted model."""

    model_id: str
    formula: str
    coefficients: dict[str, float]
    complexity_score: int
    train_metrics: ErrorMetrics
    test_metrics: ErrorMetrics
    composite_score: float


def compute_error_metrics(predicted: np.ndarray, expected: np.ndarray) -> ErrorMetrics:
    """Compute relative error summaries for a prediction array."""
    predicted_array = np.asarray(predicted, dtype=float)
    expected_array = np.asarray(expected, dtype=float)
    relative_error = np.abs(predicted_array - expected_array) / expected_array
    return ErrorMetrics(
        mean_relative_error=float(np.mean(relative_error)),
        max_relative_error=float(np.max(relative_error)),
    )


def score_model(
    fitted_model: FittedModel,
    train_theta: np.ndarray,
    train_target: np.ndarray,
    test_theta: np.ndarray,
    test_target: np.ndarray,
) -> ModelScore:
    """Evaluate a fitted model on train and test data."""
    train_metrics = compute_error_metrics(fitted_model.predict(train_theta), train_target)
    test_metrics = compute_error_metrics(fitted_model.predict(test_theta), test_target)
    complexity_score = fitted_model.candidate.complexity_score
    composite_score = (
        test_metrics.mean_relative_error
        + (0.25 * test_metrics.max_relative_error)
        + (0.001 * complexity_score)
    )
    return ModelScore(
        model_id=fitted_model.candidate.model_id,
        formula=fitted_model.candidate.formula,
        coefficients=fitted_model.coefficients,
        complexity_score=complexity_score,
        train_metrics=train_metrics,
        test_metrics=test_metrics,
        composite_score=float(composite_score),
    )
