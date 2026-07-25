"""Frozen within-OQMD formation-energy benchmark for TASK-1066."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import re
from statistics import mean, median
from typing import Any, Callable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = Path("data/materials/oqmd_within_source_benchmark_config.yaml")
ABSOLUTE_MARGIN = 0.02
RELATIVE_MARGIN = 0.05
ABSOLUTE_TOLERANCE = 1.0e-12
CONTROL_SEEDS = (1054, 2054, 3054, 4054, 5054)
SENSITIVITY_SEEDS = CONTROL_SEEDS

IUPAC_GROUP = {
    "Li": 1,
    "Na": 1,
    "K": 1,
    "Rb": 1,
    "Cs": 1,
    "Be": 2,
    "Mg": 2,
    "Ca": 2,
    "Sr": 2,
    "Ba": 2,
    "Sc": 3,
    "Ti": 4,
    "V": 5,
    "Cr": 6,
    "Mn": 7,
    "Fe": 8,
    "Co": 9,
    "Ni": 10,
    "Cu": 11,
    "Zn": 12,
}


@dataclass(frozen=True)
class OqmdRow:
    entry_id: int
    name: str
    reduced_composition: str
    cation_pair: tuple[str, str]
    iupac_group_pair: tuple[int, int]
    value: float
    partition: str


Predictor = Callable[[OqmdRow], float]
Labeler = Callable[[OqmdRow], tuple[Any, ...]]


def run_oqmd_within_source_benchmark(
    config_path: str | Path = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Execute the one frozen OQMD benchmark and return JSON-safe evidence."""
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    paths = _resolve_and_verify_inputs(config)
    _verify_prerequisites(paths)
    rows = _load_rows(paths["normalized_snapshot"], paths["split"])
    partitions = _partition_rows(rows)

    fixed = _evaluate_partition(
        partitions["train"],
        partitions["validation"],
        partitions["holdout"],
        control_seeds=CONTROL_SEEDS,
    )
    sensitivity = [
        _evaluate_sensitivity_seed(rows, seed) for seed in SENSITIVITY_SEEDS
    ]
    row_order = _row_order_invariance(partitions["train"], partitions["holdout"])
    leakage = _composition_leakage(partitions)

    fixed_pass = fixed["survival_gate"]["all_comparators_pass"]
    sensitivity_pass = all(item["all_comparators_pass"] for item in sensitivity)
    structural_pass = not leakage and row_order["drift"] <= ABSOLUTE_TOLERANCE
    verdict = "PASS" if fixed_pass and sensitivity_pass and structural_pass else "FAIL"

    return {
        "task_id": "TASK-1066",
        "benchmark_id": "oqmd-within-source-cation-pair-v1",
        "source_scope": {
            "source": "OQMD",
            "snapshot_id": "oqmd-live-api-2026-07-14",
            "target_field": "delta_e",
            "target_units": "eV_per_atom_per_OQMD_canonical_definition",
            "provenance_class": "computed_dft",
            "within_source_only": True,
            "cross_database_numeric_pooling": False,
            "live_external_fetch": False,
        },
        "input_hashes": {
            key: {"path": path.relative_to(REPO_ROOT).as_posix(), "sha256": _sha256(path)}
            for key, path in paths.items()
        },
        "partition_counts": {
            key: len(value) for key, value in partitions.items()
        },
        "partition_group_counts": {
            key: len({row.reduced_composition for row in value})
            for key, value in partitions.items()
        },
        "missing_or_invalid_target_exclusions": 0,
        "composition_leakage": leakage,
        "fixed_split": fixed,
        "row_order_invariance": row_order,
        "sensitivity": {
            "method": "identity-group-preserving seeded 120/26/26 repartition",
            "seeds": list(SENSITIVITY_SEEDS),
            "per_seed": sensitivity,
            "all_seeds_pass": sensitivity_pass,
        },
        "failure_cases": _failure_cases(partitions["train"], partitions["holdout"], fixed),
        "verdict": verdict,
        "limitations": [
            "One bounded 172-row OQMD computed-DFT slice under OQMD delta_e semantics only.",
            "The benchmark is within-source; OQMD values are not pooled with or treated as numerically equal to Materials Project values.",
            "The exact cation-pair mean is a simple train-only baseline with a global-mean fallback, not a materials law or production predictor.",
            "Seeded sensitivity reassigns whole reduced-composition identity groups and does not authorize threshold, descriptor, or model changes.",
            "No experimental validation, material recommendation, synthesis guidance, or device-performance inference is supported.",
        ],
    }


def _resolve_and_verify_inputs(config: dict[str, Any]) -> dict[str, Path]:
    if config.get("task_id") != "TASK-1066":
        raise ValueError("OQMD benchmark config must bind TASK-1066")
    if config.get("contract_id") != "oqmd-within-source-cation-pair-v1":
        raise ValueError("OQMD benchmark contract identity drift")
    expected = config.get("inputs")
    if not isinstance(expected, dict):
        raise ValueError("OQMD benchmark config inputs must be a mapping")
    paths: dict[str, Path] = {}
    for key, spec in expected.items():
        if not isinstance(spec, dict):
            raise ValueError(f"Input {key!r} must be a mapping")
        path = REPO_ROOT / str(spec["path"])
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = _sha256(path)
        if actual != str(spec["sha256"]):
            raise ValueError(f"Input hash drift for {key}: {actual}")
        paths[str(key)] = path
    required = {
        "raw_snapshot",
        "normalized_snapshot",
        "source_manifest",
        "split",
        "contract",
        "independent_replay",
    }
    if set(paths) != required:
        raise ValueError(f"OQMD benchmark input set drift: {set(paths)}")
    return paths


def _verify_prerequisites(paths: dict[str, Path]) -> None:
    manifest = yaml.safe_load(paths["source_manifest"].read_text(encoding="utf-8"))
    split = yaml.safe_load(paths["split"].read_text(encoding="utf-8"))
    contract = yaml.safe_load(paths["contract"].read_text(encoding="utf-8"))
    replay = paths["independent_replay"].read_text(encoding="utf-8")
    if manifest["verdict"] != "SNAPSHOT_READY_FOR_SPLIT_FREEZE":
        raise ValueError("SOURCE_STATE_BLOCKED: source manifest verdict drift")
    if split["verdict"] != "SPLIT_READY_FOR_BENCHMARK_PREFLIGHT":
        raise ValueError("CONTRACT_STATE_BLOCKED: split verdict drift")
    if contract["verdict"] != "CONTRACT_READY_FOR_FROZEN_SPLIT":
        raise ValueError("CONTRACT_STATE_BLOCKED: control contract verdict drift")
    if "**`INDEPENDENT_SOURCE_REPLAY_PASS`.**" not in replay:
        raise ValueError("SOURCE_STATE_BLOCKED: independent source replay missing")
    if manifest["normalized_snapshot"]["sha256"] != _sha256(paths["normalized_snapshot"]):
        raise ValueError("SOURCE_STATE_BLOCKED: normalized snapshot binding drift")
    if manifest["raw_snapshot"]["sha256"] != _sha256(paths["raw_snapshot"]):
        raise ValueError("SOURCE_STATE_BLOCKED: raw snapshot binding drift")
    if tuple(contract["required_controls"]["label_shuffle"]["seeds"]) != CONTROL_SEEDS:
        raise ValueError("CONTRACT_STATE_BLOCKED: label-shuffle seeds drift")
    if tuple(contract["sensitivity"]["seeds"]) != SENSITIVITY_SEEDS:
        raise ValueError("CONTRACT_STATE_BLOCKED: sensitivity seeds drift")


def _load_rows(normalized_path: Path, split_path: Path) -> list[OqmdRow]:
    payload = json.loads(normalized_path.read_text(encoding="utf-8"))
    split = yaml.safe_load(split_path.read_text(encoding="utf-8"))
    partition_by_id: dict[int, str] = {}
    for partition, manifest in split["split_manifests"].items():
        for entry_id in manifest["entry_ids"]:
            if int(entry_id) in partition_by_id:
                raise ValueError(f"Duplicate split entry id: {entry_id}")
            partition_by_id[int(entry_id)] = str(partition)
    rows: list[OqmdRow] = []
    for raw in payload["rows"]:
        value = raw.get("delta_e")
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ValueError(f"INCONCLUSIVE: invalid delta_e for entry {raw.get('entry_id')}")
        entry_id = int(raw["entry_id"])
        if entry_id not in partition_by_id:
            raise ValueError(f"Split binding missing entry {entry_id}")
        cations = tuple(sorted(_non_oxygen_elements(str(raw["composition"]))))
        if len(cations) != 2:
            raise ValueError(f"Entry {entry_id} does not have exactly two cations")
        try:
            groups = tuple(sorted(IUPAC_GROUP[element] for element in cations))
        except KeyError as exc:
            raise ValueError(f"Unsupported cation in entry {entry_id}: {exc}") from exc
        rows.append(
            OqmdRow(
                entry_id=entry_id,
                name=str(raw["name"]),
                reduced_composition=str(raw["reduced_composition"]),
                cation_pair=(cations[0], cations[1]),
                iupac_group_pair=(groups[0], groups[1]),
                value=float(value),
                partition=partition_by_id[entry_id],
            )
        )
    if len(rows) != 172 or len(partition_by_id) != 172:
        raise ValueError(f"INCONCLUSIVE: expected 172 bound rows, got {len(rows)}")
    return sorted(rows, key=lambda row: row.entry_id)


def _non_oxygen_elements(composition: str) -> list[str]:
    return [element for element in re.findall(r"([A-Z][a-z]?)[0-9.]+", composition) if element != "O"]


def _partition_rows(rows: list[OqmdRow]) -> dict[str, list[OqmdRow]]:
    result = {"train": [], "validation": [], "holdout": []}
    for row in rows:
        result[row.partition].append(row)
    counts = {key: len(value) for key, value in result.items()}
    if counts != {"train": 120, "validation": 26, "holdout": 26}:
        raise ValueError(f"Frozen partition count drift: {counts}")
    return result


def _evaluate_partition(
    train: list[OqmdRow],
    validation: list[OqmdRow],
    holdout: list[OqmdRow],
    *,
    control_seeds: tuple[int, ...],
) -> dict[str, Any]:
    global_mean = mean(row.value for row in train)
    candidate, candidate_seen = _fit_group_mean(train, lambda row: row.cation_pair, global_mean)
    group_null, group_seen = _fit_group_mean(
        train, lambda row: row.iupac_group_pair, global_mean
    )
    global_median = float(median(row.value for row in train))

    def global_null(_row: OqmdRow) -> float:
        return global_median

    model_metrics = {
        "candidate": _partition_metrics(train, validation, holdout, candidate, candidate_seen, lambda row: row.cation_pair),
        "global_median_null": _partition_metrics(train, validation, holdout, global_null, None, None),
        "iupac_group_pair_null": _partition_metrics(train, validation, holdout, group_null, group_seen, lambda row: row.iupac_group_pair),
    }
    controls = _controls(train, validation, holdout, control_seeds)
    candidate_mae = model_metrics["candidate"]["holdout"]["mae"]
    comparisons = []
    for comparator_id, comparator_mae in (
        ("global_median_null", model_metrics["global_median_null"]["holdout"]["mae"]),
        ("iupac_group_pair_null", model_metrics["iupac_group_pair_null"]["holdout"]["mae"]),
        *[(item["control_id"], item["holdout"]["mae"]) for item in controls],
    ):
        required_margin = max(ABSOLUTE_MARGIN, RELATIVE_MARGIN * comparator_mae)
        comparisons.append(
            {
                "comparator_id": comparator_id,
                "candidate_mae": candidate_mae,
                "comparator_mae": comparator_mae,
                "required_margin": _round(required_margin),
                "observed_margin": _round(comparator_mae - candidate_mae),
                "passes": candidate_mae <= comparator_mae - required_margin - ABSOLUTE_TOLERANCE,
            }
        )
    return {
        "train_global_mean": _round(global_mean),
        "train_global_median": _round(global_median),
        "distinct_train_cation_pairs": len(candidate_seen),
        "distinct_train_iupac_group_pairs": len(group_seen),
        "model_metrics": model_metrics,
        "controls": controls,
        "survival_gate": {
            "absolute_margin_eV_per_atom": ABSOLUTE_MARGIN,
            "relative_margin_fraction": RELATIVE_MARGIN,
            "comparisons": comparisons,
            "all_comparators_pass": all(item["passes"] for item in comparisons),
        },
    }


def _fit_group_mean(
    train: list[OqmdRow], labeler: Labeler, fallback: float, *,
    labels: list[tuple[Any, ...]] | None = None,
    values: list[float] | None = None,
) -> tuple[Predictor, frozenset[tuple[Any, ...]]]:
    grouped: dict[tuple[Any, ...], list[float]] = defaultdict(list)
    resolved_labels = labels or [labeler(row) for row in train]
    resolved_values = values or [row.value for row in train]
    for label, value in zip(resolved_labels, resolved_values, strict=True):
        grouped[label].append(value)
    means = {label: mean(group_values) for label, group_values in grouped.items()}
    return (lambda row: means.get(labeler(row), fallback)), frozenset(means)


def _partition_metrics(
    train: list[OqmdRow], validation: list[OqmdRow], holdout: list[OqmdRow],
    predictor: Predictor, seen: frozenset[tuple[Any, ...]] | None, labeler: Labeler | None,
) -> dict[str, Any]:
    return {
        name: _metrics(rows, predictor, seen=seen, labeler=labeler)
        for name, rows in (("train", train), ("validation", validation), ("holdout", holdout))
    }


def _metrics(
    rows: list[OqmdRow], predictor: Predictor, *,
    seen: frozenset[tuple[Any, ...]] | None = None, labeler: Labeler | None = None,
) -> dict[str, Any]:
    residuals = [row.value - predictor(row) for row in rows]
    relative = [
        abs(residual) / max(abs(row.value), 1.0e-12)
        for row, residual in zip(rows, residuals, strict=True)
    ]
    unseen = 0 if seen is None or labeler is None else sum(labeler(row) not in seen for row in rows)
    return {
        "count": len(rows),
        "mae": _round(mean(abs(value) for value in residuals)),
        "rmse": _round(mean(value * value for value in residuals) ** 0.5),
        "mean_relative_error": _round(mean(relative)),
        "max_relative_error": _round(max(relative)),
        "unseen_group_count": unseen,
    }


def _controls(
    train: list[OqmdRow], validation: list[OqmdRow], holdout: list[OqmdRow],
    seeds: tuple[int, ...],
) -> list[dict[str, Any]]:
    fallback = mean(row.value for row in train)
    labels = [row.cation_pair for row in train]
    values = [row.value for row in train]
    controls: list[dict[str, Any]] = []
    for seed in seeds:
        shuffled_values = list(values)
        random.Random(seed).shuffle(shuffled_values)
        predictor, seen = _fit_group_mean(
            train, lambda row: row.cation_pair, fallback, values=shuffled_values
        )
        controls.append(
            {
                "control_id": f"label_shuffle_seed_{seed}",
                **_partition_metrics(train, validation, holdout, predictor, seen, lambda row: row.cation_pair),
            }
        )
        shuffled_labels = list(labels)
        random.Random(seed).shuffle(shuffled_labels)
        predictor, seen = _fit_group_mean(
            train, lambda row: row.cation_pair, fallback, labels=shuffled_labels
        )
        controls.append(
            {
                "control_id": f"cation_pair_label_shuffle_seed_{seed}",
                **_partition_metrics(train, validation, holdout, predictor, seen, lambda row: row.cation_pair),
            }
        )
    return controls


def _evaluate_sensitivity_seed(rows: list[OqmdRow], seed: int) -> dict[str, Any]:
    groups: dict[str, list[OqmdRow]] = defaultdict(list)
    for row in rows:
        groups[row.reduced_composition].append(row)
    ordered = [groups[key] for key in sorted(groups)]
    random.Random(seed).shuffle(ordered)
    train = [row for group in ordered[:120] for row in group]
    validation = [row for group in ordered[120:146] for row in group]
    holdout = [row for group in ordered[146:] for row in group]
    evaluated = _evaluate_partition(
        train, validation, holdout, control_seeds=(seed,)
    )
    return {
        "seed": seed,
        "train_count": len(train),
        "validation_count": len(validation),
        "holdout_count": len(holdout),
        "candidate_holdout_mae": evaluated["model_metrics"]["candidate"]["holdout"]["mae"],
        "comparisons": evaluated["survival_gate"]["comparisons"],
        "all_comparators_pass": evaluated["survival_gate"]["all_comparators_pass"],
    }


def _row_order_invariance(train: list[OqmdRow], holdout: list[OqmdRow]) -> dict[str, Any]:
    fallback = mean(row.value for row in train)
    canonical, _ = _fit_group_mean(
        sorted(train, key=lambda row: row.entry_id), lambda row: row.cation_pair, fallback
    )
    reversed_predictor, _ = _fit_group_mean(
        sorted(train, key=lambda row: row.entry_id, reverse=True), lambda row: row.cation_pair, fallback
    )
    canonical_mae = _metrics(holdout, canonical)["mae"]
    reversed_mae = _metrics(holdout, reversed_predictor)["mae"]
    return {
        "canonical_holdout_mae": canonical_mae,
        "reversed_holdout_mae": reversed_mae,
        "drift": _round(abs(canonical_mae - reversed_mae)),
        "passes": abs(canonical_mae - reversed_mae) <= ABSOLUTE_TOLERANCE,
    }


def _composition_leakage(partitions: dict[str, list[OqmdRow]]) -> list[str]:
    owners: dict[str, str] = {}
    leakage: list[str] = []
    for partition, rows in partitions.items():
        for row in rows:
            previous = owners.setdefault(row.reduced_composition, partition)
            if previous != partition:
                leakage.append(row.reduced_composition)
    return sorted(set(leakage))


def _failure_cases(
    train: list[OqmdRow], holdout: list[OqmdRow], fixed: dict[str, Any]
) -> list[dict[str, Any]]:
    fallback = float(fixed["train_global_mean"])
    predictor, seen = _fit_group_mean(train, lambda row: row.cation_pair, fallback)
    return [
        {
            "entry_id": row.entry_id,
            "name": row.name,
            "cation_pair": list(row.cation_pair),
            "target": _round(row.value),
            "prediction": _round(predictor(row)),
            "residual": _round(row.value - predictor(row)),
            "absolute_residual": _round(abs(row.value - predictor(row))),
            "used_global_fallback": row.cation_pair not in seen,
        }
        for row in sorted(holdout, key=lambda row: row.entry_id)
    ]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round(value: float) -> float:
    return round(float(value), 12)


__all__ = ["run_oqmd_within_source_benchmark"]
