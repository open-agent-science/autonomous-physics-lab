"""Frozen Joback Tb family-stratified transfer audit for TASK-0851."""

from __future__ import annotations

from collections import Counter, defaultdict
import math
from pathlib import Path
import random
import statistics
from typing import Any

import numpy as np
import yaml

from physics_lab.engines.joback_tb import JOBACK_BASE_JR1987, joback_tb

SHUFFLE_SEED = 851
SURVIVAL_MARGIN_K = 5.0


def load_audit_fixture(path: str | Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if payload.get("task_id") != "TASK-0851":
        raise ValueError("ThermoML audit fixture must belong to TASK-0851")
    if payload.get("source", {}).get("archive_bytes_committed") is not False:
        raise ValueError("ThermoML source archive must not be committed")
    rows = payload.get("rows") or []
    if not rows:
        raise ValueError("ThermoML audit fixture must contain bounded rows")
    family_counts = Counter(row["family"] for row in rows)
    if len(family_counts) < 5 or len(set(family_counts.values())) != 1:
        raise ValueError("Fixture must be balanced across at least five families")
    for row in rows:
        if not row.get("joback_group_counts"):
            raise ValueError(f"{row.get('row_id')} lacks frozen Joback groups")
        if float(row["experimental_tb_k"]) <= 0:
            raise ValueError(f"{row.get('row_id')} has invalid experimental Tb")
    return rows, payload


def _mae(observed: list[float], predicted: list[float]) -> float:
    return float(np.mean(np.abs(np.asarray(observed) - np.asarray(predicted))))


def _rmse(observed: list[float], predicted: list[float]) -> float:
    residual = np.asarray(observed) - np.asarray(predicted)
    return float(np.sqrt(np.mean(residual * residual)))


def _weighted_mae(rows: list[dict[str, Any]], predicted: list[float]) -> float | None:
    selected = [
        (row, value)
        for row, value in zip(rows, predicted, strict=True)
        if row.get("expanded_uncertainty_k") not in (None, 0)
    ]
    if not selected:
        return None
    weights = np.asarray(
        [1.0 / max(float(row["expanded_uncertainty_k"]), 0.1) ** 2 for row, _ in selected]
    )
    errors = np.asarray([abs(float(row["experimental_tb_k"]) - value) for row, value in selected])
    return float(np.average(errors, weights=weights))


def _score(rows: list[dict[str, Any]], predicted: list[float]) -> dict[str, Any]:
    observed = [float(row["experimental_tb_k"]) for row in rows]
    weighted = _weighted_mae(rows, predicted)
    return {
        "row_count": len(rows),
        "mae_k": round(_mae(observed, predicted), 6),
        "rmse_k": round(_rmse(observed, predicted), 6),
        "uncertainty_weighted_mae_k": None if weighted is None else round(weighted, 6),
    }


def _group_similarity(left: dict[str, int], right: dict[str, int]) -> float:
    keys = set(left) | set(right)
    intersection = sum(min(left.get(key, 0), right.get(key, 0)) for key in keys)
    union = sum(max(left.get(key, 0), right.get(key, 0)) for key in keys)
    return 0.0 if union == 0 else intersection / union


def _nearest_homolog_predictions(
    train: list[dict[str, Any]], holdout: list[dict[str, Any]]
) -> list[float]:
    predictions: list[float] = []
    for row in holdout:
        groups = row["joback_group_counts"]
        nearest = min(
            train,
            key=lambda candidate: (
                -_group_similarity(groups, candidate["joback_group_counts"]),
                abs(
                    float(row["molecular_weight_g_mol"])
                    - float(candidate["molecular_weight_g_mol"])
                ),
                candidate["inchi_key"],
            ),
        )
        predictions.append(float(nearest["experimental_tb_k"]))
    return predictions


def _molecular_weight_predictions(
    train: list[dict[str, Any]], holdout: list[dict[str, Any]]
) -> list[float]:
    x = np.asarray([float(row["molecular_weight_g_mol"]) for row in train])
    y = np.asarray([float(row["experimental_tb_k"]) for row in train])
    slope, intercept = np.polyfit(x, y, 1)
    return [float(intercept + slope * float(row["molecular_weight_g_mol"])) for row in holdout]


def run_family_transfer(rows: list[dict[str, Any]]) -> dict[str, Any]:
    families = sorted({row["family"] for row in rows})
    shuffled_groups = [row["joback_group_counts"] for row in rows]
    random.Random(SHUFFLE_SEED).shuffle(shuffled_groups)
    shuffled_by_id = {
        row["row_id"]: groups for row, groups in zip(rows, shuffled_groups, strict=True)
    }

    pooled: dict[str, list[tuple[dict[str, Any], float]]] = defaultdict(list)
    per_family: dict[str, Any] = {}
    for family in families:
        holdout = [row for row in rows if row["family"] == family]
        train = [row for row in rows if row["family"] != family]
        observed = [float(row["experimental_tb_k"]) for row in holdout]
        predictions = {
            "joback": [joback_tb(row["joback_group_counts"], base=JOBACK_BASE_JR1987) for row in holdout],
            "global_median": [statistics.median(float(row["experimental_tb_k"]) for row in train)] * len(holdout),
            "molecular_weight_only": _molecular_weight_predictions(train, holdout),
            "nearest_homolog": _nearest_homolog_predictions(train, holdout),
            "shuffled_group_counts": [
                joback_tb(shuffled_by_id[row["row_id"]], base=JOBACK_BASE_JR1987)
                for row in holdout
            ],
            "within_family_constant": [statistics.mean(observed)] * len(holdout),
        }
        scores = {name: _score(holdout, values) for name, values in predictions.items()}
        best_control = min(
            (name for name in scores if name not in {"joback", "within_family_constant"}),
            key=lambda name: float(scores[name]["mae_k"]),
        )
        margin = float(scores[best_control]["mae_k"]) - float(scores["joback"]["mae_k"])
        per_family[family] = {
            "scores": scores,
            "best_non_oracle_control": best_control,
            "joback_margin_vs_best_non_oracle_k": round(margin, 6),
            "clears_survival_margin": margin >= SURVIVAL_MARGIN_K,
        }
        for name, values in predictions.items():
            pooled[name].extend(zip(holdout, values, strict=True))

    aggregate = {
        name: _score([row for row, _ in pairs], [value for _, value in pairs])
        for name, pairs in pooled.items()
    }
    best_control = min(
        (name for name in aggregate if name not in {"joback", "within_family_constant"}),
        key=lambda name: float(aggregate[name]["mae_k"]),
    )
    margin = float(aggregate[best_control]["mae_k"]) - float(aggregate["joback"]["mae_k"])
    passing_families = sum(item["clears_survival_margin"] for item in per_family.values())
    required_families = math.ceil(2 * len(per_family) / 3)
    verdict = (
        "TRANSFER_SUPPORTED_IN_SCOPE"
        if margin >= SURVIVAL_MARGIN_K and passing_families >= required_families
        else "FAMILY_DEPENDENT"
    )
    return {
        "verdict": verdict,
        "row_count": len(rows),
        "family_count": len(families),
        "family_counts": dict(sorted(Counter(row["family"] for row in rows).items())),
        "survival_margin_k": SURVIVAL_MARGIN_K,
        "required_family_pass_fraction": "2/3",
        "aggregate": aggregate,
        "best_non_oracle_control": best_control,
        "joback_margin_vs_best_non_oracle_k": round(margin, 6),
        "families_clearing_margin": passing_families,
        "families_required_to_clear": required_families,
        "per_family": per_family,
    }


def run_fixture(path: str | Path) -> dict[str, Any]:
    rows, payload = load_audit_fixture(path)
    return {
        "task_id": "TASK-0851",
        "benchmark_id": "thermoml-tb-family-stratified-transfer",
        "source": payload["source"],
        "selection": payload["extraction"],
        "rights": payload["rights"],
        "transfer": run_family_transfer(rows),
    }


__all__ = ["load_audit_fixture", "run_family_transfer", "run_fixture"]

