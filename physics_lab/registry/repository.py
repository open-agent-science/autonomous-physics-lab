"""Repository-wide validation for public scientific memory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
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
    "linear, unforced",
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
STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS = {
    "evidence_policy",
    "repository_validation",
    "release_preparation",
    "release_prep",
}
STRICT_TEXT_SCAN_ROOTS = (
    "README.md",
    "AGENTS.md",
    "CODEX_TASK.md",
    "CONTRIBUTING.md",
    "docs",
    "claims",
    "knowledge",
    "results",
)
LOCAL_PATH_MARKERS = (
    "/Users/",
    "Autonomous%20Physics%20Lab",
    "MacBook",
)


@dataclass(frozen=True)
class ValidationIssue:
    """Structured strict-validation issue."""

    severity: str
    code: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class RepositoryValidationSummary:
    """Summary of validated repository artifacts."""

    root: Path
    counts: dict[str, int]
    strict: bool = False
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def total_files(self) -> int:
        return sum(self.counts.values())

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "WARNING")

    @property
    def info_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "INFO")


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _issue(
    severity: str,
    code: str,
    message: str,
    *,
    path: Path | str | None = None,
    root: Path | None = None,
) -> ValidationIssue:
    normalized_path: str | None = None
    if path is not None:
        if isinstance(path, Path):
            normalized_path = _relative_path(path, root or path.parent)
        else:
            normalized_path = path
    return ValidationIssue(severity=severity, code=code, message=message, path=normalized_path)


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


def _tracked_git_files(root_path: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root_path), "ls-files"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _strict_text_paths(root_path: Path) -> list[Path]:
    paths: list[Path] = []
    for entry in STRICT_TEXT_SCAN_ROOTS:
        candidate = root_path / entry
        if candidate.is_file():
            paths.append(candidate)
        elif candidate.is_dir():
            for path in sorted(candidate.rglob("*")):
                if path.is_file() and path.name != ".DS_Store":
                    paths.append(path)
    return paths


def _line_has_local_path_leak(line: str) -> bool:
    stripped = line.strip()
    if "git grep -n " in stripped:
        return False
    if "LOCAL_PATH_MARKERS" in stripped:
        return False
    return any(marker in stripped for marker in LOCAL_PATH_MARKERS)


def _strict_required_run_artifacts(
    result_path: Path,
    payload: dict[str, Any],
    *,
    root_path: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    run_dir = result_path.parent
    required_paths = {
        "result.yaml": run_dir / "result.yaml",
        "metrics.json": run_dir / "metrics.json",
        "report.md": run_dir / "report.md",
        "claim_update.md": run_dir / "claim_update.md",
        "claim_update.patch.md": run_dir / "claim_update.patch.md",
        "knowledge_update.md": run_dir / "knowledge_update.md",
        "knowledge_update.patch.md": run_dir / "knowledge_update.patch.md",
        "review_summary.md": run_dir / "review_summary.md",
        "inputs/config.yaml": run_dir / "inputs" / "config.yaml",
        "inputs/experiment.yaml": run_dir / "inputs" / "experiment.yaml",
        "inputs/hypothesis.yaml": run_dir / "inputs" / "hypothesis.yaml",
        "inputs/task.yaml": run_dir / "inputs" / "task.yaml",
    }
    for label, required_path in required_paths.items():
        if not required_path.exists():
            issues.append(
                _issue(
                    "ERROR",
                    "missing_run_artifact",
                    f"Missing required run artifact: {label}",
                    path=result_path,
                    root=root_path,
                )
            )

    expected_artifact_paths = {
        "report": _relative_path(run_dir / "report.md", root_path),
        "metrics": _relative_path(run_dir / "metrics.json", root_path),
        "claim_update": _relative_path(run_dir / "claim_update.md", root_path),
        "claim_update_patch": _relative_path(run_dir / "claim_update.patch.md", root_path),
        "knowledge_update": _relative_path(run_dir / "knowledge_update.md", root_path),
        "knowledge_update_patch": _relative_path(run_dir / "knowledge_update.patch.md", root_path),
        "review_summary": _relative_path(run_dir / "review_summary.md", root_path),
    }
    for artifact_name, expected_path in expected_artifact_paths.items():
        actual_path = str(payload["artifacts"].get(artifact_name, ""))
        if actual_path != expected_path:
            issues.append(
                _issue(
                    "ERROR",
                    "noncanonical_artifact_path",
                    f"{artifact_name} should point to {expected_path}, not {actual_path or 'missing value'}",
                    path=result_path,
                    root=root_path,
                )
            )

    expected_input_paths = {
        "config": _relative_path(run_dir / "inputs" / "config.yaml", root_path),
        "experiment": _relative_path(run_dir / "inputs" / "experiment.yaml", root_path),
        "hypothesis": _relative_path(run_dir / "inputs" / "hypothesis.yaml", root_path),
        "task": _relative_path(run_dir / "inputs" / "task.yaml", root_path),
    }
    for artifact_name, expected_path in expected_input_paths.items():
        actual_path = str(payload["input_file_hashes"].get(artifact_name, {}).get("path", ""))
        if actual_path != expected_path:
            issues.append(
                _issue(
                    "ERROR",
                    "noncanonical_input_snapshot",
                    f"{artifact_name} hash should point to immutable run snapshot {expected_path}, not {actual_path or 'missing value'}",
                    path=result_path,
                    root=root_path,
                )
            )
    return issues


def _strict_claim_status_issues(
    claim_path: Path,
    claim_payload: dict[str, Any],
    *,
    referenced_results: list[dict[str, Any]],
    root_path: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    claim_status = str(claim_payload["status"])
    verification_all_pass = all(bool(result["verification"]["passed"]) for result in referenced_results)
    has_range_limited_result = any(
        str(result["best_verdict"]) == "VALID_IN_RANGE" for result in referenced_results
    )
    scope_text = str(claim_payload["scope"])
    body_text = str(claim_payload["body"])
    combined_text = f"{scope_text}\n{body_text}".lower()

    if claim_status == "PARTIALLY_SUPPORTED":
        if not referenced_results:
            issues.append(
                _issue(
                    "ERROR",
                    "claim_without_results",
                    "PARTIALLY_SUPPORTED claim must reference at least one result.",
                    path=claim_path,
                    root=root_path,
                )
            )
        if not verification_all_pass:
            issues.append(
                _issue(
                    "ERROR",
                    "claim_failed_verification",
                    "PARTIALLY_SUPPORTED claim references result evidence with failing verification checks.",
                    path=claim_path,
                    root=root_path,
                )
            )
        if has_range_limited_result and not any(marker in combined_text for marker in RANGE_LANGUAGE_MARKERS):
            issues.append(
                _issue(
                    "ERROR",
                    "claim_missing_range_language",
                    "PARTIALLY_SUPPORTED claim with range-limited evidence must describe scope explicitly.",
                    path=claim_path,
                    root=root_path,
                )
            )

    if claim_status == "DRAFT" and referenced_results and verification_all_pass:
        issues.append(
            _issue(
                "INFO",
                "draft_with_passing_evidence",
                "Claim remains DRAFT despite passing referenced evidence; human review may still be appropriate.",
                path=claim_path,
                root=root_path,
            )
        )

    return issues


def _collect_strict_issues(
    *,
    hypotheses: list[tuple[Path, dict[str, Any]]],
    experiments: list[tuple[Path, dict[str, Any]]],
    tasks: list[tuple[Path, dict[str, Any]]],
    claims: list[tuple[Path, dict[str, Any]]],
    knowledge_files: list[tuple[Path, dict[str, Any]]],
    example_configs: list[tuple[Path, dict[str, Any]]],
    results: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    tracked_files = _tracked_git_files(root_path)
    results_by_id = {payload["result_id"]: payload for _, payload in results}
    referenced_result_ids = {
        result_id
        for _, payload in hypotheses
        for result_id in payload["evidence"].get("results", [])
    } | {
        result_id
        for _, payload in claims
        for result_id in payload["evidence"]["results"]
    }
    result_task_ids = {str(payload["task_id"]) for _, payload in results}

    if not (root_path / "README.md").exists():
        issues.append(_issue("ERROR", "missing_readme", "Repository is missing README.md"))
    if not (root_path / "LICENSE").exists():
        issues.append(_issue("ERROR", "missing_license", "Repository is missing LICENSE"))

    for tracked_path in sorted(tracked_files):
        if tracked_path.endswith(".DS_Store"):
            issues.append(
                _issue(
                    "ERROR",
                    "tracked_ds_store",
                    "Tracked .DS_Store files should not be committed.",
                    path=tracked_path,
                )
            )
        if tracked_path.startswith(".pytest_cache/") or tracked_path.startswith(".ruff_cache/"):
            issues.append(
                _issue(
                    "ERROR",
                    "tracked_cache_file",
                    "Tracked cache files should not be committed.",
                    path=tracked_path,
                )
            )

    for path in _strict_text_paths(root_path):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line in content.splitlines():
            if _line_has_local_path_leak(line):
                issues.append(
                    _issue(
                        "ERROR",
                        "absolute_local_path",
                        "Found local path marker in tracked text.",
                        path=path,
                        root=root_path,
                    )
                )
                break

    for result_path, result_payload in results:
        issues.extend(
            _strict_required_run_artifacts(
                result_path,
                result_payload,
                root_path=root_path,
            )
        )
        result_id = str(result_payload["result_id"])
        if result_id not in referenced_result_ids:
            issues.append(
                _issue(
                    "WARNING",
                    "orphan_result",
                    "Result artifact is not referenced by any hypothesis or claim evidence.",
                    path=result_path,
                    root=root_path,
                )
            )

    for claim_path, claim_payload in claims:
        referenced_results = [
            results_by_id[result_id]
            for result_id in claim_payload["evidence"]["results"]
            if result_id in results_by_id
        ]
        issues.extend(
            _strict_claim_status_issues(
                claim_path,
                claim_payload,
                referenced_results=referenced_results,
                root_path=root_path,
            )
        )

    for task_path, task_payload in tasks:
        task_id = str(task_payload["id"])
        task_status = str(task_payload["status"])
        task_type = str(task_payload["type"])
        if task_status == "DONE" and task_id not in result_task_ids and task_type not in STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS:
            issues.append(
                _issue(
                    "WARNING",
                    "done_task_without_result",
                    "DONE task does not have a linked result artifact and is not on the documented exception list.",
                    path=task_path,
                    root=root_path,
                )
            )

    for knowledge_path, knowledge_payload in knowledge_files:
        linked = knowledge_payload["linked_objects"]
        if not any(linked.values()):
            issues.append(
                _issue(
                    "WARNING",
                    "knowledge_without_links",
                    "Knowledge note has no linked objects.",
                    path=knowledge_path,
                    root=root_path,
                )
            )

    for example_path, example_payload in example_configs:
        result_root = (example_path.parent / example_payload["result_root"]).resolve()
        expected_run_dir = result_root / str(example_payload["run_id"])
        canonical_result = expected_run_dir / "result.yaml"
        if not canonical_result.exists():
            issues.append(
                _issue(
                    "ERROR",
                    "missing_canonical_result",
                    "Example config points to a run directory without canonical result.yaml.",
                    path=example_path,
                    root=root_path,
                )
            )

    return issues


def validate_repository(
    root: str | Path,
    *,
    strict: bool = False,
) -> RepositoryValidationSummary:
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
    issues = tuple(
        _collect_strict_issues(
            hypotheses=hypotheses,
            experiments=experiments,
            tasks=tasks,
            claims=claims,
            knowledge_files=knowledge_files,
            example_configs=example_configs,
            results=results,
            root_path=root_path,
        )
    ) if strict else ()
    return RepositoryValidationSummary(root=root_path, counts=counts, strict=strict, issues=issues)
