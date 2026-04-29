"""Verdict generation for scientific model evaluations."""

from __future__ import annotations

from physics_lab.engines.scoring import ModelScore


def classify_model_score(score: ModelScore) -> str:
    """Assign a cautious verdict to a fitted pendulum approximation."""
    train_mean = score.train_metrics.mean_relative_error
    test_mean = score.test_metrics.mean_relative_error
    test_max = score.test_metrics.max_relative_error

    if test_mean <= 0.001 and test_max <= 0.003:
        return "VALID"
    if test_mean <= 0.005 and test_max <= 0.012:
        return "PARTIALLY_VALID"
    if train_mean > 0.0 and test_mean / train_mean >= 3.0:
        return "OVERFITTED"
    if not all(metric >= 0.0 for metric in (train_mean, test_mean, test_max)):
        return "INCONCLUSIVE"
    return "INVALID"
