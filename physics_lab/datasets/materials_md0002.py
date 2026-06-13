"""Deterministic MD-0002 normalized dataset loader.

This module validates the Materials MD-0002 row shape before any benchmark
metrics run. It reads committed YAML only; it does not fetch Materials Project
data, score residuals, recommend materials, or promote claims.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

DATASET_FAMILY = "MD-0002"
SOURCE_ID = "materials-project"
PROVENANCE_COMPUTED_DFT = "computed_dft"
PROVENANCE_EXCLUDED = "excluded"
INCLUDED = "included"
EXCLUDED = "excluded"
PLACEHOLDER_SOURCE_VERSION = "TO_BE_PINNED_BY_ACQUISITION"
PLACEHOLDER_CHECKSUM = "TO_BE_COMPUTED_BY_ACQUISITION"

AXIS_UNITS: dict[str, str] = {
    "formation_energy_per_atom": "eV_per_atom",
    "band_gap": "eV",
}

REQUIRED_ROW_FIELDS: frozenset[str] = frozenset(
    {
        "row_id",
        "material_id",
        "formula_pretty",
        "composition",
        "cations",
        "composition_family",
        "property_kind",
        "value",
        "units",
        "method",
        "dft_functional",
        "database_version",
        "record_locator",
        "snapshot_checksum_sha256",
        "source_id",
        "provenance_class",
        "inclusion_status",
        "exclusion_reason",
    }
)


@dataclass(frozen=True)
class MaterialsMd0002Dataset:
    """Validated MD-0002 payload plus axis-separated row summaries."""

    path: Path
    payload: dict[str, Any]
    rows: tuple[dict[str, Any], ...]
    rows_by_axis: dict[str, tuple[dict[str, Any], ...]]
    included_counts_by_axis: dict[str, int]
    excluded_counts_by_axis: dict[str, int]


def load_md0002_dataset(path: str | Path) -> MaterialsMd0002Dataset:
    """Load and validate an MD-0002 normalized dataset or schema fixture."""

    dataset_path = Path(path)
    payload = _safe_yaml_load_mapping(dataset_path)
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{dataset_path} must contain a non-empty rows list")

    errors = validate_md0002_payload(payload)
    if errors:
        joined = "\n- ".join(errors)
        raise ValueError(f"{dataset_path} failed MD-0002 validation:\n- {joined}")

    rows_by_axis = _group_rows_by_axis(rows)
    return MaterialsMd0002Dataset(
        path=dataset_path,
        payload=payload,
        rows=tuple(rows),
        rows_by_axis={axis: tuple(axis_rows) for axis, axis_rows in rows_by_axis.items()},
        included_counts_by_axis={
            axis: sum(row["inclusion_status"] == INCLUDED for row in axis_rows)
            for axis, axis_rows in rows_by_axis.items()
        },
        excluded_counts_by_axis={
            axis: sum(row["inclusion_status"] == EXCLUDED for row in axis_rows)
            for axis, axis_rows in rows_by_axis.items()
        },
    )


def validate_md0002_payload(payload: dict[str, Any]) -> list[str]:
    """Return validation errors for the MD-0002 normalized row contract."""

    errors: list[str] = []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return ["rows must be a list"]

    _validate_top_level(payload, rows, errors)
    _validate_axis_policies(payload, errors)
    _validate_rows(rows, bool(payload.get("fixture_only")), errors)
    return errors


def summarize_md0002_dataset(dataset: MaterialsMd0002Dataset) -> dict[str, Any]:
    """Return a JSON-serializable loader summary without metric fields."""

    return {
        "dataset_family": dataset.payload["dataset_family"],
        "source_id": dataset.payload["source_id"],
        "source_version": dataset.payload["source_version"],
        "snapshot_checksum_sha256": dataset.payload["snapshot_checksum_sha256"],
        "row_count": len(dataset.rows),
        "axes": {
            axis: {
                "units": AXIS_UNITS[axis],
                "rows": len(rows),
                "included": dataset.included_counts_by_axis[axis],
                "excluded": dataset.excluded_counts_by_axis[axis],
            }
            for axis, rows in sorted(dataset.rows_by_axis.items())
        },
    }


def _safe_yaml_load_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loader = YAML_LOADER(handle)
        try:
            payload = loader.get_single_data()
        finally:
            loader.dispose()
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping at top of {path}")
    return payload


def _validate_top_level(
    payload: dict[str, Any], rows: list[dict[str, Any]], errors: list[str]
) -> None:
    if payload.get("dataset_family") != DATASET_FAMILY:
        errors.append("dataset_family must be MD-0002")
    if payload.get("source_id") != SOURCE_ID:
        errors.append("source_id must be materials-project")
    if payload.get("live_external_fetch_allowed") is not False:
        errors.append("live_external_fetch_allowed must be false")
    if payload.get("row_count") != len(rows):
        errors.append("row_count must match rows length")
    if not isinstance(payload.get("no_claim_boundary"), str) or not payload[
        "no_claim_boundary"
    ].strip():
        errors.append("no_claim_boundary must be a non-empty string")

    is_fixture = bool(payload.get("fixture_only"))
    source_version = payload.get("source_version")
    checksum = payload.get("snapshot_checksum_sha256")
    if is_fixture:
        if source_version != PLACEHOLDER_SOURCE_VERSION:
            errors.append("fixture source_version must remain the acquisition placeholder")
        if checksum != PLACEHOLDER_CHECKSUM:
            errors.append("fixture checksum must remain the acquisition placeholder")
    else:
        if source_version in {None, "", PLACEHOLDER_SOURCE_VERSION}:
            errors.append("non-fixture source_version must be pinned")
        if checksum in {None, "", PLACEHOLDER_CHECKSUM}:
            errors.append("non-fixture snapshot_checksum_sha256 must be pinned")


def _validate_axis_policies(payload: dict[str, Any], errors: list[str]) -> None:
    axis_policies = payload.get("axis_policies")
    if not isinstance(axis_policies, list):
        errors.append("axis_policies must be a list")
        return
    policies = {axis.get("property_kind"): axis for axis in axis_policies}
    if set(policies) != set(AXIS_UNITS):
        errors.append("axis_policies must define formation_energy_per_atom and band_gap")
        return
    for property_kind, units in AXIS_UNITS.items():
        policy = policies[property_kind]
        if policy.get("units") != units:
            errors.append(f"{property_kind} axis policy must use units {units}")
        if policy.get("provenance_class") != PROVENANCE_COMPUTED_DFT:
            errors.append(f"{property_kind} axis policy must use computed_dft provenance")


def _validate_rows(
    rows: list[dict[str, Any]], is_fixture: bool, errors: list[str]
) -> None:
    row_ids: set[str] = set()
    material_axis_pairs: set[tuple[str, str]] = set()
    axis_counts: Counter[str] = Counter()

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"row {index} must be a mapping")
            continue
        missing = sorted(REQUIRED_ROW_FIELDS - set(row))
        if missing:
            errors.append(f"row {index} missing required fields: {', '.join(missing)}")
            continue

        row_id = str(row["row_id"])
        if row_id in row_ids:
            errors.append(f"duplicate row_id {row_id}")
        row_ids.add(row_id)

        property_kind = row["property_kind"]
        if property_kind not in AXIS_UNITS:
            errors.append(f"row {row_id} has unsupported property_kind {property_kind}")
            continue
        axis_counts[property_kind] += 1
        if row["units"] != AXIS_UNITS[property_kind]:
            errors.append(f"row {row_id} units must be {AXIS_UNITS[property_kind]}")

        material_id = str(row["material_id"])
        material_axis_pair = (material_id, property_kind)
        if material_axis_pair in material_axis_pairs:
            errors.append(f"duplicate material_id {material_id} on axis {property_kind}")
        material_axis_pairs.add(material_axis_pair)

        _validate_material_shape(row, row_id, errors)
        _validate_provenance(row, row_id, is_fixture, errors)
        _validate_inclusion_state(row, row_id, errors)

    missing_axes = set(AXIS_UNITS) - set(axis_counts)
    for axis in sorted(missing_axes):
        errors.append(f"missing required axis {axis}")


def _validate_material_shape(
    row: dict[str, Any], row_id: str, errors: list[str]
) -> None:
    composition = row["composition"]
    if not isinstance(composition, dict) or "O" not in composition:
        errors.append(f"row {row_id} composition must include oxygen")
        return
    non_oxygen = {element for element in composition if element != "O"}
    if len(non_oxygen) != 2:
        errors.append(f"row {row_id} must contain exactly two non-oxygen cations")
    cations = row["cations"]
    if not isinstance(cations, list) or set(cations) != non_oxygen:
        errors.append(f"row {row_id} cations must match non-oxygen composition keys")
    if row["composition_family"] != "ternary_oxide":
        errors.append(f"row {row_id} composition_family must be ternary_oxide")
    if row["record_locator"] != row["material_id"]:
        errors.append(f"row {row_id} record_locator must match material_id")


def _validate_provenance(
    row: dict[str, Any], row_id: str, is_fixture: bool, errors: list[str]
) -> None:
    if row["source_id"] != SOURCE_ID:
        errors.append(f"row {row_id} source_id must be materials-project")
    if row["dft_functional"] in {None, ""}:
        errors.append(f"row {row_id} must record dft_functional")

    if is_fixture:
        if row.get("fixture_value") is not True:
            errors.append(f"fixture row {row_id} must set fixture_value true")
        if row["database_version"] != PLACEHOLDER_SOURCE_VERSION:
            errors.append(f"fixture row {row_id} database_version must remain placeholder")
        if row["snapshot_checksum_sha256"] != PLACEHOLDER_CHECKSUM:
            errors.append(f"fixture row {row_id} checksum must remain placeholder")
    else:
        if row["database_version"] in {None, "", PLACEHOLDER_SOURCE_VERSION}:
            errors.append(f"row {row_id} database_version must be pinned")
        if row["snapshot_checksum_sha256"] in {None, "", PLACEHOLDER_CHECKSUM}:
            errors.append(f"row {row_id} snapshot_checksum_sha256 must be pinned")


def _validate_inclusion_state(
    row: dict[str, Any], row_id: str, errors: list[str]
) -> None:
    inclusion_status = row["inclusion_status"]
    provenance_class = row["provenance_class"]
    if inclusion_status == INCLUDED:
        if provenance_class != PROVENANCE_COMPUTED_DFT:
            errors.append(f"included row {row_id} must use computed_dft provenance")
        if row["value"] is None:
            errors.append(f"included row {row_id} must have a value")
        if row["exclusion_reason"] is not None:
            errors.append(f"included row {row_id} must not have exclusion_reason")
    elif inclusion_status == EXCLUDED:
        if provenance_class != PROVENANCE_EXCLUDED:
            errors.append(f"excluded row {row_id} must use excluded provenance")
        if not isinstance(row["exclusion_reason"], str) or not row[
            "exclusion_reason"
        ].strip():
            errors.append(f"excluded row {row_id} must record exclusion_reason")
    else:
        errors.append(f"row {row_id} has unsupported inclusion_status {inclusion_status}")


def _group_rows_by_axis(
    rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped = {axis: [] for axis in AXIS_UNITS}
    for row in rows:
        grouped[row["property_kind"]].append(row)
    return grouped
