"""Append-only microtask run registry helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from physics_lab.registry.validation import validate_document


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in microtask run file: {path}")
    return data


def _load_queue_payload(root: Path, queue_id: str) -> dict[str, Any]:
    queue_path = root / "tasks" / "microtasks" / f"{queue_id}.yaml"
    if not queue_path.exists():
        raise ValueError(f"Microtask run references missing queue file: {queue_path}")
    with queue_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in microtask queue file: {queue_path}")
    if str(payload.get("queue_id") or "").strip() != queue_id:
        raise ValueError(f"Microtask queue file {queue_path} declares a mismatched queue_id")
    return payload


def _queue_contains_microtask(queue_payload: dict[str, Any], microtask_id: str) -> bool:
    microtasks = queue_payload.get("microtasks")
    if not isinstance(microtasks, list):
        return False
    return any(isinstance(item, dict) and item.get("id") == microtask_id for item in microtasks)


def _assert_repo_relative(path_value: str, *, source: str | Path) -> None:
    path = Path(path_value)
    if path.is_absolute():
        raise ValueError(f"{source} must use repository-relative paths, not {path_value}")
    if ".." in path.parts:
        raise ValueError(f"{source} must not use parent-directory paths: {path_value}")


def validate_microtask_run_payload(
    payload: dict[str, Any],
    *,
    source: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate an append-only microtask run record."""
    validate_document(payload, kind="microtask_run", source=source)

    queue_id = str(payload["queue_id"])
    microtask_id = str(payload["microtask_id"])
    branch = str(payload["branch"])
    result_note = payload.get("result_note")

    if not branch.startswith("agent/"):
        raise ValueError(f"{source} branch must use an agent-owned branch: {branch}")
    if result_note is not None:
        _assert_repo_relative(str(result_note), source=source)

    root_path = Path(root).resolve() if root is not None else None
    if root_path is not None:
        source_path = Path(source).resolve()
        try:
            relative_source = source_path.relative_to(root_path)
        except ValueError as exc:
            raise ValueError(f"{source} must live under repository root {root_path}") from exc
        if not relative_source.parts or relative_source.parts[0] != "microtask_runs":
            raise ValueError(f"{source} must live under microtask_runs/")
        if len(relative_source.parts) < 3 or relative_source.parts[1] != queue_id:
            raise ValueError(
                f"{source} must live under microtask_runs/{queue_id}/"
            )
        queue_payload = _load_queue_payload(root_path, queue_id)
        if not _queue_contains_microtask(queue_payload, microtask_id):
            raise ValueError(f"{source} references unknown microtask id {microtask_id} in {queue_id}")
        if result_note is not None and not (root_path / str(result_note)).exists():
            raise ValueError(f"{source} references missing result note: {result_note}")

    return payload


def load_microtask_run(
    path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate an append-only microtask run record."""
    payload = _load_yaml_mapping(path)
    return validate_microtask_run_payload(payload, source=path, root=root)
