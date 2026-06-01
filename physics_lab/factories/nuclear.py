"""Nuclear residual-law factory adapter (TASK-0506).

The first campaign adapter for the shared Research Factory core. It loads a
committed nuclear-mass slice, fits a frozen semi-empirical baseline, generates
bounded residual-correction candidates from approved feature families, applies
null and shuffled controls, and routes each candidate — without creating any
canonical artifact. See docs/nuclear-residual-factory-sprint-protocol.md.

This is a bounded smoke adapter, not the full 50-100 candidate sprint (TASK-0507).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    evaluate_baseline,
    fit_semi_empirical_coefficients,
    pairing_sign,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.factories.core import Candidate, FactoryRun, FactorySpec, register_adapter

# Feature families this adapter can evaluate as structural (no target leakage).
SUPPORTED_FAMILIES = ("shell_distance", "odd_even_pairing")
# Families that require an explicit leakage check before they may be executed.
LEAKAGE_SENSITIVE_FAMILIES = (
    "residual_free_local_topology",
    "separation_energy_derived",
    "local_curvature",
)
MIN_HOLDOUT_ROWS = 3
SHORTLIST_MIN_REDUCTION = 0.05


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _feature(family: str, z: int, n: int) -> float:
    if family == "shell_distance":
        return float(min(_nearest_magic_distance(z), _nearest_magic_distance(n)))
    if family == "odd_even_pairing":
        return float(pairing_sign(z, n))
    raise ValueError(f"Unsupported structural family: {family}")


def _rms(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(values))))


def _fit_coefficient(feature: np.ndarray, residual: np.ndarray) -> float:
    denom = float(np.sum(np.square(feature)))
    if denom == 0.0:
        return 0.0
    return float(np.sum(feature * residual) / denom)


class NuclearResidualFactoryAdapter:
    """Bounded residual-law adapter over a committed nuclear-mass slice."""

    adapter_id = "nuclear_residual_factory"
    adapter_version = "0.1"

    def build_run(self, spec: FactorySpec) -> FactoryRun:
        snapshot_ref = str(spec.dataset["snapshot_ref"])
        dataset = load_nuclear_mass_dataset(Path(snapshot_ref))
        entries = list(dataset.entries)

        coefficients = fit_semi_empirical_coefficients(entries)
        baseline_rows = evaluate_baseline(
            entries=entries,
            model_id=str(spec.baseline.get("baseline_id", "nuclear-semi-empirical-fit")),
            coefficients=coefficients,
        )
        # Deterministic order; residual + (Z, N) per nuclide.
        rows = sorted(baseline_rows, key=lambda r: (r.A, r.Z, r.N, r.nuclide_id))
        residual = np.asarray([r.residual_mev for r in rows], dtype=float)
        z_values = [r.Z for r in rows]
        n_values = [r.N for r in rows]

        # Deterministic train/holdout split: ~70% train by sorted order.
        split = max(1, int(round(0.7 * len(rows))))
        train_idx = list(range(split))
        holdout_idx = list(range(split, len(rows)))

        leakage_checked = bool(spec.options.get("leakage_check_applied", False))
        candidates: list[Candidate] = []
        for family in spec.families:
            if len(candidates) >= spec.candidate_cap:
                break
            if family in LEAKAGE_SENSITIVE_FAMILIES and not leakage_checked:
                candidates.append(
                    Candidate(
                        candidate_id=f"CAND-{len(candidates) + 1:04d}",
                        family=family,
                        complexity=1.0,
                        leakage_status="NOT_CHECKED",
                        candidate_state="PREFLIGHT_REJECTED",
                        route_verdict="DATA_QUALITY_BLOCKED",
                        parameters={"form": "linear"},
                        control_outcomes=(
                            {"name": "leakage_guard", "outcome": "blocked: no leakage check applied"},
                        ),
                    )
                )
                continue
            if family not in SUPPORTED_FAMILIES:
                continue

            feature = np.asarray([_feature(family, z, n) for z, n in zip(z_values, n_values)], dtype=float)
            f_train, r_train = feature[train_idx], residual[train_idx]
            f_holdout, r_holdout = feature[holdout_idx], residual[holdout_idx]

            coef = _fit_coefficient(f_train, r_train)
            baseline_rms = _rms(r_holdout)
            candidate_rms = _rms(r_holdout - coef * f_holdout)
            reduction = 0.0 if baseline_rms == 0 else (baseline_rms - candidate_rms) / baseline_rms

            # Shuffled-feature control: destroy the feature->residual pairing on train.
            coef_shuf = _fit_coefficient(f_train[::-1], r_train)
            shuf_rms = _rms(r_holdout - coef_shuf * f_holdout[::-1])
            shuf_reduction = 0.0 if baseline_rms == 0 else (baseline_rms - shuf_rms) / baseline_rms

            state, verdict, control_beaten = self._route(reduction, shuf_reduction, len(holdout_idx))
            candidates.append(
                Candidate(
                    candidate_id=f"CAND-{len(candidates) + 1:04d}",
                    family=family,
                    complexity=1.0,
                    leakage_status="CHECKED_CLEAN",
                    candidate_state=state,
                    route_verdict=verdict,
                    parameters={"form": "linear", "coefficient": round(coef, 6)},
                    metrics={
                        "holdout_baseline_rms_mev": round(baseline_rms, 6),
                        "holdout_candidate_rms_mev": round(candidate_rms, 6),
                        "holdout_reduction": round(reduction, 6),
                        "shuffled_reduction": round(shuf_reduction, 6),
                    },
                    control_outcomes=(
                        {"name": "null_baseline", "outcome": f"holdout baseline rms {baseline_rms:.4f} MeV"},
                        {"name": "shuffled_feature", "outcome": "beaten" if control_beaten else "passed"},
                    ),
                )
            )

        dataset_block = {
            "snapshot_ref": snapshot_ref,
            "retrieval_policy": str(spec.dataset.get("retrieval_policy", "no_live_fetch")),
            "checksum_policy": str(spec.dataset.get("checksum_policy", "recorded in source manifest")),
        }
        baseline_block = {
            "baseline_id": str(spec.baseline.get("baseline_id", "nuclear-semi-empirical-fit")),
            "baseline_type": str(spec.baseline.get("baseline_type", "frozen")),
        }
        controls = (
            {"name": "null_baseline", "outcome": "applied"},
            {"name": "shuffled_feature", "outcome": "applied"},
        )
        campaign_specific = {
            "magic_numbers": list(MAGIC_NUMBERS),
            "train_count": len(train_idx),
            "holdout_count": len(holdout_idx),
            "baseline_model_id": baseline_block["baseline_id"],
        }
        return FactoryRun(
            dataset=dataset_block,
            baseline=baseline_block,
            controls=controls,
            candidates=tuple(candidates),
            campaign_specific=campaign_specific,
        )

    @staticmethod
    def _route(reduction: float, shuf_reduction: float, holdout_rows: int) -> tuple[str, str, bool]:
        if holdout_rows < MIN_HOLDOUT_ROWS:
            return "EXECUTED", "DATA_QUALITY_BLOCKED", False
        if reduction <= 0.0:
            return "EXECUTED", "NEGATIVE_RESULT", False
        if shuf_reduction >= 0.5 * reduction:
            return "REJECTED_BY_CONTROL", "REJECTED_BY_CONTROL", True
        if reduction < SHORTLIST_MIN_REDUCTION:
            return "EXECUTED", "INCONCLUSIVE", False
        return "SHORTLISTED", "SHORTLIST_CANDIDATE", False


register_adapter(NuclearResidualFactoryAdapter())
