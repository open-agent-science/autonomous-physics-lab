"""MD-0001 band-gap null-control audit (TASK-0579).

Tests whether the cation-group-mean composition baseline genuinely beats null
predictors on the frozen band-gap holdout, or whether its apparent edge is
within the noise of deterministic label / composition shuffles.

It uses only committed MD-0001 rows and the frozen split from the TASK-0550
baseline engine. It adds no rows, changes no holdout membership, and makes no
material-property claim. Formation energy is reference context only and is never
pooled with band gap.
"""
from __future__ import annotations

import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from physics_lab.engines.materials_md0001_baseline import (
    _included_rows,
    _load_axis_rows,
    _split_rows,
    cation_group,
)

BAND_GAP_PROPERTY = "band_gap"


def _global_mean_mae(train_values: list[float], holdout_values: list[float]) -> float:
    mean = sum(train_values) / len(train_values)
    return sum(abs(v - mean) for v in holdout_values) / len(holdout_values)


def _cation_group_mean_mae(
    train_groups: list[str],
    train_values: list[float],
    holdout_groups: list[str],
    holdout_values: list[float],
) -> float:
    by_group: dict[str, list[float]] = defaultdict(list)
    for group, value in zip(train_groups, train_values):
        by_group[group].append(value)
    group_mean = {g: sum(v) / len(v) for g, v in by_group.items()}
    global_mean = sum(train_values) / len(train_values)
    preds = [group_mean.get(g, global_mean) for g in holdout_groups]
    return sum(abs(t - p) for t, p in zip(holdout_values, preds)) / len(holdout_values)


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    idx = min(len(sorted_values) - 1, max(0, round(q * (len(sorted_values) - 1))))
    return sorted_values[idx]


def _control_distribution(maes: list[float], real_mae: float) -> dict[str, Any]:
    ordered = sorted(maes)
    n = len(ordered)
    # one-sided: fraction of controls at least as good (low) as the real baseline
    at_least_as_good = sum(1 for m in ordered if m <= real_mae)
    return {
        "permutations": n,
        "control_mae_mean": round(sum(ordered) / n, 6),
        "control_mae_p05": round(_quantile(ordered, 0.05), 6),
        "control_mae_p50": round(_quantile(ordered, 0.50), 6),
        "control_mae_p95": round(_quantile(ordered, 0.95), 6),
        "control_mae_min": round(ordered[0], 6),
        "fraction_controls_at_least_as_good_as_real": round(at_least_as_good / n, 6),
    }


def run_band_gap_null_control_audit(
    config_path: Path,
    *,
    permutations: int = 1000,
    seed: int = 0,
) -> dict[str, Any]:
    """Deterministic band-gap null-control audit. Reproducible for a fixed seed."""
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8")) or {}
    dataset_cfg = config["dataset"]
    axis = next(a for a in dataset_cfg["axes"] if a["property_kind"] == BAND_GAP_PROPERTY)

    rows = _load_axis_rows(Path(axis["dataset_file"]))
    included = _included_rows(rows, expected_property_kind=BAND_GAP_PROPERTY)
    splits = _split_rows(included)
    train, holdout = splits["train"], splits["holdout"]

    train_groups = [cation_group(r) for r in train]
    train_values = [r.value for r in train]
    holdout_groups = [cation_group(r) for r in holdout]
    holdout_values = [r.value for r in holdout]

    real_global = _global_mean_mae(train_values, holdout_values)
    real_cation = _cation_group_mean_mae(train_groups, train_values, holdout_groups, holdout_values)
    skill_vs_null = round(real_global - real_cation, 6)

    rng = random.Random(seed)
    label_shuffle_maes: list[float] = []
    group_shuffle_maes: list[float] = []
    for _ in range(permutations):
        shuffled_values = train_values[:]
        rng.shuffle(shuffled_values)
        label_shuffle_maes.append(
            _cation_group_mean_mae(train_groups, shuffled_values, holdout_groups, holdout_values)
        )
        shuffled_groups = train_groups[:]
        rng.shuffle(shuffled_groups)
        group_shuffle_maes.append(
            _cation_group_mean_mae(shuffled_groups, train_values, holdout_groups, holdout_values)
        )

    label_ctrl = _control_distribution(label_shuffle_maes, real_cation)
    group_ctrl = _control_distribution(group_shuffle_maes, real_cation)

    # The composition signal "survives" only if the real baseline both beats the
    # global null and is rarely matched by either shuffle control (one-sided 5%).
    survives = (
        real_cation < real_global
        and label_ctrl["fraction_controls_at_least_as_good_as_real"] < 0.05
        and group_ctrl["fraction_controls_at_least_as_good_as_real"] < 0.05
    )
    verdict = "SIGNAL_SURVIVES_CONTROLS" if survives else "NO_SIGNAL_BEYOND_NULL"

    return {
        "task_id": "TASK-0579",
        "audit_id": "materials-md0001-band-gap-null-control-audit",
        "axis": BAND_GAP_PROPERTY,
        "units": axis["units"],
        "provenance_class": axis["provenance_class"],
        "input_references": {
            "band_gap_dataset": axis["dataset_file"],
            "holdout_manifest": dataset_cfg["holdout_manifest_ref"],
            "snapshot_checksum_sha256": dataset_cfg["snapshot_checksum_sha256"],
        },
        "split_counts": {"train": len(train), "holdout": len(holdout)},
        "config": {"permutations": permutations, "seed": seed},
        "real_baselines_holdout_mae": {
            "global_mean_null": round(real_global, 6),
            "cation_group_mean": round(real_cation, 6),
            "cation_group_skill_vs_global_null": skill_vs_null,
        },
        "controls": {
            "label_shuffle": label_ctrl,
            "cation_group_shuffle": group_ctrl,
        },
        "verdict": verdict,
        "limitations": [
            "Computed-DFT stable binary oxides only; no experimental band gaps.",
            "Frozen TASK-0550 split and holdout membership; not retuned.",
            "Null-control audit only; no benchmark promotion, PRED, CLAIM, or material-design claim.",
            "Formation energy is reference context and is never pooled with band gap.",
            "Small holdout (n=33): absence of survived signal is a null result, not a falsification of band-gap structure.",
        ],
        "output_routing": {
            "canonical_destination": "agent_runs/AGENT-RUN-0058/",
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
        },
    }
