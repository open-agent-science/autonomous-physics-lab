"""Workflow runner for pendulum formula discovery."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.formula_discovery import fit_all_models
from physics_lab.engines.scoring import ModelScore, score_model
from physics_lab.engines.simulation import generate_pendulum_dataset


@dataclass(frozen=True)
class ExperimentArtifacts:
    """Filesystem artifact locations for a workflow run."""

    report_path: Path
    metrics_path: Path


@dataclass(frozen=True)
class ExperimentOutcome:
    """Structured result of a workflow run."""

    title: str
    hypothesis_id: str
    train_range: tuple[float, float]
    test_range: tuple[float, float]
    scores: list[ModelScore]
    verdicts: dict[str, str]
    best_model_id: str
    artifacts: ExperimentArtifacts


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load a YAML document from disk."""
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in YAML file: {path}")
    return data


def _resolve_path(base_path: Path, relative_path: str) -> Path:
    return (base_path.parent / relative_path).resolve()


def _split_dataset(sample_count: int, train_fraction: float) -> int:
    split_index = int(sample_count * train_fraction)
    return min(max(split_index, 2), sample_count - 1)


def _serialize_scores(scores: list[ModelScore], verdicts: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "model_id": score.model_id,
            "formula": score.formula,
            "coefficients": score.coefficients,
            "complexity_score": score.complexity_score,
            "train_metrics": {
                "mean_relative_error": score.train_metrics.mean_relative_error,
                "max_relative_error": score.train_metrics.max_relative_error,
            },
            "test_metrics": {
                "mean_relative_error": score.test_metrics.mean_relative_error,
                "max_relative_error": score.test_metrics.max_relative_error,
            },
            "composite_score": score.composite_score,
            "verdict": verdicts[score.model_id],
        }
        for score in scores
    ]


def _build_report(
    title: str,
    hypothesis_id: str,
    assumptions: list[str],
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    scores: list[ModelScore],
    verdicts: dict[str, str],
    best_model_id: str,
) -> str:
    best_score = next(score for score in scores if score.model_id == best_model_id)
    lines = [
        f"# {title}",
        "",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Train range (rad): `{train_range[0]:.4f}` to `{train_range[1]:.4f}`",
        f"- Test range (rad): `{test_range[0]:.4f}` to `{test_range[1]:.4f}`",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend([f"- {assumption}" for assumption in assumptions])
    lines.extend(
        [
            "",
            "## Candidate Models",
            "",
            "| Model | Formula | Coefficients | Mean Relative Error (test) | Max Relative Error (test) | Complexity | Verdict |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for score in scores:
        coefficient_text = ", ".join(
            f"{name}={value:.8f}" for name, value in score.coefficients.items()
        )
        lines.append(
            "| "
            f"{score.model_id} | "
            f"`{score.formula}` | "
            f"`{coefficient_text}` | "
            f"{score.test_metrics.mean_relative_error:.6f} | "
            f"{score.test_metrics.max_relative_error:.6f} | "
            f"{score.complexity_score} | "
            f"{verdicts[score.model_id]} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"Best candidate: `{best_score.model_id}` with verdict `{verdicts[best_model_id]}`.",
            "",
            "## Conclusion",
            "",
            "This report describes approximation behavior within the tested amplitude ranges.",
            "It does not claim exact discovery; it identifies the best-performing candidate formula under the current benchmark.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_pendulum_experiment(config_path: str | Path) -> ExperimentOutcome:
    """Execute the pendulum formula discovery workflow from an example config."""
    config_path = Path(config_path).resolve()
    config = load_yaml_file(config_path)
    experiment = load_yaml_file(_resolve_path(config_path, config["experiment_path"]))
    hypothesis = load_yaml_file(_resolve_path(config_path, config["hypothesis_path"]))

    amplitude_range = experiment["data"]["amplitude_range_radians"]
    sample_count = int(experiment["data"]["sample_count"])
    train_fraction = float(config.get("train_fraction", 0.7))
    dataset = generate_pendulum_dataset(
        amplitude_start=float(amplitude_range["start"]),
        amplitude_end=float(amplitude_range["end"]),
        sample_count=sample_count,
    )

    split_index = _split_dataset(sample_count=sample_count, train_fraction=train_fraction)
    train_theta = dataset.theta[:split_index]
    train_target = dataset.period_ratio[:split_index]
    test_theta = dataset.theta[split_index:]
    test_target = dataset.period_ratio[split_index:]

    fitted_models = fit_all_models(train_theta, train_target)
    scores = [
        score_model(
            fitted_model=model,
            train_theta=train_theta,
            train_target=train_target,
            test_theta=test_theta,
            test_target=test_target,
        )
        for model in fitted_models
    ]
    scores.sort(key=lambda model_score: model_score.composite_score)
    verdicts = {score.model_id: classify_model_score(score) for score in scores}
    best_model_id = scores[0].model_id

    report_path = _resolve_path(config_path, config["report_path"])
    metrics_path = _resolve_path(config_path, config["metrics_path"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    report_text = _build_report(
        title=str(experiment["title"]),
        hypothesis_id=str(experiment["hypothesis_id"]),
        assumptions=list(hypothesis.get("assumptions", [])),
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
    )
    report_path.write_text(report_text, encoding="utf-8")

    metrics_payload = {
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(experiment["hypothesis_id"]),
        "train_range": [float(train_theta[0]), float(train_theta[-1])],
        "test_range": [float(test_theta[0]), float(test_theta[-1])],
        "best_model_id": best_model_id,
        "scores": _serialize_scores(scores, verdicts),
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    return ExperimentOutcome(
        title=str(experiment["title"]),
        hypothesis_id=str(experiment["hypothesis_id"]),
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        artifacts=ExperimentArtifacts(report_path=report_path, metrics_path=metrics_path),
    )
