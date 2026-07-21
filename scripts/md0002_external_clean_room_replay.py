"""Public-archive clean-room replay for the MD-0002 formation-energy baseline.

The script consumes required bytes directly from a SHA-256-verified Zenodo ZIP.
It intentionally has no import from an Autonomous Physics Lab workflow module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

DOI = "10.5281/zenodo.21207072"
ARCHIVE_FILENAME = "md0002-v0.1.0.zip"
ARCHIVE_BYTES = 795_018
ARCHIVE_SHA256 = "19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22"

SNAPSHOT_MANIFEST_MEMBER = "data/materials/materials_md0002_snapshot_manifest.yaml"
NORMALIZED_DATASET_MEMBER = "data/materials/md-0002-materials-project-stable-ternary-oxides.yaml"
HOLDOUT_MANIFEST_MEMBER = "data/materials/md0002_holdout_manifest.yaml"
RAW_SNAPSHOT_MEMBER = "data/materials/snapshots/materials_project_md0002_2026.04.13.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def load_yaml_bytes(content: bytes, member_name: str) -> dict[str, Any]:
    parsed = yaml.safe_load(content.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{member_name} must contain a YAML mapping")
    return parsed


def safe_relative_member_name(member_name: str) -> str:
    path = PurePosixPath(member_name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe ZIP member path: {member_name}")
    return path.as_posix()


def read_required_member(archive: zipfile.ZipFile, required_name: str) -> tuple[str, bytes]:
    required_name = safe_relative_member_name(required_name)
    candidates: list[zipfile.ZipInfo] = []
    for info in archive.infolist():
        if info.is_dir():
            continue
        member_name = safe_relative_member_name(info.filename)
        if member_name == required_name:
            candidates.append(info)

    if len(candidates) != 1:
        raise ValueError(
            f"Expected exactly one required ZIP member {required_name!r}; found {len(candidates)}"
        )

    info = candidates[0]
    return info.filename, archive.read(info)


def mean_absolute_error(observed: list[float], predicted: list[float]) -> float:
    return sum(abs(actual - estimate) for actual, estimate in zip(observed, predicted)) / len(observed)


def cation_pair(row: dict[str, Any]) -> tuple[str, str]:
    cations = row.get("cations")
    if not isinstance(cations, list):
        raise ValueError(f"{row['material_id']} has no cations list")
    pair = tuple(sorted(str(element) for element in cations if element != "O"))
    if len(pair) != 2:
        raise ValueError(f"{row['material_id']} does not have exactly two non-oxygen cations")
    return pair


def material_split_digest(rows: list[dict[str, Any]]) -> str:
    mapping = {str(row["material_id"]): str(row["split"]) for row in rows}
    payload = "\n".join(f"{material_id}:{mapping[material_id]}" for material_id in sorted(mapping))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", dest="zip_path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    zip_path = args.zip_path
    if (
        zip_path.name != ARCHIVE_FILENAME
        or zip_path.stat().st_size != ARCHIVE_BYTES
        or sha256(zip_path) != ARCHIVE_SHA256
    ):
        raise ValueError("Zenodo archive identity check failed")

    with zipfile.ZipFile(zip_path) as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ValueError(f"Zenodo archive CRC check failed for {bad_member}")

        snapshot_manifest_name, snapshot_manifest_bytes = read_required_member(
            archive, SNAPSHOT_MANIFEST_MEMBER
        )
        normalized_name, normalized_bytes = read_required_member(
            archive, NORMALIZED_DATASET_MEMBER
        )
        holdout_manifest_name, holdout_manifest_bytes = read_required_member(
            archive, HOLDOUT_MANIFEST_MEMBER
        )
        raw_snapshot_name, raw_snapshot_bytes = read_required_member(
            archive, RAW_SNAPSHOT_MEMBER
        )

    snapshot_manifest = load_yaml_bytes(snapshot_manifest_bytes, snapshot_manifest_name)
    dataset = load_yaml_bytes(normalized_bytes, normalized_name)
    holdout_manifest = load_yaml_bytes(holdout_manifest_bytes, holdout_manifest_name)

    expected_normalized = snapshot_manifest["artifacts"]["normalized_dataset"]["checksum_sha256"]
    expected_snapshot = snapshot_manifest["artifacts"]["raw_snapshot"]["checksum_sha256"]
    if sha256_bytes(normalized_bytes) != expected_normalized:
        raise ValueError("Normalized dataset bytes differ from the internal public manifest")
    if sha256_bytes(raw_snapshot_bytes) != expected_snapshot:
        raise ValueError("Raw snapshot bytes differ from the internal public manifest")

    rows = dataset.get("rows")
    if not isinstance(rows, list):
        raise ValueError("Released dataset does not expose a rows list")
    formation = [row for row in rows if row.get("property_kind") == "formation_energy_per_atom"]
    band_gap = [row for row in rows if row.get("property_kind") == "band_gap"]
    if len(formation) != 362 or len(band_gap) != 362 or len(rows) != 724:
        raise ValueError("Released row counts differ from the frozen public schema")

    formation_ids = [str(row["material_id"]) for row in formation]
    band_gap_ids = [str(row["material_id"]) for row in band_gap]
    if len(set(formation_ids)) != 362 or set(formation_ids) != set(band_gap_ids):
        raise ValueError("The two public property axes do not share the expected 362 material identifiers")
    formation_splits = {str(row["material_id"]): str(row["split"]) for row in formation}
    band_gap_splits = {str(row["material_id"]): str(row["split"]) for row in band_gap}
    if formation_splits != band_gap_splits:
        raise ValueError("The public property axes do not share the frozen material-level split")

    split_counts = {
        split: sum(row["split"] == split for row in formation)
        for split in ("train", "validation", "holdout")
    }
    if split_counts != {"train": 253, "validation": 55, "holdout": 54}:
        raise ValueError("Formation-energy split counts differ from the public holdout manifest")
    if holdout_manifest["scope"]["frozen_split_counts_per_axis"] != split_counts:
        raise ValueError("Holdout manifest split counts disagree with released rows")

    train = [row for row in formation if row["split"] == "train"]
    holdout = [row for row in formation if row["split"] == "holdout"]
    train_values = [float(row["value"]) for row in train]
    holdout_values = [float(row["value"]) for row in holdout]
    global_train_mean = statistics.fmean(train_values)
    global_train_median = statistics.median(train_values)

    pair_values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in train:
        pair_values[cation_pair(row)].append(float(row["value"]))
    pair_means = {pair: statistics.fmean(values) for pair, values in pair_values.items()}

    unseen_pair_count = sum(cation_pair(row) not in pair_means for row in holdout)
    pair_predictions = [pair_means.get(cation_pair(row), global_train_mean) for row in holdout]
    median_predictions = [global_train_median] * len(holdout)
    null_predictions = [0.0] * len(holdout)

    consumed_members = {
        snapshot_manifest_name: sha256_bytes(snapshot_manifest_bytes),
        normalized_name: sha256_bytes(normalized_bytes),
        holdout_manifest_name: sha256_bytes(holdout_manifest_bytes),
        raw_snapshot_name: sha256_bytes(raw_snapshot_bytes),
    }
    result = {
        "artifact": {
            "doi": DOI,
            "filename": ARCHIVE_FILENAME,
            "bytes": ARCHIVE_BYTES,
            "sha256": ARCHIVE_SHA256,
            "consumed_directly_from_verified_zip": True,
        },
        "checks": {
            "normalized_rows": len(rows),
            "unique_materials": len(set(formation_ids)),
            "property_axes": ["band_gap", "formation_energy_per_atom"],
            "material_level_split_identity": True,
            "split_counts_per_axis": split_counts,
            "split_digest_sha256": material_split_digest(formation),
            "normalized_dataset_sha256": sha256_bytes(normalized_bytes),
            "raw_snapshot_sha256": sha256_bytes(raw_snapshot_bytes),
            "consumed_member_sha256": consumed_members,
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "pyyaml": yaml.__version__,
        },
        "method": {
            "axis": "formation_energy_per_atom",
            "metric": "holdout_mae_eV_per_atom",
            "baseline": (
                "train-only unordered non-oxygen cation-pair mean; "
                "global training mean fallback"
            ),
            "controls": ["global_training_median", "null_zero"],
            "holdout_rows": len(holdout),
            "pair_count_from_train": len(pair_means),
            "unseen_pair_holdout_rows": unseen_pair_count,
        },
        "metrics": {
            "cation_pair_baseline_mae": mean_absolute_error(holdout_values, pair_predictions),
            "global_training_median_mae": mean_absolute_error(holdout_values, median_predictions),
            "null_zero_mae": mean_absolute_error(holdout_values, null_predictions),
        },
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "INDEPENDENT_RUN_SEALED_PENDING_CANONICAL_COMPARISON",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sha256": sha256(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())