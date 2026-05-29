"""TASK-0449 nuclear residual-free high-error cluster hypothesis audit.

This runner tests whether cluster labels built ONLY from residual-free nuclear
features (Z, N, A, parity, magic-distance, asymmetry) produce a per-cluster
correction that beats matched-random and smooth-A controls under leave-one-out
on the NMD-0002 training slice without regressing the post-AME2020 primary
holdout.

It follows the controls-first gauntlet
(`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`) and the
no-leakage contract
(`docs/nuclear-residual-feature-no-leakage-contract.md`).

The runner is sandbox-only. It does NOT fetch live data, score the prediction
registry, write canonical RESULT-* artifacts, update claims, or edit knowledge.
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
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    semi_empirical_binding_energy,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0043"
TASK_ID = "TASK-0449"
HYP_PROPOSAL_PATH = (
    "hypothesis_proposals/nuclear-mass/"
    "HYP-PROPOSAL-0051-residual-free-high-error-cluster.yaml"
)
EXP_PROPOSAL_PATH = (
    "experiment_proposals/nuclear-mass/"
    "EXP-PROPOSAL-0017-nuclear-residual-free-high-error-cluster.yaml"
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
    REPO_ROOT
    / "docs"
    / "reviews"
    / "nuclear-residual-free-high-error-cluster-hypothesis-audit.md"
)

MAGIC_DISTANCE_THRESHOLD = 2
NEUTRON_RICH_ASYMMETRY_THRESHOLD = 0.18
LIGHT_A_THRESHOLD = 50
MATCHED_RANDOM_SEED = 449
SURVIVAL_MARGIN_MEV = 0.25

CLUSTER_TAXONOMY: tuple[str, ...] = (
    "near_magic_z_or_n",
    "neutron_rich",
    "light_a_lt_50",
    "other",
)


# --------------------------------------------------------------------------- #
# Residual-free cluster labels (F2 promotion path)
# --------------------------------------------------------------------------- #


def magic_distance(value: int) -> int:
    """Minimum absolute distance from ``value`` to any published magic number."""
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def assign_cluster_label(z: int, n: int, a: int) -> str:
    """Return the residual-free cluster label for row (Z, N, A).

    This function depends ONLY on Z, N, A and the published magic-number list.
    It does not access any baseline residual, candidate-fit residual, baseline
    error rank, target residual sign, or any error-derived quantity. It is the
    F2-REQ-LABEL-FROM-Z-N-ONLY rule from the no-leakage contract.
    """
    if z < 0 or n < 0 or a <= 0:
        raise ValueError(f"invalid nuclide coordinates: Z={z}, N={n}, A={a}")
    z_dist = magic_distance(z)
    n_dist = magic_distance(n)
    asymmetry = (n - z) / a
    if z_dist <= MAGIC_DISTANCE_THRESHOLD or n_dist <= MAGIC_DISTANCE_THRESHOLD:
        return "near_magic_z_or_n"
    if asymmetry >= NEUTRON_RICH_ASYMMETRY_THRESHOLD:
        return "neutron_rich"
    if a < LIGHT_A_THRESHOLD:
        return "light_a_lt_50"
    return "other"


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #


def load_frozen_baseline_coefficients() -> SemiEmpiricalCoefficients:
    """Load RESULT-0015 fitted semi-empirical coefficients."""
    payload = yaml.safe_load(RESULT_PATH.read_text(encoding="utf-8"))
    for score in payload["scores"]:
        if score["model_id"] == "model_fitted_semi_empirical":
            coefficients = score["coefficients"]
            return SemiEmpiricalCoefficients(
                volume=float(coefficients["volume"]),
                surface=float(coefficients["surface"]),
                coulomb=float(coefficients["coulomb"]),
                asymmetry=float(coefficients["asymmetry"]),
                pairing=float(coefficients["pairing"]),
            )
    raise RuntimeError("RESULT-0015 fitted semi-empirical coefficients not found")


def load_training_rows(
    coefficients: SemiEmpiricalCoefficients,
) -> list[dict[str, Any]]:
    """Return the NMD-0002 training-slice rows with baseline residuals."""
    nmd = load_nuclear_mass_dataset(NMD_PATH)
    baseline_rows = evaluate_baseline(
        entries=nmd.entries,
        model_id="model_fitted_semi_empirical",
        coefficients=coefficients,
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
                "source_surface": "training_loo",
            }
        )
    return rows


def load_holdout_rows(
    coefficients: SemiEmpiricalCoefficients,
) -> list[dict[str, Any]]:
    """Return the committed post-AME2020 primary holdout rows."""
    payload = yaml.safe_load(POST_AME_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for entry in payload["entries"]:
        if not bool(entry["included_in_time_split_holdout"]):
            continue
        z = int(entry["Z"])
        n = int(entry["N"])
        a = int(entry["A"])
        observed = float(entry["new_measurement"]["value_mev"])
        predicted = semi_empirical_binding_energy(z=z, n=n, coefficients=coefficients)
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
            }
        )
    return rows


# --------------------------------------------------------------------------- #
# Cluster correction (leave-one-out)
# --------------------------------------------------------------------------- #


def cluster_assignments(rows: list[dict[str, Any]]) -> list[str]:
    """Assign each row to its residual-free cluster label."""
    return [
        assign_cluster_label(z=int(r["Z"]), n=int(r["N"]), a=int(r["A"]))
        for r in rows
    ]


def cluster_counts(labels: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {name: 0 for name in CLUSTER_TAXONOMY}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return counts


def leave_one_out_offsets_training(
    training_rows: list[dict[str, Any]],
    training_labels: list[str],
) -> list[float]:
    """For each training row return the per-cluster LOO mean baseline residual.

    For a row in cluster c, the candidate's correction is the mean of
    baseline_residual_mev over OTHER training rows whose label is also c.
    If no other training rows share the cluster, the correction is 0.0.
    """
    n_rows = len(training_rows)
    residuals = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    offsets: list[float] = []
    for index in range(n_rows):
        label = training_labels[index]
        other_mask = [
            other_index != index and training_labels[other_index] == label
            for other_index in range(n_rows)
        ]
        if not any(other_mask):
            offsets.append(0.0)
            continue
        other_values = residuals[np.asarray(other_mask, dtype=bool)]
        offsets.append(float(np.mean(other_values)))
    return offsets


def cluster_mean_offsets_full_training(
    training_rows: list[dict[str, Any]],
    training_labels: list[str],
) -> dict[str, float]:
    """Return per-cluster mean baseline residual across the full training slice.

    These full-training means are applied to held-out rows (which were never
    in the training fit) under the same residual-free cluster assignment.
    """
    residuals = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    labels = np.asarray(training_labels, dtype=object)
    out: dict[str, float] = {}
    for name in CLUSTER_TAXONOMY:
        mask = labels == name
        if not mask.any():
            out[name] = 0.0
            continue
        out[name] = float(np.mean(residuals[mask]))
    return out


# --------------------------------------------------------------------------- #
# Controls
# --------------------------------------------------------------------------- #


def matched_random_labels(
    training_labels: list[str],
    *,
    seed: int = MATCHED_RANDOM_SEED,
) -> list[str]:
    """Permute the cluster labels across training rows using a fixed seed.

    Preserves the marginal label distribution but breaks the (Z, N, A) -> label
    mapping. This is the matched-random control from the gauntlet.
    """
    rng = np.random.default_rng(seed)
    permutation = list(training_labels)
    indices = rng.permutation(len(permutation))
    return [permutation[index] for index in indices]


def smooth_a_linear_correction(
    training_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    *,
    leave_one_out: bool,
) -> list[float]:
    """Compute the smooth-A linear control correction for each target row.

    Fit r ~ a + b * A on the training rows (with LOO if requested) and apply
    the resulting slope/intercept to each target row's A value. This replaces
    the per-cluster offset with a single mass-scale linear correction.
    """
    train_a = np.asarray([float(r["A"]) for r in training_rows], dtype=float)
    train_r = np.asarray(
        [float(r["baseline_residual_mev"]) for r in training_rows], dtype=float
    )
    target_a = np.asarray([float(r["A"]) for r in target_rows], dtype=float)
    out: list[float] = []
    if leave_one_out:
        # one-fit-per-target-row, holding out only the matching row by row_id
        train_ids = [r["row_id"] for r in training_rows]
        for index in range(len(target_rows)):
            target_id = target_rows[index]["row_id"]
            keep = np.asarray(
                [other_id != target_id for other_id in train_ids], dtype=bool
            )
            if not keep.any():
                out.append(0.0)
                continue
            beta = _fit_linear(train_a[keep], train_r[keep])
            out.append(float(beta[0] + beta[1] * target_a[index]))
        return out
    beta = _fit_linear(train_a, train_r)
    return [float(beta[0] + beta[1] * a) for a in target_a.tolist()]


def _fit_linear(x_values: np.ndarray, y_values: np.ndarray) -> tuple[float, float]:
    """Closed-form least-squares fit of ``y = a + b * x`` returning (a, b)."""
    if x_values.size < 2:
        if x_values.size == 0:
            return (0.0, 0.0)
        return (float(y_values[0]), 0.0)
    design = np.column_stack([np.ones_like(x_values), x_values])
    beta, *_ = np.linalg.lstsq(design, y_values, rcond=None)
    return (float(beta[0]), float(beta[1]))


# --------------------------------------------------------------------------- #
# Surfaces and metrics
# --------------------------------------------------------------------------- #


def _errors(rows: list[dict[str, Any]], corrections: list[float]) -> list[float]:
    return [
        float(row["observed_mev"])
        - (float(row["baseline_predicted_mev"]) + correction)
        for row, correction in zip(rows, corrections)
    ]


def _abs_errors(errors: list[float]) -> list[float]:
    return [abs(e) for e in errors]


def _mae(errors: list[float]) -> float | None:
    if not errors:
        return None
    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))


def _rmse(errors: list[float]) -> float | None:
    if not errors:
        return None
    return float(np.sqrt(np.mean(np.square(np.asarray(errors, dtype=float)))))


def _summarize(rows: list[dict[str, Any]], corrections: list[float]) -> dict[str, Any]:
    errors = _errors(rows, corrections)
    return {
        "count": len(errors),
        "mae_mev": _mae(errors),
        "rmse_mev": _rmse(errors),
        "mean_signed_error_mev": (
            float(np.mean(np.asarray(errors, dtype=float))) if errors else None
        ),
    }


def _per_cluster_summary(
    rows: list[dict[str, Any]],
    labels: list[str],
    corrections: list[float],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name in CLUSTER_TAXONOMY:
        mask = [label == name for label in labels]
        cluster_rows = [r for r, m in zip(rows, mask) if m]
        cluster_corr = [c for c, m in zip(corrections, mask) if m]
        out[name] = _summarize(cluster_rows, cluster_corr)
    return out


# --------------------------------------------------------------------------- #
# Verdict
# --------------------------------------------------------------------------- #


def decide_verdict(metrics: dict[str, Any]) -> tuple[str, list[str]]:
    """Apply the controls-first gauntlet verdict logic.

    Returns the verdict label and a list of human-readable rationale lines.
    """
    rationale: list[str] = []
    candidate = metrics["candidate"]
    matched_random = metrics["control_matched_random"]
    smooth_a = metrics["control_smooth_a"]
    baseline = metrics["baseline"]
    cluster_counts_training = metrics["cluster_counts"]["training_loo"]
    cluster_counts_holdout = metrics["cluster_counts"]["primary_holdout"]

    full_known_baseline = baseline["full_known"]["mae_mev"]
    full_known_candidate = candidate["full_known"]["mae_mev"]
    full_known_random = matched_random["full_known"]["mae_mev"]
    full_known_smooth = smooth_a["full_known"]["mae_mev"]

    holdout_baseline = baseline["primary_holdout"]["mae_mev"]
    holdout_candidate = candidate["primary_holdout"]["mae_mev"]

    # Inconclusive checks
    nonempty_training = sum(1 for c in cluster_counts_training.values() if c >= 2)
    if nonempty_training < 2:
        rationale.append(
            "Fewer than two clusters have ≥2 training rows; "
            "leave-one-out cannot evaluate per-cluster structure."
        )
        return "INCONCLUSIVE", rationale
    if full_known_baseline is None or full_known_candidate is None:
        rationale.append("Full-known MAE is undefined; cannot score.")
        return "INCONCLUSIVE", rationale

    candidate_improvement_full = full_known_baseline - full_known_candidate
    rationale.append(
        f"full_known candidate improvement vs baseline: "
        f"{candidate_improvement_full:+.4f} MeV"
    )

    if full_known_random is not None:
        vs_random = full_known_random - full_known_candidate
        rationale.append(
            f"full_known candidate vs matched_random: {vs_random:+.4f} MeV"
        )
    else:
        vs_random = None
        rationale.append("full_known matched_random MAE undefined.")
    if full_known_smooth is not None:
        vs_smooth = full_known_smooth - full_known_candidate
        rationale.append(
            f"full_known candidate vs smooth_a: {vs_smooth:+.4f} MeV"
        )
    else:
        vs_smooth = None
        rationale.append("full_known smooth_a MAE undefined.")

    if vs_random is None or vs_smooth is None:
        return "INCONCLUSIVE", rationale

    if candidate_improvement_full < SURVIVAL_MARGIN_MEV:
        rationale.append(
            f"Candidate fails the {SURVIVAL_MARGIN_MEV} MeV survival margin on "
            "full_known vs baseline."
        )
        return "NEGATIVE_RESULT", rationale

    if vs_random < SURVIVAL_MARGIN_MEV or vs_smooth < SURVIVAL_MARGIN_MEV:
        rationale.append(
            "Candidate beats baseline but does not beat both declared controls by "
            f"the {SURVIVAL_MARGIN_MEV} MeV margin."
        )
        return "DIAGNOSTIC_ONLY", rationale

    # Holdout regression check
    holdout_regression_flag = False
    if (
        holdout_baseline is not None
        and holdout_candidate is not None
        and sum(cluster_counts_holdout.values()) > 0
    ):
        holdout_change = holdout_candidate - holdout_baseline
        rationale.append(
            f"primary_holdout candidate change vs baseline: "
            f"{holdout_change:+.4f} MeV (positive = regression)"
        )
        if holdout_change > 0.0:
            holdout_regression_flag = True

    if holdout_regression_flag:
        rationale.append(
            "Candidate beats both controls on full_known but regresses the "
            "primary holdout panel."
        )
        return "DIAGNOSTIC_ONLY", rationale

    rationale.append(
        "Candidate beats both controls by the survival margin on full_known and "
        "does not regress the primary holdout."
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

    training_labels = cluster_assignments(training_rows)
    holdout_labels = cluster_assignments(holdout_rows)
    full_known_labels = training_labels + holdout_labels

    counts_training = cluster_counts(training_labels)
    counts_holdout = cluster_counts(holdout_labels)
    counts_full_known = cluster_counts(full_known_labels)

    # Candidate corrections
    candidate_training = leave_one_out_offsets_training(training_rows, training_labels)
    full_training_means = cluster_mean_offsets_full_training(
        training_rows, training_labels
    )
    candidate_holdout = [full_training_means[label] for label in holdout_labels]
    candidate_full = candidate_training + candidate_holdout

    # Matched-random control
    random_labels = matched_random_labels(training_labels, seed=MATCHED_RANDOM_SEED)
    random_training = leave_one_out_offsets_training(training_rows, random_labels)
    random_full_means = cluster_mean_offsets_full_training(training_rows, random_labels)
    random_holdout_labels = matched_random_labels(
        holdout_labels, seed=MATCHED_RANDOM_SEED + 1
    )
    random_holdout = [random_full_means[label] for label in random_holdout_labels]
    random_full = random_training + random_holdout

    # Smooth-A linear control
    smooth_training = smooth_a_linear_correction(
        training_rows, training_rows, leave_one_out=True
    )
    smooth_holdout = smooth_a_linear_correction(
        training_rows, holdout_rows, leave_one_out=False
    )
    smooth_full = smooth_training + smooth_holdout

    # Baseline zero correction
    zero_training = [0.0] * len(training_rows)
    zero_holdout = [0.0] * len(holdout_rows)
    zero_full = zero_training + zero_holdout

    def summarize_block(
        zero: list[float],
        corr: list[float],
    ) -> dict[str, Any]:
        return {
            "training_loo": _summarize(training_rows, corr[: len(training_rows)]),
            "primary_holdout": _summarize(
                holdout_rows, corr[len(training_rows):]
            ),
            "full_known": _summarize(full_known_rows, corr),
        }

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
        "cluster_taxonomy": list(CLUSTER_TAXONOMY),
        "cluster_label_inputs": [
            "Z",
            "N",
            "A",
            "magic_distance_z",
            "magic_distance_n",
            "asymmetry = (N - Z) / A",
        ],
        "cluster_label_forbidden_inputs": [
            "baseline_residual_mev",
            "candidate_fit_residual",
            "baseline_error_rank",
            "target_residual_sign",
            "high_error_percentile_flag",
            "source_status",
        ],
        "cluster_label_thresholds": {
            "magic_distance_threshold": MAGIC_DISTANCE_THRESHOLD,
            "neutron_rich_asymmetry_threshold": NEUTRON_RICH_ASYMMETRY_THRESHOLD,
            "light_a_threshold": LIGHT_A_THRESHOLD,
        },
        "cluster_counts": {
            "training_loo": counts_training,
            "primary_holdout": counts_holdout,
            "full_known": counts_full_known,
        },
        "training_loo_offsets_mev": dict(
            zip(
                [r["row_id"] for r in training_rows],
                [round(value, 6) for value in candidate_training],
            )
        ),
        "full_training_cluster_means_mev": {
            name: round(value, 6) for name, value in full_training_means.items()
        },
        "baseline": summarize_block(zero_full, zero_full),
        "candidate": summarize_block(zero_full, candidate_full),
        "control_matched_random": summarize_block(zero_full, random_full),
        "control_smooth_a": summarize_block(zero_full, smooth_full),
        "per_cluster_candidate_full_known": _per_cluster_summary(
            full_known_rows, full_known_labels, candidate_full
        ),
        "per_cluster_baseline_full_known": _per_cluster_summary(
            full_known_rows, full_known_labels, zero_full
        ),
        "survival_margin_mev": SURVIVAL_MARGIN_MEV,
        "matched_random_seed": MATCHED_RANDOM_SEED,
    }

    metrics["candidate_vs_matched_random_full_known_delta_mev"] = _delta(
        metrics["control_matched_random"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_smooth_a_full_known_delta_mev"] = _delta(
        metrics["control_smooth_a"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["candidate_vs_baseline_full_known_delta_mev"] = _delta(
        metrics["baseline"]["full_known"]["mae_mev"],
        metrics["candidate"]["full_known"]["mae_mev"],
    )
    metrics["primary_holdout_regression_flag"] = _holdout_regressed(metrics)

    verdict, rationale = decide_verdict(metrics)
    metrics["verdict"] = verdict
    metrics["verdict_rationale"] = rationale
    return metrics


def _delta(reference: float | None, candidate: float | None) -> float | None:
    if reference is None or candidate is None:
        return None
    return float(reference - candidate)


def _holdout_regressed(metrics: dict[str, Any]) -> bool:
    holdout_baseline = metrics["baseline"]["primary_holdout"]["mae_mev"]
    holdout_candidate = metrics["candidate"]["primary_holdout"]["mae_mev"]
    if holdout_baseline is None or holdout_candidate is None:
        return False
    return bool(holdout_candidate > holdout_baseline)


# --------------------------------------------------------------------------- #
# Report rendering and agent_run files
# --------------------------------------------------------------------------- #


def _fmt(value: float | None, decimals: int = 4) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{decimals}f}"


def render_report(metrics: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Nuclear Residual-Free High-Error Cluster Hypothesis Audit")
    lines.append("")
    lines.append(f"**Task:** `{TASK_ID}`")
    lines.append(f"**Agent run:** `{AGENT_RUN_ID}`")
    lines.append("**Campaign:** `nuclear-mass-surface`")
    lines.append(f"**Verdict:** `{metrics['verdict']}`")
    lines.append("**Sandbox only:** true")
    lines.append("")
    lines.append("## Cluster Taxonomy (residual-free)")
    lines.append("")
    lines.append("Cluster labels are deterministic functions of `Z`, `N`, `A` only:")
    lines.append("")
    lines.append("- `near_magic_z_or_n`: `min(|Z - m|) ≤ 2` or `min(|N - m|) ≤ 2`")
    lines.append("- `neutron_rich`: `(N - Z) / A ≥ 0.18` (and not near-magic)")
    lines.append("- `light_a_lt_50`: `A < 50` (and not near-magic or neutron-rich)")
    lines.append("- `other`: everything else")
    lines.append("")
    lines.append("Magic numbers: `{2, 8, 20, 28, 50, 82, 126, 184}`.")
    lines.append("")
    lines.append("## Cluster Counts")
    lines.append("")
    lines.append("| Cluster | training_loo | primary_holdout | full_known |")
    lines.append("| --- | ---: | ---: | ---: |")
    for name in CLUSTER_TAXONOMY:
        train = metrics["cluster_counts"]["training_loo"][name]
        holdout = metrics["cluster_counts"]["primary_holdout"][name]
        full = metrics["cluster_counts"]["full_known"][name]
        lines.append(f"| `{name}` | {train} | {holdout} | {full} |")
    lines.append("")
    lines.append("## Aggregate Metrics (MAE, MeV)")
    lines.append("")
    lines.append(
        "| Surface | baseline | candidate | matched_random | smooth_a |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for surface in ("training_loo", "primary_holdout", "full_known"):
        baseline_mae = metrics["baseline"][surface]["mae_mev"]
        candidate_mae = metrics["candidate"][surface]["mae_mev"]
        random_mae = metrics["control_matched_random"][surface]["mae_mev"]
        smooth_mae = metrics["control_smooth_a"][surface]["mae_mev"]
        lines.append(
            f"| `{surface}` | {_fmt(baseline_mae)} | {_fmt(candidate_mae)} "
            f"| {_fmt(random_mae)} | {_fmt(smooth_mae)} |"
        )
    lines.append("")
    lines.append("## Verdict Rationale")
    lines.append("")
    for note in metrics["verdict_rationale"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Per-Cluster Candidate vs Baseline (full_known)")
    lines.append("")
    lines.append("| Cluster | count | baseline MAE | candidate MAE | delta |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for name in CLUSTER_TAXONOMY:
        per_baseline = metrics["per_cluster_baseline_full_known"][name]
        per_candidate = metrics["per_cluster_candidate_full_known"][name]
        delta = _delta(per_baseline["mae_mev"], per_candidate["mae_mev"])
        lines.append(
            f"| `{name}` | {per_baseline['count']} | {_fmt(per_baseline['mae_mev'])} "
            f"| {_fmt(per_candidate['mae_mev'])} | {_fmt(delta, decimals=4)} |"
        )
    lines.append("")
    lines.append("## Leakage Audit (per the no-leakage contract)")
    lines.append("")
    lines.append(
        "- Cluster labels use only `Z`, `N`, `A`, parity, magic-distance, "
        "asymmetry. No baseline residual, error rank, or any residual-derived "
        "quantity enters label construction."
    )
    lines.append(
        "- Per-cluster candidate offsets are computed leave-one-out within the "
        "NMD-0002 training slice; for held-out rows the full training-slice mean "
        "is used (the holdout rows never enter the fit)."
    )
    lines.append(
        "- Both controls share the same fold logic: matched_random permutes the "
        "training labels under a fixed seed; smooth_a fits `r = a + b * A` with "
        "leave-one-out on the training slice."
    )
    lines.append(
        "- No candidate-fit residuals feed any aggregate. No future comparison "
        "row contributes to label construction."
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
                        "hypothesis-gauntlet.md: residual-free labels, two "
                        "declared controls, declared failure condition, "
                        "declared output routing, declared wording boundary."
                    ),
                },
                {
                    "name": "no_leakage_contract_F2",
                    "status": "PASS",
                    "notes": (
                        "Cluster labels are deterministic functions of Z/N/A "
                        "only, per the F2 promotion path of "
                        "docs/nuclear-residual-feature-no-leakage-contract.md."
                    ),
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": (
                        "Only committed NMD-0002 and post-AME2020 holdout rows "
                        "and the frozen RESULT-0015 baseline are read; no live "
                        "fetch."
                    ),
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": (
                        "matched_random and smooth_a controls are executed "
                        "end-to-end under the same fold logic as the candidate."
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
            "NMD-0002 has 11 training rows; per-cluster leave-one-out can be sparse for small cells.",
            "Frozen baseline residuals are retrospective; this is not a blind prediction.",
            "Cluster taxonomy is fixed before the run and may not exhaust useful residual-free partitions.",
            "The post-AME2020 primary holdout has limited cluster coverage; some cluster verdicts are dominated by training-loo behavior alone.",
            "Matched-random and smooth-A controls are decisive for interpretation; the candidate may not survive both.",
        ],
        "verdict": metrics["verdict"],
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
        "# AGENT-RUN-0043 Limitations\n\n"
        "- NMD-0002 has 11 training rows; per-cluster leave-one-out can be "
        "sparse for small cells.\n"
        "- Frozen baseline residuals are retrospective; this is not a blind "
        "prediction.\n"
        "- The cluster taxonomy is fixed before the run and may not exhaust "
        "useful residual-free partitions.\n"
        "- The post-AME2020 primary holdout has limited cluster coverage; "
        "some cluster verdicts are dominated by training_loo behavior alone.\n"
        "- Matched-random and smooth-A controls are decisive for "
        "interpretation; the candidate may not survive both.\n"
        f"- Verdict: `{metrics['verdict']}`. See `report.md` rationale.\n"
    )


def render_preflight(metrics: dict[str, Any]) -> str:
    return (
        "# AGENT-RUN-0043 Preflight\n\n"
        "Compliance with the controls-first gauntlet "
        "(`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`):\n\n"
        "- Hypothesis family: F2 (high-error cluster) under residual-free "
        "labels per `docs/nuclear-residual-feature-no-leakage-contract.md`.\n"
        "- Allowed inputs: Z, N, A, magic-distance (from published magic-number "
        "list), asymmetry (N - Z) / A. No baseline residual or any "
        "residual-derived quantity enters label construction.\n"
        "- Forbidden inputs (none used): target residual, baseline error rank, "
        "candidate-fit residual, source-status flag, future comparison rows.\n"
        "- Baseline: RESULT-0015 frozen semi-empirical coefficients. No "
        "candidate-fit residuals feed neighbor aggregates.\n"
        "- Controls (both run end-to-end): matched_random cluster-label "
        "permutation + smooth_a linear (`r = a + b * A`).\n"
        "- Leave-one-out logic: each training row's candidate correction uses "
        "the mean of OTHER training rows in the same cluster.\n"
        "- Holdout: post-AME2020 primary holdout rows use the full "
        "training-slice cluster mean. Holdout rows never enter the fit.\n"
        "- Failure condition declared before scoring: candidate must beat "
        "baseline by ≥ 0.25 MeV on full_known MAE and beat both controls by "
        "the same margin; primary-holdout regression demotes the verdict to "
        "DIAGNOSTIC_ONLY.\n"
        "- Output routing: this agent_runs/ bundle + "
        "docs/reviews/nuclear-residual-free-high-error-cluster-hypothesis-"
        "audit.md. No PRED/CLAIM/KNOW/RESULT artifacts.\n"
        "- Wording boundary: forbidden terms include discovery, new nuclear "
        "law, broad formula, first-principles. Verdict vocabulary fixed at "
        "{BOUNDED_FOLLOWUP_CANDIDATE, DIAGNOSTIC_ONLY, NEGATIVE_RESULT, "
        "INCONCLUSIVE}.\n"
    )


def render_review_summary(metrics: dict[str, Any]) -> str:
    return (
        "# AGENT-RUN-0043 Review Summary\n\n"
        f"- Verdict: `{metrics['verdict']}`.\n"
        f"- Survival margin: {SURVIVAL_MARGIN_MEV} MeV.\n"
        f"- Full-known candidate vs baseline: "
        f"{_fmt(metrics['candidate_vs_baseline_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs matched_random: "
        f"{_fmt(metrics['candidate_vs_matched_random_full_known_delta_mev'])} MeV.\n"
        f"- Full-known candidate vs smooth_a: "
        f"{_fmt(metrics['candidate_vs_smooth_a_full_known_delta_mev'])} MeV.\n"
        f"- Primary-holdout regression flag: "
        f"{metrics['primary_holdout_regression_flag']}.\n"
        f"- Sandbox only; no PRED/CLAIM/KNOW/RESULT artifact written.\n"
    )


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write agent_run bundle to the canonical paths under "
        "agent_runs/AGENT-RUN-0043/.",
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
