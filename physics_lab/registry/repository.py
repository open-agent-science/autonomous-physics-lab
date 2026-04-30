"""Repository-wide validation for public scientific memory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Union

from physics_lab.registry.agents import load_agent
from physics_lab.registry.claims import load_claim
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.knowledge import load_knowledge
from physics_lab.registry.results import load_result
from physics_lab.registry.tasks import load_task
from physics_lab.workflows.artifacts import hash_file


Loader = Callable[[Union[str, Path]], dict[str, Any]]
LOADERS: dict[str, Loader] = {
    "agents": load_agent,
    "claims": load_claim,
    "examples": load_example_config,
    "experiments": load_experiment,
    "hypotheses": load_hypothesis,
    "knowledge": load_knowledge,
    "results": load_result,
    "tasks": load_task,
}
RANGE_LANGUAGE_MARKERS = (
    "valid only",
    "tested range",
    "configured range",
    "range-limited",
    "within the tested",
    "within the sampled",
    "in scope",
)
PATTERNS: dict[str, str] = {
    "agents": "*.yaml",
    "claims": "*.md",
    "examples": "*.yaml",
    "experiments": "*.yaml",
    "hypotheses": "*.yaml",
    "knowledge": "*.md",
    "results": "result.yaml",
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
    recursive_directories = {"knowledge", "results"}
    iterator = (
        (root / directory).rglob(pattern)
        if directory in recursive_directories
        else (root / directory).glob(pattern)
    )
    for path in sorted(iterator):
        items.append((path, loader(path)))
    return items


def _validate_references(
    hypotheses: list[tuple[Path, dict[str, Any]]],
    experiments: list[tuple[Path, dict[str, Any]]],
    tasks: list[tuple[Path, dict[str, Any]]],
    claims: list[tuple[Path, dict[str, Any]]],
    knowledge_files: list[tuple[Path, dict[str, Any]]],
    example_configs: list[tuple[Path, dict[str, Any]]],
    results: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> None:
    hypothesis_ids = {payload["id"] for _, payload in hypotheses}
    experiment_ids = {payload["id"] for _, payload in experiments}
    task_ids = {payload["id"] for _, payload in tasks}
    claim_ids = {payload["id"] for _, payload in claims}
    results_by_id = {payload["result_id"]: payload for _, payload in results}
    result_ids = {payload["result_id"] for _, payload in results}

    for path, payload in experiments:
        if payload["hypothesis_id"] not in hypothesis_ids:
            raise ValueError(
                f"{path} references missing hypothesis_id: {payload['hypothesis_id']}"
            )

    for path, payload in hypotheses:
        for experiment_id in payload["evidence"]["experiments"]:
            if experiment_id not in experiment_ids:
                raise ValueError(f"{path} references missing experiment id: {experiment_id}")
        for result_id in payload["evidence"].get("results", []):
            if result_id not in result_ids:
                raise ValueError(f"{path} references missing result id: {result_id}")

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
        for result_id in payload["evidence"]["results"]:
            if result_id not in result_ids:
                raise ValueError(f"{path} references missing result id: {result_id}")
        referenced_results = [results_by_id[result_id] for result_id in payload["evidence"]["results"]]
        verification_all_pass = all(
            bool(result["verification"]["passed"]) for result in referenced_results
        )
        has_range_limited_result = any(
            str(result["best_verdict"]) == "VALID_IN_RANGE" for result in referenced_results
        )
        claim_status = str(payload["status"])
        if claim_status == "SUPPORTED":
            if not verification_all_pass:
                raise ValueError(
                    f"{path} is marked SUPPORTED but references result evidence with failing verification checks"
                )
            if has_range_limited_result:
                body = str(payload["body"])
                scope = str(payload["scope"])
                combined_text = f"{scope}\n{body}".lower()
                if not any(marker in combined_text for marker in RANGE_LANGUAGE_MARKERS):
                    raise ValueError(
                        f"{path} is marked SUPPORTED from range-limited evidence but does not describe scope or range limits clearly"
                    )

    for path, payload in knowledge_files:
        for hypothesis_id in payload["linked_objects"]["hypotheses"]:
            if hypothesis_id not in hypothesis_ids:
                raise ValueError(f"{path} references missing hypothesis_id: {hypothesis_id}")
        for experiment_id in payload["linked_objects"]["experiments"]:
            if experiment_id not in experiment_ids:
                raise ValueError(f"{path} references missing experiment id: {experiment_id}")
        for claim_id in payload["linked_objects"]["claims"]:
            if claim_id not in claim_ids:
                raise ValueError(f"{path} references missing claim id: {claim_id}")
        for task_id in payload["linked_objects"]["tasks"]:
            if task_id not in task_ids:
                raise ValueError(f"{path} references missing task id: {task_id}")

    for path, payload in example_configs:
        experiment_path = (path.parent / payload["experiment_path"]).resolve()
        hypothesis_path = (path.parent / payload["hypothesis_path"]).resolve()
        result_root = (path.parent / payload["result_root"]).resolve()
        if not experiment_path.exists():
            raise ValueError(f"{path} references missing experiment_path: {payload['experiment_path']}")
        if not hypothesis_path.exists():
            raise ValueError(f"{path} references missing hypothesis_path: {payload['hypothesis_path']}")
        if payload["task_id"] not in task_ids:
            raise ValueError(f"{path} references missing task_id: {payload['task_id']}")
        expected_run_dir = result_root / payload["run_id"]
        if not expected_run_dir.exists():
            raise ValueError(
                f"{path} references missing run directory for run_id {payload['run_id']}: {expected_run_dir}"
            )

    for path, payload in results:
        if payload["hypothesis_id"] not in hypothesis_ids:
            raise ValueError(
                f"{path} references missing hypothesis_id: {payload['hypothesis_id']}"
            )
        if payload["experiment_id"] not in experiment_ids:
            raise ValueError(
                f"{path} references missing experiment_id: {payload['experiment_id']}"
            )
        if path.parent.name != payload["run_id"]:
            raise ValueError(
                f"{path} lives in {path.parent.name} but declares run_id {payload['run_id']}"
            )
        if path.parent.parent.name != payload["experiment_id"]:
            raise ValueError(
                f"{path} lives under {path.parent.parent.name} but declares experiment_id {payload['experiment_id']}"
            )
        if payload["task_id"] not in task_ids:
            raise ValueError(f"{path} references missing task_id: {payload['task_id']}")
        code_reference = (root_path / payload["code_reference"]).resolve()
        if not code_reference.exists():
            raise ValueError(
                f"{path} references missing code_reference: {payload['code_reference']}"
            )
        for artifact_kind, hash_payload in payload["input_file_hashes"].items():
            recorded_input_path = Path(str(hash_payload["path"]))
            resolved_input_path = (
                recorded_input_path.resolve()
                if recorded_input_path.is_absolute()
                else (root_path / recorded_input_path).resolve()
            )
            if not resolved_input_path.exists():
                raise ValueError(
                    f"{path} references missing input file for {artifact_kind}: {hash_payload['path']}"
                )
            current_hash = hash_file(resolved_input_path, root_path)["sha256"]
            if current_hash != hash_payload["sha256"]:
                raise ValueError(
                    f"{path} has input hash drift for {artifact_kind}: {hash_payload['path']}"
                )
        for artifact_name, artifact_path in payload["artifacts"].items():
            resolved_artifact = (root_path / artifact_path).resolve()
            if not resolved_artifact.exists():
                raise ValueError(
                    f"{path} references missing artifact {artifact_name}: {artifact_path}"
                )


def validate_repository(root: str | Path) -> RepositoryValidationSummary:
    """Validate all structured repository artifacts and their cross-references."""
    root_path = Path(root).resolve()
    hypotheses = _load_directory(root_path, "hypotheses")
    experiments = _load_directory(root_path, "experiments")
    tasks = _load_directory(root_path, "tasks")
    agents = _load_directory(root_path, "agents")
    claims = _load_directory(root_path, "claims")
    knowledge_files = _load_directory(root_path, "knowledge")
    example_configs = [
        (path, load_example_config(path))
        for path in sorted((root_path / "examples").glob("*.yaml"))
    ]
    results = _load_directory(root_path, "results")

    _validate_references(
        hypotheses=hypotheses,
        experiments=experiments,
        tasks=tasks,
        claims=claims,
        knowledge_files=knowledge_files,
        example_configs=example_configs,
        results=results,
        root_path=root_path,
    )

    counts = {
        "hypotheses": len(hypotheses),
        "experiments": len(experiments),
        "tasks": len(tasks),
        "agents": len(agents),
        "claims": len(claims),
        "knowledge": len(knowledge_files),
        "examples": len(example_configs),
        "results": len(results),
    }
    return RepositoryValidationSummary(root=root_path, counts=counts)
