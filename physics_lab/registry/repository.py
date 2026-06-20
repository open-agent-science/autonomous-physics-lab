"""Repository-wide validation for public scientific memory."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import shlex
from typing import Any, Callable, Union

import yaml

from physics_lab.registry.agents import load_agent
from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.campaigns import load_campaign_catalog
from physics_lab.registry.claims import load_claim
from physics_lab.registry.docs_links import find_docs_link_issues
from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.golden_results import (
    GOLDEN_RESULTS_MANIFEST,
    golden_result_drifts,
    load_golden_result_entries,
)
from physics_lab.registry.hypotheses import load_hypothesis
from physics_lab.registry.knowledge import load_knowledge
from physics_lab.registry.microtask_runs import load_microtask_run
from physics_lab.registry.mission_freshness import validate_mission_freshness
from physics_lab.registry.nuclear_mass_predictions import load_nuclear_mass_prediction
from physics_lab.registry.research_proposals import (
    load_experiment_proposal,
    load_hypothesis_proposal,
)
from physics_lab.registry.results import load_result
from physics_lab.registry.scientific_memory_integrity import (
    RANGE_LANGUAGE_MARKERS,
    collect_scientific_memory_integrity_issues,
)
from physics_lab.registry.task_discovery import iter_canonical_task_files
from physics_lab.registry.task_views import TASK_VIEW_PATHS, render_task_views
from physics_lab.registry.task_proposals import load_task_proposal
from physics_lab.registry.tasks import load_task, load_task_minimal, task_input_mode
from physics_lab.workflows.artifacts import hash_file


Loader = Callable[[Union[str, Path]], dict[str, Any]]
LOADERS: dict[str, Loader] = {
    "agents": load_agent,
    "campaigns": load_campaign_catalog,
    "agent_runs": load_agent_run,
    "claims": load_claim,
    "examples": load_example_config,
    "experiment_proposals": load_experiment_proposal,
    "experiments": load_experiment,
    "hypothesis_proposals": load_hypothesis_proposal,
    "hypotheses": load_hypothesis,
    "knowledge": load_knowledge,
    "microtask_runs": load_microtask_run,
    "prediction_registry": load_nuclear_mass_prediction,
    "results": load_result,
    "tasks": load_task,
    "task_proposals": load_task_proposal,
}
PATTERNS: dict[str, str] = {
    "agents": "*.yaml",
    "campaigns": "_catalog.yaml",
    "agent_runs": "*/agent_run.yaml",
    "claims": "*.md",
    "examples": "*.yaml",
    "experiment_proposals": "**/*.yaml",
    "experiments": "*.yaml",
    "hypothesis_proposals": "**/*.yaml",
    "hypotheses": "*.yaml",
    "knowledge": "*.md",
    "microtask_runs": "**/*.yaml",
    "prediction_registry": "nuclear_masses/*.yaml",
    "results": "result.yaml",
    "tasks": "*.yaml",
    "task_proposals": "*.yaml",
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
VALIDATION_COMMAND_PATH_PREFIXES = (
    "tests/",
    "scripts/",
    "docs/",
    "physics_lab/",
    "examples/",
    "data/",
    "tasks/",
    "agent_runs/",
    "results/",
)
TASK_VALIDATION_PATH_ERROR_STATUSES = frozenset({"REVIEW_READY"})


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


# Env var that restores the historical ERROR severity for generated task-view
# staleness checks. The default severity is INFO because the post-merge
# sync-active-board GitHub Action regenerates task views on main automatically,
# so PR branches do not need to carry regeneration. Set
# APL_ENFORCE_BOARD_STALENESS=1 in environments that explicitly want a strict
# audit (for example, a maintainer dry-run before disabling the action).
# Missing files remain ERROR regardless.
BOARD_STALENESS_ENV_VAR: str = "APL_ENFORCE_BOARD_STALENESS"


def _board_staleness_severity() -> str:
    """Severity used for generated task-view staleness issues."""

    if os.environ.get(BOARD_STALENESS_ENV_VAR) == "1":
        return "ERROR"
    return "INFO"


# Proposal-status drift (declared status vs effective state derived from the
# canonical task pool) is reported as INFO by default so it never breaks the
# standard --strict --fail-on-warnings flow. A maintainer running an explicit
# proposal-pool audit can escalate it to ERROR. See TASK-0468.
PROPOSAL_DRIFT_ENV_VAR: str = "APL_ENFORCE_PROPOSAL_DRIFT"


def _proposal_drift_severity() -> str:
    """Severity used for task-proposal status-drift issues."""

    if os.environ.get(PROPOSAL_DRIFT_ENV_VAR) == "1":
        return "ERROR"
    return "INFO"


# Research proposal ids were initially allocated inside campaign folders, so
# historical files contain duplicate unscoped ids such as HYP-PROPOSAL-0049 in
# multiple campaigns. Keep the default as INFO so current strict validation does
# not fail on history, but let explicit architecture audits promote this to an
# ERROR while the namespace is being cleaned up.
RESEARCH_PROPOSAL_ID_UNIQUENESS_ENV_VAR: str = (
    "APL_ENFORCE_RESEARCH_PROPOSAL_ID_UNIQUENESS"
)


def _research_proposal_id_uniqueness_severity() -> str:
    """Severity used for duplicate research-proposal id issues."""

    if os.environ.get(RESEARCH_PROPOSAL_ID_UNIQUENESS_ENV_VAR) == "1":
        return "ERROR"
    return "INFO"


def _strict_proposal_drift_issues(root_path: Path) -> list[ValidationIssue]:
    from physics_lab.registry.proposal_triage import proposal_drift_paths

    severity = _proposal_drift_severity()
    issues: list[ValidationIssue] = []
    for path, reasons in proposal_drift_paths(root_path):
        issues.append(
            _issue(
                severity,
                "proposal_status_drift",
                "Proposal status drifts from its effective state: "
                + "; ".join(reasons)
                + ". Run scripts/apl_proposal_triage.py and reconcile via a "
                "maintainer-approved closeout.",
                path=path,
            )
        )
    return issues


def _strict_research_proposal_id_issues(
    *,
    proposal_kind: str,
    proposals: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> list[ValidationIssue]:
    """Report duplicate unscoped research-proposal ids.

    Hypothesis and experiment proposal files are campaign-scoped by path, but
    their ids look globally scoped. Until the historical duplicates are
    normalized, references should include the full path. This check keeps that
    ambiguity visible without making old scientific memory fail CI by default.
    """

    seen: dict[str, Path] = {}
    duplicates: dict[str, list[Path]] = {}
    for path, payload in proposals:
        proposal_id = str(payload.get("id") or "").strip()
        if not proposal_id:
            continue
        previous_path = seen.get(proposal_id)
        if previous_path is not None:
            duplicates.setdefault(proposal_id, [previous_path]).append(path)
        else:
            seen[proposal_id] = path

    severity = _research_proposal_id_uniqueness_severity()
    issues: list[ValidationIssue] = []
    for proposal_id, paths in sorted(duplicates.items()):
        rel_paths = [_relative_path(path, root_path) for path in paths]
        issues.append(
            _issue(
                severity,
                "duplicate_research_proposal_id",
                f"{proposal_kind} id {proposal_id} is declared by multiple files: "
                + ", ".join(rel_paths)
                + ". Treat references to this proposal as path-scoped until the "
                "namespace is normalized; do not add new duplicate unscoped ids.",
                path=rel_paths[0],
            )
        )
    return issues


def _strict_generated_task_navigation_issues(root_path: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    any_task_views_exist = any((root_path / relpath).exists() for relpath in TASK_VIEW_PATHS.values())
    if not any_task_views_exist:
        return issues

    staleness_severity = _board_staleness_severity()
    staleness_message_suffix = (
        " The post-merge sync-active-board GitHub Action regenerates this "
        "file automatically; agents do not need to commit it."
    )

    if any_task_views_exist:
        rendered_views = render_task_views(root_path)
        for lane, relpath in TASK_VIEW_PATHS.items():
            path = root_path / relpath
            if not path.exists():
                # Missing file stays ERROR regardless of env var.
                issues.append(
                    _issue(
                        "ERROR",
                        "missing_generated_task_view",
                        f"Generated task view for {lane} is missing; run sync-active-board.",
                        path=path,
                        root=root_path,
                    )
                )
                continue
            expected_text = rendered_views[lane]
            actual_text = path.read_text(encoding="utf-8")
            if actual_text != expected_text:
                issues.append(
                    _issue(
                        staleness_severity,
                        "stale_generated_task_view",
                        f"Generated task view for {lane} is stale." + staleness_message_suffix,
                        path=path,
                        root=root_path,
                    )
                )
    return issues


def _task_validation_command_tokens(command: str) -> tuple[str, ...]:
    try:
        return tuple(shlex.split(command, posix=False))
    except ValueError:
        return ()


def _normalize_validation_path_token(token: str) -> str | None:
    candidate = token.strip().strip("\"'")
    if not candidate or candidate.startswith("-"):
        return None
    if candidate in {".", ".."}:
        return None
    if "$" in candidate or "%" in candidate:
        return None
    if "://" in candidate or any(marker in candidate for marker in "*?"):
        return None

    candidate = candidate.split("::", 1)[0].rstrip(".,;)")
    normalized = candidate.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("/") or ":" in Path(normalized).anchor:
        return None
    if not any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in VALIDATION_COMMAND_PATH_PREFIXES
    ):
        return None
    return normalized


def _accepted_output_paths(payload: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for value in payload.get("accepted_outputs", []):
        text = str(value).strip().replace("\\", "/")
        if "/" in text:
            paths.add(text.strip("/"))
    return paths


def _is_accepted_output_path(path_text: str, accepted_paths: set[str]) -> bool:
    return any(
        path_text == accepted_path or path_text.startswith(f"{accepted_path.rstrip('/')}/")
        for accepted_path in accepted_paths
    )


def _strict_task_validation_command_path_issues(
    *,
    tasks: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path, payload in tasks:
        if "archive" in path.parts:
            continue
        commands = payload.get("validation", {}).get("commands", [])
        if not isinstance(commands, list):
            continue
        accepted_paths = _accepted_output_paths(payload)
        missing_paths: list[str] = []
        for command in commands:
            if not isinstance(command, str):
                continue
            for token in _task_validation_command_tokens(command):
                path_text = _normalize_validation_path_token(token)
                if path_text is None or _is_accepted_output_path(path_text, accepted_paths):
                    continue
                if not (root_path / path_text).exists():
                    missing_paths.append(path_text)
        if not missing_paths:
            continue

        status = str(payload.get("status", ""))
        severity = "ERROR" if status in TASK_VALIDATION_PATH_ERROR_STATUSES else "INFO"
        unique_missing = ", ".join(sorted(set(missing_paths)))
        issues.append(
            _issue(
                severity,
                "missing_task_validation_command_path",
                "Task validation.commands reference missing repository-local path(s): "
                f"{unique_missing}. Update the task validation command before PR review.",
                path=path,
                root=root_path,
            )
        )
    return issues


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
    if directory == "task_proposals":
        base_path = root / "tasks" / "proposals"
    elif directory == "campaigns":
        # Historical validation count key; the generated portfolio index now
        # lives beside editable campaign profiles.
        base_path = root / "campaign_profiles"
    else:
        base_path = root / directory
    recursive_directories = {"knowledge", "results"}
    if directory == "tasks":
        # Archive-aware: canonical task files may live flat under tasks/ or in
        # tasks/archive/<bucket>/ (see docs/task-archive-migration-plan.md). The
        # shared helper matches TASK-NNNN-*.yaml recursively, excluding the
        # template and the proposals/microtasks subtrees. On the current flat
        # tree this is identical to the previous flat glob.
        iterator: Any = iter_canonical_task_files(root)
    elif directory in recursive_directories:
        iterator = base_path.rglob(pattern)
    else:
        iterator = base_path.glob(pattern)
    for path in sorted(iterator):
        if directory == "tasks" and path.name == "TASK-TEMPLATE.yaml":
            continue
        if directory == "task_proposals" and path.name == "TASK-PROPOSAL-TEMPLATE.yaml":
            continue
        if directory == "hypothesis_proposals" and path.name == "HYP-PROPOSAL-TEMPLATE.yaml":
            continue
        if directory == "experiment_proposals" and path.name == "EXP-PROPOSAL-TEMPLATE.yaml":
            continue
        if directory == "microtask_runs" and path.name == "MICROTASK-RUN-TEMPLATE.yaml":
            continue
        if directory == "prediction_registry" and path.name == "PRED-TEMPLATE.yaml":
            continue
        if directory in {"hypothesis_proposals", "experiment_proposals", "agent_runs", "microtask_runs"}:
            items.append((path, loader(path, root=root)))
        elif directory == "tasks" and (root / "tasks" / "archive") in path.parents:
            # Archived tasks are frozen history: parse without full schema
            # validation so an evolving task schema never forces edits to
            # history (see docs/task-archive-migration-plan.md). Active tasks
            # under tasks/ still go through full load_task schema validation.
            items.append((path, load_task_minimal(path)))
        else:
            items.append((path, loader(path)))
    return items


def _validate_unique_task_ids(
    tasks: list[tuple[Path, dict[str, Any]]],
) -> None:
    """Fail fast when canonical task ids are duplicated."""
    seen_by_id: dict[str, Path] = {}
    for path, payload in tasks:
        task_id = str(payload["id"])
        previous_path = seen_by_id.get(task_id)
        if previous_path is not None:
            raise ValueError(
                "Duplicate canonical task id "
                f"{task_id}: {previous_path} and {path}"
            )
        seen_by_id[task_id] = path


def _validate_unique_result_ids(
    results: list[tuple[Path, dict[str, Any]]],
) -> None:
    """Fail fast when canonical result ids are duplicated."""
    seen_by_id: dict[str, Path] = {}
    for path, payload in results:
        result_id = str(payload["result_id"])
        previous_path = seen_by_id.get(result_id)
        if previous_path is not None:
            raise ValueError(
                "Duplicate canonical result id "
                f"{result_id}: {previous_path} and {path}"
            )
        seen_by_id[result_id] = path


def _validate_microtask_queue_consistency(root_path: Path) -> None:
    """Validate basic consistency for campaign microtask queue files."""
    microtask_root = root_path / "tasks" / "microtasks"
    if not microtask_root.exists():
        return

    for path in sorted(microtask_root.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a YAML mapping")

        expected_queue_id = path.stem
        declared_queue_id = str(payload.get("queue_id") or "").strip()
        if declared_queue_id != expected_queue_id:
            raise ValueError(
                f"{path} declares queue_id {declared_queue_id or '<missing>'}, "
                f"expected {expected_queue_id}"
            )

        microtasks = payload.get("microtasks")
        if not isinstance(microtasks, list):
            raise ValueError(f"{path} must declare microtasks as a list")

        seen_ids: dict[str, int] = {}
        for index, item in enumerate(microtasks, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"{path} microtasks[{index}] must be a mapping")
            microtask_id = str(item.get("id") or "").strip()
            if not microtask_id:
                raise ValueError(f"{path} microtasks[{index}] is missing id")
            previous_index = seen_ids.get(microtask_id)
            if previous_index is not None:
                raise ValueError(
                    f"{path} declares duplicate microtask id {microtask_id} "
                    f"at items {previous_index} and {index}"
                )
            seen_ids[microtask_id] = index


def _validate_microtask_run_conflicts(
    microtask_runs: list[tuple[Path, dict[str, Any]]],
) -> None:
    """Fail fast when microtask run records duplicate active or completed work."""
    seen_by_id: dict[str, Path] = {}
    seen_active_by_item: dict[tuple[str, str], Path] = {}
    seen_completed_by_item: dict[tuple[str, str], Path] = {}
    active_statuses = {"CLAIMED", "IN_PROGRESS", "PR_OPEN", "REVIEW_READY"}
    completed_statuses = {"COMPLETED"}

    for path, payload in microtask_runs:
        run_id = str(payload["id"])
        previous_path = seen_by_id.get(run_id)
        if previous_path is not None:
            raise ValueError(
                "Duplicate microtask run id "
                f"{run_id}: {previous_path} and {path}"
            )
        seen_by_id[run_id] = path

        key = (str(payload["queue_id"]), str(payload["microtask_id"]))
        status = str(payload["status"])
        if status in active_statuses:
            previous_active_path = seen_active_by_item.get(key)
            if previous_active_path is not None:
                queue_id, microtask_id = key
                raise ValueError(
                    "Duplicate active microtask run for "
                    f"{queue_id}/{microtask_id}: {previous_active_path} and {path}"
                )
            seen_active_by_item[key] = path
        if status in completed_statuses:
            previous_completed_path = seen_completed_by_item.get(key)
            if previous_completed_path is not None:
                queue_id, microtask_id = key
                raise ValueError(
                    "Duplicate completed microtask run for "
                    f"{queue_id}/{microtask_id}: {previous_completed_path} and {path}"
                )
            seen_completed_by_item[key] = path


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
        if task_input_mode(payload) == "science_execution":
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
        if payload.get("config_kind") in {
            "nuclear_prediction_variant_factory",
            "nuclear_prediction_synthetic_reveal",
            "quantum_size_effects_baseline",
            "textbook_wien_exact_reference_fixture",
        }:
            continue
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


def _strict_golden_result_issues(root_path: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    manifest_path = root_path / GOLDEN_RESULTS_MANIFEST
    try:
        entries = load_golden_result_entries(root_path)
        drifts = golden_result_drifts(root_path)
    except ValueError as exc:
        return [
            _issue(
                "ERROR",
                "invalid_golden_result_manifest",
                str(exc),
                path=manifest_path,
                root=root_path,
            )
        ]

    for entry in entries:
        if not (root_path / entry.result_path).exists():
            issues.append(
                _issue(
                    "ERROR",
                    "missing_golden_result",
                    f"Golden result target is missing: {entry.result_path}",
                    path=manifest_path,
                    root=root_path,
                )
            )

    for drift in drifts:
        issues.append(
            _issue(
                "ERROR",
                "golden_result_material_drift",
                "Golden result material hash drift for "
                f"{drift.result_id}: expected {drift.expected_hash}, observed {drift.actual_hash}",
                path=drift.result_path,
                root=root_path,
            )
        )
    return issues


def _line_has_local_path_leak(line: str) -> bool:
    stripped = line.strip()
    if "git grep -n " in stripped:
        return False
    if "LOCAL_PATH_MARKERS" in stripped:
        return False
    return any(marker in stripped for marker in LOCAL_PATH_MARKERS)


def _collect_strict_issues(
    *,
    hypotheses: list[tuple[Path, dict[str, Any]]],
    experiments: list[tuple[Path, dict[str, Any]]],
    hypothesis_proposals: list[tuple[Path, dict[str, Any]]],
    experiment_proposals: list[tuple[Path, dict[str, Any]]],
    tasks: list[tuple[Path, dict[str, Any]]],
    claims: list[tuple[Path, dict[str, Any]]],
    knowledge_files: list[tuple[Path, dict[str, Any]]],
    example_configs: list[tuple[Path, dict[str, Any]]],
    results: list[tuple[Path, dict[str, Any]]],
    root_path: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    tracked_files = _tracked_git_files(root_path)

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

    issues.extend(
        ValidationIssue(
            severity=issue.severity,
            code=issue.code,
            message=issue.message,
            path=issue.path,
        )
        for issue in collect_scientific_memory_integrity_issues(
            hypotheses=hypotheses,
            tasks=tasks,
            claims=claims,
            knowledge_files=knowledge_files,
            example_configs=example_configs,
            results=results,
            root_path=root_path,
        )
    )
    issues.extend(_strict_golden_result_issues(root_path))
    issues.extend(
        _strict_research_proposal_id_issues(
            proposal_kind="Hypothesis proposal",
            proposals=hypothesis_proposals,
            root_path=root_path,
        )
    )
    issues.extend(
        _strict_research_proposal_id_issues(
            proposal_kind="Experiment proposal",
            proposals=experiment_proposals,
            root_path=root_path,
        )
    )

    for link_issue in find_docs_link_issues(root_path):
        issues.append(
            _issue(
                "ERROR",
                "broken_docs_link",
                link_issue.message,
                path=link_issue.source_path,
            )
        )

    issues.extend(_strict_generated_task_navigation_issues(root_path))
    issues.extend(
        _strict_task_validation_command_path_issues(
            tasks=tasks,
            root_path=root_path,
        )
    )

    for freshness_issue in validate_mission_freshness(root_path):
        issues.append(
            _issue(
                freshness_issue.severity,
                freshness_issue.code,
                freshness_issue.message,
                path=freshness_issue.path,
                root=root_path,
            )
        )

    issues.extend(_strict_proposal_drift_issues(root_path))

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
    task_proposals = _load_directory(root_path, "task_proposals")
    hypothesis_proposals = _load_directory(root_path, "hypothesis_proposals")
    experiment_proposals = _load_directory(root_path, "experiment_proposals")
    agent_runs = _load_directory(root_path, "agent_runs")
    microtask_runs = _load_directory(root_path, "microtask_runs")
    agents = _load_directory(root_path, "agents")
    campaign_catalogs = _load_directory(root_path, "campaigns")
    claims = _load_directory(root_path, "claims")
    knowledge_files = _load_directory(root_path, "knowledge")
    example_configs = [
        (path, load_example_config(path))
        for path in sorted((root_path / "examples").glob("*.yaml"))
    ]
    results = _load_directory(root_path, "results")
    _validate_unique_task_ids(tasks)
    _validate_unique_result_ids(results)
    _validate_microtask_queue_consistency(root_path)
    _validate_microtask_run_conflicts(microtask_runs)

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
        "task_proposals": len(task_proposals),
        "hypothesis_proposals": len(hypothesis_proposals),
        "experiment_proposals": len(experiment_proposals),
        "agent_runs": len(agent_runs),
        "microtask_runs": len(microtask_runs),
        "agents": len(agents),
        "campaigns": len(campaign_catalogs),
        "claims": len(claims),
        "knowledge": len(knowledge_files),
        "examples": len(example_configs),
        "results": len(results),
    }
    issues = tuple(
        _collect_strict_issues(
            hypotheses=hypotheses,
            experiments=experiments,
            hypothesis_proposals=hypothesis_proposals,
            experiment_proposals=experiment_proposals,
            tasks=tasks,
            claims=claims,
            knowledge_files=knowledge_files,
            example_configs=example_configs,
            results=results,
            root_path=root_path,
        )
    ) if strict else ()
    return RepositoryValidationSummary(root=root_path, counts=counts, strict=strict, issues=issues)
