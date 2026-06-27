"""Golden-result policy checks for canonical scientific result artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
from pathlib import Path
import string
from typing import Any

import yaml

from physics_lab.registry.results import load_result


GOLDEN_RESULTS_MANIFEST = Path("results") / "golden-results.yaml"
MATERIAL_POLICY = "material_fields_v1"
IGNORED_TOP_LEVEL_FIELDS = frozenset(
    {
        "generated_at",
        "git_commit",
        "command",
        "engine_version",
        "artifacts",
        "review_tier",
        "agent_proposal_evaluation",
    }
)
IGNORED_INPUT_HASH_FIELDS = frozenset({"path"})


@dataclass(frozen=True)
class GoldenResultEntry:
    """One frozen canonical result expectation from the golden manifest."""

    result_path: str
    result_id: str
    policy: str
    material_hash_sha256: str


@dataclass(frozen=True)
class GoldenResultDrift:
    """Material drift detected for a golden result artifact."""

    result_path: str
    result_id: str
    expected_hash: str
    actual_hash: str


def material_result_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only fields treated as material scientific result content."""
    material = copy.deepcopy(payload)
    for field in IGNORED_TOP_LEVEL_FIELDS:
        material.pop(field, None)

    input_hashes = material.get("input_file_hashes")
    if isinstance(input_hashes, dict):
        for hash_payload in input_hashes.values():
            if isinstance(hash_payload, dict):
                for field in IGNORED_INPUT_HASH_FIELDS:
                    hash_payload.pop(field, None)
    return material


def material_result_hash(payload: dict[str, Any]) -> str:
    """Return the deterministic hash for a result's material scientific payload."""
    encoded = json.dumps(
        material_result_payload(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_golden_result_entries(root: Path) -> tuple[GoldenResultEntry, ...]:
    """Load golden-result expectations from the repository manifest."""
    manifest_path = root / GOLDEN_RESULTS_MANIFEST
    if not manifest_path.exists():
        return ()
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {manifest_path}")
    entries = payload.get("golden_results")
    if not isinstance(entries, list):
        raise ValueError(f"{manifest_path} must declare golden_results as a list")

    parsed: list[GoldenResultEntry] = []
    seen_paths: set[str] = set()
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{manifest_path} golden_results[{index}] must be a mapping")
        entry = GoldenResultEntry(
            result_path=str(item.get("result_path") or "").strip(),
            result_id=str(item.get("result_id") or "").strip(),
            policy=str(item.get("policy") or "").strip(),
            material_hash_sha256=str(item.get("material_hash_sha256") or "").strip(),
        )
        if not entry.result_path:
            raise ValueError(f"{manifest_path} golden_results[{index}] is missing result_path")
        entry_path = Path(entry.result_path)
        if entry_path.is_absolute() or ".." in entry_path.parts:
            raise ValueError(
                f"{manifest_path} golden_results[{index}] must use a repository-relative path"
            )
        if entry.result_path in seen_paths:
            raise ValueError(f"{manifest_path} declares duplicate result_path {entry.result_path}")
        seen_paths.add(entry.result_path)
        if entry.policy != MATERIAL_POLICY:
            raise ValueError(
                f"{manifest_path} golden_results[{index}] uses unsupported policy "
                f"{entry.policy or '<missing>'}"
            )
        if len(entry.material_hash_sha256) != 64 or any(
            char not in string.hexdigits for char in entry.material_hash_sha256
        ):
            raise ValueError(
                f"{manifest_path} golden_results[{index}] must declare a sha256 material hash"
            )
        parsed.append(entry)
    return tuple(parsed)


def golden_result_drifts(root: Path) -> tuple[GoldenResultDrift, ...]:
    """Return golden-result entries whose material content no longer matches."""
    drifts: list[GoldenResultDrift] = []
    for entry in load_golden_result_entries(root):
        result_path = root / entry.result_path
        if not result_path.exists():
            continue
        payload = load_result(result_path)
        actual_result_id = str(payload["result_id"])
        actual_hash = material_result_hash(payload)
        if actual_result_id != entry.result_id or actual_hash != entry.material_hash_sha256:
            drifts.append(
                GoldenResultDrift(
                    result_path=entry.result_path,
                    result_id=entry.result_id,
                    expected_hash=entry.material_hash_sha256,
                    actual_hash=actual_hash,
                )
            )
    return tuple(drifts)
