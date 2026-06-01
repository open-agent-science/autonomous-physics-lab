"""Nuclear residual-law factory adapter (TASK-0506, sprint grid TASK-0507).

The first campaign adapter for the shared Research Factory core. It loads a
committed nuclear-mass slice, reads frozen semi-empirical baseline coefficients
from a committed RESULT artifact (no refit), generates bounded residual-correction
candidates from approved structural feature families, applies null / shuffled /
matched-random controls with a complexity penalty, and routes each candidate —
without creating any canonical artifact. See
docs/nuclear-residual-factory-sprint-protocol.md.

Two candidate grids:
- ``smoke`` (default): one linear candidate per family (TASK-0506 smoke).
- ``sweep``: a bounded power/scale/mask grid for the first real sprint (TASK-0507).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    pairing_sign,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset
from physics_lab.factories.core import Candidate, FactoryRun, FactorySpec, register_adapter

# Structural feature families this adapter can evaluate (no target leakage).
SUPPORTED_FAMILIES = (
    "shell_distance",
    "odd_even_pairing",
    "valence_z",
    "valence_n",
    "asymmetry",
)
# Families that can carry a per-row magic-proximity mask variant.
MASKABLE_FAMILIES = ("shell_distance", "valence_z", "valence_n")
# Families that require a dedicated no-leakage implementation before executing.
LEAKAGE_SENSITIVE_FAMILIES = (
    "residual_free_local_topology",
    "separation_energy_derived",
    "local_curvature",
)
MIN_HOLDOUT_ROWS = 3
# A holdout this small cannot support a shortlist; would-be shortlists route to
# INCONCLUSIVE (underpowered) so a tiny slice never produces a false positive.
MIN_SHORTLIST_HOLDOUT_ROWS = 8
SHORTLIST_MIN_REDUCTION = 0.05
COMPLEXITY_PENALTY_PER_PARAM = 0.02
COEFFICIENT_KEYS = ("volume", "surface", "coulomb", "asymmetry", "pairing")

SWEEP_POWERS = (1, 2, 3)
SWEEP_SCALE_EXPS = (0.0, 1.0 / 3.0, 2.0 / 3.0)


@dataclass(frozen=True)
class _Variant:
    family: str
    power: int
    scale_exp: float
    mask: str  # "all" or "near_magic"

    @property
    def complexity(self) -> float:
        extra = (self.power - 1) + (1 if self.scale_exp > 0 else 0) + (1 if self.mask != "all" else 0)
        return float(1 + extra)

    @property
    def params(self) -> dict[str, object]:
        return {
            "form": "linear_transformed_feature",
            "power": self.power,
            "scale_exp": round(self.scale_exp, 4),
            "mask": self.mask,
        }


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _base_feature(family: str, z: int, n: int) -> float:
    if family == "shell_distance":
        return float(min(_nearest_magic_distance(z), _nearest_magic_distance(n)))
    if family == "valence_z":
        return float(_nearest_magic_distance(z))
    if family == "valence_n":
        return float(_nearest_magic_distance(n))
    if family == "odd_even_pairing":
        return float(pairing_sign(z, n))
    if family == "asymmetry":
        return float(n - z)
    raise ValueError(f"Unsupported structural family: {family}")


def _near_magic_mask(z: int, n: int) -> float:
    return 1.0 if min(_nearest_magic_distance(z), _nearest_magic_distance(n)) <= 2 else 0.0


def _rms(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(values))))


def _fit_coefficient(feature: np.ndarray, residual: np.ndarray) -> float:
    denom = float(np.sum(np.square(feature)))
    if denom == 0.0:
        return 0.0
    return float(np.sum(feature * residual) / denom)


def _reduction(baseline_rms: float, candidate_rms: float) -> float:
    return 0.0 if baseline_rms == 0 else (baseline_rms - candidate_rms) / baseline_rms


def _coefficients_from_mapping(payload: dict[str, object]) -> SemiEmpiricalCoefficients:
    missing = [key for key in COEFFICIENT_KEYS if key not in payload]
    if missing:
        raise ValueError(f"Frozen baseline coefficients missing keys: {', '.join(missing)}")
    return SemiEmpiricalCoefficients(
        volume=float(payload["volume"]),
        surface=float(payload["surface"]),
        coulomb=float(payload["coulomb"]),
        asymmetry=float(payload["asymmetry"]),
        pairing=float(payload["pairing"]),
    )


def _load_frozen_coefficients(baseline: dict[str, object]) -> SemiEmpiricalCoefficients:
    if "coefficients" in baseline:
        coefficients = baseline["coefficients"]
        if not isinstance(coefficients, dict):
            raise ValueError("baseline.coefficients must be a mapping")
        return _coefficients_from_mapping(coefficients)

    coefficients_ref = baseline.get("coefficients_ref")
    if not coefficients_ref:
        raise ValueError(
            "Nuclear factory requires frozen baseline coefficients via "
            "baseline.coefficients or baseline.coefficients_ref; no baseline refit is allowed."
        )

    path = Path(str(coefficients_ref))
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    scores = payload.get("scores", [])
    wanted_model = str(baseline.get("coefficients_model_id", "model_fitted_semi_empirical"))
    for score in scores:
        if isinstance(score, dict) and score.get("model_id") == wanted_model:
            coefficients = score.get("coefficients")
            if not isinstance(coefficients, dict):
                raise ValueError(f"Model {wanted_model!r} has no coefficient mapping")
            return _coefficients_from_mapping(coefficients)

    raise ValueError(f"Frozen baseline coefficient model {wanted_model!r} not found in {path}")


def _variants_for_family(family: str, grid: str) -> list[_Variant]:
    if grid == "smoke":
        return [_Variant(family=family, power=1, scale_exp=0.0, mask="all")]
    masks = ("all", "near_magic") if family in MASKABLE_FAMILIES else ("all",)
    variants: list[_Variant] = []
    for power in SWEEP_POWERS:
        for scale_exp in SWEEP_SCALE_EXPS:
            for mask in masks:
                variants.append(_Variant(family=family, power=power, scale_exp=scale_exp, mask=mask))
    return variants


class NuclearResidualFactoryAdapter:
    """Bounded residual-law adapter over a committed nuclear-mass slice."""

    adapter_id = "nuclear_residual_factory"
    adapter_version = "0.2"

    def build_run(self, spec: FactorySpec) -> FactoryRun:
        snapshot_ref = str(spec.dataset["snapshot_ref"])
        dataset = load_nuclear_mass_dataset(Path(snapshot_ref))
        entries = list(dataset.entries)

        coefficients = _load_frozen_coefficients(spec.baseline)
        baseline_rows = evaluate_baseline(
            entries=entries,
            model_id=str(spec.baseline.get("baseline_id", "nuclear-semi-empirical-fit")),
            coefficients=coefficients,
        )
        rows = sorted(baseline_rows, key=lambda r: (r.A, r.Z, r.N, r.nuclide_id))
        residual = np.asarray([r.residual_mev for r in rows], dtype=float)
        a_values = np.asarray([r.A for r in rows], dtype=float)
        z_values = [r.Z for r in rows]
        n_values = [r.N for r in rows]

        split = max(1, int(round(0.7 * len(rows))))
        train_idx = list(range(split))
        holdout_idx = list(range(split, len(rows)))
        grid = str(spec.options.get("candidate_grid", "smoke"))

        # Deterministic matched-random target permutation (random-slice control).
        rng = np.random.default_rng(0)
        random_residual = residual.copy()
        rng.shuffle(random_residual)

        candidates: list[Candidate] = []
        for family in spec.families:
            if len(candidates) >= spec.candidate_cap:
                break
            if family in LEAKAGE_SENSITIVE_FAMILIES:
                candidates.append(self._blocked_leakage_candidate(len(candidates) + 1, family))
                continue
            if family not in SUPPORTED_FAMILIES:
                continue

            base = np.asarray(
                [_base_feature(family, z, n) for z, n in zip(z_values, n_values)], dtype=float
            )
            mask_vec = np.asarray(
                [_near_magic_mask(z, n) for z, n in zip(z_values, n_values)], dtype=float
            )
            for variant in _variants_for_family(family, grid):
                if len(candidates) >= spec.candidate_cap:
                    break
                feature = np.power(base, variant.power) / np.power(a_values, variant.scale_exp)
                if variant.mask == "near_magic":
                    feature = feature * mask_vec
                candidates.append(
                    self._evaluate_candidate(
                        index=len(candidates) + 1,
                        variant=variant,
                        feature=feature,
                        residual=residual,
                        random_residual=random_residual,
                        train_idx=train_idx,
                        holdout_idx=holdout_idx,
                    )
                )

        return FactoryRun(
            dataset={
                "snapshot_ref": snapshot_ref,
                "retrieval_policy": str(spec.dataset.get("retrieval_policy", "no_live_fetch")),
                "checksum_policy": str(spec.dataset.get("checksum_policy", "recorded in source manifest")),
            },
            baseline={
                "baseline_id": str(spec.baseline.get("baseline_id", "nuclear-semi-empirical-fit")),
                "baseline_type": str(spec.baseline.get("baseline_type", "frozen")),
            },
            controls=(
                {"name": "null_baseline", "outcome": "applied"},
                {"name": "shuffled_feature", "outcome": "applied"},
                {"name": "matched_random_slice", "outcome": "applied"},
                {"name": "complexity_penalty", "outcome": f"per_param {COMPLEXITY_PENALTY_PER_PARAM}"},
                {"name": "post_ame2020_check", "outcome": "not_applicable: slice has no time-split rows"},
            ),
            candidates=tuple(candidates),
            campaign_specific={
                "magic_numbers": list(MAGIC_NUMBERS),
                "candidate_grid": grid,
                "train_count": len(train_idx),
                "holdout_count": len(holdout_idx),
                "baseline_model_id": str(spec.baseline.get("baseline_id", "nuclear-semi-empirical-fit")),
                "baseline_coefficients_ref": str(spec.baseline.get("coefficients_ref", "inline")),
            },
        )

    @staticmethod
    def _blocked_leakage_candidate(index: int, family: str) -> Candidate:
        return Candidate(
            candidate_id=f"CAND-{index:04d}",
            family=family,
            complexity=1.0,
            leakage_status="NOT_CHECKED",
            candidate_state="PREFLIGHT_REJECTED",
            route_verdict="DATA_QUALITY_BLOCKED",
            parameters={"form": "linear"},
            control_outcomes=(
                {
                    "name": "leakage_guard",
                    "outcome": "blocked: family requires a dedicated no-leakage implementation",
                },
            ),
        )

    def _evaluate_candidate(
        self,
        *,
        index: int,
        variant: _Variant,
        feature: np.ndarray,
        residual: np.ndarray,
        random_residual: np.ndarray,
        train_idx: list[int],
        holdout_idx: list[int],
    ) -> Candidate:
        f_train, r_train = feature[train_idx], residual[train_idx]
        f_holdout, r_holdout = feature[holdout_idx], residual[holdout_idx]

        coef = _fit_coefficient(f_train, r_train)
        baseline_rms = _rms(r_holdout)
        candidate_rms = _rms(r_holdout - coef * f_holdout)
        reduction = _reduction(baseline_rms, candidate_rms)

        # Shuffled-feature control (destroy feature->residual pairing).
        coef_shuf = _fit_coefficient(f_train[::-1], r_train)
        shuf_reduction = _reduction(baseline_rms, _rms(r_holdout - coef_shuf * f_holdout[::-1]))

        # Matched-random-slice control (fit against a permuted target).
        coef_rand = _fit_coefficient(f_train, random_residual[train_idx])
        rand_reduction = _reduction(baseline_rms, _rms(r_holdout - coef_rand * f_holdout))

        effective = reduction - COMPLEXITY_PENALTY_PER_PARAM * variant.complexity
        state, verdict = self._route(
            reduction=reduction,
            effective=effective,
            shuf_reduction=shuf_reduction,
            rand_reduction=rand_reduction,
            holdout_rows=len(holdout_idx),
        )
        return Candidate(
            candidate_id=f"CAND-{index:04d}",
            family=variant.family,
            complexity=variant.complexity,
            leakage_status="CHECKED_CLEAN",
            candidate_state=state,
            route_verdict=verdict,
            parameters={**variant.params, "coefficient": round(coef, 6)},
            metrics={
                "holdout_baseline_rms_mev": round(baseline_rms, 6),
                "holdout_candidate_rms_mev": round(candidate_rms, 6),
                "holdout_reduction": round(reduction, 6),
                "effective_reduction": round(effective, 6),
                "shuffled_reduction": round(shuf_reduction, 6),
                "random_slice_reduction": round(rand_reduction, 6),
            },
            control_outcomes=(
                {"name": "null_baseline", "outcome": f"holdout baseline rms {baseline_rms:.4f} MeV"},
                {"name": "shuffled_feature", "outcome": f"reduction {shuf_reduction:.4f}"},
                {"name": "matched_random_slice", "outcome": f"reduction {rand_reduction:.4f}"},
            ),
        )

    @staticmethod
    def _route(
        *,
        reduction: float,
        effective: float,
        shuf_reduction: float,
        rand_reduction: float,
        holdout_rows: int,
    ) -> tuple[str, str]:
        if holdout_rows < MIN_HOLDOUT_ROWS:
            return "EXECUTED", "DATA_QUALITY_BLOCKED"
        if reduction <= 0.0 or effective <= 0.0:
            return "EXECUTED", "NEGATIVE_RESULT"
        if shuf_reduction >= 0.5 * reduction or rand_reduction >= 0.5 * reduction:
            return "REJECTED_BY_CONTROL", "REJECTED_BY_CONTROL"
        if effective < SHORTLIST_MIN_REDUCTION:
            return "EXECUTED", "INCONCLUSIVE"
        if holdout_rows < MIN_SHORTLIST_HOLDOUT_ROWS:
            # Survives controls but the holdout is too small to shortlist.
            return "EXECUTED", "INCONCLUSIVE"
        return "SHORTLISTED", "SHORTLIST_CANDIDATE"


register_adapter(NuclearResidualFactoryAdapter())
