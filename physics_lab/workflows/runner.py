"""Workflow runner for pendulum formula discovery."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess
from typing import Any

import yaml

from physics_lab import __version__
from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.formula_discovery import FittedModel, fit_all_models
from physics_lab.engines.scoring import ModelScore, score_model
from physics_lab.engines.simulation import generate_pendulum_dataset
from physics_lab.engines.verification import serialize_verification_summary, verify_candidate_model
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.results import validate_result_payload


@dataclass(frozen=True)
class ExperimentArtifacts:
    """Filesystem artifact locations for a workflow run."""

    result_path: Path
    report_path: Path
    metrics_path: Path
    claim_update_path: Path
    knowledge_update_path: Path


@dataclass(frozen=True)
class ExperimentOutcome:
    """Structured result of a workflow run."""

    title: str
    result_id: str
    run_id: str
    hypothesis_id: str
    task_id: str
    train_range: tuple[float, float]
    test_range: tuple[float, float]
    scores: list[ModelScore]
    verdicts: dict[str, str]
    best_model_id: str
    artifacts: ExperimentArtifacts


def _resolve_path(base_path: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        return candidate.resolve()
    base_directory = base_path.parent if base_path.is_file() else base_path
    return (base_directory / candidate).resolve()


def _hash_file(path: Path, repo_root: Path) -> dict[str, str]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        relative_path = path.resolve().relative_to(repo_root.resolve())
        normalized_path = relative_path.as_posix()
    except ValueError:
        normalized_path = str(path.resolve())
    return {"path": normalized_path, "sha256": digest}


def _relative_or_absolute(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _write_text_atomic(path: Path, content: str) -> None:
    temporary_path = path.with_name(f"{path.name}.tmp")
    temporary_path.write_text(content, encoding="utf-8")
    temporary_path.replace(path)


def _git_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip() or None


def _task_path(repo_root: Path, task_id: str) -> Path:
    matches = sorted((repo_root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        raise ValueError(f"Unable to locate task file for {task_id}")
    return matches[0]


def _find_repo_root(start_path: Path) -> Path:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists():
            return directory
    return current


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
    result_id: str,
    run_id: str,
    hypothesis_id: str,
    task_id: str,
    assumptions: list[str],
    limitations: list[str],
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    scores: list[ModelScore],
    verdicts: dict[str, str],
    best_model_id: str,
    verification_summary: dict[str, Any],
) -> str:
    best_score = next(score for score in scores if score.model_id == best_model_id)
    lines = [
        f"# {title}",
        "",
        f"- Result: `{result_id}`",
        f"- Run: `{run_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Task: `{task_id}`",
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
            "## Limitations",
            "",
        ]
    )
    lines.extend([f"- {limitation}" for limitation in limitations])
    lines.extend(
        [
            "",
            "## Verification",
            "",
            f"- Verification gate passed: `{verification_summary['passed']}`",
        ]
    )
    lines.extend(
        [
            *[
                f"- {check['name']}: `{check['status']}`"
                for check in verification_summary["checks"]
            ],
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


def _build_limitations() -> list[str]:
    return [
        "This workflow assumes an ideal mathematical pendulum with no damping or driving force.",
        "Verdicts apply only to the sampled amplitude ranges used in the train and test split.",
        "Candidate formulas are limited to predefined low-order approximation families.",
    ]


def _best_fitted_model(fitted_models: list[FittedModel], model_id: str) -> FittedModel:
    for model in fitted_models:
        if model.candidate.model_id == model_id:
            return model
    raise ValueError(f"Unable to find fitted model for {model_id}")


def _build_claim_update(
    claim_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    best_score: ModelScore,
    best_verdict: str,
    train_range: tuple[float, float],
    test_range: tuple[float, float],
    verification_passed: bool,
) -> str:
    suggested_status = "PARTIALLY_SUPPORTED" if verification_passed and best_verdict in {"VALID", "PARTIALLY_VALID"} else "DRAFT"
    return "\n".join(
        [
            f"# Proposed Update for {claim_id}",
            "",
            f"- Result: `{result_id}`",
            f"- Hypothesis: `{hypothesis_id}`",
            f"- Experiment: `{experiment_id}`",
            f"- Task: `{task_id}`",
            f"- Suggested claim status: `{suggested_status}`",
            "",
            "## Suggested Evidence Update",
            "",
            (
                "The pendulum period depends on amplitude, and within the tested benchmark "
                f"the best candidate approximation was `{best_score.model_id}` "
                f"with verdict `{best_verdict}`."
            ),
            "",
            "## Suggested Range Language",
            "",
            (
                "Valid only within the sampled ranges used by this workflow: "
                f"train `{train_range[0]:.4f}` to `{train_range[1]:.4f}` rad, "
                f"test `{test_range[0]:.4f}` to `{test_range[1]:.4f}` rad."
            ),
            "",
            "## Suggested Metrics",
            "",
            f"- Mean relative error (test): `{best_score.test_metrics.mean_relative_error:.6f}`",
            f"- Max relative error (test): `{best_score.test_metrics.max_relative_error:.6f}`",
            f"- Complexity score: `{best_score.complexity_score}`",
            "",
            "## Suggested Caution",
            "",
            (
                "Keep the claim range-aware and avoid wording that implies exact discovery or universal validity. "
                "Do not auto-promote the claim status unless verification checks pass."
            ),
            "",
        ]
    )


def _build_knowledge_update(
    knowledge_id: str,
    result_id: str,
    experiment_id: str,
    hypothesis_id: str,
    task_id: str,
    best_score: ModelScore,
    best_verdict: str,
    limitations: list[str],
    verification_summary: dict[str, Any],
) -> str:
    lines = [
        f"# Proposed Update for {knowledge_id}",
        "",
        f"- Result: `{result_id}`",
        f"- Hypothesis: `{hypothesis_id}`",
        f"- Experiment: `{experiment_id}`",
        f"- Task: `{task_id}`",
        "",
        "## Suggested Addition",
        "",
        (
            f"The current pendulum benchmark selected `{best_score.model_id}` "
            f"(`{best_score.formula}`) as the best-performing candidate with verdict `{best_verdict}`."
        ),
        "",
        "## Suggested Coefficients",
        "",
    ]
    lines.extend(
        [f"- `{name}` = `{value:.8f}`" for name, value in best_score.coefficients.items()]
    )
    lines.extend(
        [
            "",
            "## Suggested Verification Notes",
            "",
            f"- Verification gate passed: `{verification_summary['passed']}`",
        ]
    )
    lines.extend(
        [
            *[
                f"- {check['name']}: `{check['status']}`"
                for check in verification_summary["checks"]
            ],
            "",
            "## Suggested Limitations Section",
            "",
        ]
    )
    lines.extend([f"- {limitation}" for limitation in limitations])
    lines.extend(
        [
            "",
            "## Suggested Open Questions",
            "",
            "- Can a known-limit-aware approximation outperform the current candidate?",
            "- Should the next benchmark include damping, forcing, or a wider amplitude regime?",
            "",
        ]
    )
    return "\n".join(lines)


def run_pendulum_experiment(config_path: str | Path) -> ExperimentOutcome:
    """Execute the pendulum formula discovery workflow from an example config."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    experiment_path = _resolve_path(config_path, config["experiment_path"])
    hypothesis_path = _resolve_path(config_path, config["hypothesis_path"])
    repo_root = _find_repo_root(config_path)
    experiment = load_experiment(experiment_path)
    hypothesis = load_hypothesis(hypothesis_path)
    task_id = str(config.get("task_id", ""))
    run_id = str(config.get("run_id", ""))
    result_id = str(config.get("result_id", ""))
    result_root = _resolve_path(config_path, str(config.get("result_root", "")))
    if experiment["hypothesis_id"] != hypothesis["id"]:
        raise ValueError(
            "Experiment hypothesis_id does not match loaded hypothesis id: "
            f"{experiment['hypothesis_id']} != {hypothesis['id']}"
        )
    if not task_id:
        raise ValueError("Experiment config must define task_id for result traceability")
    if not run_id:
        raise ValueError("Experiment config must define run_id for run-based artifacts")
    if not result_id:
        raise ValueError("Experiment config must define result_id for result traceability")
    if not str(config.get("result_root", "")):
        raise ValueError("Experiment config must define result_root for run-based outputs")

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
    best_verdict = verdicts[best_model_id]
    best_score = scores[0]
    best_model = _best_fitted_model(fitted_models, best_model_id)

    verification_summary = verify_candidate_model(
        best_model,
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )
    verification_payload = serialize_verification_summary(verification_summary)

    run_dir = result_root / run_id
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    run_dir.mkdir(parents=True, exist_ok=True)
    limitations = _build_limitations()
    task_path = _task_path(repo_root, task_id)
    command_path = _relative_or_absolute(config_path, repo_root)
    command = f"physics-lab run {command_path}"
    input_hashes = {
        "config": _hash_file(config_path, repo_root),
        "experiment": _hash_file(experiment_path, repo_root),
        "hypothesis": _hash_file(hypothesis_path, repo_root),
        "task": _hash_file(task_path, repo_root),
    }
    git_commit = _git_commit(repo_root)

    report_text = _build_report(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        assumptions=list(hypothesis.get("assumptions", [])),
        limitations=limitations,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        verification_summary=verification_payload,
    )
    _write_text_atomic(report_path, report_text)

    result_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": str(experiment["id"]),
        "title": str(experiment["title"]),
        "hypothesis_id": str(experiment["hypothesis_id"]),
        "task_id": task_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_version": __version__,
        "git_commit": git_commit,
        "command": command,
        "input_file_hashes": input_hashes,
        "code_reference": "physics_lab/workflows/runner.py",
        "limitations": limitations,
        "train_range": [float(train_theta[0]), float(train_theta[-1])],
        "test_range": [float(test_theta[0]), float(test_theta[-1])],
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
        "artifacts": {
            "report": _relative_or_absolute(report_path, repo_root),
            "metrics": _relative_or_absolute(metrics_path, repo_root),
            "claim_update": _relative_or_absolute(claim_update_path, repo_root),
            "knowledge_update": _relative_or_absolute(knowledge_update_path, repo_root),
        },
        "scores": _serialize_scores(scores, verdicts),
    }
    validate_result_payload(result_payload, source=result_path)
    _write_text_atomic(result_path, yaml.safe_dump(result_payload, sort_keys=False))

    metrics_payload = {
        "result_id": result_id,
        "run_id": run_id,
        "best_model_id": best_model_id,
        "best_verdict": best_verdict,
        "verification": verification_payload,
        "scores": result_payload["scores"],
    }
    _write_text_atomic(metrics_path, json.dumps(metrics_payload, indent=2))

    claim_update_text = _build_claim_update(
        claim_id="CLAIM-0001",
        result_id=result_id,
        experiment_id=str(experiment["id"]),
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        best_score=best_score,
        best_verdict=best_verdict,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        verification_passed=verification_summary.passed,
    )
    knowledge_update_text = _build_knowledge_update(
        knowledge_id="KNOW-0001",
        result_id=result_id,
        experiment_id=str(experiment["id"]),
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        best_score=best_score,
        best_verdict=best_verdict,
        limitations=limitations,
        verification_summary=verification_payload,
    )
    _write_text_atomic(claim_update_path, claim_update_text)
    _write_text_atomic(knowledge_update_path, knowledge_update_text)

    return ExperimentOutcome(
        title=str(experiment["title"]),
        result_id=result_id,
        run_id=run_id,
        hypothesis_id=str(experiment["hypothesis_id"]),
        task_id=task_id,
        train_range=(float(train_theta[0]), float(train_theta[-1])),
        test_range=(float(test_theta[0]), float(test_theta[-1])),
        scores=scores,
        verdicts=verdicts,
        best_model_id=best_model_id,
        artifacts=ExperimentArtifacts(
            result_path=result_path,
            report_path=report_path,
            metrics_path=metrics_path,
            claim_update_path=claim_update_path,
            knowledge_update_path=knowledge_update_path,
        ),
    )
