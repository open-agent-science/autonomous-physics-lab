"""Shared artifact helpers for workflow execution."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess
from typing import Any

from physics_lab.engines.scoring import ModelScore


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


def resolve_path(base_path: Path, relative_path: str) -> Path:
    """Resolve a possibly relative path from a config or directory."""
    candidate = Path(relative_path)
    if candidate.is_absolute():
        return candidate.resolve()
    base_directory = base_path.parent if base_path.is_file() else base_path
    return (base_directory / candidate).resolve()


def hash_file(path: Path, repo_root: Path) -> dict[str, str]:
    """Return a stable SHA-256 digest payload for a repository input file."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        relative_path = path.resolve().relative_to(repo_root.resolve())
        normalized_path = relative_path.as_posix()
    except ValueError:
        normalized_path = str(path.resolve())
    return {"path": normalized_path, "sha256": digest}


def relative_or_absolute(path: Path, repo_root: Path) -> str:
    """Prefer repository-relative paths when possible."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_text_atomic(path: Path, content: str) -> None:
    """Write a text file via a temporary path, then replace atomically."""
    temporary_path = path.with_name(f"{path.name}.tmp")
    temporary_path.write_text(content, encoding="utf-8")
    temporary_path.replace(path)


def git_commit(repo_root: Path) -> str | None:
    """Return the current git commit hash when available."""
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


def task_path(repo_root: Path, task_id: str) -> Path:
    """Locate a task file by task id."""
    matches = sorted((repo_root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        raise ValueError(f"Unable to locate task file for {task_id}")
    return matches[0]


def find_repo_root(start_path: Path) -> Path:
    """Walk up from a path until pyproject.toml is found."""
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists():
            return directory
    return current


def split_dataset(sample_count: int, train_fraction: float) -> int:
    """Compute a safe train/test split index with at least 2 samples on each side."""
    split_index = int(sample_count * train_fraction)
    return min(max(split_index, 2), sample_count - 1)


def serialize_scores(scores: list[ModelScore], verdicts: dict[str, str]) -> list[dict[str, Any]]:
    """Convert scored models to a repository result payload."""
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


def best_result_verdict(model_verdict: str) -> str:
    """Promote a model-level VALID verdict to the repository-level range-aware label."""
    if model_verdict == "VALID":
        return "VALID_IN_RANGE"
    return model_verdict
