"""Engine: transfer benchmark of the frozen RESULT-0022 stellar M-L relation.

Takes the RESULT-0022 mass-luminosity relation ``log L = alpha * log M``
(fixed intercept ``log L0 = 0``) with its train-fitted exponent
``alpha = 4.526004`` and evaluates it BY TRANSFER on the disjoint high-mass
DEBCat regime (``mass_solar > 2.0``) selected by the TASK-0819 transfer scout.

The relation is FROZEN: ``alpha`` is the value RESULT-0022 fitted on the
``0.5-2.0 M_sun`` main-sequence train lane and is NOT refit on the high-mass
holdout. This module never edits RESULT-0022 or the committed DEBCat
main-sequence slice; it only reads the committed Route-2 rows.

Discipline (blind-holdout / controls-first):

- The survival margin and every control are PREDECLARED as module constants
  *before* any high-mass holdout error is computed.
- The judge is experimental: DEBCat dynamical masses are real measurements.
- Per-row luminosity provenance (catalogue vs Stefan-Boltzmann) and
  evolutionary stage are stratified, because the high-mass regime is
  stage-confounded and provenance-mixed (TASK-0819 scout finding).
- Deterministic and pure: re-running yields identical numbers (Gate-B style).

Both outcomes are recorded honestly: the frozen relation either clears the
predeclared margin over the best control on the high-mass holdout (transfer
survives) or it does not (an honest regime-limited boundary). No refit, no
added free parameters, no claim promotion.
"""

from __future__ import annotations

import hashlib
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROWS_PATH = REPO_ROOT / "data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml"

# ---------------------------------------------------------------------------
# FROZEN PREDICTOR (RESULT-0022 best model: model_train_fitted_alpha).
# log L = ALPHA_FROZEN * log M, fixed intercept log L0 = 0.
# This value was fit by RESULT-0022 on the 0.5-2.0 M_sun main-sequence TRAIN
# lane only. It is frozen here and is NEVER refit on the high-mass holdout.
# ---------------------------------------------------------------------------
ALPHA_FROZEN = 4.526004
FROZEN_INTERCEPT_LOG_L0 = 0.0
RESULT_0022_ID = "RESULT-0022"

# Source main-sequence slice used only to re-derive/verify the frozen alpha
# (so the predictor stays pinned to RESULT-0022); not part of the holdout.
MAIN_SEQUENCE_MASS_RANGE = (0.5, 2.0)  # half-open [lo, hi)
MAIN_SEQUENCE_STAGE = "main_sequence_compatible"
ALPHA_VERIFY_TOLERANCE = 1e-6

# ---------------------------------------------------------------------------
# PREDECLARED TRANSFER CONTRACT (frozen BEFORE any holdout error is read).
# ---------------------------------------------------------------------------
# Disjoint high-mass transfer regime selected by the TASK-0819 scout.
HIGH_MASS_THRESHOLD_SOLAR = 2.0  # strict: mass_solar > 2.0
SPLIT_KEY = "system_id"  # leakage guard: binaries never split across lanes
TARGET_FIELD = "log_luminosity_solar"
# Primary lane is the high-mass MAIN-SEQUENCE-COMPATIBLE holdout, the apples-to-
# apples stage match to the RESULT-0022 fit slice. All-stage high-mass holdout
# is reported as a documented secondary stratum (stage-confounded diagnostic).
PRIMARY_STAGE = "main_sequence_compatible"
# Survival margin: the frozen relation must beat the BEST control's holdout MAE
# by at least this many dex. 0.04 dex is the RESULT-0022 split-noise reference
# (the across-seed margin spread established by the source result); it is a
# pre-existing principled threshold, not chosen by inspecting high-mass error.
SURVIVAL_MARGIN_DEX = 0.04
# Deterministic control seeds (same family RESULT-0022 used).
CONTROL_SEEDS = (11, 23, 37, 53, 71)
MISSING_VALUE_SENTINEL = -9.99

STAGE_ORDER = ("main_sequence_compatible", "subgiant", "evolved", "unknown")


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_admitted_rows() -> list[dict[str, Any]]:
    doc = yaml.safe_load(ROWS_PATH.read_text(encoding="utf-8"))
    rows = doc["rows"] if isinstance(doc, dict) and "rows" in doc else doc
    out: list[dict[str, Any]] = []
    for r in rows:
        if r.get("admissibility") != "admitted":
            continue
        log_m = float(r["log_mass_solar"])
        log_l = float(r[TARGET_FIELD])
        # Defensive: drop any sentinel-missing log values (none expected here).
        if abs(log_m - MISSING_VALUE_SENTINEL) < 1e-9 or abs(log_l - MISSING_VALUE_SENTINEL) < 1e-9:
            continue
        out.append(r)
    return out


def _frozen_predict_log_l(row: dict[str, Any]) -> float:
    return ALPHA_FROZEN * float(row["log_mass_solar"]) + FROZEN_INTERCEPT_LOG_L0


def _mae(rows: list[dict[str, Any]], predict: Callable[[dict[str, Any]], float]) -> float:
    return statistics.fmean(abs(float(r[TARGET_FIELD]) - predict(r)) for r in rows)


def _verify_frozen_alpha(admitted: list[dict[str, Any]]) -> float:
    """Re-derive RESULT-0022's train-fitted alpha and confirm the frozen value.

    Guards against silent drift between this transfer benchmark and the source
    relation. Raises if the committed rows no longer reproduce ALPHA_FROZEN.
    """
    lo, hi = MAIN_SEQUENCE_MASS_RANGE
    ms_train = [
        r
        for r in admitted
        if lo <= float(r["mass_solar"]) < hi
        and r.get("evolutionary_stage_flag") == MAIN_SEQUENCE_STAGE
        and r["lane"] == "train"
    ]
    sxx = sum(float(r["log_mass_solar"]) ** 2 for r in ms_train)
    sxy = sum(float(r["log_mass_solar"]) * float(r[TARGET_FIELD]) for r in ms_train)
    rederived = sxy / sxx
    if abs(rederived - ALPHA_FROZEN) > ALPHA_VERIFY_TOLERANCE:
        raise ValueError(
            "Frozen RESULT-0022 alpha does not reproduce from committed rows: "
            f"re-derived {rederived:.6f} vs frozen {ALPHA_FROZEN:.6f}. The frozen "
            "predictor must match RESULT-0022; refusing to transfer a drifted relation."
        )
    return rederived


# --- Controls (predeclared). All evaluated on the SAME high-mass holdout. -----


def _massband_null_predictor(train: list[dict[str, Any]]) -> Callable[[dict[str, Any]], float]:
    """Per-mass-band train-median log L, with global-median fallback (null)."""
    band: dict[str, list[float]] = defaultdict(list)
    for r in train:
        band[r["mass_band"]].append(float(r[TARGET_FIELD]))
    band_median = {k: statistics.median(v) for k, v in band.items()}
    global_median = statistics.median([float(r[TARGET_FIELD]) for r in train])
    return lambda r: band_median.get(r["mass_band"], global_median)


def _massmatched_predictor(train: list[dict[str, Any]]) -> Callable[[dict[str, Any]], float]:
    """Mass-matched control: per-mass-band train-MEAN log L (mass-aware constant).

    Distinct from the null (band median) and from the relation (slope in log M):
    it captures only the mean luminosity level within a mass band, with no
    power-law structure. A relation that merely tracks the band-mean luminosity
    cannot beat this control.
    """
    band: dict[str, list[float]] = defaultdict(list)
    for r in train:
        band[r["mass_band"]].append(float(r[TARGET_FIELD]))
    band_mean = {k: statistics.fmean(v) for k, v in band.items()}
    global_mean = statistics.fmean([float(r[TARGET_FIELD]) for r in train])
    return lambda r: band_mean.get(r["mass_band"], global_mean)


def _shuffled_control_mae(holdout: list[dict[str, Any]], seeds: tuple[int, ...]) -> dict[str, Any]:
    """Deterministic shuffled control: permute holdout luminosities, score the
    frozen relation against the shuffled targets. A real signal must beat the
    best (lowest-MAE) shuffle across seeds."""
    per_seed: list[float] = []
    for seed in seeds:
        lums = [float(r[TARGET_FIELD]) for r in holdout]
        random.Random(seed).shuffle(lums)
        permuted = [dict(r, **{TARGET_FIELD: lum}) for r, lum in zip(holdout, lums)]
        per_seed.append(round(_mae(permuted, _frozen_predict_log_l), 6))
    return {
        "per_seed_mae_dex": per_seed,
        "best_mae_dex": round(min(per_seed), 6),  # most adversarial (lowest) shuffle
        "mean_mae_dex": round(statistics.fmean(per_seed), 6),
    }


def _rel_errors(rows: list[dict[str, Any]], log_predict: Callable[[dict[str, Any]], float]) -> tuple[float, float]:
    errors = [abs(10 ** log_predict(r) - float(r["luminosity_solar"])) / float(r["luminosity_solar"]) for r in rows]
    return round(statistics.fmean(errors), 6), round(max(errors), 6)


def _regime_composition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def counts(key: str, default: str = "unknown") -> dict[str, int]:
        c: dict[str, int] = defaultdict(int)
        for r in rows:
            c[str(r.get(key, default))] += 1
        return dict(sorted(c.items()))

    masses = [float(r["mass_solar"]) for r in rows]
    return {
        "component_rows": len(rows),
        "distinct_systems": len({r[SPLIT_KEY] for r in rows}),
        "mass_solar_min": round(min(masses), 4),
        "mass_solar_max": round(max(masses), 4),
        "by_lane": counts("lane"),
        "by_stage": counts("evolutionary_stage_flag"),
        "by_mass_band": counts("mass_band"),
        "by_luminosity_source": counts("luminosity_source"),
        "by_luminosity_uncertainty_class": counts("luminosity_uncertainty_class"),
        "by_mass_uncertainty_class": counts("mass_uncertainty_class"),
        "mass_provenance_classes": counts("mass_provenance_class"),
    }


def compute_transfer_metrics() -> dict[str, Any]:
    """Transfer the frozen RESULT-0022 relation onto the high-mass holdout.

    Deterministic. The predeclared survival margin and controls are fixed as
    module constants above before any holdout error is read here.
    """
    admitted = _load_admitted_rows()
    rederived_alpha = _verify_frozen_alpha(admitted)

    high_mass = [r for r in admitted if float(r["mass_solar"]) > HIGH_MASS_THRESHOLD_SOLAR]

    # Primary lane: high-mass main-sequence-compatible (stage-matched to fit).
    primary = [r for r in high_mass if r.get("evolutionary_stage_flag") == PRIMARY_STAGE]
    primary_train = [r for r in primary if r["lane"] == "train"]
    primary_holdout = [r for r in primary if r["lane"] == "holdout"]

    # Secondary stratum (diagnostic): ALL-stage high-mass.
    allstage_train = [r for r in high_mass if r["lane"] == "train"]
    allstage_holdout = [r for r in high_mass if r["lane"] == "holdout"]

    def evaluate(train: list[dict[str, Any]], holdout: list[dict[str, Any]]) -> dict[str, Any]:
        frozen_mae = round(_mae(holdout, _frozen_predict_log_l), 6)
        null_mae = round(_mae(holdout, _massband_null_predictor(train)), 6)
        massmatched_mae = round(_mae(holdout, _massmatched_predictor(train)), 6)
        shuffled = _shuffled_control_mae(holdout, CONTROL_SEEDS)
        controls = {
            "null_massband_median": null_mae,
            "mass_matched_massband_mean": massmatched_mae,
            "shuffled_target_best": shuffled["best_mae_dex"],
        }
        # Best (lowest-MAE) control is the hardest to beat.
        best_control_name = min(controls, key=lambda k: controls[k])
        best_control_mae = controls[best_control_name]
        margin_over_best = round(best_control_mae - frozen_mae, 6)
        clears = bool(margin_over_best >= SURVIVAL_MARGIN_DEX)
        beats_all_shuffle = bool(frozen_mae < shuffled["best_mae_dex"])
        train_rel = _rel_errors(train, _frozen_predict_log_l)
        holdout_rel = _rel_errors(holdout, _frozen_predict_log_l)
        return {
            "train_count": len(train),
            "holdout_count": len(holdout),
            "holdout_systems": len({r[SPLIT_KEY] for r in holdout}),
            "frozen_relation_holdout_mae_dex": frozen_mae,
            "controls_holdout_mae_dex": controls,
            "shuffled_control_detail": shuffled,
            "best_control_name": best_control_name,
            "best_control_mae_dex": best_control_mae,
            "frozen_minus_best_control_dex": margin_over_best,
            "survival_margin_dex": SURVIVAL_MARGIN_DEX,
            "clears_survival_margin": clears,
            "beats_all_shuffle_seeds": beats_all_shuffle,
            "frozen_relation_train_mean_relative_error": train_rel[0],
            "frozen_relation_train_max_relative_error": train_rel[1],
            "frozen_relation_holdout_mean_relative_error": holdout_rel[0],
            "frozen_relation_holdout_max_relative_error": holdout_rel[1],
        }

    primary_eval = evaluate(primary_train, primary_holdout)
    allstage_eval = evaluate(allstage_train, allstage_holdout)

    # Luminosity-provenance sensitivity on the primary holdout (scout requirement).
    by_provenance: dict[str, Any] = {}
    for source in ("debcat_catalogue_reported_logL", "stefan_boltzmann_from_debcat_logR_logT"):
        subset = [r for r in primary_holdout if r.get("luminosity_source") == source]
        if subset:
            by_provenance[source] = {
                "holdout_count": len(subset),
                "frozen_relation_holdout_mae_dex": round(_mae(subset, _frozen_predict_log_l), 6),
            }

    # By-stage diagnostic over the full high-mass holdout (stage confound).
    by_stage_holdout_mae: dict[str, float] = {}
    for stage in STAGE_ORDER:
        subset = [r for r in allstage_holdout if r.get("evolutionary_stage_flag", "unknown") == stage]
        if subset:
            by_stage_holdout_mae[stage] = round(_mae(subset, _frozen_predict_log_l), 6)

    # Overall transfer verdict on the PRIMARY (stage-matched) high-mass holdout.
    transfers = bool(primary_eval["clears_survival_margin"] and primary_eval["beats_all_shuffle_seeds"])
    verdict = "TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS" if transfers else "REGIME_LIMITED_DOES_NOT_TRANSFER"

    return {
        "frozen_predictor": {
            "source_result_id": RESULT_0022_ID,
            "source_model_id": "model_train_fitted_alpha",
            "formula": "log L = alpha * log M (fixed intercept log L0 = 0)",
            "alpha_frozen": ALPHA_FROZEN,
            "alpha_rederived_from_committed_main_sequence_train": round(rederived_alpha, 6),
            "fixed_intercept_log_l0": FROZEN_INTERCEPT_LOG_L0,
            "refit_on_holdout": False,
        },
        "predeclared_contract": {
            "high_mass_threshold_solar": HIGH_MASS_THRESHOLD_SOLAR,
            "split_key": SPLIT_KEY,
            "target_field": TARGET_FIELD,
            "primary_lane_stage": PRIMARY_STAGE,
            "survival_margin_dex": SURVIVAL_MARGIN_DEX,
            "survival_margin_basis": "RESULT-0022 across-seed split-noise reference (0.04 dex)",
            "control_seeds": list(CONTROL_SEEDS),
            "controls": ["null_massband_median", "mass_matched_massband_mean", "shuffled_target_best"],
            "judge": "experimental DEBCat dynamical masses (direct_observation)",
            "frozen_before_holdout_read": True,
        },
        "regime_composition": {
            "high_mass_all_stage": _regime_composition(high_mass),
            "high_mass_primary_main_sequence": _regime_composition(primary),
        },
        "primary_high_mass_main_sequence_holdout": primary_eval,
        "secondary_all_stage_high_mass_holdout": allstage_eval,
        "luminosity_provenance_sensitivity_primary_holdout": by_provenance,
        "by_stage_high_mass_holdout_mae_dex": by_stage_holdout_mae,
        "transfers_to_high_mass": transfers,
        "verdict": verdict,
    }


__all__ = [
    "ALPHA_FROZEN",
    "SURVIVAL_MARGIN_DEX",
    "HIGH_MASS_THRESHOLD_SOLAR",
    "compute_transfer_metrics",
]
