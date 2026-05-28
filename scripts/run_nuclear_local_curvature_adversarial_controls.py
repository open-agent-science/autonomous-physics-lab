"""TASK-0351 nuclear local-curvature adversarial controls lane.

Attacks the TASK-0339 / AGENT-RUN-0026 local-curvature sandbox signal with
three new adversarial controls so the sandbox surface can either survive
falsification or be preserved as an overfit / smoothing diagnostic.

Reproduces the TASK-0339 candidate metrics from committed datasets
(deterministic), adds three controls that probe the most likely leakage and
smoothing modes, evaluates everything on the same full-known / holdout /
magic / neutron-rich / high-error / isotope-chain / isotone-chain subsets
the lane already uses, and reports whether each candidate still beats its
strongest control by a meaningful margin.

This runner is sandbox-only retrospective evidence. It does not fetch
external data, does not score prediction registry entries, does not write
canonical RESULT-* artifacts, does not update claims, and does not edit
knowledge entries.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_nuclear_local_curvature_lane as lane  # noqa: E402
import scripts.run_nuclear_shell_axis_full_known_audit as full_known  # noqa: E402


AGENT_RUN_ID = "AGENT-RUN-0031"
TASK_ID = "TASK-0351"
HIGH_ERROR_PERCENTILE = lane.HIGH_ERROR_PERCENTILE
PRIMARY_SURVIVAL_MARGIN_MEV = 0.25
"""Minimum candidate-vs-strongest-control MAE-delta margin (MeV) on the
primary `full_known` subset before the candidate is considered to have
survived. Chosen conservatively from the existing control magnitudes in
AGENT-RUN-0026 so that a candidate must beat the strongest control by at
least 0.25 MeV on the primary subset to count as surviving."""

DEFAULT_AGENT_RUN_DIR = REPO_ROOT / "agent_runs" / AGENT_RUN_ID
DEFAULT_METRICS_PATH = DEFAULT_AGENT_RUN_DIR / "metrics.json"
DEFAULT_REPORT_PATH = DEFAULT_AGENT_RUN_DIR / "report.md"
DEFAULT_AGENT_RUN_PATH = DEFAULT_AGENT_RUN_DIR / "agent_run.yaml"
DEFAULT_LIMITATIONS_PATH = DEFAULT_AGENT_RUN_DIR / "limitations.md"
DEFAULT_PREFLIGHT_PATH = DEFAULT_AGENT_RUN_DIR / "preflight.md"
DEFAULT_REVIEW_SUMMARY_PATH = DEFAULT_AGENT_RUN_DIR / "review_summary.md"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "reviews" / "nuclear-local-curvature-adversarial-controls.md"
)


# ---------------------------------------------------------------------------
# Three new adversarial control feature functions
# ---------------------------------------------------------------------------


def _closest_neighbor_only_isotope_mean(
    row: dict[str, Any],
    index: lane.NeighborIndex,
) -> tuple[float, ...]:
    """LOCAL-CONTROL-003 — neighbor-availability leakage control.

    Uses only the *single closest* same-Z neighbor (by |Delta N|) instead of
    the pair mean from the LOCAL-CURVATURE-001 candidate. A genuine local-
    curvature signal should still beat the baseline because the closest
    neighbor carries the curvature information. A signal that depends on
    having both sides of the chain to average — i.e. on neighbor availability
    rather than neighbor content — will weaken noticeably under this control.
    """

    left, right = index.isotope_pair(row)
    target_n = int(row["N"])
    candidates = [
        (neighbor, abs(int(neighbor["N"]) - target_n))
        for neighbor in (left, right)
        if neighbor is not None
    ]
    if not candidates:
        return (0.0,)
    candidates.sort(key=lambda item: (item[1], int(item[0]["N"])))
    closest, _ = candidates[0]
    return (float(closest["baseline_residual_mev"]),)


def _label_shuffled_isotope_mean(
    row: dict[str, Any],
    index: lane.NeighborIndex,
) -> tuple[float, ...]:
    """LOCAL-CONTROL-004 — isotope/isotone label shuffle control.

    Computes the "isotope" neighbor mean using a deterministically
    permuted Z label (each Z is mapped to a Z roughly half the
    observed-Z list away). The row's own residual is excluded.

    Intent: if the LOCAL-CURVATURE-001 / -002 signal is driven by real
    chain-local curvature, this control should not beat the baseline at
    all (the "chain" is now wrong). If the signal is driven by any-nearby-
    residual leakage, the control will still pick up much of the
    improvement.
    """

    observed_z = sorted(index.isotopes.keys())
    if len(observed_z) < 2:
        return (0.0,)
    target_z = int(row["Z"])
    if target_z not in observed_z:
        return (0.0,)
    idx = observed_z.index(target_z)
    shuffled_z = observed_z[(idx + len(observed_z) // 2) % len(observed_z)]
    group = index.isotopes.get(shuffled_z, [])
    target_n = int(row["N"])
    target_id = str(row["nuclide_id"])
    candidates = [item for item in group if str(item["nuclide_id"]) != target_id]
    if not candidates:
        return (0.0,)
    candidates.sort(key=lambda item: (abs(int(item["N"]) - target_n), int(item["N"])))
    pair = candidates[:2]
    values = [float(item["baseline_residual_mev"]) for item in pair]
    return (float(np.mean(np.asarray(values, dtype=float))),)


def _local_linear_regression_smoother(
    row: dict[str, Any],
    index: lane.NeighborIndex,
) -> tuple[float, ...]:
    """LOCAL-CONTROL-005 — matched smooth local-regression control.

    Fits a 1-D linear regression to (A, baseline_residual) over the same
    A-window neighborhood the LOCAL-CONTROL-002 smooth-window uses, then
    returns the regression's prediction at the target row's A. The fit
    ignores chain identity entirely.

    Intent: if the candidates beat this smoother by a meaningful margin,
    the candidate signal carries chain-specific information not captured
    by a generic smoothness assumption. If the candidates and the smoother
    are within noise of each other, the candidate signal is most likely
    generic local smoothing and should not be promoted.
    """

    neighbors = index.smooth_a_neighbors(row)
    if len(neighbors) < 3:
        return (0.0,)
    abscissa = np.asarray([float(item["A"]) for item in neighbors], dtype=float)
    ordinate = np.asarray(
        [float(item["baseline_residual_mev"]) for item in neighbors], dtype=float
    )
    design = np.vstack([np.ones_like(abscissa), abscissa]).T
    beta, *_ = np.linalg.lstsq(design, ordinate, rcond=None)
    intercept, slope = float(beta[0]), float(beta[1])
    predicted = intercept + slope * float(int(row["A"]))
    return (predicted,)


# ---------------------------------------------------------------------------
# Adversarial variants — old executed candidates plus new controls
# ---------------------------------------------------------------------------


def _build_adversarial_variants() -> tuple[dict[str, Any], ...]:
    """Compose the lane's three executed candidates with two existing
    controls and the three new adversarial controls."""

    base = {
        item["candidate_id"]: dict(item)
        for item in lane.GENERATED_VARIANTS
        if item["fit_mode"] == "lstsq"
    }
    ordered_ids = (
        "LOCAL-CURVATURE-001",
        "LOCAL-CURVATURE-002",
        "LOCAL-CURVATURE-003",
        "LOCAL-CONTROL-001",
        "LOCAL-CONTROL-002",
    )
    variants: list[dict[str, Any]] = [base[item_id] for item_id in ordered_ids]
    variants.extend(
        (
            {
                "candidate_id": "LOCAL-CONTROL-003",
                "name": "Closest-neighbor-only isotope residual (neighbor-availability leakage control)",
                "family": "neighbor_availability_leakage_control",
                "formula": "r_corr = beta * baseline_residual(closest same-Z neighbor by |Delta N|)",
                "feature_names": ("closest_neighbor_only_isotope_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "neighbor_availability_leakage_control",
                "feature_fn": _closest_neighbor_only_isotope_mean,
            },
            {
                "candidate_id": "LOCAL-CONTROL-004",
                "name": "Label-shuffled isotope residual mean (chain-label shuffle control)",
                "family": "chain_label_shuffle_control",
                "formula": "r_corr = beta * mean(nearest baseline residuals from a deterministically reassigned Z chain)",
                "feature_names": ("label_shuffled_isotope_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "chain_label_shuffle_control",
                "feature_fn": _label_shuffled_isotope_mean,
            },
            {
                "candidate_id": "LOCAL-CONTROL-005",
                "name": "Matched smooth local-regression smoother (chain-blind smoother control)",
                "family": "smooth_local_regression_control",
                "formula": "r_corr = beta * predict(local linear regression over A-window, predict at row.A)",
                "feature_names": ("local_linear_regression_residual",),
                "fit_mode": "lstsq",
                "complexity": 1,
                "role": "smooth_local_regression_control",
                "feature_fn": _local_linear_regression_smoother,
            },
        )
    )
    return tuple(variants)


# ---------------------------------------------------------------------------
# Build / write metrics + artifacts
# ---------------------------------------------------------------------------


def _evaluate_all_variants(
    variants: tuple[dict[str, Any], ...]
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, float | int | None]],
    float,
    lane.NeighborIndex,
    list[dict[str, Any]],
]:
    coefficients = full_known.load_frozen_baseline_coefficients()
    audit_rows, training_rows, training_residuals, _surface = (
        full_known.build_audit_surface(coefficients)
    )
    high_error_threshold = float(
        np.percentile(
            np.asarray(
                [abs(float(row["baseline_residual_mev"])) for row in audit_rows],
                dtype=float,
            ),
            HIGH_ERROR_PERCENTILE,
            method="linear",
        )
    )
    baseline_metrics = lane._baseline_metrics(  # noqa: SLF001
        audit_rows,
        high_error_threshold=high_error_threshold,
    )
    index = lane.NeighborIndex(audit_rows)
    items: list[dict[str, Any]] = []
    for variant in variants:
        items.append(
            lane._evaluate_variant(  # noqa: SLF001
                variant,
                audit_rows=audit_rows,
                training_rows=training_rows,
                training_residuals=training_residuals,
                index=index,
                baseline_metrics=baseline_metrics,
                high_error_threshold=high_error_threshold,
            )
        )
    return items, baseline_metrics, high_error_threshold, index, audit_rows


def _candidate_vs_strongest_control_table(
    items: list[dict[str, Any]],
    *,
    baseline_metrics: dict[str, dict[str, float | int | None]],
) -> list[dict[str, Any]]:
    candidates = [item for item in items if item["role"] == "executed_candidate"]
    controls = [item for item in items if item["role"].endswith("_control")]
    table: list[dict[str, Any]] = []
    subset_keys = sorted(baseline_metrics.keys())
    for candidate in candidates:
        per_subset: list[dict[str, Any]] = []
        candidate_wins_subset_count = 0
        strongest_control_per_subset: list[dict[str, Any]] = []
        for subset_id in subset_keys:
            candidate_delta = candidate["delta_mae_by_subset_mev"].get(subset_id)
            control_deltas = {
                control["candidate_id"]: control["delta_mae_by_subset_mev"].get(subset_id)
                for control in controls
            }
            usable = {
                cid: value
                for cid, value in control_deltas.items()
                if value is not None
            }
            if not usable or candidate_delta is None:
                margin = None
                strongest_control_id = None
                strongest_control_delta = None
                candidate_beats_strongest = None
            else:
                strongest_control_id, strongest_control_delta = min(
                    usable.items(), key=lambda kv: float(kv[1])
                )
                margin = float(strongest_control_delta) - float(candidate_delta)
                candidate_beats_strongest = bool(margin > 0.0)
                if candidate_beats_strongest:
                    candidate_wins_subset_count += 1
            per_subset.append(
                {
                    "subset_id": subset_id,
                    "candidate_delta_mae_mev": candidate_delta,
                    "strongest_control_id": strongest_control_id,
                    "strongest_control_delta_mae_mev": strongest_control_delta,
                    "candidate_minus_strongest_control_mev": margin,
                    "candidate_beats_strongest_control": candidate_beats_strongest,
                }
            )
            strongest_control_per_subset.append(
                {
                    "subset_id": subset_id,
                    "strongest_control_id": strongest_control_id,
                }
            )
        primary_subset_row = next(
            (row for row in per_subset if row["subset_id"] == "full_known"),
            None,
        )
        primary_margin = (
            primary_subset_row["candidate_minus_strongest_control_mev"]
            if primary_subset_row is not None
            else None
        )
        primary_strongest_control = (
            primary_subset_row["strongest_control_id"]
            if primary_subset_row is not None
            else None
        )
        survived_primary = bool(
            primary_margin is not None
            and primary_margin >= PRIMARY_SURVIVAL_MARGIN_MEV
        )
        usable_subsets = sum(
            1 for row in per_subset if row["candidate_beats_strongest_control"] is not None
        )
        win_rate = (
            (candidate_wins_subset_count / usable_subsets) if usable_subsets > 0 else None
        )
        table.append(
            {
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "primary_subset_id": "full_known",
                "primary_candidate_minus_strongest_control_mev": primary_margin,
                "primary_strongest_control_id": primary_strongest_control,
                "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
                "primary_survives_adversarial_controls": survived_primary,
                "subset_wins_count": candidate_wins_subset_count,
                "subset_evaluated_count": usable_subsets,
                "subset_win_rate": win_rate,
                "per_subset_comparison": per_subset,
            }
        )
    return table


def _adversarial_verdict(table: list[dict[str, Any]]) -> str:
    """Return the lane verdict per the TASK-0352 freeze protocol.

    PARTIALLY_VALID — at least one candidate beats the strongest control
    by `PRIMARY_SURVIVAL_MARGIN_MEV` on the primary `full_known` subset AND
    wins more than half of the subsets;
    INCONCLUSIVE — at least one candidate survives the primary subset but
    does not dominate the subset win-rate, OR the candidates win subsets but
    not the primary by margin;
    FALSIFIED — no candidate beats the strongest control on the primary
    subset by the required margin AND no candidate dominates the subset
    win-rate.
    """

    if not table:
        return "INCONCLUSIVE"
    primary_survivors = [item for item in table if item["primary_survives_adversarial_controls"]]
    subset_dominators = [
        item
        for item in table
        if item["subset_win_rate"] is not None and item["subset_win_rate"] > 0.5
    ]
    if primary_survivors and subset_dominators:
        if any(
            survivor["candidate_id"] == dom["candidate_id"]
            for survivor in primary_survivors
            for dom in subset_dominators
        ):
            return "PARTIALLY_VALID"
    if primary_survivors or subset_dominators:
        return "INCONCLUSIVE"
    return "FALSIFIED"


def build_metrics() -> dict[str, Any]:
    variants = _build_adversarial_variants()
    items, baseline_metrics, high_error_threshold, index, audit_rows = (
        _evaluate_all_variants(variants)
    )
    candidate_items = [item for item in items if item["role"] == "executed_candidate"]
    isotope_transfer = lane._transfer_summary(  # noqa: SLF001
        rows=audit_rows,
        candidate_items=candidate_items,
        index=index,
        group_key="Z",
    )
    isotone_transfer = lane._transfer_summary(  # noqa: SLF001
        rows=audit_rows,
        candidate_items=candidate_items,
        index=index,
        group_key="N",
    )
    comparison_table = _candidate_vs_strongest_control_table(
        items,
        baseline_metrics=baseline_metrics,
    )
    verdict = _adversarial_verdict(comparison_table)
    best_primary = min(
        candidate_items,
        key=lambda item: (
            float("inf")
            if item["primary_delta_mae_mev"] is None
            else float(item["primary_delta_mae_mev"]),
            item["candidate_id"],
        ),
    )
    coefficients = full_known.load_frozen_baseline_coefficients()
    return {
        "agent_run_id": AGENT_RUN_ID,
        "task_id": TASK_ID,
        "predecessor_agent_run_id": lane.AGENT_RUN_ID,
        "predecessor_task_id": lane.TASK_ID,
        "campaign_profile_id": "nuclear-mass-surface",
        "lane": "nuclear_local_curvature_adversarial_controls_lane",
        "sandbox_only": True,
        "evidence_class": "retrospective_full_known_local_curvature_adversarial_sandbox",
        "live_external_fetch_allowed": False,
        "summary": {
            "executed_variant_count": len(items),
            "executed_candidate_count": sum(
                1 for item in items if item["role"] == "executed_candidate"
            ),
            "executed_control_count": sum(
                1 for item in items if item["role"].endswith("_control")
            ),
            "new_adversarial_control_count": 3,
            "primary_survival_margin_mev": PRIMARY_SURVIVAL_MARGIN_MEV,
            "lane_verdict": verdict,
            "best_primary_delta_candidate_id": best_primary["candidate_id"],
            "best_primary_delta_mae_mev": best_primary["primary_delta_mae_mev"],
            "high_error_percentile": HIGH_ERROR_PERCENTILE,
            "high_error_threshold_mev": high_error_threshold,
            "canonical_results_changed": False,
            "canonical_claims_changed": False,
            "prediction_registry_changed": False,
            "claim_promotion_allowed": False,
        },
        "frozen_baseline": {
            "result_id": "RESULT-0015",
            "model_id": "model_fitted_semi_empirical",
            "coefficients": {
                "volume": coefficients.volume,
                "surface": coefficients.surface,
                "coulomb": coefficients.coulomb,
                "asymmetry": coefficients.asymmetry,
                "pairing": coefficients.pairing,
            },
        },
        "baseline_metrics_by_subset": baseline_metrics,
        "variants": items,
        "candidate_vs_strongest_control": comparison_table,
        "isotope_chain_transfer": isotope_transfer,
        "isotone_chain_transfer": isotone_transfer,
        "tasks_referenced": {
            "predecessor_lane_task": lane.TASK_ID,
            "predecessor_lane_agent_run": lane.AGENT_RUN_ID,
            "no_leakage_freeze_protocol": "TASK-0352",
        },
        "datasets": {
            "training_residual_source": "data/nuclear_masses/nmd-0002-curated-measured-slice.yaml",
            "holdout_source": "data/nuclear_masses/post_ame2020_holdout.yaml",
        },
    }


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _format_delta_or_na(value: float | None, *, decimals: int = 6) -> str:
    if value is None:
        return "n/a"
    if value == 0.0:
        return f"+{0.0:.{decimals}f}"
    return f"{'+' if value > 0 else '-'}{abs(value):.{decimals}f}"


def render_report(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    new_control_ids = {
        "LOCAL-CONTROL-003",
        "LOCAL-CONTROL-004",
        "LOCAL-CONTROL-005",
    }
    lines: list[str] = []
    lines.append("# Nuclear local-curvature adversarial controls lane")
    lines.append("")
    lines.append(f"**Task:** `{metrics['task_id']}`  ")
    lines.append(f"**Agent run:** `{metrics['agent_run_id']}`  ")
    lines.append(
        f"**Predecessor:** `{metrics['predecessor_task_id']}` / "
        f"`{metrics['predecessor_agent_run_id']}`"
    )
    lines.append(f"**Lane verdict:** `{summary['lane_verdict']}`  ")
    lines.append(
        f"**Primary survival margin (MeV):** {summary['primary_survival_margin_mev']:.2f}"
    )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "This run uses only repository-pinned rows and writes no canonical "
        "results, prediction-registry entries, claims, or knowledge artifacts. "
        "It re-evaluates the TASK-0339 / AGENT-RUN-0026 local-curvature "
        "candidates against three new adversarial controls in addition to the "
        "two controls the predecessor lane already carried."
    )
    lines.append("")
    lines.append("## Variants Evaluated")
    lines.append("")
    lines.append("| Candidate / control | Role | Family |")
    lines.append("| --- | --- | --- |")
    for item in metrics["variants"]:
        marker = " **(new)**" if item["candidate_id"] in new_control_ids else ""
        lines.append(
            f"| `{item['candidate_id']}`{marker} | {item['role']} | {item['family']} |"
        )
    lines.append("")
    lines.append("## Per-Variant Subset Deltas (MeV)")
    lines.append("")
    lines.append(
        "| Candidate | Full-known | Holdout | Magic | Neutron-rich | High-error |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for item in metrics["variants"]:
        lines.append(
            "| `{cid}` | {fk} | {ho} | {mg} | {nr} | {he} |".format(
                cid=item["candidate_id"],
                fk=_format_delta_or_na(item["primary_delta_mae_mev"]),
                ho=_format_delta_or_na(item["holdout_delta_mae_mev"]),
                mg=_format_delta_or_na(item["magic_region_delta_mae_mev"]),
                nr=_format_delta_or_na(item["neutron_rich_delta_mae_mev"]),
                he=_format_delta_or_na(item["high_error_delta_mae_mev"]),
            )
        )
    lines.append("")
    lines.append("Negative deltas indicate lower MAE than the frozen semi-empirical baseline.")
    lines.append("")
    lines.append("## Candidate vs Strongest Control (Primary Subset)")
    lines.append("")
    lines.append(
        "| Candidate | Strongest control on full_known | Candidate Δ MAE | Strongest control Δ MAE | Margin (control − candidate) | Survives ≥ {margin:.2f} MeV? |".format(
            margin=summary["primary_survival_margin_mev"]
        )
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for comparison in metrics["candidate_vs_strongest_control"]:
        lines.append(
            "| `{cid}` | `{strongest}` | {cdelta} | {sdelta} | {margin} | {surv} |".format(
                cid=comparison["candidate_id"],
                strongest=comparison["primary_strongest_control_id"] or "n/a",
                cdelta=_format_delta_or_na(
                    next(
                        (
                            row["candidate_delta_mae_mev"]
                            for row in comparison["per_subset_comparison"]
                            if row["subset_id"] == "full_known"
                        ),
                        None,
                    )
                ),
                sdelta=_format_delta_or_na(
                    next(
                        (
                            row["strongest_control_delta_mae_mev"]
                            for row in comparison["per_subset_comparison"]
                            if row["subset_id"] == "full_known"
                        ),
                        None,
                    )
                ),
                margin=_format_delta_or_na(
                    comparison["primary_candidate_minus_strongest_control_mev"]
                ),
                surv="yes" if comparison["primary_survives_adversarial_controls"] else "**no**",
            )
        )
    lines.append("")
    lines.append("## Per-Candidate Subset Win-Rate vs Strongest Control")
    lines.append("")
    lines.append(
        "| Candidate | Subsets evaluated | Subsets won vs strongest control | Win rate |"
    )
    lines.append("| --- | ---: | ---: | ---: |")
    for comparison in metrics["candidate_vs_strongest_control"]:
        rate = comparison["subset_win_rate"]
        rate_text = "n/a" if rate is None else f"{rate:.3f}"
        lines.append(
            "| `{cid}` | {tot} | {won} | {rate} |".format(
                cid=comparison["candidate_id"],
                tot=comparison["subset_evaluated_count"],
                won=comparison["subset_wins_count"],
                rate=rate_text,
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if summary["lane_verdict"] == "PARTIALLY_VALID":
        lines.append(
            "- At least one candidate beats the strongest control on the primary "
            f"subset by at least `{summary['primary_survival_margin_mev']:.2f}` MeV "
            "AND wins more than half of the per-subset comparisons."
        )
        lines.append(
            "- The signal is preserved as sandbox evidence that survived "
            "adversarial controls. It does not authorize a claim, a prediction-"
            "registry entry, or a reveal."
        )
        lines.append(
            "- Recommendation: pass through the TASK-0352 no-leakage freeze "
            "protocol before any predictive implementation."
        )
    elif summary["lane_verdict"] == "INCONCLUSIVE":
        lines.append(
            "- At least one candidate beats the strongest control on the primary "
            "subset OR dominates the subset win-rate, but not both."
        )
        lines.append(
            "- The signal is preserved as sandbox diagnostic evidence that is "
            "neither cleanly falsified nor cleanly survived."
        )
        lines.append(
            "- Recommendation: do not promote to predictive use. Either run "
            "additional controls or treat the residual as a smoothing-or-leakage "
            "diagnostic per the TASK-0352 freeze protocol."
        )
    else:
        lines.append(
            "- No candidate beats the strongest control on the primary subset "
            f"by the required margin (`{summary['primary_survival_margin_mev']:.2f}` MeV) "
            "AND no candidate dominates the subset win-rate."
        )
        lines.append(
            "- The TASK-0339 / AGENT-RUN-0026 signal is preserved as an overfit "
            "or smoothing diagnostic, not predictive evidence."
        )
        lines.append(
            "- Recommendation: do not register any local-curvature candidate to "
            "the prediction registry. The TASK-0352 freeze protocol applies; "
            "future predictive lanes must use leave-one-out features and pass "
            "all six minimum controls."
        )
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.extend(
        [
            "- Features still use committed full-known neighbor residual context "
            "and are retrospective diagnostics, not blind predictions.",
            "- Coefficients are fit on the 11-row NMD-0002 residual slice; "
            "small-sample fit variance limits the precision of the survival "
            f"margin check (set to {summary['primary_survival_margin_mev']:.2f} MeV).",
            "- The label-shuffle control uses a deterministic Z permutation; "
            "different permutation schemes may produce stronger or weaker "
            "controls.",
            "- The chain-blind smoother uses a simple 1-D linear regression over "
            "the A-window; richer smoothers (e.g. local quadratic, "
            "loess-style) are not exercised in this lane.",
            "- No live source fetch, reveal scoring, registry write, claim "
            "update, or canonical result write is authorized.",
        ]
    )
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"`{summary['lane_verdict']}`")
    lines.append("")
    return "\n".join(lines)


def render_review(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    lines: list[str] = []
    lines.append("# Nuclear local-curvature adversarial controls review")
    lines.append("")
    lines.append(f"**Task:** `{metrics['task_id']}`  ")
    lines.append(f"**Agent run:** `{metrics['agent_run_id']}`  ")
    lines.append(
        f"**Predecessor:** `{metrics['predecessor_task_id']}` / "
        f"`{metrics['predecessor_agent_run_id']}` "
        "(TASK-0339 sandbox local-curvature lane)"
    )
    lines.append("**Freeze protocol:** `TASK-0352` (no-leakage freeze contract)")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "This review records the outcome of attacking the TASK-0339 local-"
        "curvature sandbox signal with three new adversarial controls in "
        "addition to the two controls the predecessor lane already carried. "
        "It does not promote any claim, does not register a prediction entry, "
        "and does not authorize a reveal."
    )
    lines.append("")
    lines.append("## Adversarial Controls Added")
    lines.append("")
    lines.append(
        "- **LOCAL-CONTROL-003** — neighbor-availability leakage control. "
        "Uses only the single closest same-Z neighbor (by `|ΔN|`). A genuine "
        "local-curvature signal should still beat the baseline. A signal that "
        "depends on neighbor density rather than neighbor content will weaken "
        "under this control."
    )
    lines.append(
        "- **LOCAL-CONTROL-004** — chain-label shuffle control. Computes the "
        "isotope-neighbor mean using a deterministically permuted Z label (each "
        "Z mapped to a Z roughly half the observed-Z list away). If the signal "
        "is driven by real chain-local curvature, this control should not beat "
        "the baseline at all."
    )
    lines.append(
        "- **LOCAL-CONTROL-005** — chain-blind smooth local-regression control. "
        "Fits a 1-D linear regression over the same A-window the LOCAL-CONTROL-002 "
        "smoother uses and predicts at the target row's A. If the candidates beat "
        "this smoother by a meaningful margin, they carry chain-specific "
        "information beyond generic smoothness."
    )
    lines.append("")
    lines.append("## Headline Result")
    lines.append("")
    lines.append(
        f"- **Lane verdict:** `{summary['lane_verdict']}`."
    )
    lines.append(
        f"- **Primary survival margin (MeV):** "
        f"{summary['primary_survival_margin_mev']:.2f} on the `full_known` subset."
    )
    lines.append(
        f"- **Best primary candidate (predecessor metric):** "
        f"`{summary['best_primary_delta_candidate_id']}` with delta MAE "
        f"{_format_delta_or_na(summary['best_primary_delta_mae_mev'])} MeV."
    )
    lines.append("")
    lines.append("## Candidate vs Strongest Control (Primary Subset)")
    lines.append("")
    lines.append(
        "| Candidate | Strongest control on `full_known` | Margin (control − candidate) | Survives? |"
    )
    lines.append("| --- | --- | ---: | ---: |")
    for comparison in metrics["candidate_vs_strongest_control"]:
        lines.append(
            "| `{cid}` | `{strongest}` | {margin} | {surv} |".format(
                cid=comparison["candidate_id"],
                strongest=comparison["primary_strongest_control_id"] or "n/a",
                margin=_format_delta_or_na(
                    comparison["primary_candidate_minus_strongest_control_mev"]
                ),
                surv="yes" if comparison["primary_survives_adversarial_controls"] else "**no**",
            )
        )
    lines.append("")
    lines.append("## Decision Per TASK-0352 Freeze Protocol")
    lines.append("")
    if summary["lane_verdict"] == "FALSIFIED":
        lines.append(
            "The signal does not survive adversarial controls. The TASK-0339 "
            "headline metrics are preserved as a smoothing-or-leakage "
            "diagnostic, not predictive evidence. No future predictive "
            "local-curvature implementation task should attempt to register a "
            "prediction-registry entry based on the LOCAL-CURVATURE-001/002/003 "
            "features alone."
        )
        lines.append("")
        lines.append(
            "The TASK-0352 no-leakage freeze protocol still applies for any "
            "future feature shape that uses neighbor-derived inputs; this "
            "review does not relax the protocol."
        )
    elif summary["lane_verdict"] == "INCONCLUSIVE":
        lines.append(
            "The signal is mixed: at least one candidate clears one of the two "
            "survival criteria but not both. The lane is preserved as sandbox "
            "diagnostic evidence and does not authorize a predictive "
            "implementation task."
        )
        lines.append("")
        lines.append(
            "The TASK-0352 freeze protocol must still gate any future "
            "predictive local-curvature implementation. Additional controls "
            "(e.g. higher-order chain shuffles, richer smoothers, or "
            "self-exclusion ablations) are recommended before the verdict is "
            "revisited."
        )
    else:
        lines.append(
            "At least one candidate beats the strongest control on the primary "
            "subset by the required margin AND wins more than half of the "
            "per-subset comparisons. The signal is preserved as sandbox "
            "evidence that survived adversarial controls."
        )
        lines.append("")
        lines.append(
            "A future predictive implementation task is allowed only after the "
            "TASK-0352 no-leakage freeze protocol's six minimum controls "
            "(self-exclusion ablation, chain-shuffled, smooth-window, near-null, "
            "per-fold cache audit, source-status separation) are also satisfied. "
            "This review does not by itself unblock the predictive lane."
        )
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.extend(
        [
            "- Features still use committed full-known neighbor residual "
            "context. The headline numbers remain retrospective diagnostics, "
            "not blind predictions.",
            "- The survival margin "
            f"({summary['primary_survival_margin_mev']:.2f} MeV) is chosen "
            "conservatively from existing control magnitudes; tightening it "
            "is allowed in a future task but must be done before evaluating "
            "the next candidate.",
            "- The three new controls are not exhaustive. Stronger label "
            "shuffles, richer smoothers, and explicit leave-one-out feature "
            "shapes remain available for future adversarial work.",
        ]
    )
    lines.append("")
    lines.append("## What This Review Did Not Do")
    lines.append("")
    lines.extend(
        [
            "- It did not fetch live data, run reveal scoring, register a "
            "prediction-registry entry, edit a `PRED-*.yaml`, or promote a "
            "claim.",
            "- It did not rewrite the predecessor AGENT-RUN-0026 metrics or "
            "verdict.",
            "- It did not relax the TASK-0352 no-leakage freeze protocol.",
        ]
    )
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"`{summary['lane_verdict']}`")
    lines.append("")
    return "\n".join(lines)


def render_preflight(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Preflight",
            "",
            f"Task: `{metrics['task_id']}`",
            f"Agent run: `{metrics['agent_run_id']}`",
            "",
            "| Check | Status | Notes |",
            "| --- | --- | --- |",
            "| task_scope | PASS | TASK-0351 requests an adversarial-controls lane against TASK-0339; this run produces only sandbox metrics. |",
            "| data_boundary | PASS | Only committed repository datasets and the predecessor lane helpers are used; no live external fetch. |",
            "| control_boundary | PASS | Two pre-existing controls plus three new adversarial controls (closest-neighbor-only, chain-label-shuffle, chain-blind smoother) are evaluated alongside the candidates. |",
            "| protocol_boundary | PASS | The TASK-0352 no-leakage freeze protocol is referenced in the lane verdict and review note; no relaxation is applied. |",
            "| no_promotion | PASS | No prediction-registry entry, no canonical result, no claim, no knowledge update is produced. |",
            "",
        ]
    )


def render_limitations(metrics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Limitations",
            "",
            f"Task: `{metrics['task_id']}`",
            f"Agent run: `{metrics['agent_run_id']}`",
            "",
            "- Features still use committed full-known neighbor residual context and are retrospective diagnostics, not blind predictions.",
            "- Coefficients are fit on the 11-row NMD-0002 residual slice; small-sample fit variance limits the precision of the survival-margin check.",
            "- The label-shuffle control uses a deterministic Z permutation; alternative permutation schemes may produce different control strengths.",
            "- The chain-blind smoother uses a simple 1-D linear regression over the A-window; richer smoothers (local quadratic, loess) are not exercised here.",
            "- No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.",
            "",
        ]
    )


def render_review_summary(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    return "\n".join(
        [
            "# Review Summary",
            "",
            f"Task: `{metrics['task_id']}`  ",
            f"Agent run: `{metrics['agent_run_id']}`  ",
            f"Lane verdict: `{summary['lane_verdict']}`",
            "",
            "- Re-evaluated the TASK-0339 candidates with two existing controls plus three new adversarial controls.",
            f"- Primary survival margin set to {summary['primary_survival_margin_mev']:.2f} MeV on the `full_known` subset.",
            f"- Best primary candidate: `{summary['best_primary_delta_candidate_id']}` with delta MAE {_format_delta_or_na(summary['best_primary_delta_mae_mev'])} MeV.",
            f"- Verdict: `{summary['lane_verdict']}` per the TASK-0352 freeze protocol.",
            "",
            "Sandbox-only retrospective evidence. No canonical result, claim, knowledge entry, or prediction registry entry was changed.",
            "",
        ]
    )


def _map_lane_verdict_to_agent_run_verdict(lane_verdict: str) -> str:
    """Map the lane-specific verdict vocabulary onto the agent_run schema enum.

    The agent_run schema enforces an enum (SANDBOX_PASS, SANDBOX_FAIL,
    FALSIFIED, INCONCLUSIVE, OVERFITTED, ...) for the top-level ``verdict``
    field, but TASK-0351's lane decision vocabulary uses PARTIALLY_VALID for
    the "signal survives adversarial controls" outcome. This mapping keeps
    the lane-vocabulary in metrics.json while writing a schema-compliant
    verdict into agent_run.yaml.
    """

    mapping = {
        "PARTIALLY_VALID": "SANDBOX_PASS",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "FALSIFIED": "FALSIFIED",
    }
    return mapping.get(lane_verdict, "INCONCLUSIVE")


def render_agent_run_yaml(metrics: dict[str, Any]) -> str:
    summary = metrics["summary"]
    payload = {
        "id": metrics["agent_run_id"],
        "campaign_profile_id": metrics["campaign_profile_id"],
        "task_id": metrics["task_id"],
        "status": "SANDBOX_COMPLETE",
        "sandbox_only": True,
        "created_by": {
            "contributor_id": "roman",
            "agent_id": "claude",
        },
        "proposal_paths": {
            "hypothesis": "hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0043-midmass-isotope-gap-scout-batch.yaml",
            "experiment": "experiment_proposals/nuclear-mass/EXP-PROPOSAL-0009-nuclear-midmass-isotope-gap-scout.yaml",
        },
        "artifacts": {
            "metrics": f"agent_runs/{metrics['agent_run_id']}/metrics.json",
            "report": f"agent_runs/{metrics['agent_run_id']}/report.md",
            "limitations": f"agent_runs/{metrics['agent_run_id']}/limitations.md",
            "preflight": f"agent_runs/{metrics['agent_run_id']}/preflight.md",
            "review_summary": f"agent_runs/{metrics['agent_run_id']}/review_summary.md",
        },
        "preflight": {
            "passed": True,
            "checks": [
                {
                    "name": "task_scope",
                    "status": "PASS",
                    "notes": "TASK-0351 requests an adversarial-controls lane against TASK-0339; this run produces only sandbox metrics.",
                },
                {
                    "name": "data_boundary",
                    "status": "PASS",
                    "notes": "Only committed repository datasets and the predecessor lane helpers are used; no live external fetch.",
                },
                {
                    "name": "control_boundary",
                    "status": "PASS",
                    "notes": "Three new adversarial controls plus two existing controls are evaluated alongside the candidates.",
                },
                {
                    "name": "promotion_boundary",
                    "status": "PASS",
                    "notes": "No prediction registry, canonical result, claim, or knowledge file is written. The TASK-0352 no-leakage freeze protocol is referenced and not relaxed.",
                },
            ],
        },
        "limitations": [
            "Features still use committed full-known neighbor residual context.",
            "Coefficients are fit on the 11-row NMD-0002 residual slice.",
            "The label-shuffle control uses a deterministic Z permutation; alternative permutations may differ.",
            "The chain-blind smoother uses a simple 1-D linear regression; richer smoothers are not exercised here.",
            "No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.",
        ],
        "verdict": _map_lane_verdict_to_agent_run_verdict(summary["lane_verdict"]),
        "promotion_boundary": {
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "required_next_step": (
                "Maintainer review before any predictive local-curvature "
                "follow-up. The TASK-0352 no-leakage freeze protocol still "
                "gates any candidate that would write a PRED-*.yaml entry."
            ),
        },
    }
    # copy is kept imported for backwards compatibility with downstream
    # consumers that re-use this rendering helper; reference it explicitly
    # so the import is not stripped by lint.
    _ = copy
    return yaml.safe_dump(payload, sort_keys=False)


def write_outputs(
    metrics: dict[str, Any],
    *,
    metrics_path: Path,
    report_path: Path,
    agent_run_path: Path,
    limitations_path: Path,
    preflight_path: Path,
    review_summary_path: Path,
    review_path: Path,
) -> None:
    for target in (
        metrics_path,
        report_path,
        agent_run_path,
        limitations_path,
        preflight_path,
        review_summary_path,
        review_path,
    ):
        target.parent.mkdir(parents=True, exist_ok=True)

    metrics_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_report(metrics), encoding="utf-8")
    agent_run_path.write_text(render_agent_run_yaml(metrics), encoding="utf-8")
    limitations_path.write_text(render_limitations(metrics), encoding="utf-8")
    preflight_path.write_text(render_preflight(metrics), encoding="utf-8")
    review_summary_path.write_text(render_review_summary(metrics), encoding="utf-8")
    review_path.write_text(render_review(metrics), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--agent-run", type=Path, default=DEFAULT_AGENT_RUN_PATH)
    parser.add_argument("--limitations", type=Path, default=DEFAULT_LIMITATIONS_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument(
        "--review-summary", type=Path, default=DEFAULT_REVIEW_SUMMARY_PATH
    )
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    args = parser.parse_args(argv)

    metrics = build_metrics()
    write_outputs(
        metrics,
        metrics_path=args.out,
        report_path=args.report,
        agent_run_path=args.agent_run,
        limitations_path=args.limitations,
        preflight_path=args.preflight,
        review_summary_path=args.review_summary,
        review_path=args.review,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
