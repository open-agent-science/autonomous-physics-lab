"""Deterministic MD-0002 formation-energy baseline benchmark (TASK-0703)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import random
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable

import yaml

from physics_lab.datasets.materials_md0002 import load_md0002_dataset
from physics_lab.engines.materials_md0001_baseline import ELEMENT_GROUPS


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = Path("data/materials/md-0002-materials-project-stable-ternary-oxides.yaml")
DEFAULT_MANIFEST = Path("data/materials/md0002_holdout_manifest.yaml")
DEFAULT_CONFIG = Path("examples/benchmarks/materials_md0002_formation_energy.yaml")

CONTROL_SEEDS = (0, 1, 2, 7, 11)
SPLIT_SEEDS = (0, 1, 2, 3, 4)
BASELINE_IDS = (
    "global_mean",
    "global_median",
    "cation_group_mean",
    "cation_pair_mean",
    "structure_or_prototype_mean",
)
COMPOSITION_BASELINE_IDS = ("cation_group_mean", "cation_pair_mean")
MIN_SEED_WINS = 4
MIN_RELATIVE_IMPROVEMENT = 0.10
MIN_ABSOLUTE_IMPROVEMENT = 0.05

FORMATION_ENERGY_BINS = (
    {"id": "strongly_negative", "max": -3.0},
    {"id": "moderate_negative", "min": -3.0, "max": -1.0},
    {"id": "near_zero", "min": -1.0},
)


@dataclass(frozen=True)
class MaterialsMd0002Row:
    row_id: str
    material_id: str
    formula_pretty: str
    composition: dict[str, float]
    cations: tuple[str, str]
    nsites: int | None
    spacegroup_symbol: str | None
    value: float
    units: str
    split: str


Predictor = Callable[[MaterialsMd0002Row], float]
Labeler = Callable[[MaterialsMd0002Row], str]


def run_materials_md0002_formation_energy_benchmark(
    config_path: Path | str = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Run the frozen TASK-0703 benchmark and return JSON-safe metrics."""
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    _assert_config_matches_frozen_contract(config)
    dataset_path = Path(config["dataset"]["dataset_file"])
    manifest_path = Path(config["dataset"]["holdout_manifest"])
    dataset = load_md0002_dataset(dataset_path)
    rows = _load_formation_energy_rows(dataset)
    splits = _frozen_splits(rows)
    _assert_frozen_binding(dataset.payload, splits)

    baselines = _fit_baselines(splits["train"])
    baseline_summaries = {
        baseline_id: _summarize_baseline(rows, splits, predictor)
        for baseline_id, predictor in baselines.items()
    }
    best_global_id = min(
        ("global_mean", "global_median"),
        key=lambda baseline_id: baseline_summaries[baseline_id]["metrics"]["holdout"]["mae"],
    )
    best_composition_id = min(
        COMPOSITION_BASELINE_IDS,
        key=lambda baseline_id: baseline_summaries[baseline_id]["metrics"]["holdout"]["mae"],
    )

    controls = _run_controls(splits["train"], splits["holdout"], best_composition_id)
    split_sensitivity = _seeded_split_sensitivity(rows, best_composition_id)
    stress_tests = {
        "leave_one_cation_pair_out": _leave_one_group_out(
            rows, cation_pair, best_composition_id
        ),
        "leave_one_cation_family_out": _leave_one_group_out(
            rows, cation_group, best_composition_id
        ),
        "leave_one_structure_or_prototype_out": _leave_one_group_out(
            rows, structure_or_prototype, best_composition_id
        ),
    }
    promotion = _promotion_assessment(
        baseline_summaries=baseline_summaries,
        best_global_id=best_global_id,
        best_composition_id=best_composition_id,
        controls=controls,
        split_sensitivity=split_sensitivity,
    )
    verdict = "VALID_IN_RANGE" if promotion["eligible_for_gate_a"] else "INCONCLUSIVE"

    return {
        "task_id": "TASK-0703",
        "agent_run_id": "AGENT-RUN-0072",
        "benchmark_id": "materials-md0002-formation-energy-baseline-benchmark",
        "method": (
            "Train-only global, cation-family, exact cation-pair, and exact "
            "spacegroup mean baselines on the frozen MD-0002 formation-energy axis."
        ),
        "input_references": {
            "config": config_path.as_posix(),
            "dataset": dataset_path.as_posix(),
            "holdout_manifest": manifest_path.as_posix(),
            "control_plan": "docs/reviews/materials-md0002-benchmark-control-plan.md",
            "acquisition_validation": (
                "docs/reviews/materials-md0002-acquisition-validation-and-holdout-freeze.md"
            ),
        },
        "input_file_hashes": {
            config_path.as_posix(): _sha256(config_path),
            dataset_path.as_posix(): _sha256(dataset_path),
            manifest_path.as_posix(): _sha256(manifest_path),
        },
        "dataset_summary": {
            "dataset_family": dataset.payload["dataset_family"],
            "source_id": dataset.payload["source_id"],
            "source_version": str(dataset.payload["source_version"]),
            "snapshot_checksum_sha256": dataset.payload["snapshot_checksum_sha256"],
            "property_kind": "formation_energy_per_atom",
            "units": "eV_per_atom",
            "provenance_class": "computed_dft",
            "row_count": len(rows),
            "split_counts": {split: len(split_rows) for split, split_rows in splits.items()},
            "live_external_fetch": False,
        },
        "frozen_contract": {
            "baseline_ids": list(BASELINE_IDS),
            "control_seeds": list(CONTROL_SEEDS),
            "split_sensitivity_seeds": list(SPLIT_SEEDS),
            "minimum_seed_wins": MIN_SEED_WINS,
            "minimum_relative_improvement": MIN_RELATIVE_IMPROVEMENT,
            "minimum_absolute_improvement_eV_per_atom": MIN_ABSOLUTE_IMPROVEMENT,
            "property_range_bins": list(FORMATION_ENERGY_BINS),
            "fallback": "global train mean for unseen groups",
            "row_order": "material_id ascending",
        },
        "baseline_summaries": baseline_summaries,
        "best_global_null": {
            "baseline_id": best_global_id,
            **baseline_summaries[best_global_id]["metrics"]["holdout"],
        },
        "best_composition_baseline": {
            "baseline_id": best_composition_id,
            **baseline_summaries[best_composition_id]["metrics"]["holdout"],
        },
        "deterministic_controls": controls,
        "split_sensitivity": split_sensitivity,
        "extrapolation_stress_tests": stress_tests,
        "promotion_assessment": promotion,
        "verdict": verdict,
        "limitations": [
            "Computed DFT Materials Project values only; no experimental measurements.",
            "The narrowed slice contains 362 materials, below the original 600-row target "
            "but accepted by the maintainer before scoring.",
            "Exact cation-pair and spacegroup means are simple train-only comparators, not "
            "learned physical laws; unseen groups fall back to the global train mean.",
            "Leave-one-group-out views are extrapolation stress tests and can force grouped "
            "baselines to their global fallback by construction.",
            "Formation energy is evaluated alone; band gap is not scored or pooled.",
            "No material ranking, synthesis, device, biomedical, or materials-law claim is made.",
        ],
        "output_routing": {
            "canonical_destination": (
                "future task-authorized result packaging"
                if promotion["eligible_for_gate_a"]
                else "agent_runs/AGENT-RUN-0072/ and diagnostic review memory"
            ),
            "review_tier": "none",
            "gate_a_status": (
                "blocked_missing_task_authorized_canonical_identities"
                if promotion["eligible_for_gate_a"]
                else "blocked_by_predeclared_benchmark_gates"
            ),
            "gate_b_status": "not_attempted",
            "claim_impact": "no claim change",
            "knowledge_impact": "no knowledge change",
            "publication_blocker": (
                "TASK-0703 does not authorize new hypotheses/ or experiments/ "
                "artifacts; package a RESULT only under a separate task with "
                "explicit protected-path authority."
                if promotion["eligible_for_gate_a"]
                else "predeclared benchmark gates did not all pass"
            ),
        },
    }


def _assert_config_matches_frozen_contract(config: dict[str, Any]) -> None:
    if config.get("task_id") != "TASK-0703":
        raise ValueError("Benchmark config must bind TASK-0703")
    if config.get("benchmark_id") != "materials-md0002-formation-energy-baseline-benchmark":
        raise ValueError("Unexpected benchmark_id")
    dataset = config.get("dataset", {})
    if dataset.get("dataset_file") != DEFAULT_DATASET.as_posix():
        raise ValueError("Benchmark config must use the committed MD-0002 dataset")
    if dataset.get("holdout_manifest") != DEFAULT_MANIFEST.as_posix():
        raise ValueError("Benchmark config must use the committed MD-0002 holdout manifest")
    if dataset.get("property_kind") != "formation_energy_per_atom":
        raise ValueError("TASK-0703 must score formation_energy_per_atom only")
    if tuple(config.get("baselines", ())) != BASELINE_IDS:
        raise ValueError("Benchmark baseline family differs from the frozen contract")
    controls = config.get("controls", {})
    if tuple(controls.get("seeds", ())) != CONTROL_SEEDS:
        raise ValueError("Control seeds differ from the frozen contract")
    split_sensitivity = config.get("split_sensitivity", {})
    if tuple(split_sensitivity.get("seeds", ())) != SPLIT_SEEDS:
        raise ValueError("Split-sensitivity seeds differ from the frozen contract")


def _load_formation_energy_rows(dataset: Any) -> list[MaterialsMd0002Row]:
    rows: list[MaterialsMd0002Row] = []
    for raw in dataset.rows_by_axis["formation_energy_per_atom"]:
        if raw["inclusion_status"] != "included" or raw["provenance_class"] != "computed_dft":
            continue
        cations = tuple(sorted(str(cation) for cation in raw["cations"]))
        if len(cations) != 2:
            raise ValueError(f"{raw['row_id']} does not contain exactly two cations")
        split = str(raw.get("split", ""))
        if split not in {"train", "validation", "holdout"}:
            raise ValueError(f"{raw['row_id']} has unsupported frozen split {split!r}")
        rows.append(
            MaterialsMd0002Row(
                row_id=str(raw["row_id"]),
                material_id=str(raw["material_id"]),
                formula_pretty=str(raw["formula_pretty"]),
                composition={str(key): float(value) for key, value in raw["composition"].items()},
                cations=(cations[0], cations[1]),
                nsites=int(raw["nsites"]) if raw.get("nsites") is not None else None,
                spacegroup_symbol=(
                    str(raw["spacegroup_symbol"])
                    if raw.get("spacegroup_symbol") is not None
                    else None
                ),
                value=float(raw["value"]),
                units=str(raw["units"]),
                split=split,
            )
        )
    if not rows:
        raise ValueError("No included MD-0002 formation-energy rows")
    return sorted(rows, key=lambda row: row.material_id)


def _frozen_splits(
    rows: list[MaterialsMd0002Row],
) -> dict[str, list[MaterialsMd0002Row]]:
    splits = {"train": [], "validation": [], "holdout": []}
    for row in rows:
        splits[row.split].append(row)
    return splits


def _assert_frozen_binding(
    payload: dict[str, Any],
    splits: dict[str, list[MaterialsMd0002Row]],
) -> None:
    expected = payload["split_counts_per_axis"]
    actual = {split: len(rows) for split, rows in splits.items()}
    if actual != expected:
        raise ValueError(f"Frozen split count mismatch: expected {expected}, got {actual}")
    if payload["live_external_fetch_allowed"] is not False:
        raise ValueError("MD-0002 payload unexpectedly allows live fetch")


def _fit_baselines(
    train_rows: list[MaterialsMd0002Row],
) -> dict[str, Predictor]:
    values = [row.value for row in train_rows]
    global_mean = mean(values)
    return {
        "global_mean": lambda _row: global_mean,
        "global_median": lambda _row: float(median(values)),
        "cation_group_mean": _fit_group_predictor(train_rows, cation_group, global_mean),
        "cation_pair_mean": _fit_group_predictor(train_rows, cation_pair, global_mean),
        "structure_or_prototype_mean": _fit_group_predictor(
            train_rows, structure_or_prototype, global_mean
        ),
    }


def _fit_group_predictor(
    train_rows: list[MaterialsMd0002Row],
    labeler: Labeler,
    fallback: float,
    *,
    labels: list[str] | None = None,
    values: list[float] | None = None,
) -> Predictor:
    grouped: dict[str, list[float]] = defaultdict(list)
    resolved_labels = labels or [labeler(row) for row in train_rows]
    resolved_values = values or [row.value for row in train_rows]
    for label, value in zip(resolved_labels, resolved_values, strict=True):
        grouped[label].append(value)
    means = {label: mean(group_values) for label, group_values in grouped.items()}
    return lambda row: means.get(labeler(row), fallback)


def _summarize_baseline(
    rows: list[MaterialsMd0002Row],
    splits: dict[str, list[MaterialsMd0002Row]],
    predictor: Predictor,
) -> dict[str, Any]:
    return {
        "metrics": {
            split: _residual_metrics(split_rows, predictor)
            for split, split_rows in splits.items()
        },
        "full_axis_metrics": _residual_metrics(rows, predictor),
        "holdout_subset_metrics": {
            "cation_group": _subset_metrics(splits["holdout"], predictor, cation_group),
            "cation_pair": _subset_metrics(splits["holdout"], predictor, cation_pair),
            "structure_or_prototype": _subset_metrics(
                splits["holdout"], predictor, structure_or_prototype
            ),
            "property_range": _subset_metrics(
                splits["holdout"], predictor, formation_energy_range
            ),
        },
    }


def _residual_metrics(
    rows: list[MaterialsMd0002Row], predictor: Predictor
) -> dict[str, float | int]:
    residuals = [row.value - predictor(row) for row in rows]
    absolute = [abs(value) for value in residuals]
    if not rows:
        return {"count": 0, "mae": 0.0, "rmse": 0.0, "median_abs_residual": 0.0}
    return {
        "count": len(rows),
        "mae": round(mean(absolute), 6),
        "rmse": round(mean(value * value for value in residuals) ** 0.5, 6),
        "median_abs_residual": round(float(median(absolute)), 6),
    }


def _subset_metrics(
    rows: list[MaterialsMd0002Row],
    predictor: Predictor,
    labeler: Labeler,
) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[MaterialsMd0002Row]] = defaultdict(list)
    for row in rows:
        grouped[labeler(row)].append(row)
    return {
        label: _residual_metrics(group_rows, predictor)
        for label, group_rows in sorted(grouped.items())
    }


def _run_controls(
    train_rows: list[MaterialsMd0002Row],
    holdout_rows: list[MaterialsMd0002Row],
    baseline_id: str,
) -> dict[str, Any]:
    labeler = _labeler_for_baseline(baseline_id)
    fallback = mean(row.value for row in train_rows)
    real_predictor = _fit_group_predictor(train_rows, labeler, fallback)
    real_mae = float(_residual_metrics(holdout_rows, real_predictor)["mae"])
    labels = [labeler(row) for row in train_rows]
    values = [row.value for row in train_rows]
    per_seed = []
    label_shuffle_maes = []
    group_shuffle_maes = []
    for seed in CONTROL_SEEDS:
        shuffled_values = list(values)
        random.Random(seed).shuffle(shuffled_values)
        label_predictor = _fit_group_predictor(
            train_rows, labeler, fallback, values=shuffled_values
        )
        label_mae = float(_residual_metrics(holdout_rows, label_predictor)["mae"])

        shuffled_labels = list(labels)
        random.Random(seed).shuffle(shuffled_labels)
        group_predictor = _fit_group_predictor(
            train_rows, labeler, fallback, labels=shuffled_labels
        )
        group_mae = float(_residual_metrics(holdout_rows, group_predictor)["mae"])
        label_shuffle_maes.append(label_mae)
        group_shuffle_maes.append(group_mae)
        per_seed.append(
            {
                "seed": seed,
                "label_shuffle_holdout_mae": label_mae,
                "cation_label_shuffle_holdout_mae": group_mae,
            }
        )
    return {
        "baseline_id": baseline_id,
        "real_holdout_mae": real_mae,
        "seeds": list(CONTROL_SEEDS),
        "per_seed": per_seed,
        "label_shuffle": _control_summary(real_mae, label_shuffle_maes),
        "cation_label_shuffle": _control_summary(real_mae, group_shuffle_maes),
        "row_order_invariance": _row_order_invariance(train_rows, holdout_rows, baseline_id),
    }


def _control_summary(real_mae: float, control_maes: list[float]) -> dict[str, Any]:
    return {
        "control_mae_min": round(min(control_maes), 6),
        "control_mae_median": round(float(median(control_maes)), 6),
        "control_mae_max": round(max(control_maes), 6),
        "real_beats_every_seed": real_mae < min(control_maes),
    }


def _row_order_invariance(
    train_rows: list[MaterialsMd0002Row],
    holdout_rows: list[MaterialsMd0002Row],
    baseline_id: str,
) -> dict[str, Any]:
    canonical = _fit_baselines(sorted(train_rows, key=lambda row: row.material_id))[baseline_id]
    reversed_predictor = _fit_baselines(
        sorted(train_rows, key=lambda row: row.material_id, reverse=True)
    )[baseline_id]
    canonical_mae = float(_residual_metrics(holdout_rows, canonical)["mae"])
    reversed_mae = float(_residual_metrics(holdout_rows, reversed_predictor)["mae"])
    return {
        "canonical_holdout_mae": canonical_mae,
        "reversed_input_holdout_mae": reversed_mae,
        "invariant": canonical_mae == reversed_mae,
    }


def _seeded_split_sensitivity(
    rows: list[MaterialsMd0002Row], selected_baseline_id: str
) -> dict[str, Any]:
    per_seed = []
    per_baseline: dict[str, list[float]] = {baseline_id: [] for baseline_id in BASELINE_IDS}
    wins = {baseline_id: 0 for baseline_id in BASELINE_IDS}
    for seed in SPLIT_SEEDS:
        shuffled = list(rows)
        random.Random(seed).shuffle(shuffled)
        cut = int(round(0.7 * len(shuffled)))
        train_rows, holdout_rows = shuffled[:cut], shuffled[cut:]
        predictors = _fit_baselines(train_rows)
        maes = {
            baseline_id: float(_residual_metrics(holdout_rows, predictor)["mae"])
            for baseline_id, predictor in predictors.items()
        }
        winner = min(maes, key=maes.get)
        wins[winner] += 1
        for baseline_id, value in maes.items():
            per_baseline[baseline_id].append(value)
        per_seed.append(
            {
                "seed": seed,
                "train_count": len(train_rows),
                "holdout_count": len(holdout_rows),
                "holdout_mae": maes,
                "winner": winner,
            }
        )
    summaries = {
        baseline_id: {
            "holdout_mae_mean": round(mean(values), 6),
            "holdout_mae_std": round(pstdev(values), 6),
            "holdout_mae_min": round(min(values), 6),
            "holdout_mae_max": round(max(values), 6),
            "seed_win_count": wins[baseline_id],
        }
        for baseline_id, values in per_baseline.items()
    }
    mean_winner = min(summaries, key=lambda baseline_id: summaries[baseline_id]["holdout_mae_mean"])
    runner_up = min(
        (baseline_id for baseline_id in BASELINE_IDS if baseline_id != selected_baseline_id),
        key=lambda baseline_id: summaries[baseline_id]["holdout_mae_mean"],
    )
    margin = round(
        summaries[runner_up]["holdout_mae_mean"]
        - summaries[selected_baseline_id]["holdout_mae_mean"],
        6,
    )
    noise = round(
        max(
            summaries[selected_baseline_id]["holdout_mae_std"],
            summaries[runner_up]["holdout_mae_std"],
        ),
        6,
    )
    robust = (
        mean_winner == selected_baseline_id
        and summaries[selected_baseline_id]["seed_win_count"] >= MIN_SEED_WINS
        and margin > noise
    )
    return {
        "seeds": list(SPLIT_SEEDS),
        "train_fraction": 0.7,
        "per_seed": per_seed,
        "per_baseline": summaries,
        "selected_baseline_id": selected_baseline_id,
        "seeded_mean_winner": mean_winner,
        "runner_up_baseline": runner_up,
        "seeded_mean_margin_over_runner_up": margin,
        "across_seed_noise": noise,
        "verdict": "split_robust" if robust else "split_sensitive",
    }


def _leave_one_group_out(
    rows: list[MaterialsMd0002Row],
    labeler: Labeler,
    baseline_id: str,
) -> dict[str, Any]:
    groups = sorted({labeler(row) for row in rows})
    per_group = {}
    maes = []
    for group in groups:
        holdout_rows = [row for row in rows if labeler(row) == group]
        train_rows = [row for row in rows if labeler(row) != group]
        if not holdout_rows or not train_rows:
            continue
        predictor = _fit_baselines(train_rows)[baseline_id]
        metrics = _residual_metrics(holdout_rows, predictor)
        per_group[group] = {
            "train_count": len(train_rows),
            "holdout_count": len(holdout_rows),
            **metrics,
        }
        maes.append(float(metrics["mae"]))
    return {
        "group_count": len(per_group),
        "per_group": per_group,
        "macro_holdout_mae": round(mean(maes), 6) if maes else None,
    }


def _promotion_assessment(
    *,
    baseline_summaries: dict[str, Any],
    best_global_id: str,
    best_composition_id: str,
    controls: dict[str, Any],
    split_sensitivity: dict[str, Any],
) -> dict[str, Any]:
    global_mae = float(baseline_summaries[best_global_id]["metrics"]["holdout"]["mae"])
    composition_mae = float(
        baseline_summaries[best_composition_id]["metrics"]["holdout"]["mae"]
    )
    absolute = round(global_mae - composition_mae, 6)
    relative = round(absolute / global_mae, 6) if global_mae else 0.0
    gates = {
        "beats_global_mean": composition_mae
        < float(baseline_summaries["global_mean"]["metrics"]["holdout"]["mae"]),
        "beats_global_median": composition_mae
        < float(baseline_summaries["global_median"]["metrics"]["holdout"]["mae"]),
        "relative_improvement_at_least_10_percent": relative >= MIN_RELATIVE_IMPROVEMENT,
        "absolute_improvement_at_least_0_05_eV_per_atom": absolute
        >= MIN_ABSOLUTE_IMPROVEMENT,
        "label_shuffle_control_pass": controls["label_shuffle"]["real_beats_every_seed"],
        "cation_label_shuffle_control_pass": controls["cation_label_shuffle"][
            "real_beats_every_seed"
        ],
        "row_order_invariant": controls["row_order_invariance"]["invariant"],
        "split_robust": split_sensitivity["verdict"] == "split_robust",
        "provenance_and_no_peek_stop_conditions_clear": True,
    }
    return {
        "selected_composition_baseline": best_composition_id,
        "best_global_null": best_global_id,
        "holdout_mae_absolute_improvement": absolute,
        "holdout_mae_relative_improvement": relative,
        "gates": gates,
        "failed_gates": [gate for gate, passed in gates.items() if not passed],
        "eligible_for_gate_a": all(gates.values()),
    }


def cation_pair(row: MaterialsMd0002Row) -> str:
    return "__".join(sorted(row.cations))


def cation_group(row: MaterialsMd0002Row) -> str:
    return "__".join(sorted(_element_group(element) for element in row.cations))


def structure_or_prototype(row: MaterialsMd0002Row) -> str:
    return row.spacegroup_symbol or "missing_spacegroup"


def formation_energy_range(row: MaterialsMd0002Row) -> str:
    for bin_spec in FORMATION_ENERGY_BINS:
        if "min" in bin_spec and row.value < float(bin_spec["min"]):
            continue
        if "max" in bin_spec and row.value >= float(bin_spec["max"]):
            continue
        return str(bin_spec["id"])
    return "unbinned"


def _element_group(element: str) -> str:
    for group, elements in ELEMENT_GROUPS.items():
        if element in elements:
            return group
    return "mixed_or_ambiguous"


def _labeler_for_baseline(baseline_id: str) -> Labeler:
    if baseline_id == "cation_group_mean":
        return cation_group
    if baseline_id == "cation_pair_mean":
        return cation_pair
    raise ValueError(f"{baseline_id} is not a composition baseline")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
