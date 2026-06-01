"""Advisory local-validation planning for canonical task work."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import platform

from physics_lab.registry.review_git import (
    changed_files_vs_main,
    current_branch,
    working_tree_changed_files,
)
from physics_lab.registry.tasks import load_task


FAST_LANE_PREFIXES = (
    "examples/",
    "physics_lab/cli.py",
    "physics_lab/engines/",
    "physics_lab/factories/",
    "physics_lab/workflows/",
)
FAST_LANE_PATHS = (
    ".github/workflows/ci.yml",
    "pyproject.toml",
    "scripts/validate_fast.py",
)


@dataclass(frozen=True)
class TaskValidationPlan:
    """A dynamic, reviewable recommendation for local task validation."""

    task_id: str
    task_file: str
    changed_files: tuple[str, ...]
    task_commands: tuple[str, ...]
    fast_lane_recommended: bool
    windows_runtime_probe_recommended: bool
    validation_layers: tuple[str, ...]
    notes: tuple[str, ...]


def _task_file(root: Path, task_id: str) -> Path:
    matches = sorted((root / "tasks").glob(f"{task_id}-*.yaml"))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one canonical task file for {task_id}; found {len(matches)}")
    return matches[0]


def _changed_files(root: Path) -> tuple[str, ...]:
    branch = current_branch(root)
    if branch:
        return changed_files_vs_main(root, branch)
    return working_tree_changed_files(root)


def _needs_fast_lane(changed_files: tuple[str, ...]) -> bool:
    for path in changed_files:
        normalized = path.replace("\\", "/")
        if normalized in FAST_LANE_PATHS:
            return True
        if any(normalized.startswith(prefix) for prefix in FAST_LANE_PREFIXES):
            return True
    return False


def build_task_validation_plan(
    root: Path,
    task_id: str,
    *,
    changed_files: tuple[str, ...] | None = None,
    system: str | None = None,
) -> TaskValidationPlan:
    """Build an advisory plan without writing repository state."""
    root = root.resolve()
    task_file = _task_file(root, task_id)
    payload = load_task(task_file)
    validation = payload.get("validation", {})
    commands = tuple(str(command) for command in validation.get("commands", ()))
    files = changed_files if changed_files is not None else _changed_files(root)
    fast_lane_recommended = _needs_fast_lane(files)
    windows = (system or platform.system()).lower() == "windows"

    notes = [
        "Run the canonical task commands locally before handoff.",
        "CI remains the broad cross-platform validation authority for the PR.",
    ]
    if fast_lane_recommended:
        notes.append(
            "The changed surface touches runtime or validation configuration; run the parallel fast lane locally."
        )
    else:
        notes.append(
            "The changed surface is narrow; do not add a serial full-suite run unless targeted debugging requires it."
        )
    if windows:
        notes.append(
            "If parallel pytest fails on Windows, run the doctor probe and use targeted `-n0` debugging instead of an automatic serial full-suite fallback."
        )
    validation_layers = [
        "preflight: run cheap deterministic task commands first",
        (
            "fast_parallel: run `python3 scripts/validate_fast.py` locally"
            if fast_lane_recommended
            else "fast_parallel: optional for this narrow diff"
        ),
        (
            "resource_sensitive: Windows fast lane runs measured heavy tests as a final `-n0` layer"
            if windows
            else "resource_sensitive: xdist `loadgroup` keeps measured heavy tests on one worker"
        ),
        "broad_ci: let PR CI run the broad cross-platform lane",
        "full_repo: keep slow smoke tests as a final release or explicitly required layer",
    ]

    return TaskValidationPlan(
        task_id=str(payload["id"]),
        task_file=task_file.relative_to(root).as_posix(),
        changed_files=tuple(files),
        task_commands=commands,
        fast_lane_recommended=fast_lane_recommended,
        windows_runtime_probe_recommended=windows,
        validation_layers=tuple(validation_layers),
        notes=tuple(notes),
    )
