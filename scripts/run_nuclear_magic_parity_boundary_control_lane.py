"""TASK-0475 nuclear magic-parity boundary control lane.

Tests whether a single residual-free magic-parity boundary feature
`r_corr = beta * pairing_sign(Z,N) * max(exp(-z_dist^2/8), exp(-n_dist^2/8))`
fit on the NMD-0002 training slice survives five controls plus a
leave-one-out coefficient-stability check on the post-AME2020 primary
holdout.

The runner uses a custom verdict vocabulary capped at
BOUNDED_DIAGNOSTIC (no registry expansion is authorized
regardless of outcome). Maps to agent_run.yaml schema verdicts at write
time.

Sandbox-only. Does NOT fetch live data, score the prediction registry,
write canonical RESULT-* artifacts, modify claims, or edit knowledge.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0047"
TASK_ID = "TASK-0475"
HYP_PROPOSAL_PATH = (
    "hypothesis_proposals/nuclear-mass/"
    "HYP-PROPOSAL-0057-magic-parity-boundary.yaml"
)
EXP_PROPOSAL_PATH = (
    "experiment_proposals/nuclear-mass/"
    "EXP-PROPOSAL-0023-nuclear-magic-parity-boundary.yaml"
)
NMD_PATH = REPO_ROOT / "data" / "nuclear_masses" / "nmd-0002-curated-measured-slice.yaml"
POST_AME_PATH = REPO_ROOT / "data" / "nuclear_masses" / "post_ame2020_holdout.yaml"
RESULT_PATH = REPO_ROOT / "results" / "EXP-0012" / "RUN-0001" / "result.yaml"

RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = RUN_DIR / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = RUN_DIR / "limitations.md"
DEFAULT_PREFLIGHT_PATH = RUN_DIR / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = RUN_DIR / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-magic-parity-boundary-control-lane.md"
)

GAUSSIAN_TWO_SIGMA_SQUARED = 8.0
SHUFFLED_LABEL_SEED = 475
SURVIVAL_MARGIN_MEV = 0.25
LOO_SIGN_FLIP_THRESHOLD = 2

# Custom verdict vocabulary per TASK-0475 specification
CUSTOM_VERDICTS = (
    "BOUNDED_DIAGNOSTIC",
    "CONTROL_DOMINATED",
    "FRAGILE_INCONCLUSIVE",
    "NEGATIVE_RESULT",
)

# Map custom verdicts to agent_run.yaml schema vocabulary
CUSTOM_TO_SCHEMA_VERDICT = {
    "BOUNDED_DIAGNOSTIC": "REVIEW_NEEDED",
    "CONTROL_DOMINATED": "REVIEW_NEEDED",
    "FRAGILE_INCONCLUSIVE": "INCONCLUSIVE",
    "NEGATIVE_RESULT": "FALSIFIED",
}


# --------------------------------------------------------------------------- #
# Residual-free magic-parity boundary feature
# --------------------------------------------------------------------------- #


def magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _magic_proximity(value: int) -> float:
    dist = magic_distance(value)
    return math.exp(-(dist**2) / GAUSSIAN_TWO_SIGMA_SQUARED)


def magic_boundary_score(z: int, n: int) -> float:
    """Near-either-axis magic boundary score. Closed-form and residual-free."""
    return max(_magic_proximity(z), _magic_proximity(n))


def pairing_sign(z: int, n: int) -> float:
    if z % 2 == 0 and n % 2 == 0:
        return 1.0
    if z % 2 == 1 and n % 2 == 1:
        return -1.0
    return 0.0


def interaction_feature(z: int, n: int) -> float:
    """`pairing_sign(Z,N) * magic_boundary_score(Z,N)`. Residual-free."""
    return pairing_sign(z, n) * magic_boundary_score(z, n)


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #


def load_frozen_baseline_coefficients() -> SemiEmpiricalCoefficients:
    payload = yaml.safe_load(RESULT_PATH.read_text(encoding="utf-8"))
    for score in payload["scores"]:
        if score["model_id"] == "model_fitted_semi_empirical":
            c = score["coefficients"]
            return SemiEmpiricalCoefficients(
                volume=float(c["volume"]),
                surface=float(c["surface"]),
                coulomb=float(c["coulomb"]),
                asymmetry=float(c["asymmetry"]),
                pairing=float(c["pairing"]),
            )
    raise RuntimeError("RESULT-0015 fitted semi-empirical coefficients not found")


def load_training_rows(c: SemiEmpiricalCoefficients) -> list[dict[str, Any]]:
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=c,
    )
    entries_by_id = {entry.nuclide_id: entry for entry in nmd.entries}
    rows: list[dict[str, Any]] = []
    for baseline_row in baseline_rows:
        entry = entries_by_id[baseline_row.nuclide_id]
        rows.append(
            {
                "row_id": f"nmd-0002::{entry.nuclide_id}",
                "nuclide_id": entry.nuclide_id,
                "Z": int(entry.Z),
                "N": int(entry.N),
                "A": int(entry.A),
                "observed_mev": float(entry.binding_energy_mev),
                "baseline_predicted_mev": float(
                    baseline_row.predicted_binding_energy_mev
                ),
                "baseline_residual_mev": float(baseline_row.residual_mev),
                "source_surface": "training_lstsq",
                "was_extrapolated": False,
            }
        )
    return rows


def load_holdout_rows(c: SemiEmpiricalCoefficients) -> list[dict[str, Any]]:
    payload = yaml.safe_load(POST_AME_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for entry in payload["entries"]:
        if not bool(entry["included_in_time_split_holdout"]):
            continue
        z = int(entry["Z"])
        n = int(entry["N"])
        a = int(entry["A"])
        observed = float(entry["new_measurement"]["value_mev"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=c)
        rows.append(
            {
                "row_id": str(entry["row_id"]),
                "nuclide_id": str(entry["nuclide_id"]),
                "Z": z,
                "N": n,
                "A": a,
                "observed_mev": observed,
                "baseline_predicted_mev": predicted,
                "baseline_residual_mev": observed - predicted,
                "source_surface": "primary_holdout",
                "was_extrapolated": bool(entry.get("was_extrapolated", False)),
            }
        )
    return rows


# --------------------------------------------------------------------------- #
# Fit helpers
# --------------------------------------------------------------------------- #


def _fit_scalar(feature_values: np.ndarray, residuals: np.ndarray) -> float:
    denominator = float(np.dot(feature_values, feature_values))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(feature_values, residuals) / denominator)


def fit_beta(training_rows: list[dict[str, Any]]) -> float:
    x = np.asarray(
        [interaction_feature(int(r["Z"]), int(r["N"])) for r in training_rows],
        dtype=float,
    )
    y = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    return _fit_scalar(x, y)


def candidate_correction(rows: list[dict[str, Any]], beta: float) -> list[float]:
    return [beta * interaction_feature(int(r["Z"]), int(r["N"])) for r in rows]


# --------------------------------------------------------------------------- #
# Controls
# --------------------------------------------------------------------------- #


def smooth_a_control(
    training_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[float]:
    train_a = np.asarray([float(r["A"]) for r in training_rows], dtype=float)
    train_r = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    design = np.column_stack([np.ones_like(train_a), train_a])
    if train_a.size < 2:
        return [0.0] * len(rows)
    beta, *_ = np.linalg.lstsq(design, train_r, rcond=None)
    return [float(beta[0] + beta[1] * float(r["A"])) for r in rows]


def asymmetry_only_control(
    training_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[float]:
    def asym(row: dict[str, Any]) -> float:
        a = int(row["A"])
        return (int(row["N"]) - int(row["Z"])) / a if a > 0 else 0.0

    train_x = np.asarray([asym(r) for r in training_rows], dtype=float)
    train_y = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    beta = _fit_scalar(train_x, train_y)
    return [beta * asym(r) for r in rows]


def _parity_class(z: int, n: int) -> str:
    return f"{'e' if z % 2 == 0 else 'o'}{'e' if n % 2 == 0 else 'o'}"


def parity_only_control(
    training_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[float]:
    per_class: dict[str, list[float]] = {}
    for row in training_rows:
        cls = _parity_class(int(row["Z"]), int(row["N"]))
        per_class.setdefault(cls, []).append(float(row["baseline_residual_mev"]))
    class_means = {cls: float(np.mean(values)) for cls, values in per_class.items()}
    return [
        class_means.get(_parity_class(int(r["Z"]), int(r["N"])), 0.0) for r in rows
    ]


def magic_distance_only_control(
    training_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
 ) -> list[float]:
    train_x = np.asarray(
        [magic_boundary_score(int(r["Z"]), int(r["N"])) for r in training_rows],
        dtype=float,
    )
    train_y = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    beta = _fit_scalar(train_x, train_y)
    return [beta * magic_boundary_score(int(r["Z"]), int(r["N"])) for r in rows]


def shuffled_label_control(
    training_rows: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    seed: int = SHUFFLED_LABEL_SEED,
) -> list[float]:
    """Shuffle candidate labels across training rows, fit beta, apply."""
    feature_values = np.asarray(
        [interaction_feature(int(r["Z"]), int(r["N"])) for r in training_rows],
        dtype=float,
    )
    if feature_values.size == 0:
        return [0.0] * len(rows)
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(feature_values.size)
    shuffled_train = feature_values[permutation]
    train_y = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    beta = _fit_scalar(shuffled_train, train_y)
    return [beta * interaction_feature(int(r["Z"]), int(r["N"])) for r in rows]


# --------------------------------------------------------------------------- #
# Coefficient stability (leave-one-out)
# --------------------------------------------------------------------------- #


def loo_beta_distribution(training_rows: list[dict[str, Any]]) -> list[float]:
    n = len(training_rows)
    betas: list[float] = []
    if n < 2:
        return betas
    for hold in range(n):
        rows_minus = [r for index, r in enumerate(training_rows) if index != hold]
        betas.append(fit_beta(rows_minus))
    return betas


def loo_stability_summary(loo_betas: list[float]) -> dict[str, Any]:
    if not loo_betas:
        return {
            "count": 0,
            "mean_mev": None,
            "std_mev": None,
            "sign_flip_count": 0,
        }
    arr = np.asarray(loo_betas, dtype=float)
    mean = float(np.mean(arr))
    sign_flips = int(np.sum(np.sign(arr) != np.sign(mean))) if mean != 0.0 else 0
    return {
        "count": len(loo_betas),
        "mean_mev": mean,
        "std_mev": float(np.std(arr)),
        "sign_flip_count": sign_flips,
    }


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #


def _errors(rows: list[dict[str, Any]], corrections: list[float]) -> list[float]:
    return [
        float(row["observed_mev"])
        - (float(row["baseline_predicted_mev"]) + correction)
        for row, correction in zip(rows, corrections)
    ]


def _summarize(rows: list[dict[str, Any]], corrections: list[float]) -> dict[str, Any]:
    errors = _errors(rows, corrections)
    if not errors:
        return {"count": 0, "mae_mev": None, "rmse_mev": None}
    abs_errors = np.abs(np.asarray(errors, dtype=float))
    return {
        "count": len(errors),
        "mae_mev": float(np.mean(abs_errors)),
        "rmse_mev": float(np.sqrt(np.mean(np.square(abs_errors)))),
    }


def _subset_labels(row: dict[str, Any]) -> list[str]:
    z, n, a = int(row["Z"]), int(row["N"]), int(row["A"])
    out: list[str] = []
    if z in MAGIC_NUMBERS:
        out.append("magic_z")
    if n in MAGIC_NUMBERS:
        out.append("magic_n")
    if z in MAGIC_NUMBERS and n in MAGIC_NUMBERS:
        out.append("double_magic")
    if a < 50:
        out.append("light_a_lt_50")
    if a > 0 and (n - z) / a >= 0.18:
        out.append("neutron_rich")
    return out


def _per_subset(
    rows: list[dict[str, Any]], corrections: list[float]
) -> dict[str, dict[str, Any]]:
    by_subset: dict[str, list[tuple[dict[str, Any], float]]] = {}
    for row, correction in zip(rows, corrections):
        for subset in _subset_labels(row):
            by_subset.setdefault(subset, []).append((row, correction))
    out: dict[str, dict[str, Any]] = {}
    for subset in sorted(by_subset):
        items = by_subset[subset]
        s_rows = [r for r, _ in items]
        s_corr = [c for _, c in items]
        zero = [0.0] * len(s_corr)
        cand = _summarize(s_rows, s_corr)
        base = _summarize(s_rows, zero)
        delta = (
            None
            if (cand["mae_mev"] is None or base["mae_mev"] is None)
            else float(base["mae_mev"] - cand["mae_mev"])
        )
        out[subset] = {
            "count": cand["count"],
            "baseline_mae_mev": base["mae_mev"],
            "candidate_mae_mev": cand["mae_mev"],
            "delta_mae_mev": delta,
        }
    return out


# --------------------------------------------------------------------------- #
# Custom verdict
# --------------------------------------------------------------------------- #


def decide_verdict(metrics: dict[str, Any]) -> tuple[str, list[str]]:
    rationale: list[str] = []
    candidate = metrics["candidate"]
    baseline = metrics["baseline"]
    controls = {
        "smooth_a": metrics["control_smooth_a"],
        "asymmetry_only": metrics["control_asymmetry_only"],
        "parity_only": metrics["control_parity_only"],
        "magic_distance_only": metrics["control_magic_distance_only"],
        "shuffled_label": metrics["control_shuffled_label"],
    }
    loo = metrics["coefficient_loo_stability"]

    fk_base = baseline["full_known"]["mae_mev"]
    fk_cand = candidate["full_known"]["mae_mev"]
    if fk_base is None or fk_cand is None:
        rationale.append("Full-known MAE undefined.")
        return "FRAGILE_INCONCLUSIVE", rationale

    candidate_improvement = fk_base - fk_cand
    rationale.append(
        f"full_known candidate vs baseline: {candidate_improvement:+.4f} MeV"
    )

    if candidate_improvement < SURVIVAL_MARGIN_MEV:
        rationale.append(
            f"Candidate fails the {SURVIVAL_MARGIN_MEV} MeV survival margin "
            "on full_known vs baseline."
        )
        return "NEGATIVE_RESULT", rationale

    for control_name, control_block in controls.items():
        ctrl_mae = control_block["full_known"]["mae_mev"]
        if ctrl_mae is None:
            rationale.append(f"Control `{control_name}` MAE undefined.")
            return "FRAGILE_INCONCLUSIVE", rationale
        margin = ctrl_mae - fk_cand
        rationale.append(
            f"full_known candidate vs {control_name}: {margin:+.4f} MeV"
        )
        if margin < SURVIVAL_MARGIN_MEV:
            rationale.append(
                f"Control `{control_name}` matches candidate within margin."
            )
            return "CONTROL_DOMINATED", rationale

    flips = loo.get("sign_flip_count", 0)
    if flips >= LOO_SIGN_FLIP_THRESHOLD:
        rationale.append(
            f"Coefficient sign flips {flips} times under LOO refit "
            f"(>= {LOO_SIGN_FLIP_THRESHOLD}); fit is fragile."
        )
        return "FRAGILE_INCONCLUSIVE", rationale

    rationale.append(
        "Candidate beats baseline and all five controls by the survival margin "
        "and shows stable coefficient sign under LOO. Capped at "
        "BOUNDED_DIAGNOSTIC per the custom verdict vocabulary; no "
        "registry expansion is authorized."
    )
    return "BOUNDED_DIAGNOSTIC", rationale


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def build_metrics() -> dict[str, Any]:
    coefficients = load_frozen_baseline_coefficients()
    training_rows = load_training_rows(coefficients)
    holdout_rows = load_holdout_rows(coefficients)
    full_known_rows = training_rows + holdout_rows

    beta = fit_beta(training_rows)
    candidate_full = candidate_correction(full_known_rows, beta)
    smooth_full = smooth_a_control(training_rows, full_known_rows)
    asym_full = asymmetry_only_control(training_rows, full_known_rows)
    parity_full = parity_only_control(training_rows, full_known_rows)
    magic_full = magic_distance_only_control(training_rows, full_known_rows)
    shuffled_full = shuffled_label_control(training_rows, full_known_rows)
    zero_full = [0.0] * len(full_known_rows)

    def split(corr: list[float]) -> dict[str, Any]:
        return {
            "training_lstsq": _summarize(training_rows, corr[: len(training_rows)]),
            "primary_holdout": _summarize(
                holdout_rows, corr[len(training_rows):]
            ),
            "full_known": _summarize(full_known_rows, corr),
        }

    loo_betas = loo_beta_distribution(training_rows)
    loo_summary = loo_stability_summary(loo_betas)

    training_overview = [
        {
            "row_id": r["row_id"],
            "Z": int(r["Z"]),
            "N": int(r["N"]),
            "A": int(r["A"]),
            "z_dist": magic_distance(int(r["Z"])),
            "n_dist": magic_distance(int(r["N"])),
            "pairing_sign": pairing_sign(int(r["Z"]), int(r["N"])),
            "magic_boundary_score": round(
                magic_boundary_score(int(r["Z"]), int(r["N"])), 6
            ),
            "interaction_feature": round(
                interaction_feature(int(r["Z"]), int(r["N"])), 6
            ),
            "baseline_residual_mev": round(float(r["baseline_residual_mev"]), 6),
        }
        for r in training_rows
    ]

    metrics: dict[str, Any] = {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "data_boundary": {
            "live_fetch": False,
            "training_dataset": str(NMD_PATH.relative_to(REPO_ROOT)),
            "holdout_dataset": str(POST_AME_PATH.relative_to(REPO_ROOT)),
            "frozen_baseline_result": str(RESULT_PATH.relative_to(REPO_ROOT)),
        },
        "feature_definition": {
            "name": "magic_parity_boundary",
            "formula": "pairing_sign(Z,N) * max(exp(-z_dist^2/8), exp(-n_dist^2/8))",
            "inputs": ["Z", "N"],
            "forbidden_inputs": [
                "baseline_residual_mev",
                "candidate_fit_residual",
                "baseline_error_rank",
                "source_status",
                "future_comparison_row",
            ],
        },
        "candidate_coefficient_beta_mev": round(beta, 6),
        "coefficient_loo_stability": loo_summary,
        "coefficient_loo_betas_mev": [round(b, 6) for b in loo_betas],
        "training_rows_overview": training_overview,
        "baseline": split(zero_full),
        "candidate": split(candidate_full),
        "control_smooth_a": split(smooth_full),
        "control_asymmetry_only": split(asym_full),
        "control_parity_only": split(parity_full),
        "control_magic_distance_only": split(magic_full),
        "control_shuffled_label": split(shuffled_full),
        "per_subset_candidate_full_known": _per_subset(full_known_rows, candidate_full),
        "survival_margin_mev": SURVIVAL_MARGIN_MEV,
        "loo_sign_flip_threshold": LOO_SIGN_FLIP_THRESHOLD,
        "custom_verdict_vocabulary": list(CUSTOM_VERDICTS),
    }

    metrics["candidate_vs_baseline_full_known_delta_mev"] = _delta(
        metrics["baseline"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_smooth_a_full_known_delta_mev"] = _delta(
        metrics["control_smooth_a"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_asymmetry_only_full_known_delta_mev"] = _delta(
        metrics["control_asymmetry_only"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_parity_only_full_known_delta_mev"] = _delta(
        metrics["control_parity_only"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_magic_distance_only_full_known_delta_mev"] = _delta(
        metrics["control_magic_distance_only"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_shuffled_label_full_known_delta_mev"] = _delta(
        metrics["control_shuffled_label"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )

    holdout_base = metrics["baseline"]["primary_holdout"]["mae_mev"]
    holdout_cand = metrics["candidate"]["primary_holdout"]["mae_mev"]
    metrics["primary_holdout_regression_flag"] = bool(
        holdout_base is not None
        and holdout_cand is not None
        and holdout_cand > holdout_base
    )

    verdict, rationale = decide_verdict(metrics)
    metrics["verdict"] = verdict
    metrics["verdict_rationale"] = rationale
    metrics["schema_verdict"] = CUSTOM_TO_SCHEMA_VERDICT[verdict]
    return metrics


def _delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return float(a - b)


# --------------------------------------------------------------------------- #
# Report + agent_run rendering
# --------------------------------------------------------------------------- #


def _fmt(value: float | None, decimals: int = 4) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{decimals}f}"


def render_report(metrics: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Nuclear Magic-Distance Z×N Interaction Control Lane")
    lines.append("")
    lines.append(f"**Task:** `{TASK_ID}`")
    lines.append(f"**Agent run:** `{AGENT_RUN_ID}`")
    lines.append("**Campaign:** `nuclear-mass-surface`")
    lines.append(
        f"**Verdict:** `{metrics['verdict']}` "
        f"(maps to agent_run schema `{metrics['schema_verdict']}`)"
    )
    lines.append("**Sandbox only:** true")
    lines.append("")
    lines.append("## Candidate")
    lines.append("")
    lines.append(
        "- Feature: `interaction = pairing_sign(Z,N) * max(exp(-z_dist^2/8), "
        "exp(-n_dist^2/8))` (closed-form, residual-free)."
    )
    lines.append(
        f"- Fit: `r_corr = beta * interaction` via least squares on the 11-row "
        f"NMD-0002 training slice. `beta = "
        f"{metrics['candidate_coefficient_beta_mev']:+.4f} MeV`."
    )
    lines.append("")
    lines.append("## Aggregate MAE (MeV)")
    lines.append("")
    lines.append(
        "| Surface | baseline | candidate | smooth_a | asymmetry_only | parity_only | magic_distance_only | shuffled_label |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        b = metrics["baseline"][surface]["mae_mev"]
        c = metrics["candidate"][surface]["mae_mev"]
        sa = metrics["control_smooth_a"][surface]["mae_mev"]
        ao = metrics["control_asymmetry_only"][surface]["mae_mev"]
        po = metrics["control_parity_only"][surface]["mae_mev"]
        md = metrics["control_magic_distance_only"][surface]["mae_mev"]
        sl = metrics["control_shuffled_label"][surface]["mae_mev"]
        lines.append(
            f"| `{surface}` | {_fmt(b)} | {_fmt(c)} | {_fmt(sa)} | {_fmt(ao)} "
            f"| {_fmt(po)} | {_fmt(md)} | {_fmt(sl)} |"
        )
    lines.append("")
    lines.append("## Coefficient Stability (leave-one-out)")
    lines.append("")
    loo = metrics["coefficient_loo_stability"]
    lines.append(f"- LOO folds: {loo['count']}")
    lines.append(f"- mean beta: {_fmt(loo['mean_mev'])} MeV")
    lines.append(f"- std beta: {_fmt(loo['std_mev'])} MeV")
    lines.append(
        f"- sign-flip count vs mean: {loo['sign_flip_count']} "
        f"(threshold {LOO_SIGN_FLIP_THRESHOLD})"
    )
    lines.append("")
    lines.append("## Verdict Rationale")
    lines.append("")
    for note in metrics["verdict_rationale"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Per-Subset Behavior (full_known)")
    lines.append("")
    lines.append("| Subset | count | baseline MAE | candidate MAE | delta |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for subset, entry in metrics["per_subset_candidate_full_known"].items():
        lines.append(
            f"| `{subset}` | {entry['count']} | {_fmt(entry['baseline_mae_mev'])} "
            f"| {_fmt(entry['candidate_mae_mev'])} | {_fmt(entry['delta_mae_mev'])} |"
        )
    lines.append("")
    lines.append("## Leakage Audit")
    lines.append("")
    lines.append(
        "- Feature uses only `Z`, `N` (via parity and magic-distance from the "
        "published magic-number list). No `A`, baseline residual, error rank, "
        "candidate-fit residual, source-status, or future comparison row "
        "enters feature construction. ✅"
    )
    lines.append(
        "- `beta` is fit by closed-form least squares on training only; no "
        "candidate-fit residual feeds controls. ✅"
    )
    lines.append(
        "- All five controls (smooth_a, asymmetry_only, parity_only, "
        "magic_distance_only, shuffled_label) share the same fit and "
        "evaluation surfaces. ✅"
    )
    lines.append(
        "- Coefficient stability LOO uses only training-row exclusion; no "
        "candidate-fit residual feeds the stability check. ✅"
    )
    lines.append("")
    lines.append("## Custom Verdict Vocabulary")
    lines.append("")
    lines.append(
        "Per the TASK-0475 specification, this lane uses a custom verdict set "
        "capped at `BOUNDED_DIAGNOSTIC`. No registry expansion is "
        "authorized regardless of outcome; the shell-axis post-audit decision "
        "(TASK-0333) remains in force."
    )
    lines.append("")
    lines.append("| Custom verdict | Meaning | Maps to schema |")
    lines.append("| --- | --- | --- |")
    for cv in CUSTOM_VERDICTS:
        meaning = {
            "BOUNDED_DIAGNOSTIC": "candidate beat baseline + all five controls and is sign-stable, but the lane caps here (no registry expansion)",
            "CONTROL_DOMINATED": "at least one control matches the candidate within the margin",
            "FRAGILE_INCONCLUSIVE": "coefficient sign flips under LOO or a control MAE is undefined",
            "NEGATIVE_RESULT": "candidate fails the 0.25 MeV survival margin against baseline",
        }[cv]
        lines.append(f"| `{cv}` | {meaning} | `{CUSTOM_TO_SCHEMA_VERDICT[cv]}` |")
    lines.append("")
    lines.append("## Promotion Boundary")
    lines.append("")
    lines.append("- `sandbox_only: true`")
    lines.append("- `writes_canonical_result: false`")
    lines.append("- `claim_promotion_allowed: false`")
    lines.append("- `prediction_registry_allowed: false`")
    lines.append(
        "- Required next step: maintainer review before any follow-up. No "
        "`PRED-XXXX`, `RESULT-XXXX`, `CLAIM-XXXX`, or `KNOW-XXXX` artifact is "
        "created by this run."
    )
    lines.append("")
    return "\n".join(lines) + "\n"


def render_agent_run(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "codex"},
        "proposal_paths": {
            "hypothesis": HYP_PROPOSAL_PATH,
            "experiment": EXP_PROPOSAL_PATH,
        },
        "artifacts": {
            "metrics": f"agent_runs/{AGENT_RUN_ID}/metrics.json",
            "report": f"agent_runs/{AGENT_RUN_ID}/report.md",
            "limitations": f"agent_runs/{AGENT_RUN_ID}/limitations.md",
            "preflight": f"agent_runs/{AGENT_RUN_ID}/preflight.md",
            "review_summary": f"agent_runs/{AGENT_RUN_ID}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "controls_first_gauntlet_compliance",
                    "status": "PASS",
                    "notes": (
                        "Lane follows docs/notes/nuclear-controls-first-"
                        "hypothesis-gauntlet.md: one bounded family, residual-free "
                        "feature, five declared controls + coefficient LOO stability, "
                        "declared failure condition, declared output routing, "
                        "declared wording boundary."
                    ),
                },
                {
                    "name": "no_leakage_contract",
                    "status": "PASS",
                    "notes": (
                        "Interaction feature is a closed-form product of parity sign "
                        "and magic-boundary score; uses only Z and N. No residual or future "
                        "comparison row contributes."
                    ),
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": (
                        "Only committed NMD-0002 and post-AME2020 holdout rows and "
                        "frozen RESULT-0015 baseline; no live fetch."
                    ),
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": (
                        "smooth_a, asymmetry_only, parity_only, magic_distance_only, "
                        "shuffled_label controls all run end-to-end."
                    ),
                },
                {
                    "name": "coefficient_stability",
                    "status": "PASS",
                    "notes": (
                        "Leave-one-out coefficient refit reported alongside aggregate "
                        "metrics; sign-flip count compared against threshold."
                    ),
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": (
                        "No prediction registry, canonical result, claim, or "
                        "knowledge file is written. Verdict capped at "
                        "BOUNDED_DIAGNOSTIC by custom vocabulary."
                    ),
                },
            ],
        },
        "limitations": [
            "NMD-0002 has 11 training rows; LOO coefficient stability has only 11 refit folds.",
            "Frozen baseline residuals are retrospective; this is not a blind prediction.",
            "Gaussian width (two-sigma^2 = 8) is declared before the run and not retuned.",
            "Custom verdict vocabulary caps at BOUNDED_DIAGNOSTIC; no registry expansion is authorized regardless of outcome.",
            "Shell-axis post-audit decision (TASK-0333) remains in force; this lane does not reopen registry expansion.",
        ],
        "verdict": metrics["schema_verdict"],
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any follow-up. No PRED, RESULT, "
                "claim, knowledge, or reveal-scoring task is authorized by "
                "this agent run."
            ),
        },
    }


def render_limitations(metrics: dict[str, Any]) -> str:
    return (
        f"# {AGENT_RUN_ID} Limitations\n\n"
        "- NMD-0002 has 11 training rows; LOO coefficient stability has only 11 refit folds.\n"
        "- Frozen baseline residuals are retrospective; this is not a blind prediction.\n"
        "- Gaussian width (two-sigma^2 = 8) is declared before the run and not retuned.\n"
        "- Custom verdict vocabulary caps at BOUNDED_DIAGNOSTIC; no registry expansion is authorized regardless of outcome.\n"
        "- Shell-axis post-audit decision (TASK-0333) remains in force; this lane does not reopen registry expansion.\n"
        f"- Verdict: `{metrics['verdict']}` (schema: `{metrics['schema_verdict']}`). See `report.md` rationale.\n"
    )


def render_preflight(metrics: dict[str, Any]) -> str:
    return (
        f"# {AGENT_RUN_ID} Preflight\n\n"
        "Compliance with the controls-first gauntlet "
        "(`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):\n\n"
        "- Hypothesis family: F3 (shell-axis) under residual-free interaction "
        "form per `docs/nuclear-residual-feature-no-leakage-contract.md`.\n"
        "- Allowed inputs: Z, N, magic-distance (from published magic-number list).\n"
        "- Forbidden inputs (none used): target residual, baseline error rank, "
        "candidate-fit residual, source-status, future comparison rows.\n"
        "- Baseline: RESULT-0015 frozen semi-empirical coefficients.\n"
        "- Five controls run end-to-end: smooth_a + asymmetry_only + parity_only + "
        "magic_distance_only + shuffled_label.\n"
        "- Coefficient stability LOO reported.\n"
        "- Failure condition declared before scoring: candidate must beat baseline by "
        "≥ 0.25 MeV on full_known AND beat all five controls by the same margin AND "
        "have ≤ 1 LOO sign flip; otherwise verdict drops to CONTROL_DOMINATED, "
        "FRAGILE_INCONCLUSIVE, or NEGATIVE_RESULT.\n"
        "- Output routing: this agent_runs/ bundle + "
        "docs/reviews/nuclear-magic-parity-boundary-control-lane.md.\n"
        "- Custom verdict vocabulary caps at BOUNDED_DIAGNOSTIC; no "
        "registry expansion or shell-axis PRED entry reuse is authorized.\n"
        "- Wording boundary: forbidden terms include discovery, new nuclear law, "
        "broad formula, shell-axis breakthrough.\n"
    )


def render_review_summary(metrics: dict[str, Any]) -> str:
    return (
        f"# {AGENT_RUN_ID} Review Summary\n\n"
        f"- Verdict: `{metrics['verdict']}` (schema: `{metrics['schema_verdict']}`).\n"
        f"- Beta: {metrics['candidate_coefficient_beta_mev']:+.4f} MeV.\n"
        f"- LOO std: {_fmt(metrics['coefficient_loo_stability']['std_mev'])} MeV; "
        f"sign-flip count: {metrics['coefficient_loo_stability']['sign_flip_count']}.\n"
        f"- Full-known candidate vs baseline: "
        f"{_fmt(metrics['candidate_vs_baseline_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs smooth_a: "
        f"{_fmt(metrics['candidate_vs_smooth_a_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs asymmetry_only: "
        f"{_fmt(metrics['candidate_vs_asymmetry_only_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs parity_only: "
        f"{_fmt(metrics['candidate_vs_parity_only_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs magic_distance_only: "
        f"{_fmt(metrics['candidate_vs_magic_distance_only_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs shuffled_label: "
        f"{_fmt(metrics['candidate_vs_shuffled_label_full_known_delta_mev'])} MeV.\n"
        f"- Primary-holdout regression flag: "
        f"{metrics['primary_holdout_regression_flag']}.\n"
        f"- Sandbox only; no PRED/CLAIM/KNOW/RESULT artifact written.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"Write agent_run bundle under agent_runs/{AGENT_RUN_ID}/.",
    )
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)
    metrics = build_metrics()
    report = render_report(metrics)
    if args.write:
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        DEFAULT_METRICS_PATH.write_text(
            json.dumps(metrics, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
        DEFAULT_REPORT_PATH.write_text(report, encoding="utf-8")
        DEFAULT_AGENT_RUN_PATH.write_text(
            yaml.safe_dump(render_agent_run(metrics), sort_keys=False),
            encoding="utf-8",
        )
        DEFAULT_LIMITATIONS_PATH.write_text(
            render_limitations(metrics), encoding="utf-8"
        )
        DEFAULT_PREFLIGHT_PATH.write_text(
            render_preflight(metrics), encoding="utf-8"
        )
        DEFAULT_REVIEW_SUMMARY_PATH.write_text(
            render_review_summary(metrics), encoding="utf-8"
        )
        args.review.parent.mkdir(parents=True, exist_ok=True)
        args.review.write_text(report, encoding="utf-8")
        print(f"Wrote agent_run bundle to {RUN_DIR}", file=sys.stderr)
    else:
        json.dump(metrics, sys.stdout, indent=2, sort_keys=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
