"""Materials MD-0001 conservative baseline benchmark (TASK-0550).

The benchmark uses only committed Materials Project stable-binary-oxide rows.
It keeps formation energy and band gap as separate axes, fits only simple
train-split baselines, and reports residual maps without proposing material
candidates or correction laws.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Callable

import yaml


@dataclass(frozen=True)
class MaterialsRow:
    row_id: str
    material_id: str
    formula_pretty: str
    composition: dict[str, float]
    nsites: int | None
    spacegroup_symbol: str | None
    property_kind: str
    value: float
    units: str
    provenance_class: str
    inclusion_status: str
    is_stable: bool


Predictor = Callable[[MaterialsRow], float]


ELEMENT_GROUPS = {
    "alkali_or_alkaline_earth": {
        "Li",
        "Na",
        "K",
        "Rb",
        "Cs",
        "Fr",
        "Be",
        "Mg",
        "Ca",
        "Sr",
        "Ba",
        "Ra",
    },
    "transition_metal": {
        "Sc",
        "Ti",
        "V",
        "Cr",
        "Mn",
        "Fe",
        "Co",
        "Ni",
        "Cu",
        "Zn",
        "Y",
        "Zr",
        "Nb",
        "Mo",
        "Tc",
        "Ru",
        "Rh",
        "Pd",
        "Ag",
        "Cd",
        "Hf",
        "Ta",
        "W",
        "Re",
        "Os",
        "Ir",
        "Pt",
        "Au",
        "Hg",
    },
    "rare_earth_or_lanthanoid": {
        "La",
        "Ce",
        "Pr",
        "Nd",
        "Pm",
        "Sm",
        "Eu",
        "Gd",
        "Tb",
        "Dy",
        "Ho",
        "Er",
        "Tm",
        "Yb",
        "Lu",
    },
    "post_transition_metal": {"Al", "Ga", "In", "Tl", "Sn", "Pb", "Bi", "Po"},
    "metalloid_or_p_block": {
        "B",
        "Si",
        "Ge",
        "As",
        "Sb",
        "Te",
        "C",
        "N",
        "P",
        "S",
        "Se",
        "F",
        "Cl",
        "Br",
        "I",
    },
}


def run_materials_md0001_baseline(config_path: Path) -> dict[str, Any]:
    """Run the deterministic MD-0001 baseline benchmark."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    dataset_cfg = config["dataset"]
    axis_configs = dataset_cfg["axes"]
    holdout_manifest_ref = str(dataset_cfg["holdout_manifest_ref"])
    snapshot_manifest_ref = str(dataset_cfg["snapshot_manifest_ref"])
    holdout_manifest_path = Path(holdout_manifest_ref)
    snapshot_manifest_path = Path(snapshot_manifest_ref)

    holdout_manifest = yaml.safe_load(holdout_manifest_path.read_text(encoding="utf-8")) or {}
    snapshot_manifest = yaml.safe_load(snapshot_manifest_path.read_text(encoding="utf-8")) or {}
    _assert_manifest_binding(config, holdout_manifest, snapshot_manifest)

    axis_outputs: dict[str, Any] = {}
    for axis in axis_configs:
        rows = _load_axis_rows(Path(axis["dataset_file"]))
        included_rows = _included_rows(rows, expected_property_kind=axis["property_kind"])
        split_rows = _split_rows(included_rows)
        baselines = _fit_baselines(split_rows["train"])
        baseline_summaries = {
            baseline_id: _summarize_baseline(
                rows=included_rows,
                split_rows=split_rows,
                predictor=predictor,
                property_kind=axis["property_kind"],
                property_range_bins=config["property_range_bins"][axis["property_kind"]],
            )
            for baseline_id, predictor in baselines.items()
        }
        axis_outputs[axis["property_kind"]] = {
            "dataset_file": axis["dataset_file"],
            "units": axis["units"],
            "provenance_class": axis["provenance_class"],
            "row_count": len(included_rows),
            "split_counts": {key: len(value) for key, value in split_rows.items()},
            "declared_baselines": {
                "global_mean": "Train-split global mean null baseline.",
                "global_median": "Train-split global median null baseline.",
                "cation_group_mean": (
                    "Train-split cation-group mean baseline with global-mean fallback."
                ),
            },
            "baseline_summaries": baseline_summaries,
            "best_validation_baseline": _best_baseline(baseline_summaries, "validation"),
            "best_holdout_baseline": _best_baseline(baseline_summaries, "holdout"),
        }

    return {
        "task_id": "TASK-0550",
        "benchmark_id": "materials-md0001-baseline-residual-benchmark",
        "input_references": {
            "holdout_manifest": holdout_manifest_ref,
            "snapshot_manifest": snapshot_manifest_ref,
            "formation_energy_dataset": axis_configs[0]["dataset_file"],
            "band_gap_dataset": axis_configs[1]["dataset_file"],
        },
        "dataset_summary": {
            "dataset_family": dataset_cfg["dataset_family"],
            "source_id": dataset_cfg["source_id"],
            "snapshot_checksum_sha256": dataset_cfg["snapshot_checksum_sha256"],
            "row_count_per_axis": holdout_manifest["scope"]["row_count_per_axis"],
            "live_external_fetch": False,
        },
        "split_policy": {
            "split_id": "material_id_mod10_70_10_20",
            "row_order": "sort by material_id",
            "train_rule": "sorted_index % 10 in {0, 1, 2, 3, 4, 5, 6}",
            "validation_rule": "sorted_index % 10 == 7",
            "holdout_rule": "sorted_index % 10 in {8, 9}",
            "binding_manifest": holdout_manifest_ref,
        },
        "axis_outputs": axis_outputs,
        "verdict": "INCONCLUSIVE",
        "limitations": [
            "Computed DFT Materials Project rows only; no experimental measurements.",
            "Stable binary oxides only; no material-discovery or synthesis guidance.",
            "Baselines are simple null/composition-aware controls, not tuned ML models.",
            "Formation energy and band gap are separate axes and are never pooled.",
            "No RESULT, PRED, CLAIM, KNOW, or discovery wording is promoted.",
        ],
        "output_routing": {
            "canonical_destination": "agent_runs/AGENT-RUN-0057/",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
        },
    }


def _load_axis_rows(path: Path) -> list[MaterialsRow]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows: list[MaterialsRow] = []
    for raw in doc["rows"]:
        rows.append(
            MaterialsRow(
                row_id=str(raw["row_id"]),
                material_id=str(raw["material_id"]),
                formula_pretty=str(raw["formula_pretty"]),
                composition={str(k): float(v) for k, v in raw["composition"].items()},
                nsites=int(raw["nsites"]) if raw.get("nsites") is not None else None,
                spacegroup_symbol=(
                    str(raw["spacegroup_symbol"])
                    if raw.get("spacegroup_symbol") is not None
                    else None
                ),
                property_kind=str(raw["property_kind"]),
                value=float(raw["value"]),
                units=str(raw["units"]),
                provenance_class=str(raw["provenance_class"]),
                inclusion_status=str(raw["inclusion_status"]),
                is_stable=bool(raw.get("is_stable", False)),
            )
        )
    return rows


def _included_rows(rows: list[MaterialsRow], *, expected_property_kind: str) -> list[MaterialsRow]:
    included = [
        row
        for row in rows
        if row.inclusion_status == "included"
        and row.is_stable
        and row.provenance_class == "computed_dft"
        and row.property_kind == expected_property_kind
    ]
    if not included:
        raise ValueError(f"No included rows for {expected_property_kind}")
    return sorted(included, key=lambda row: row.material_id)


def _split_rows(rows: list[MaterialsRow]) -> dict[str, list[MaterialsRow]]:
    splits = {"train": [], "validation": [], "holdout": []}
    for index, row in enumerate(rows):
        bucket = index % 10
        if bucket < 7:
            splits["train"].append(row)
        elif bucket == 7:
            splits["validation"].append(row)
        else:
            splits["holdout"].append(row)
    return splits


def _fit_baselines(train_rows: list[MaterialsRow]) -> dict[str, Predictor]:
    values = [row.value for row in train_rows]
    global_mean = sum(values) / len(values)
    global_median = float(median(values))
    by_group: dict[str, list[float]] = defaultdict(list)
    for row in train_rows:
        by_group[cation_group(row)].append(row.value)
    group_means = {group: sum(group_values) / len(group_values) for group, group_values in by_group.items()}

    return {
        "global_mean": lambda _row: global_mean,
        "global_median": lambda _row: global_median,
        "cation_group_mean": lambda row: group_means.get(cation_group(row), global_mean),
    }


def _summarize_baseline(
    *,
    rows: list[MaterialsRow],
    split_rows: dict[str, list[MaterialsRow]],
    predictor: Predictor,
    property_kind: str,
    property_range_bins: list[dict[str, Any]],
) -> dict[str, Any]:
    split_metrics = {
        split_id: _residual_metrics(split, predictor)
        for split_id, split in split_rows.items()
    }
    split_metrics["full_md0001_axis"] = _residual_metrics(rows, predictor)
    return {
        "metrics": split_metrics,
        "subset_metrics": {
            "cation_group": _subset_metrics(rows, predictor, cation_group),
            "formula_family": _subset_metrics(rows, predictor, formula_family),
            "spacegroup_bucket": _subset_metrics(rows, predictor, spacegroup_bucket),
            "property_range": _subset_metrics(
                rows,
                predictor,
                lambda row: property_range(row, property_kind, property_range_bins),
            ),
        },
    }


def _residual_metrics(rows: list[MaterialsRow], predictor: Predictor) -> dict[str, float | int]:
    residuals = [row.value - predictor(row) for row in rows]
    abs_residuals = [abs(residual) for residual in residuals]
    if not residuals:
        return {
            "count": 0,
            "mae": 0.0,
            "rmse": 0.0,
            "median_abs_residual": 0.0,
            "p90_abs_residual": 0.0,
            "max_abs_residual": 0.0,
        }
    return {
        "count": len(rows),
        "mae": round(sum(abs_residuals) / len(abs_residuals), 6),
        "rmse": round((sum(residual * residual for residual in residuals) / len(residuals)) ** 0.5, 6),
        "median_abs_residual": round(float(median(abs_residuals)), 6),
        "p90_abs_residual": round(_quantile(abs_residuals, 0.9), 6),
        "max_abs_residual": round(max(abs_residuals), 6),
    }


def _subset_metrics(
    rows: list[MaterialsRow],
    predictor: Predictor,
    grouper: Callable[[MaterialsRow], str],
) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[MaterialsRow]] = defaultdict(list)
    for row in rows:
        grouped[grouper(row)].append(row)
    return {
        key: _residual_metrics(value, predictor)
        for key, value in sorted(grouped.items())
    }


def _best_baseline(
    baseline_summaries: dict[str, dict[str, Any]],
    split_id: str,
) -> dict[str, Any]:
    best_id = min(
        baseline_summaries,
        key=lambda baseline_id: baseline_summaries[baseline_id]["metrics"][split_id]["mae"],
    )
    return {
        "baseline_id": best_id,
        "mae": baseline_summaries[best_id]["metrics"][split_id]["mae"],
        "rmse": baseline_summaries[best_id]["metrics"][split_id]["rmse"],
    }


def cation_group(row: MaterialsRow) -> str:
    cations = [element for element in row.composition if element != "O"]
    if len(cations) != 1:
        return "mixed_or_ambiguous"
    element = cations[0]
    for group, elements in ELEMENT_GROUPS.items():
        if element in elements:
            return group
    return "mixed_or_ambiguous"


def formula_family(row: MaterialsRow) -> str:
    oxygen = row.composition.get("O", 0.0)
    cation_total = sum(amount for element, amount in row.composition.items() if element != "O")
    if cation_total <= 0:
        return "ambiguous"
    ratio = oxygen / cation_total
    if abs(ratio - 1.0) < 1e-9:
        return "monoxide"
    if abs(ratio - 1.5) < 1e-9:
        return "sesquioxide"
    if abs(ratio - 2.0) < 1e-9:
        return "dioxide"
    if ratio < 1.0:
        return "oxygen_poor"
    if ratio > 2.0:
        return "oxygen_rich"
    return "intermediate_oxide"


def spacegroup_bucket(row: MaterialsRow) -> str:
    if not row.spacegroup_symbol:
        return "missing_spacegroup"
    return row.spacegroup_symbol


def property_range(
    row: MaterialsRow,
    property_kind: str,
    bins: list[dict[str, Any]],
) -> str:
    for bin_spec in bins:
        minimum = bin_spec.get("min")
        maximum = bin_spec.get("max")
        if minimum is not None and row.value < float(minimum):
            continue
        if maximum is not None and row.value >= float(maximum):
            continue
        return str(bin_spec["id"])
    return f"{property_kind}_unbinned"


def _assert_manifest_binding(
    config: dict[str, Any],
    holdout_manifest: dict[str, Any],
    snapshot_manifest: dict[str, Any],
) -> None:
    dataset = config["dataset"]
    expected_checksum = dataset["snapshot_checksum_sha256"]
    if holdout_manifest["scope"]["dataset_family"] != dataset["dataset_family"]:
        raise ValueError("Holdout manifest dataset family mismatch")
    if holdout_manifest["scope"]["snapshot_checksum_sha256"] != expected_checksum:
        raise ValueError("Holdout manifest checksum mismatch")
    if snapshot_manifest["acquisition"]["checksum_sha256"] != expected_checksum:
        raise ValueError("Snapshot manifest checksum mismatch")
    if holdout_manifest["promotion_boundary"]["live_fetch_allowed"]:
        raise ValueError("Holdout manifest unexpectedly allows live fetch")


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight
