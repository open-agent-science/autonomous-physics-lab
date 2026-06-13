"""TASK-0733: enforce redistribution declarations for committed datasets.

Every committed third-party dataset under ``data/`` must be declared in
``data/DATA_LICENSES.yaml`` with a complete redistribution basis. This guard
extends the TASK-0731 source-artifact policy (which covered PDFs and raw
``source_artifacts`` payloads) to bulk datasets committed as YAML/CSV/JSON.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
REGISTRY_PATH = DATA_DIR / "DATA_LICENSES.yaml"

# Data YAML files at or above this size are treated as committed datasets that
# must be declared. APL-authored manifests/registries are all well below this.
LARGE_YAML_THRESHOLD_BYTES = 100_000


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _registry() -> dict:
    return _load(REGISTRY_PATH)


def _declared_paths() -> set[Path]:
    declared: set[Path] = set()
    for entry in _registry()["datasets"]:
        for rel in entry["paths"]:
            declared.add((REPO_ROOT / rel).resolve())
    return declared


def _is_excluded_payload(path: Path) -> bool:
    """APL-authored / non-dataset payloads that need no licence declaration."""
    name = path.name
    if name.endswith(".schema.json"):
        return True
    if name.endswith("_template.csv"):
        return True
    if path.resolve() == REGISTRY_PATH.resolve():
        return True
    return False


def test_registry_entries_are_complete_and_paths_exist() -> None:
    registry = _registry()
    required = tuple(registry["required_fields"])
    assert required, "registry must declare required_fields"
    seen_ids: set[str] = set()
    for entry in registry["datasets"]:
        entry_id = entry.get("id")
        assert entry_id and entry_id not in seen_ids, f"missing/duplicate id: {entry_id}"
        seen_ids.add(entry_id)
        for field in required:
            assert entry.get(field), f"{entry_id}: missing/empty required field {field!r}"
        assert entry.get("paths"), f"{entry_id}: must list at least one path"
        for rel in entry["paths"]:
            assert (REPO_ROOT / rel).exists(), f"{entry_id}: declared path does not exist: {rel}"


def test_all_csv_json_datasets_are_declared() -> None:
    """Any committed CSV/JSON dataset under data/ must be in the registry."""
    declared = _declared_paths()
    undeclared: list[str] = []
    for path in DATA_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json"}:
            continue
        if _is_excluded_payload(path):
            continue
        if path.resolve() not in declared:
            undeclared.append(str(path.relative_to(REPO_ROOT)))
    assert not undeclared, (
        "Undeclared third-party data files (add to data/DATA_LICENSES.yaml): "
        + ", ".join(sorted(undeclared))
    )


def test_large_data_yaml_is_declared() -> None:
    """Any large data YAML (likely a vendored dataset) must be declared."""
    declared = _declared_paths()
    undeclared: list[str] = []
    for path in DATA_DIR.rglob("*.yaml"):
        if not path.is_file() or _is_excluded_payload(path):
            continue
        if path.stat().st_size <= LARGE_YAML_THRESHOLD_BYTES:
            continue
        if path.resolve() not in declared:
            undeclared.append(
                f"{path.relative_to(REPO_ROOT)} ({path.stat().st_size} bytes)"
            )
    assert not undeclared, (
        "Large committed data YAML not declared in data/DATA_LICENSES.yaml: "
        + ", ".join(sorted(undeclared))
    )
