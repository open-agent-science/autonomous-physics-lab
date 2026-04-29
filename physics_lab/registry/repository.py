"""Repository-wide validation for public scientific memory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Union

from physics_lab.registry.agents import load_agent
from physics_lab.registry.claims import load_claim
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.results import load_result
from physics_lab.registry.tasks import load_task


Loader = Callable[[Union[str, Path]], dict[str, Any]]
LOADERS: dict[str, Loader] = {
    "agents": load_agent,
    "claims": load_claim,
    "experiments": load_experiment,
    "hypotheses": load_hypothesis,
    "results": load_result,
    "tasks": load_task,
}
PATTERNS: dict[str, str] = {
    "agents": "*.yaml",
    "claims": "*.md",
    "experiments": "*.yaml",
    "hypotheses": "*.yaml",
    "results": "*.json",
    "tasks": "*.yaml",
}


@dataclass(frozen=True)
class RepositoryValidationSummary:
    """Summary of validated repository artifacts."""

    root: Path
    counts: dict[str, int]

    @property
    def total_files(self) -> int:
        return sum(self.counts.values())


def _load_directory(root: Path, directory: str) -> list[tuple[Path, dict[str, Any]]]:
    loader = LOADERS[directory]
    pattern = PATTERNS[directory]
    items: list[tuple[Path, dict[str, Any]]] = []
    iterator = (root / directory).rglob(pattern) if directory == "results" else (root / directory).glob(pattern)
    for path in sorted(iterator):
        items.append((path, loader(path)))
    return items


def _validate_references(
    hypotheses: list[tuple[Path, dict[str, Any]]],
    experiments: list[tuple[Path, dict[str, Any]]],
    tasks: list[tuple[Path, dict[str, Any]]],
    claims: list[tuple[Path, dict[str, Any]]],
    results: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> None:
    hypothesis_ids = {payload["id"] for _, payload in hypotheses}
    experiment_ids = {payload["id"] for _, payload in experiments}
    task_ids = {payload["id"] for _, payload in tasks}

    for path, payload in experiments:
        if payload["hypothesis_id"] not in hypothesis_ids:
            raise ValueError(
                f"{path} references missing hypothesis_id: {payload['hypothesis_id']}"
            )

    for path, payload in hypotheses:
        for experiment_id in payload["evidence"]["experiments"]:
            if experiment_id not in experiment_ids:
                raise ValueError(f"{path} references missing experiment id: {experiment_id}")

    for path, payload in tasks:
        hypothesis_id = payload["input"]["hypothesis_id"]
        experiment_id = payload["input"]["experiment_id"]
        if hypothesis_id not in hypothesis_ids:
            raise ValueError(f"{path} references missing hypothesis_id: {hypothesis_id}")
        if experiment_id not in experiment_ids:
            raise ValueError(f"{path} references missing experiment_id: {experiment_id}")

    for path, payload in claims:
        hypothesis_id = payload["hypothesis_id"]
        if hypothesis_id not in hypothesis_ids:
            raise ValueError(f"{path} references missing hypothesis_id: {hypothesis_id}")
        for experiment_id in payload["evidence"]["experiments"]:
            if experiment_id not in experiment_ids:
                raise ValueError(f"{path} references missing experiment id: {experiment_id}")

    for path, payload in results:
        if payload["hypothesis_id"] not in hypothesis_ids:
            raise ValueError(
                f"{path} references missing hypothesis_id: {payload['hypothesis_id']}"
            )
        if payload["experiment_id"] not in experiment_ids:
            raise ValueError(
                f"{path} references missing experiment_id: {payload['experiment_id']}"
            )
        if path.parent.name != payload["experiment_id"]:
            raise ValueError(
                f"{path} lives in {path.parent.name} but declares experiment_id {payload['experiment_id']}"
            )
        if payload["task_id"] not in task_ids:
            raise ValueError(f"{path} references missing task_id: {payload['task_id']}")
        code_reference = (root_path / payload["code_reference"]).resolve()
        if not code_reference.exists():
            raise ValueError(
                f"{path} references missing code_reference: {payload['code_reference']}"
            )


def validate_repository(root: str | Path) -> RepositoryValidationSummary:
    """Validate all structured repository artifacts and their cross-references."""
    root_path = Path(root).resolve()
    hypotheses = _load_directory(root_path, "hypotheses")
    experiments = _load_directory(root_path, "experiments")
    tasks = _load_directory(root_path, "tasks")
    agents = _load_directory(root_path, "agents")
    claims = _load_directory(root_path, "claims")
    results = _load_directory(root_path, "results")

    _validate_references(
        hypotheses=hypotheses,
        experiments=experiments,
        tasks=tasks,
        claims=claims,
        results=results,
        root_path=root_path,
    )

    counts = {
        "hypotheses": len(hypotheses),
        "experiments": len(experiments),
        "tasks": len(tasks),
        "agents": len(agents),
        "claims": len(claims),
        "results": len(results),
    }
    return RepositoryValidationSummary(root=root_path, counts=counts)
