"""No-refit transfer of the frozen RESULT-0022 relation to CHARA rows."""

from __future__ import annotations

import hashlib
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    REPO_ROOT
    / "data/textbook_formula_audit/stellar_ml/chara_fixed_relation_transfer_contract.yaml"
)

ALPHA_FROZEN = 4.526004
ALPHA_TEXTBOOK_3P5 = 3.5
ALPHA_TEXTBOOK_4P0 = 4.0
FIXED_INTERCEPT_LOG_L0 = 0.0
SURVIVAL_MARGIN_DEX = 0.04
MINIMUM_EFFECTIVE_GROUPS = 5


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mass_band(mass_solar: float) -> str:
    if mass_solar < 0.5:
        return "very_low"
    if mass_solar < 1.0:
        return "low"
    if mass_solar < 2.0:
        return "solar"
    if mass_solar < 8.0:
        return "intermediate"
    return "high"


def _mae(rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]) -> float:
    return statistics.fmean(
        abs(math.log10(float(row["luminosity_solar"])) - predict(row))
        for row in rows
    )


def _max_abs_error(
    rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]
) -> float:
    return max(
        abs(math.log10(float(row["luminosity_solar"])) - predict(row))
        for row in rows
    )


def _relative_errors(
    rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]
) -> tuple[float, float]:
    errors = [
        abs(10 ** predict(row) - float(row["luminosity_solar"]))
        / float(row["luminosity_solar"])
        for row in rows
    ]
    return statistics.fmean(errors), max(errors)


def _verified_inputs() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, str]
]:
    contract = _load_yaml(CONTRACT_PATH)
    documents: dict[str, dict[str, Any]] = {}
    hashes: dict[str, str] = {}
    for key, pin in contract["frozen_inputs"].items():
        path = REPO_ROOT / str(pin["path"])
        observed = _sha256(path)
        if observed != pin["sha256"]:
            raise ValueError(
                f"Frozen input hash drift for {key}: {observed} != {pin['sha256']}"
            )
        documents[key] = _load_yaml(path)
        hashes[key] = observed

    chara = documents["chara_rows"]
    replay = chara.get("independent_source_replay", {})
    if replay.get("verdict") != "INDEPENDENT_SOURCE_REPLAY_PASS":
        raise ValueError("SOURCE_CONTESTED_NO_SCORE: independent source replay is not PASS")

    rows = list(chara.get("rows", []))
    if len(rows) != 12 or len({row["system_id"] for row in rows}) != 6:
        raise ValueError("SOURCE_CONTESTED_NO_SCORE: expected exactly 12 rows from 6 systems")

    ledger = documents["dependence_ledger"]
    group_by_system = {
        item["queried_id"]: item["environment_group"]
        for item in ledger.get("candidates", [])
    }
    for row in rows:
        try:
            row["effective_group"] = group_by_system[row["system_id"]]
        except KeyError as exc:
            raise ValueError(
                f"SOURCE_CONTESTED_NO_SCORE: missing dependence group for {row['system_id']}"
            ) from exc
        if row["effective_group"] == "melotte-25":
            raise ValueError(
                "SOURCE_CONTESTED_NO_SCORE: admitted CHARA row overlaps the DEBCat environment"
            )

    return contract, chara, ledger, rows, hashes


def _null_predictor(debcat: dict[str, Any]) -> tuple[Callable[[dict[str, Any]], float], dict[str, Any]]:
    train = [
        row
        for row in debcat["rows"]
        if row.get("admissibility") == "admitted"
        and row.get("lane") == "train"
        and row.get("evolutionary_stage_flag") == "main_sequence_compatible"
        and 0.5 <= float(row["mass_solar"]) < 2.0
    ]
    if len(train) != 102:
        raise ValueError(f"Frozen RESULT-0022 train-lane drift: expected 102 rows, got {len(train)}")
    values_by_band: dict[str, list[float]] = defaultdict(list)
    for row in train:
        values_by_band[str(row["mass_band"])].append(
            float(row["log_luminosity_solar"])
        )
    medians = {
        band: statistics.median(values) for band, values in values_by_band.items()
    }
    global_median = statistics.median(
        [float(row["log_luminosity_solar"]) for row in train]
    )

    def predict(row: dict[str, Any]) -> float:
        return medians.get(_mass_band(float(row["mass_solar"])), global_median)

    return predict, {
        "train_count": len(train),
        "train_mass_band_medians_log_l": {
            key: round(value, 6) for key, value in sorted(medians.items())
        },
        "global_train_median_log_l": round(global_median, 6),
        "unseen_mass_band_fallback": "global_train_median_log_l",
        "target_rows_used_for_null": 0,
    }


def _model_metrics(
    rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]
) -> dict[str, float]:
    mean_rel, max_rel = _relative_errors(rows, predict)
    return {
        "mae_dex": round(_mae(rows, predict), 6),
        "max_abs_error_dex": round(_max_abs_error(rows, predict), 6),
        "mean_relative_error": round(mean_rel, 6),
        "max_relative_error": round(max_rel, 6),
    }


def compute_chara_transfer_metrics() -> dict[str, Any]:
    """Evaluate the frozen relation and predeclared controls without refitting."""
    contract, chara, ledger, rows, hashes = _verified_inputs()
    debcat = _load_yaml(REPO_ROOT / contract["frozen_inputs"]["debcat_rows"]["path"])
    null_predict, null_training = _null_predictor(debcat)

    predictors: dict[str, Callable[[dict[str, Any]], float]] = {
        "model_result0022_frozen_alpha": lambda row: ALPHA_FROZEN
        * math.log10(float(row["mass_solar"])),
        "control_textbook_alpha_3p5": lambda row: ALPHA_TEXTBOOK_3P5
        * math.log10(float(row["mass_solar"])),
        "control_textbook_alpha_4p0": lambda row: ALPHA_TEXTBOOK_4P0
        * math.log10(float(row["mass_solar"])),
        "control_result0022_massband_median_null": null_predict,
    }
    models = {name: _model_metrics(rows, fn) for name, fn in predictors.items()}
    control_names = [name for name in models if name.startswith("control_")]
    best_control = min(control_names, key=lambda name: models[name]["mae_dex"])
    candidate_mae = models["model_result0022_frozen_alpha"]["mae_dex"]
    best_control_mae = models[best_control]["mae_dex"]
    margin = round(best_control_mae - candidate_mae, 6)

    by_system: dict[str, Any] = {}
    for system_id in sorted({str(row["system_id"]) for row in rows}):
        subset = [row for row in rows if row["system_id"] == system_id]
        by_system[system_id] = {
            "effective_group": subset[0]["effective_group"],
            "component_count": len(subset),
            "mae_dex": {
                name: round(_mae(subset, fn), 6) for name, fn in predictors.items()
            },
        }

    effective_groups = sorted({str(row["effective_group"]) for row in rows})
    if len(effective_groups) < MINIMUM_EFFECTIVE_GROUPS:
        verdict = "HOLD_UNDERPOWERED"
    elif margin >= SURVIVAL_MARGIN_DEX:
        verdict = "VALID_IN_RANGE"
    elif margin > 0:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "INVALID"

    leave_one_group_out: list[dict[str, Any]] = []
    for group in effective_groups:
        subset = [row for row in rows if row["effective_group"] != group]
        candidate = _mae(subset, predictors["model_result0022_frozen_alpha"])
        control_scores = {
            name: _mae(subset, predictors[name]) for name in control_names
        }
        loo_best = min(control_scores, key=control_scores.get)
        leave_one_group_out.append(
            {
                "excluded_group": group,
                "remaining_group_count": len(effective_groups) - 1,
                "best_control": loo_best,
                "margin_over_best_control_dex": round(
                    control_scores[loo_best] - candidate, 6
                ),
            }
        )

    by_source: dict[str, Any] = {}
    for source_id in sorted({str(row["source_id"]) for row in rows}):
        subset = [row for row in rows if row["source_id"] == source_id]
        by_source[source_id] = {
            "component_count": len(subset),
            "candidate_mae_dex": round(
                _mae(subset, predictors["model_result0022_frozen_alpha"]), 6
            ),
        }

    return {
        "task_id": "TASK-1050",
        "source_integrity": {
            "verified_hashes": hashes,
            "source_replay_verdict": chara["independent_source_replay"]["verdict"],
            "component_count": len(rows),
            "system_count": len({row["system_id"] for row in rows}),
            "effective_group_count": len(effective_groups),
            "effective_groups": effective_groups,
            "melotte_25_rows_admitted": 0,
            "minimum_effective_group_count": int(
                ledger["grouping_contract"]["minimum_effective_independent_group_count"]
            ),
        },
        "frozen_contract": {
            "source_result_id": "RESULT-0022",
            "formula": "log10(L/Lsun) = 4.526004 * log10(M/Msun)",
            "alpha": ALPHA_FROZEN,
            "fixed_intercept_log_l0": FIXED_INTERCEPT_LOG_L0,
            "refit_on_chara": False,
            "survival_margin_dex": SURVIVAL_MARGIN_DEX,
            "primary_metric": "component_level_log_luminosity_mae_dex",
            "selection_after_metrics": False,
        },
        "null_training": null_training,
        "models": models,
        "best_control": best_control,
        "best_control_mae_dex": best_control_mae,
        "candidate_mae_dex": candidate_mae,
        "margin_over_best_control_dex": margin,
        "clears_survival_margin": margin >= SURVIVAL_MARGIN_DEX,
        "per_system_diagnostics": by_system,
        "source_provenance_sensitivity": by_source,
        "leave_one_effective_group_out": leave_one_group_out,
        "leave_one_group_margin_min_dex": min(
            item["margin_over_best_control_dex"] for item in leave_one_group_out
        ),
        "leave_one_group_margin_max_dex": max(
            item["margin_over_best_control_dex"] for item in leave_one_group_out
        ),
        "verdict": verdict,
    }


__all__ = [
    "ALPHA_FROZEN",
    "CONTRACT_PATH",
    "MINIMUM_EFFECTIVE_GROUPS",
    "SURVIVAL_MARGIN_DEX",
    "compute_chara_transfer_metrics",
]
