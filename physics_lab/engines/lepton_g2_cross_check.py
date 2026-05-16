"""Lepton g-2 cross-observable falsifier.

Compares electron g-2 against the electron analogs of the muon g-2 candidate
formulas surfaced in EXP-0010 (see ``physics_lab.engines.g2_formula_search``).

Scope
-----
This is a guarded cross-observable check, not a new formula-search campaign.
For each registered muon g-2 candidate, the engine builds an electron analog
by formal substitution ``m_mu -> m_e`` and compares the analog value to the
two α-source-dependent Δa_e residuals. Each candidate is reported as one of:

- ``null``: predicted |Δa_e| is below 0.5σ of both Cs and Rb residuals, so the
  cross-check cannot distinguish the candidate from "no effect at electron";
- ``inconsistent``: predicted Δa_e is > 3σ from both residuals;
- ``overfit``: predicted Δa_e is consistent (≤ 2σ) with one α-source and
  inconsistent (> 3σ) with the other, i.e. the cross-check only "works" by
  cherry-picking the α input;
- ``review_needed``: anything else (ambiguous or no clean electron analog).

The cross-check does not promote any candidate to an electron g-2 formula
and does not aggregate Cs and Rb residuals as if they shared an SM input.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from physics_lab.engines.g2_formula_search import (
    ALPHA,
    ALPHA_OVER_PI,
    MU_OVER_ME,
    MU_OVER_MPI0,
    MU_OVER_MTAU,
    DELTA_AMU,
)

# ── Electron-scale mass ratios derived from the muon-scale ratios ─────────────
# Substitution rule: every occurrence of ``m_mu`` in a muon-g-2 formula is
# replaced with ``m_e``. Mass ratios involving ``m_mu`` translate as follows.

ME_OVER_MTAU = MU_OVER_MTAU / MU_OVER_ME       # ≈ 2.876e-4
ME_OVER_MPI0 = MU_OVER_MPI0 / MU_OVER_ME       # ≈ 3.787e-3
ME_OVER_ME = 1.0                                # by definition, after swap


# ── Default electron g-2 data path ──────────────────────────────────────────
DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "particle_physics"
    / "electron_g2.yaml"
)


# ── Result dataclasses ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ElectronResidual:
    residual_id: str
    label: str
    delta_ae: float
    sigma: float
    alpha_source: str


@dataclass(frozen=True)
class CandidateCrossCheck:
    candidate_id: str
    muon_formula: str
    electron_analog_formula: str
    electron_value: float
    comparisons: list[dict[str, Any]]
    verdict: str   # null | inconsistent | overfit | review_needed
    notes: str


# ── Data loader ────────────────────────────────────────────────────────────

def load_electron_g2_data(path: Path | None = None) -> list[ElectronResidual]:
    """Load Δa_e residuals from the source-data YAML file."""
    data_path = Path(path) if path is not None else DEFAULT_DATA_PATH
    raw = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    residuals: list[ElectronResidual] = []
    for entry in raw.get("derived_residuals", []):
        residuals.append(
            ElectronResidual(
                residual_id=entry["id"],
                label=entry["label"],
                delta_ae=float(entry["value"]),
                sigma=float(entry["uncertainty"]["value"]),
                alpha_source=entry.get("sm_prediction", "unknown"),
            )
        )
    if not residuals:
        raise ValueError(f"No derived_residuals found in {data_path}")
    return residuals


# ── Candidate registry ─────────────────────────────────────────────────────
#
# The candidates here are the EXP-0010 muon-g-2 hits we want to cross-check.
# Each candidate records:
#   - muon_formula: the muon-side expression as printed in EXP-0010
#   - electron_formula: the human-readable electron analog after m_mu -> m_e
#   - electron_value_fn: callable returning the analog's predicted Δa_e
#   - notes: source within EXP-0010 and any caveats
#
# This list is intentionally small. Adding candidates is the job of a new
# maintainer-approved task, not of this falsifier.


def _f4_electron_analog() -> float:
    # Muon: α^3 × (m_mu/m_e)^-2 × (m_mu/m_tau)^-2
    # Electron analog: α^3 × (m_e/m_e)^-2 × (m_e/m_tau)^-2
    return ALPHA**3 * ME_OVER_ME**-2 * ME_OVER_MTAU**-2


def _f3_one_third_electron_analog() -> float:
    # Muon: (1/3) × (α/π)^3 × (m_mu/m_pi0)^2
    # Electron analog: (1/3) × (α/π)^3 × (m_e/m_pi0)^2
    return (1.0 / 3.0) * ALPHA_OVER_PI**3 * ME_OVER_MPI0**2


def _naive_mass_squared_scaling() -> float:
    # Δa_e / Δa_mu under naive same-mechanism (m_l/M)^2 scaling
    # equals (m_e/m_mu)^2 = MU_OVER_ME^-2.
    return DELTA_AMU * (MU_OVER_ME**-2)


CANDIDATES: list[dict[str, Any]] = [
    {
        "candidate_id": "F4_hit",
        "muon_formula": "α^3 × (m_mu/m_e)^-2 × (m_mu/m_tau)^-2",
        "electron_formula": "α^3 × (m_e/m_tau)^-2",
        "value_fn": _f4_electron_analog,
        "notes": (
            "EXP-0010 F4 guardrail-screened muon hit. After m_mu -> m_e the "
            "(m_mu/m_e)^-2 factor collapses to 1 and the (m_mu/m_tau)^-2 "
            "factor becomes (m_e/m_tau)^-2, which is much larger than 1."
        ),
    },
    {
        "candidate_id": "F3_one_third",
        "muon_formula": "(1/3) × (α/π)^3 × (m_mu/m_pi0)^2",
        "electron_formula": "(1/3) × (α/π)^3 × (m_e/m_pi0)^2",
        "value_fn": _f3_one_third_electron_analog,
        "notes": (
            "EXP-0010 F3 c=1/3 candidate. The hadronic-style form survives "
            "the m_mu -> m_e swap but produces a much smaller magnitude."
        ),
    },
    {
        "candidate_id": "naive_msq_scaling",
        "muon_formula": "Δa_mu (target)",
        "electron_formula": "Δa_mu × (m_e/m_mu)^2",
        "value_fn": _naive_mass_squared_scaling,
        "notes": (
            "Naive same-mechanism cross-lepton scaling baseline. Provided "
            "as a comparison anchor; not a model prediction."
        ),
    },
]


# ── Classification ─────────────────────────────────────────────────────────

NULL_SIGMA_THRESHOLD = 0.5
CONSISTENT_SIGMA_THRESHOLD = 2.0
INCONSISTENT_SIGMA_THRESHOLD = 3.0


def _z(predicted: float, residual: ElectronResidual) -> float:
    return abs(predicted - residual.delta_ae) / residual.sigma


def _classify(predicted: float, residuals: list[ElectronResidual]) -> str:
    """Classify a candidate prediction against the available Δa_e residuals.

    Verdicts:
      - ``null``: |predicted| / sigma < NULL_SIGMA_THRESHOLD for every residual.
        The candidate is too small for the current measurement to distinguish.
      - ``inconsistent``: every residual has z > INCONSISTENT_SIGMA_THRESHOLD.
      - ``overfit``: at least one residual has z <= CONSISTENT_SIGMA_THRESHOLD
        and at least one has z > INCONSISTENT_SIGMA_THRESHOLD.
      - ``review_needed``: anything else (mixed marginal results).
    """
    relative_magnitudes = [abs(predicted) / r.sigma for r in residuals]
    if all(rel < NULL_SIGMA_THRESHOLD for rel in relative_magnitudes):
        return "null"
    zs = [_z(predicted, r) for r in residuals]
    if all(z > INCONSISTENT_SIGMA_THRESHOLD for z in zs):
        return "inconsistent"
    has_consistent = any(z <= CONSISTENT_SIGMA_THRESHOLD for z in zs)
    has_inconsistent = any(z > INCONSISTENT_SIGMA_THRESHOLD for z in zs)
    if has_consistent and has_inconsistent:
        return "overfit"
    return "review_needed"


# ── Main entry point ──────────────────────────────────────────────────────

def run_cross_check(
    data_path: Path | None = None,
    candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run the lepton g-2 cross-observable falsifier.

    Returns a structured dict suitable for sandbox-only reporting. The output
    is intentionally not packaged as an EXP/RESULT artifact because this is a
    guarded falsification check rather than a new scientific result.
    """
    residuals = load_electron_g2_data(data_path)
    cand_list = candidates if candidates is not None else CANDIDATES

    cross_checks: list[CandidateCrossCheck] = []
    for cand in cand_list:
        value_fn: Callable[[], float] = cand["value_fn"]
        predicted = float(value_fn())
        comparisons = [
            {
                "residual_id": r.residual_id,
                "alpha_source_ref": r.alpha_source,
                "delta_ae_meas": r.delta_ae,
                "delta_ae_sigma": r.sigma,
                "z_score": _z(predicted, r),
                "relative_magnitude": abs(predicted) / r.sigma,
            }
            for r in residuals
        ]
        verdict = _classify(predicted, residuals)
        cross_checks.append(
            CandidateCrossCheck(
                candidate_id=cand["candidate_id"],
                muon_formula=cand["muon_formula"],
                electron_analog_formula=cand["electron_formula"],
                electron_value=predicted,
                comparisons=comparisons,
                verdict=verdict,
                notes=cand["notes"],
            )
        )

    verdict_counts: dict[str, int] = {}
    for cc in cross_checks:
        verdict_counts[cc.verdict] = verdict_counts.get(cc.verdict, 0) + 1

    # Global verdict: collapse the per-candidate findings into the most
    # conservative single label. The order below is intentionally pessimistic
    # so that mixed reports never round up to "null".
    if any(cc.verdict == "inconsistent" for cc in cross_checks):
        global_verdict = "INCONSISTENT_AT_ELECTRON"
    elif any(cc.verdict == "overfit" for cc in cross_checks):
        global_verdict = "OVERFIT_SUSPECT"
    elif any(cc.verdict == "review_needed" for cc in cross_checks):
        global_verdict = "REVIEW_NEEDED"
    elif all(cc.verdict == "null" for cc in cross_checks):
        global_verdict = "NULL"
    else:
        global_verdict = "REVIEW_NEEDED"

    return {
        "task_id": "TASK-0227",
        "scope": "cross-observable falsifier (sandbox-only)",
        "input_residuals": [
            {
                "residual_id": r.residual_id,
                "label": r.label,
                "delta_ae": r.delta_ae,
                "sigma": r.sigma,
                "alpha_source_ref": r.alpha_source,
            }
            for r in residuals
        ],
        "candidates": [
            {
                "candidate_id": cc.candidate_id,
                "muon_formula": cc.muon_formula,
                "electron_analog_formula": cc.electron_analog_formula,
                "electron_value": cc.electron_value,
                "comparisons": cc.comparisons,
                "verdict": cc.verdict,
                "notes": cc.notes,
            }
            for cc in cross_checks
        ],
        "verdict_counts": verdict_counts,
        "global_verdict": global_verdict,
        "guardrails": {
            "thresholds": {
                "null_sigma": NULL_SIGMA_THRESHOLD,
                "consistent_sigma": CONSISTENT_SIGMA_THRESHOLD,
                "inconsistent_sigma": INCONSISTENT_SIGMA_THRESHOLD,
            },
            "forbidden": [
                "do not present any candidate as an electron g-2 explanation",
                "do not aggregate Cs and Rb residuals as if they shared an SM input",
                "do not expand the candidate registry without a new maintainer-approved task",
            ],
        },
    }
