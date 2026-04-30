"""Model fitting utilities for pendulum formula discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


FeatureBuilder = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class CandidateModel:
    """A candidate approximation family with a fixed unit intercept."""

    model_id: str
    formula: str
    coefficient_names: tuple[str, ...]
    feature_builder: FeatureBuilder

    @property
    def complexity_score(self) -> int:
        return len(self.coefficient_names)


@dataclass(frozen=True)
class FittedModel:
    """A fitted candidate model."""

    candidate: CandidateModel
    coefficients: dict[str, float]

    def predict(self, theta: np.ndarray) -> np.ndarray:
        features = self.candidate.feature_builder(theta)
        coefficient_vector = np.array(
            [self.coefficients[name] for name in self.candidate.coefficient_names],
            dtype=float,
        )
        return 1.0 + features @ coefficient_vector


def _column_stack(*columns: np.ndarray) -> np.ndarray:
    return np.column_stack(columns).astype(float)


def _x(theta: np.ndarray) -> np.ndarray:
    return np.sin(theta / 2.0) ** 2


def _x_log_one_minus_x(theta: np.ndarray) -> np.ndarray:
    x = _x(theta)
    epsilon = np.clip(1.0 - x, 1.0e-12, None)
    return x * np.log(1.0 / epsilon)


def build_candidate_models(candidate_ids: list[str] | None = None) -> list[CandidateModel]:
    """Return the supported pendulum approximation families for the benchmark."""
    available_models = [
        CandidateModel(
            model_id="model_theta2",
            formula="1 + a*theta^2",
            coefficient_names=("a",),
            feature_builder=lambda theta: _column_stack(theta**2),
        ),
        CandidateModel(
            model_id="model_theta2_theta4",
            formula="1 + a*theta^2 + b*theta^4",
            coefficient_names=("a", "b"),
            feature_builder=lambda theta: _column_stack(theta**2, theta**4),
        ),
        CandidateModel(
            model_id="model_sin2",
            formula="1 + a*sin(theta/2)^2",
            coefficient_names=("a",),
            feature_builder=lambda theta: _column_stack(_x(theta)),
        ),
        CandidateModel(
            model_id="model_x_x2",
            formula="1 + a*x + b*x^2 where x = sin(theta/2)^2",
            coefficient_names=("a", "b"),
            feature_builder=lambda theta: _column_stack(_x(theta), _x(theta) ** 2),
        ),
        CandidateModel(
            model_id="model_x_x2_log",
            formula="1 + a*x + b*x^2 + c*x*log(1/(1 - x)) where x = sin(theta/2)^2",
            coefficient_names=("a", "b", "c"),
            feature_builder=lambda theta: _column_stack(
                _x(theta),
                _x(theta) ** 2,
                _x_log_one_minus_x(theta),
            ),
        ),
    ]
    if candidate_ids is None:
        return available_models
    requested_ids = set(candidate_ids)
    selected_models = [model for model in available_models if model.model_id in requested_ids]
    if len(selected_models) != len(requested_ids):
        available_ids = {model.model_id for model in available_models}
        missing_ids = sorted(requested_ids - available_ids)
        raise ValueError(f"Unsupported candidate model ids: {', '.join(missing_ids)}")
    return selected_models


def fit_candidate_model(model: CandidateModel, theta: np.ndarray, target: np.ndarray) -> FittedModel:
    """Fit a candidate model with a fixed intercept of 1.0."""
    features = model.feature_builder(np.asarray(theta, dtype=float))
    response = np.asarray(target, dtype=float) - 1.0
    solution, *_ = np.linalg.lstsq(features, response, rcond=None)
    coefficients = {
        name: float(value)
        for name, value in zip(model.coefficient_names, solution)
    }
    return FittedModel(candidate=model, coefficients=coefficients)


def fit_all_models(
    theta: np.ndarray,
    target: np.ndarray,
    candidate_ids: list[str] | None = None,
) -> list[FittedModel]:
    """Fit the default candidate families to the training data."""
    return [
        fit_candidate_model(model, theta, target)
        for model in build_candidate_models(candidate_ids=candidate_ids)
    ]
