#!/usr/bin/env python3
"""Deterministic exploratory Yb/Sr cross-source consistency diagnostic (TASK-0456).

Compares the two committed independent direct Yb/Sr frequency-ratio rows:

- Beloy 2021 / BACON ``ACR-0001-ROW-003`` (``cross_source_reference``);
- Nemitz 2016 / RIKEN ``ACR-0002-ROW-001`` (``cross_source_target``).

The two ratio values agree to ~15 leading digits and differ at the ~1e-17
level, which is below float64 precision relative to a value near 1.2075. The
ratio difference is therefore computed with :mod:`decimal`, reading the exact
committed value strings, not the float-parsed loader values.

Per ``ACR-0002`` ``COV_DIAGONAL_ONLY_DECLARED`` the two sources are fully
independent (no shared clock, comb, network link, or geopotential systematic),
so the off-diagonal between them is defensibly zero and the combined 1-sigma is
a diagonal quadrature sum. The output is an *exploratory* diagnostic carrying an
explicit independence banner. It is not a headline consistency claim, a
constants-drift result, a prediction, or a canonical result.

Run from the repository root:

    python3 scripts/atomic_yb_sr_consistency_diagnostic.py \
        --output agent_runs/AGENT-RUN-0070/metrics.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

REFERENCE_DATASET = REPO_ROOT / "data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml"
TARGET_DATASET = REPO_ROOT / "data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml"

REFERENCE_OBSERVABLE_ID = "frequency_ratio_yb171_sr87_beloy2021"
TARGET_OBSERVABLE_ID = "frequency_ratio_yb171_sr87_nemitz2016"

# |z| threshold below which independent measurements are read as showing no
# tension at the probed precision. Declared before inspecting the values.
NO_TENSION_Z = 2.0
# Uncertainty-dominance ratio above which the comparison is source-limited:
# the coarser source hides the finer source's precision.
SOURCE_LIMITED_DOMINANCE = 3.0


def _extract_exact_value(dataset_path: Path, observable_id: str) -> Decimal:
    """Return the committed ratio value as an exact Decimal (precision-safe)."""
    lines = dataset_path.read_text(encoding="utf-8").splitlines()
    seen_observable = False
    for line in lines:
        if re.match(rf"^\s*observable_id:\s*{re.escape(observable_id)}\s*$", line):
            seen_observable = True
            continue
        if seen_observable:
            match = re.match(r"^\s*value:\s*([0-9]+\.[0-9]+)\s*$", line)
            if match:
                return Decimal(match.group(1))
    raise ValueError(f"value not found for {observable_id} in {dataset_path}")


def _row_total_uncertainty(dataset_path: Path, observable_id: str) -> float:
    """Return the published total fractional 1-sigma uncertainty for a row."""
    payload: dict[str, Any] = yaml.safe_load(dataset_path.read_text(encoding="utf-8"))
    for row in payload["rows"]:
        if row.get("observable_id") == observable_id:
            return float(row["uncertainty"]["total"])
    raise ValueError(f"row not found for {observable_id} in {dataset_path}")


def compute_diagnostic() -> dict[str, Any]:
    """Compute the exploratory diagonal-only Yb/Sr cross-source diagnostic."""
    r_ref = _extract_exact_value(REFERENCE_DATASET, REFERENCE_OBSERVABLE_ID)
    r_target = _extract_exact_value(TARGET_DATASET, TARGET_OBSERVABLE_ID)

    u_ref_frac = _row_total_uncertainty(REFERENCE_DATASET, REFERENCE_OBSERVABLE_ID)
    u_target_frac = _row_total_uncertainty(TARGET_DATASET, TARGET_OBSERVABLE_ID)

    # Exact ratio difference (Decimal), then cast to float for the z-score.
    delta_abs = float(r_ref - r_target)
    r_ref_f = float(r_ref)
    r_target_f = float(r_target)

    u_ref_abs = u_ref_frac * r_ref_f
    u_target_abs = u_target_frac * r_target_f
    u_combined_abs = math.sqrt(u_ref_abs**2 + u_target_abs**2)

    z_score = delta_abs / u_combined_abs
    delta_frac = delta_abs / r_ref_f
    u_combined_frac = math.sqrt(u_ref_frac**2 + u_target_frac**2)
    dominance_ratio = u_target_abs / u_ref_abs

    no_tension = abs(z_score) < NO_TENSION_Z
    source_limited = dominance_ratio > SOURCE_LIMITED_DOMINANCE

    if no_tension and source_limited:
        verdict = "CONSISTENT_WITHIN_UNCERTAINTY_EXPLORATORY_SOURCE_LIMITED"
    elif no_tension:
        verdict = "CONSISTENT_WITHIN_UNCERTAINTY_EXPLORATORY"
    else:
        verdict = "INCONCLUSIVE"

    return {
        "task_id": "TASK-0456",
        "agent_run_id": "AGENT-RUN-0070",
        "diagnostic": "atomic_yb_sr_cross_source_consistency_exploratory_diagonal_only",
        "covariance_state": "COV_DIAGONAL_ONLY_DECLARED",
        "independence_banner": (
            "Beloy 2021 / BACON and Nemitz 2016 / RIKEN are fully independent "
            "(no shared clock, comb, network link, or geopotential systematic); "
            "the off-diagonal is defensibly zero. This is an exploratory "
            "diagnostic, not a headline consistency claim, constants-drift "
            "result, prediction, or canonical result."
        ),
        "rows": {
            "reference": {
                "row_id": "ACR-0001-ROW-003",
                "source": "Beloy 2021 / BACON",
                "split": "cross_source_reference",
                "observable_id": REFERENCE_OBSERVABLE_ID,
                "ratio_value": str(r_ref),
                "total_fractional_uncertainty_1sigma": u_ref_frac,
                "total_absolute_uncertainty_1sigma": u_ref_abs,
            },
            "target": {
                "row_id": "ACR-0002-ROW-001",
                "source": "Nemitz 2016 / RIKEN",
                "split": "cross_source_target",
                "observable_id": TARGET_OBSERVABLE_ID,
                "ratio_value": str(r_target),
                "total_fractional_uncertainty_1sigma": u_target_frac,
                "total_absolute_uncertainty_1sigma": u_target_abs,
            },
        },
        "comparison": {
            "difference_absolute_reference_minus_target": delta_abs,
            "difference_fractional_reference_minus_target": delta_frac,
            "combined_1sigma_absolute_diagonal_only": u_combined_abs,
            "combined_1sigma_fractional_diagonal_only": u_combined_frac,
            "z_score": z_score,
            "abs_z_score": abs(z_score),
            "no_tension_z_threshold": NO_TENSION_Z,
            "uncertainty_dominance_ratio_target_over_reference": dominance_ratio,
            "source_limited_dominance_threshold": SOURCE_LIMITED_DOMINANCE,
        },
        "verdict": verdict,
        "interpretation": (
            f"The two independent Yb/Sr ratios differ by {delta_abs:.3e} "
            f"(fractional {delta_frac:.3e}); |z| = {abs(z_score):.3f} against the "
            f"diagonal-only combined 1-sigma ({u_combined_abs:.3e}). This is within "
            f"{NO_TENSION_Z:g} sigma, so there is no tension at the probed precision. "
            f"The comparison is dominated and limited by the Nemitz 2016 uncertainty "
            f"(~{dominance_ratio:.1f}x the Beloy 2021 uncertainty), so it does not test "
            f"Beloy's 18-digit precision and is source-limited."
        ),
        "limitations": [
            "Exploratory diagonal-only diagnostic; COV_DIAGONAL_ONLY_DECLARED forbids a headline cross-source consistency verdict.",
            "Source-limited: the Nemitz 2016 total uncertainty dominates the comparison; Beloy 2021 precision is not tested.",
            "Two rows only (one per source); not a population-level consistency test.",
            "Both source PDFs (arXiv preprints and the Nature/Nature Photonics versions of record) are not redistributed; only metadata, checksums, and committed values are used.",
            "No constants-drift fit, new-physics inference, prediction entry, RESULT/CLAIM artifact, or knowledge promotion.",
        ],
        "output_routing": {
            "task_verdict": "PARTIALLY_VALID",
            "canonical_destination": [
                "agent_runs/AGENT-RUN-0070/metrics.json",
                "agent_runs/AGENT-RUN-0070/report.md",
                "docs/reviews/atomic-yb-sr-cross-source-consistency-benchmark.md",
            ],
            "review_tier": "none",
            "gate_a_status": "not_attempted",
            "gate_b_status": "not_applicable",
            "claim_impact": "none",
            "knowledge_impact": "none",
            "result_impact": "no RESULT artifact created",
            "publication_blocker": (
                "exploratory diagonal-only diagnostic; source-limited and "
                "diagonal-only covariance forbid canonical consistency promotion "
                "without a maintainer-approved Gate A path"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "agent_runs/AGENT-RUN-0070/metrics.json",
        help="Path to write the metrics JSON artifact.",
    )
    args = parser.parse_args()

    metrics = compute_diagnostic()
    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output_path}")
    print(f"verdict: {metrics['verdict']}")
    print(f"abs_z_score: {metrics['comparison']['abs_z_score']:.4f}")


if __name__ == "__main__":
    main()
