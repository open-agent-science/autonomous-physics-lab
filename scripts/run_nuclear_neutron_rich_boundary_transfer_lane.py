"""TASK-0450 nuclear neutron-rich boundary transfer hypothesis lane.

Tests whether a single residual-free neutron-rich boundary-distance correction
`r_corr = beta * max(0, (N - Z)/A - 0.18)` survives the controls-first gauntlet
on NMD-0002 and the post-AME2020 primary holdout, with explicit matched
high-error non-neutron-rich + sign-inverted controls plus an isotope-chain
transfer test.

The runner is sandbox-only. It does NOT fetch live data, score the prediction
registry, write canonical RESULT-* artifacts, modify claims, or edit knowledge.

Follows docs/notes/nuclear-controls-first-hypothesis-gauntlet.md and
docs/nuclear-residual-feature-no-leakage-contract.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nuclear_mass_baselines import (  # noqa: E402
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0044"
TASK_ID = "TASK-0450"
HYP_PROPOSAL_PATH = (
    "hypothesis_proposals/nuclear-mass/"
    "HYP-PROPOSAL-0052-neutron-rich-boundary-transfer.yaml"
)
EXP_PROPOSAL_PATH = (
    "experiment_proposals/nuclear-mass/"
    "EXP-PROPOSAL-0018-nuclear-neutron-rich-boundary-transfer.yaml"
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

NEUTRON_RICH_ASYMMETRY_THRESHOLD = 0.18
MATCHED_HIGH_ERROR_SEED = 450
SURVIVAL_MARGIN_MEV = 0.25
CHAIN_MIN_ROWS = 2


# --------------------------------------------------------------------------- #
# Residual-free boundary feature
# --------------------------------------------------------------------------- #


def boundary_distance(z: int, n: int, a: int) -> float:
    """Return max(0, (N - Z)/A - 0.18). Closed-form, residual-free."""
    if a <= 0:
        raise ValueError(f"invalid mass number: A={a}")
    asymmetry = (n - z) / a
    return max(0.0, asymmetry - NEUTRON_RICH_ASYMMETRY_THRESHOLD)


def is_neutron_rich(z: int, n: int, a: int) -> bool:
    return boundary_distance(z, n, a) > 0.0


# --------------------------------------------------------------------------- #
# Data loading (mirrors TASK-0449 runner pattern)
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
# Candidate and controls
# --------------------------------------------------------------------------- #


def fit_beta(training_rows: list[dict[str, Any]]) -> float:
    """Least-squares fit of `r ≈ beta * boundary_distance(Z,N,A)` on training."""
    x = np.asarray(
        [boundary_distance(int(r["Z"]), int(r["N"]), int(r["A"])) for r in training_rows],
        dtype=float,
    )
    y = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    denominator = float(np.dot(x, x))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(x, y) / denominator)


def candidate_correction(rows: list[dict[str, Any]], beta: float) -> list[float]:
    return [
        beta * boundary_distance(int(r["Z"]), int(r["N"]), int(r["A"])) for r in rows
    ]


def sign_inverted_correction(rows: list[dict[str, Any]], beta: float) -> list[float]:
    return [-1.0 * value for value in candidate_correction(rows, beta)]


def matched_high_error_control_correction(
    rows: list[dict[str, Any]],
    training_rows: list[dict[str, Any]],
    *,
    seed: int = MATCHED_HIGH_ERROR_SEED,
) -> list[float]:
    """Matched-high-error control.

    For every row, compute a per-row correction equal to `beta_ctrl * indicator`,
    where `indicator` is 1 for rows whose absolute baseline residual rank is
    >= 50th percentile but whose asymmetry is BELOW the neutron-rich threshold
    (i.e. high-error but NOT neutron-rich), and 0 otherwise. `beta_ctrl` is the
    least-squares fit of `r = beta_ctrl * indicator` on the training slice. This
    matches the candidate's "high-error" intensity while breaking the
    neutron-rich axis.
    """
    rng = np.random.default_rng(seed)  # noqa: F841 — kept for future tie-breaks
    train_residuals = np.asarray(
        [abs(float(r["baseline_residual_mev"])) for r in training_rows], dtype=float
    )
    if train_residuals.size == 0:
        return [0.0] * len(rows)
    threshold = float(np.median(train_residuals))

    def _indicator(row: dict[str, Any]) -> float:
        z = int(row["Z"])
        n = int(row["N"])
        a = int(row["A"])
        if is_neutron_rich(z, n, a):
            return 0.0
        if abs(float(row["baseline_residual_mev"])) < threshold:
            return 0.0
        return 1.0

    x_train = np.asarray([_indicator(r) for r in training_rows], dtype=float)
    y_train = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    denominator = float(np.dot(x_train, x_train))
    beta_ctrl = (
        float(np.dot(x_train, y_train) / denominator) if denominator > 0.0 else 0.0
    )
    return [beta_ctrl * _indicator(row) for row in rows]


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


def _per_chain(
    rows: list[dict[str, Any]], corrections: list[float]
) -> dict[str, dict[str, Any]]:
    """Per-isotope-chain (constant Z) candidate/baseline MAE and delta."""
    by_chain: dict[int, list[tuple[dict[str, Any], float]]] = {}
    for row, correction in zip(rows, corrections):
        by_chain.setdefault(int(row["Z"]), []).append((row, correction))
    out: dict[str, dict[str, Any]] = {}
    for z, items in sorted(by_chain.items()):
        if len(items) < CHAIN_MIN_ROWS:
            continue
        chain_rows = [r for r, _ in items]
        chain_corr = [c for _, c in items]
        zero = [0.0] * len(chain_corr)
        cand = _summarize(chain_rows, chain_corr)
        base = _summarize(chain_rows, zero)
        cand_mae = cand["mae_mev"]
        base_mae = base["mae_mev"]
        delta = (
            None
            if (cand_mae is None or base_mae is None)
            else float(base_mae - cand_mae)
        )
        out[f"Z={z}"] = {
            "count": cand["count"],
            "baseline_mae_mev": base_mae,
            "candidate_mae_mev": cand_mae,
            "delta_mae_mev": delta,
        }
    return out


def _per_subset(
    rows: list[dict[str, Any]], corrections: list[float]
) -> dict[str, dict[str, Any]]:
    """Per-subset MAE/delta for declared subsets."""

    def label(row: dict[str, Any]) -> list[str]:
        z = int(row["Z"])
        n = int(row["N"])
        a = int(row["A"])
        out_labels: list[str] = []
        if is_neutron_rich(z, n, a):
            out_labels.append("neutron_rich")
        else:
            out_labels.append("not_neutron_rich")
        if a < 50:
            out_labels.append("light_a_lt_50")
        if row.get("was_extrapolated"):
            out_labels.append("post_ame2020_extrapolated")
        elif row.get("source_surface") == "primary_holdout":
            out_labels.append("post_ame2020_measured")
        return out_labels

    by_subset: dict[str, list[tuple[dict[str, Any], float]]] = {}
    for row, correction in zip(rows, corrections):
        for lab in label(row):
            by_subset.setdefault(lab, []).append((row, correction))
    out: dict[str, dict[str, Any]] = {}
    for subset, items in sorted(by_subset.items()):
        subset_rows = [r for r, _ in items]
        subset_corr = [c for _, c in items]
        zero = [0.0] * len(subset_corr)
        cand = _summarize(subset_rows, subset_corr)
        base = _summarize(subset_rows, zero)
        cand_mae = cand["mae_mev"]
        base_mae = base["mae_mev"]
        delta = (
            None
            if (cand_mae is None or base_mae is None)
            else float(base_mae - cand_mae)
        )
        out[subset] = {
            "count": cand["count"],
            "baseline_mae_mev": base_mae,
            "candidate_mae_mev": cand_mae,
            "delta_mae_mev": delta,
        }
    return out


# --------------------------------------------------------------------------- #
# Verdict (controls-first gauntlet vocabulary)
# --------------------------------------------------------------------------- #


def decide_verdict(metrics: dict[str, Any]) -> tuple[str, list[str]]:
    rationale: list[str] = []
    candidate = metrics["candidate"]
    matched = metrics["control_matched_high_error"]
    inverted = metrics["control_sign_inverted"]
    baseline = metrics["baseline"]

    fk_base = baseline["full_known"]["mae_mev"]
    fk_cand = candidate["full_known"]["mae_mev"]
    fk_match = matched["full_known"]["mae_mev"]
    fk_inv = inverted["full_known"]["mae_mev"]
    holdout_base = baseline["primary_holdout"]["mae_mev"]
    holdout_cand = candidate["primary_holdout"]["mae_mev"]

    n_neutron_rich_train = sum(
        1
        for r in metrics["training_rows_overview"]
        if r["is_neutron_rich"]
    )
    if n_neutron_rich_train < 2:
        rationale.append(
            f"Training slice has only {n_neutron_rich_train} neutron-rich rows; "
            "candidate cannot be evaluated with isotope-chain transfer."
        )
        return "INCONCLUSIVE", rationale

    if fk_base is None or fk_cand is None:
        rationale.append("Full-known MAE undefined.")
        return "INCONCLUSIVE", rationale

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

    if fk_match is not None and (fk_match - fk_cand) < SURVIVAL_MARGIN_MEV:
        rationale.append(
            f"Matched high-error non-neutron-rich control matches candidate "
            f"(delta {fk_match - fk_cand:+.4f} MeV); signal is not neutron-rich-specific."
        )
        return "DIAGNOSTIC_ONLY", rationale

    if fk_inv is not None and (fk_inv - fk_cand) < SURVIVAL_MARGIN_MEV:
        rationale.append(
            "Sign-inverted control does almost as well; coefficient sign is unstable."
        )
        return "DIAGNOSTIC_ONLY", rationale

    transfer_rate = metrics.get("isotope_chain_transfer_rate")
    if transfer_rate is None:
        rationale.append("Isotope-chain transfer rate undefined (no eligible chains).")
        return "INCONCLUSIVE", rationale
    if transfer_rate < 0.5:
        rationale.append(
            f"Isotope-chain transfer rate {transfer_rate:.2f} < 0.5; improvement is "
            "chain-local rather than transferable."
        )
        return "DIAGNOSTIC_ONLY", rationale

    if (
        holdout_base is not None
        and holdout_cand is not None
        and holdout_cand > holdout_base
    ):
        rationale.append(
            f"Candidate regresses primary holdout (delta {holdout_cand - holdout_base:+.4f} MeV)."
        )
        return "DIAGNOSTIC_ONLY", rationale

    rationale.append(
        "Candidate beats baseline, both controls, transfers across half or more of "
        "eligible chains, and does not regress the primary holdout."
    )
    return "BOUNDED_FOLLOWUP_CANDIDATE", rationale


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
    inverted_full = sign_inverted_correction(full_known_rows, beta)
    matched_full = matched_high_error_control_correction(full_known_rows, training_rows)
    zero_full = [0.0] * len(full_known_rows)

    def split(corr: list[float]) -> dict[str, Any]:
        return {
            "training_lstsq": _summarize(training_rows, corr[: len(training_rows)]),
            "primary_holdout": _summarize(
                holdout_rows, corr[len(training_rows):]
            ),
            "full_known": _summarize(full_known_rows, corr),
        }

    per_chain = _per_chain(full_known_rows, candidate_full)
    eligible_chains = list(per_chain.values())
    if eligible_chains:
        transfers = sum(
            1 for entry in eligible_chains if (entry["delta_mae_mev"] or 0.0) > 0.0
        )
        transfer_rate: float | None = transfers / len(eligible_chains)
    else:
        transfer_rate = None

    training_overview = [
        {
            "row_id": r["row_id"],
            "Z": int(r["Z"]),
            "N": int(r["N"]),
            "A": int(r["A"]),
            "asymmetry": round((int(r["N"]) - int(r["Z"])) / int(r["A"]), 6),
            "boundary_distance": round(
                boundary_distance(int(r["Z"]), int(r["N"]), int(r["A"])), 6
            ),
            "is_neutron_rich": is_neutron_rich(int(r["Z"]), int(r["N"]), int(r["A"])),
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
            "name": "neutron_rich_boundary_distance",
            "formula": "max(0, (N - Z)/A - 0.18)",
            "inputs": ["Z", "N", "A"],
            "forbidden_inputs": [
                "baseline_residual_mev",
                "candidate_fit_residual",
                "baseline_error_rank",
                "source_status",
                "future_comparison_row",
            ],
        },
        "candidate_coefficient_beta_mev": round(beta, 6),
        "training_rows_overview": training_overview,
        "baseline": split(zero_full),
        "candidate": split(candidate_full),
        "control_matched_high_error": split(matched_full),
        "control_sign_inverted": split(inverted_full),
        "per_chain_candidate_full_known": per_chain,
        "isotope_chain_transfer_rate": transfer_rate,
        "per_subset_candidate_full_known": _per_subset(full_known_rows, candidate_full),
        "survival_margin_mev": SURVIVAL_MARGIN_MEV,
        "neutron_rich_asymmetry_threshold": NEUTRON_RICH_ASYMMETRY_THRESHOLD,
    }

    metrics["candidate_vs_baseline_full_known_delta_mev"] = _delta(
        metrics["baseline"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_matched_high_error_full_known_delta_mev"] = _delta(
        metrics["control_matched_high_error"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_sign_inverted_full_known_delta_mev"] = _delta(
        metrics["control_sign_inverted"]["full_known"]["mae_mev"],
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
    return metrics


def _delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return float(a - b)


# --------------------------------------------------------------------------- #
# Report rendering
# --------------------------------------------------------------------------- #


def _fmt(value: float | None, decimals: int = 4) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{decimals}f}"


def render_report(metrics: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Nuclear Neutron-Rich Boundary Transfer Hypothesis Lane")
    lines.append("")
    lines.append(f"**Task:** `{TASK_ID}`")
    lines.append(f"**Agent run:** `{AGENT_RUN_ID}`")
    lines.append("**Campaign:** `nuclear-mass-surface`")
    lines.append(f"**Verdict:** `{metrics['verdict']}`")
    lines.append("**Sandbox only:** true")
    lines.append("")
    lines.append("## Candidate")
    lines.append("")
    lines.append(
        "- Feature: `boundary_distance = max(0, (N - Z)/A - 0.18)` "
        "(closed-form, residual-free)."
    )
    lines.append(
        f"- Fit: `r_corr = beta * boundary_distance` via least squares on the "
        f"11-row NMD-0002 training slice. `beta = "
        f"{metrics['candidate_coefficient_beta_mev']:+.4f} MeV` (per unit "
        "boundary distance)."
    )
    lines.append("")
    lines.append("## Aggregate MAE (MeV)")
    lines.append("")
    lines.append(
        "| Surface | baseline | candidate | matched_high_error | sign_inverted |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for surface in ("training_lstsq", "primary_holdout", "full_known"):
        b = metrics["baseline"][surface]["mae_mev"]
        c = metrics["candidate"][surface]["mae_mev"]
        m = metrics["control_matched_high_error"][surface]["mae_mev"]
        s = metrics["control_sign_inverted"][surface]["mae_mev"]
        lines.append(
            f"| `{surface}` | {_fmt(b)} | {_fmt(c)} | {_fmt(m)} | {_fmt(s)} |"
        )
    lines.append("")
    lines.append("## Verdict Rationale")
    lines.append("")
    for note in metrics["verdict_rationale"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Isotope-Chain Transfer")
    lines.append("")
    rate = metrics["isotope_chain_transfer_rate"]
    lines.append(
        f"- Transfer rate (fraction of eligible chains with candidate improvement > 0): "
        f"{_fmt(rate, decimals=3) if rate is not None else 'n/a'}"
    )
    lines.append(
        f"- Eligible chains (>= {CHAIN_MIN_ROWS} rows on full_known): "
        f"{len(metrics['per_chain_candidate_full_known'])}"
    )
    lines.append("")
    if metrics["per_chain_candidate_full_known"]:
        lines.append(
            "| Chain | count | baseline MAE | candidate MAE | delta |"
        )
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for chain, entry in metrics["per_chain_candidate_full_known"].items():
            lines.append(
                f"| `{chain}` | {entry['count']} | {_fmt(entry['baseline_mae_mev'])} "
                f"| {_fmt(entry['candidate_mae_mev'])} | {_fmt(entry['delta_mae_mev'])} |"
            )
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
        "- Feature uses only `Z`, `N`, `A`. No baseline residual, error rank, "
        "candidate-fit residual, source-status flag, or future comparison row "
        "enters feature construction. ✅"
    )
    lines.append(
        "- Beta is fit by closed-form least squares on the training slice only; "
        "no candidate-fit residual feeds the controls. ✅"
    )
    lines.append(
        "- Matched-high-error control uses the baseline residual rank, NOT the "
        "candidate residual; it intentionally restricts to non-neutron-rich rows "
        "to test specificity. ✅"
    )
    lines.append(
        "- Sign-inverted control reuses the same beta with opposite sign; same "
        "fit logic. ✅"
    )
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


GAUNTLET_TO_SCHEMA_VERDICT = {
    "BOUNDED_FOLLOWUP_CANDIDATE": "SANDBOX_PASS",
    "DIAGNOSTIC_ONLY": "REVIEW_NEEDED",
    "NEGATIVE_RESULT": "FALSIFIED",
    "INCONCLUSIVE": "INCONCLUSIVE",
}


def render_agent_run(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": AGENT_RUN_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "task_id": TASK_ID,
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {"contributor_id": "roman", "agent_id": "claude"},
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
                        "feature, three declared controls (matched_high_error, "
                        "sign_inverted, isotope_chain_transfer), declared failure "
                        "condition, declared output routing, declared wording boundary."
                    ),
                },
                {
                    "name": "no_leakage_contract",
                    "status": "PASS",
                    "notes": (
                        "Feature is a closed-form function of Z/N/A; no residual or "
                        "future comparison row contributes."
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
                        "matched_high_error, sign_inverted, and per-chain transfer "
                        "metrics all reported."
                    ),
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": (
                        "No prediction registry, canonical result, claim, or "
                        "knowledge file is written."
                    ),
                },
            ],
        },
        "limitations": [
            "NMD-0002 has 11 training rows; the neutron-rich subset is sparse.",
            "Frozen baseline residuals are retrospective; this is not a blind prediction.",
            "The boundary threshold (0.18) is declared before the run and not retuned.",
            "Chain-transfer metric is computed only on chains with >=2 rows on the full_known surface.",
            "Matched-high-error control depends on baseline residual rank from the same frozen baseline; the control is a non-neutron-rich proxy, not a fully orthogonal regressor.",
        ],
        "verdict": GAUNTLET_TO_SCHEMA_VERDICT[metrics["verdict"]],
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
        "- NMD-0002 has 11 training rows; the neutron-rich subset is sparse.\n"
        "- Frozen baseline residuals are retrospective; this is not a blind prediction.\n"
        "- The boundary threshold (0.18) is declared before the run and not retuned.\n"
        "- Chain-transfer metric is computed only on chains with >=2 rows on full_known.\n"
        "- Matched-high-error control depends on baseline residual rank from the same frozen baseline; control is a non-neutron-rich proxy, not a fully orthogonal regressor.\n"
        f"- Verdict: `{metrics['verdict']}`. See `report.md` rationale.\n"
    )


def render_preflight(metrics: dict[str, Any]) -> str:
    return (
        f"# {AGENT_RUN_ID} Preflight\n\n"
        "Compliance with the controls-first gauntlet "
        "(`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):\n\n"
        "- Hypothesis family: closed-form residual-free boundary-distance feature "
        "per the F1/F5 spirit of `docs/nuclear-residual-feature-no-leakage-contract.md`.\n"
        "- Allowed inputs: Z, N, A (and the derived asymmetry/boundary distance).\n"
        "- Forbidden inputs (none used): target residual, baseline error rank as a "
        "feature, candidate-fit residual, source-status, future comparison rows.\n"
        "- Baseline: RESULT-0015 frozen semi-empirical coefficients.\n"
        "- Controls run end-to-end: matched_high_error_non_neutron_rich + "
        "sign_inverted_boundary + isotope_chain_transfer.\n"
        "- Failure condition declared before scoring: candidate must beat baseline by "
        "≥ 0.25 MeV on full_known and beat both numerical controls by the same margin; "
        "isotope-chain transfer rate must be ≥ 0.5; primary-holdout regression demotes "
        "the verdict to DIAGNOSTIC_ONLY.\n"
        "- Output routing: this agent_runs/ bundle + "
        "docs/reviews/nuclear-neutron-rich-boundary-transfer-hypothesis-lane.md.\n"
        "- Wording boundary: forbidden terms include discovery, new nuclear law, "
        "broad formula, anomaly explanation.\n"
    )


def render_review_summary(metrics: dict[str, Any]) -> str:
    return (
        f"# {AGENT_RUN_ID} Review Summary\n\n"
        f"- Verdict: `{metrics['verdict']}`.\n"
        f"- Beta: {metrics['candidate_coefficient_beta_mev']:+.4f} MeV.\n"
        f"- Full-known candidate vs baseline: "
        f"{_fmt(metrics['candidate_vs_baseline_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs matched_high_error: "
        f"{_fmt(metrics['candidate_vs_matched_high_error_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs sign_inverted: "
        f"{_fmt(metrics['candidate_vs_sign_inverted_full_known_delta_mev'])} MeV.\n"
        f"- Isotope-chain transfer rate: "
        f"{_fmt(metrics['isotope_chain_transfer_rate'], decimals=3) if metrics['isotope_chain_transfer_rate'] is not None else 'n/a'}.\n"
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
        print(f"Wrote agent_run bundle to {RUN_DIR}", file=sys.stderr)
    else:
        json.dump(metrics, sys.stdout, indent=2, sort_keys=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
