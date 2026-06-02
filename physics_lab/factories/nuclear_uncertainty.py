"""Uncertainty perturbation controls for Nuclear factory candidates (TASK-0518)."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from physics_lab.engines.nuclear_mass_baselines import (
    MAGIC_NUMBERS,
    SemiEmpiricalCoefficients,
    evaluate_baseline,
    pairing_sign,
)
from physics_lab.engines.nuclear_masses import load_nuclear_mass_dataset

COEFFICIENT_KEYS = ("volume", "surface", "coulomb", "asymmetry", "pairing")
COMPLEXITY_PENALTY_PER_PARAM = 0.02
MIN_HOLDOUT_ROWS = 3
MIN_SHORTLIST_HOLDOUT_ROWS = 8
SHORTLIST_MIN_REDUCTION = 0.05


def run_uncertainty_perturbation_control(
    *,
    dataset_path: Path,
    factory_summary_path: Path,
    baseline_result_path: Path,
    top_n: int = 5,
    trials: int = 200,
    seed: int = 518,
) -> dict[str, Any]:
    """Perturb NMD-0002 rows and evaluate top TASK-0507 candidates deterministically."""
    dataset = load_nuclear_mass_dataset(dataset_path)
    entries = sorted(dataset.entries, key=lambda e: (e.A, e.Z, e.N, e.nuclide_id))
    factory_summary = yaml.safe_load(factory_summary_path.read_text(encoding="utf-8")) or {}
    top_candidates = _top_candidates(factory_summary, top_n=top_n)
    coefficients = _load_frozen_coefficients(baseline_result_path)

    modes = (
        ("declared_uncertainty", 1.0),
        ("coarse_floor_stress_10x", 10.0),
    )
    mode_summaries = {}
    for mode_index, (mode_id, sigma_scale) in enumerate(modes):
        rng = np.random.default_rng(seed + mode_index)
        mode_summaries[mode_id] = _run_mode(
            entries=entries,
            candidates=top_candidates,
            coefficients=coefficients,
            trials=trials,
            sigma_scale=sigma_scale,
            rng=rng,
        )

    uncertainty_values = [
        e.atomic_mass_uncertainty_u for e in entries if e.atomic_mass_uncertainty_u is not None
    ]
    return {
        "task_id": "TASK-0518",
        "input_references": {
            "dataset": str(dataset_path),
            "factory_summary": str(factory_summary_path),
            "baseline_result": str(baseline_result_path),
        },
        "method": (
            "Perturb atomic masses by deterministic normal draws around each committed "
            "NMD-0002 value, recompute frozen-baseline residuals, refit each predeclared "
            "candidate coefficient on the deterministic train split, and re-route by "
            "effective holdout reduction after controls."
        ),
        "seed": seed,
        "trials_per_mode": trials,
        "top_candidate_ids": [c["candidate_id"] for c in top_candidates],
        "dataset_summary": {
            "dataset_id": dataset.dataset_id,
            "row_count": len(entries),
            "uncertainty_floor_u": min(uncertainty_values) if uncertainty_values else None,
            "max_declared_uncertainty_u": max(uncertainty_values) if uncertainty_values else None,
            "all_rows_share_same_uncertainty": len(set(uncertainty_values)) == 1,
            "source_grade_per_row_uncertainty_available": False,
            "uncertainty_note": (
                "NMD-0002 records a coarse curated uncertainty floor rather than "
                "source-grade per-row uncertainties; the 10x mode is a floor-stress "
                "control, not source evidence."
            ),
        },
        "mode_summaries": mode_summaries,
        "verdict": _overall_verdict(mode_summaries),
        "limitations": [
            "NMD-0002 has only 11 rows and a 3-row holdout; survival cannot promote a candidate.",
            "The slice uses a coarse curated uncertainty floor rather than source-grade row uncertainty.",
            "The frozen baseline coefficients are NMD-0002 slice-specific and are not refit.",
            "Sandbox control evidence only; no RESULT, PRED, CLAIM, or KNOW artifact is promoted.",
        ],
    }


def _run_mode(
    *,
    entries: list[Any],
    candidates: list[dict[str, Any]],
    coefficients: SemiEmpiricalCoefficients,
    trials: int,
    sigma_scale: float,
    rng: np.random.Generator,
) -> dict[str, Any]:
    per_candidate: dict[str, dict[str, Any]] = {
        c["candidate_id"]: {
            "family": c["family"],
            "original_route_verdict": c["route_verdict"],
            "original_effective_reduction": c["metrics"]["effective_reduction"],
            "effective_reductions": [],
            "holdout_reductions": [],
            "route_verdicts": [],
            "rank_positions": [],
        }
        for c in candidates
    }
    top1_counter: Counter[str] = Counter()

    for _ in range(trials):
        perturbed_entries = _perturb_entries(entries, sigma_scale=sigma_scale, rng=rng)
        trial_results = [_evaluate_candidate(perturbed_entries, coefficients, c) for c in candidates]
        ranked = sorted(
            trial_results,
            key=lambda item: item["metrics"]["effective_reduction"],
            reverse=True,
        )
        top1_counter[ranked[0]["candidate_id"]] += 1
        for rank, result in enumerate(ranked, start=1):
            bucket = per_candidate[result["candidate_id"]]
            metrics = result["metrics"]
            bucket["effective_reductions"].append(metrics["effective_reduction"])
            bucket["holdout_reductions"].append(metrics["holdout_reduction"])
            bucket["route_verdicts"].append(result["route_verdict"])
            bucket["rank_positions"].append(rank)

    summarized_candidates = []
    for candidate_id, payload in per_candidate.items():
        effective = np.asarray(payload.pop("effective_reductions"), dtype=float)
        holdout = np.asarray(payload.pop("holdout_reductions"), dtype=float)
        ranks = np.asarray(payload.pop("rank_positions"), dtype=float)
        route_counts = Counter(payload.pop("route_verdicts"))
        original = float(payload["original_effective_reduction"])
        summarized_candidates.append(
            {
                "candidate_id": candidate_id,
                **payload,
                "effective_reduction_mean": round(float(np.mean(effective)), 6),
                "effective_reduction_std": round(float(np.std(effective)), 6),
                "effective_reduction_min": round(float(np.min(effective)), 6),
                "effective_reduction_max": round(float(np.max(effective)), 6),
                "effective_reduction_drift_from_original": round(float(np.mean(effective) - original), 6),
                "holdout_reduction_mean": round(float(np.mean(holdout)), 6),
                "rank_median": round(float(np.median(ranks)), 3),
                "rank_min": int(np.min(ranks)),
                "rank_max": int(np.max(ranks)),
                "route_verdict_counts": dict(sorted(route_counts.items())),
            }
        )

    return {
        "sigma_scale": sigma_scale,
        "top1_counts": dict(sorted(top1_counter.items())),
        "candidate_stability": sorted(
            summarized_candidates,
            key=lambda item: item["effective_reduction_mean"],
            reverse=True,
        ),
    }


def _perturb_entries(entries: list[Any], *, sigma_scale: float, rng: np.random.Generator) -> list[Any]:
    perturbed = []
    for entry in entries:
        sigma = 0.0 if entry.atomic_mass_uncertainty_u is None else entry.atomic_mass_uncertainty_u
        delta_u = float(rng.normal(0.0, sigma * sigma_scale))
        atomic_mass_u = entry.atomic_mass_u + delta_u
        mass_excess_keV = (atomic_mass_u - float(entry.A)) * 931.49410242 * 1000.0
        perturbed.append(
            replace(
                entry,
                atomic_mass_u=atomic_mass_u,
                mass_excess_keV=mass_excess_keV,
            )
        )
    return perturbed


def _evaluate_candidate(
    entries: list[Any],
    coefficients: SemiEmpiricalCoefficients,
    candidate: dict[str, Any],
) -> dict[str, Any]:
    rows = evaluate_baseline(
        entries=entries,
        model_id="nuclear-semi-empirical-fit",
        coefficients=coefficients,
    )
    residual = np.asarray([r.residual_mev for r in rows], dtype=float)
    feature = np.asarray(
        [
            _candidate_feature(candidate, z=row.Z, n=row.N, a=row.A)
            for row in rows
        ],
        dtype=float,
    )
    split = max(1, int(round(0.7 * len(rows))))
    train_idx = list(range(split))
    holdout_idx = list(range(split, len(rows)))
    rng = np.random.default_rng(0)
    random_residual = residual.copy()
    rng.shuffle(random_residual)

    f_train, r_train = feature[train_idx], residual[train_idx]
    f_holdout, r_holdout = feature[holdout_idx], residual[holdout_idx]
    coef = _fit_coefficient(f_train, r_train)
    baseline_rms = _rms(r_holdout)
    candidate_rms = _rms(r_holdout - coef * f_holdout)
    reduction = _reduction(baseline_rms, candidate_rms)

    coef_shuf = _fit_coefficient(f_train[::-1], r_train)
    shuf_reduction = _reduction(baseline_rms, _rms(r_holdout - coef_shuf * f_holdout[::-1]))
    coef_rand = _fit_coefficient(f_train, random_residual[train_idx])
    rand_reduction = _reduction(baseline_rms, _rms(r_holdout - coef_rand * f_holdout))
    complexity = float(candidate["complexity"])
    effective = reduction - COMPLEXITY_PENALTY_PER_PARAM * complexity
    route = _route(
        reduction=reduction,
        effective=effective,
        shuf_reduction=shuf_reduction,
        rand_reduction=rand_reduction,
        holdout_rows=len(holdout_idx),
    )
    return {
        "candidate_id": candidate["candidate_id"],
        "route_verdict": route,
        "metrics": {
            "holdout_reduction": round(reduction, 6),
            "effective_reduction": round(effective, 6),
            "shuffled_reduction": round(shuf_reduction, 6),
            "random_slice_reduction": round(rand_reduction, 6),
        },
    }


def _candidate_feature(candidate: dict[str, Any], *, z: int, n: int, a: int) -> float:
    family = str(candidate["family"])
    parameters = candidate["parameters"]
    base = _base_feature(family, z=z, n=n)
    value = (base ** int(parameters["power"])) / (float(a) ** float(parameters["scale_exp"]))
    if parameters.get("mask") == "near_magic":
        value *= 1.0 if min(_nearest_magic_distance(z), _nearest_magic_distance(n)) <= 2 else 0.0
    return float(value)


def _top_candidates(factory_summary: dict[str, Any], *, top_n: int) -> list[dict[str, Any]]:
    executed = [
        c for c in factory_summary["candidates"]
        if c.get("metrics") and c.get("candidate_state") != "PREFLIGHT_REJECTED"
    ]
    return sorted(
        executed,
        key=lambda c: c["metrics"]["effective_reduction"],
        reverse=True,
    )[:top_n]


def _load_frozen_coefficients(path: Path) -> SemiEmpiricalCoefficients:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for score in payload.get("scores", []):
        if score.get("model_id") != "model_fitted_semi_empirical":
            continue
        coefficients = score.get("coefficients", {})
        missing = [key for key in COEFFICIENT_KEYS if key not in coefficients]
        if missing:
            raise ValueError(f"Frozen baseline coefficients missing keys: {', '.join(missing)}")
        return SemiEmpiricalCoefficients(
            volume=float(coefficients["volume"]),
            surface=float(coefficients["surface"]),
            coulomb=float(coefficients["coulomb"]),
            asymmetry=float(coefficients["asymmetry"]),
            pairing=float(coefficients["pairing"]),
        )
    raise ValueError(f"Frozen coefficient model not found in {path}")


def _base_feature(family: str, *, z: int, n: int) -> float:
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
    raise ValueError(f"Unsupported candidate family for perturbation control: {family}")


def _nearest_magic_distance(value: int) -> int:
    return min(abs(value - magic) for magic in MAGIC_NUMBERS)


def _fit_coefficient(feature: np.ndarray, residual: np.ndarray) -> float:
    denom = float(np.sum(np.square(feature)))
    if denom == 0.0:
        return 0.0
    return float(np.sum(feature * residual) / denom)


def _rms(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(values))))


def _reduction(baseline_rms: float, candidate_rms: float) -> float:
    return 0.0 if baseline_rms == 0 else (baseline_rms - candidate_rms) / baseline_rms


def _route(
    *,
    reduction: float,
    effective: float,
    shuf_reduction: float,
    rand_reduction: float,
    holdout_rows: int,
) -> str:
    if holdout_rows < MIN_HOLDOUT_ROWS:
        return "DATA_QUALITY_BLOCKED"
    if reduction <= 0.0 or effective <= 0.0:
        return "NEGATIVE_RESULT"
    if shuf_reduction >= 0.5 * reduction or rand_reduction >= 0.5 * reduction:
        return "REJECTED_BY_CONTROL"
    if effective < SHORTLIST_MIN_REDUCTION:
        return "INCONCLUSIVE"
    if holdout_rows < MIN_SHORTLIST_HOLDOUT_ROWS:
        return "INCONCLUSIVE"
    return "SHORTLIST_CANDIDATE"


def _overall_verdict(mode_summaries: dict[str, Any]) -> str:
    any_shortlist = any(
        "SHORTLIST_CANDIDATE" in candidate["route_verdict_counts"]
        for mode in mode_summaries.values()
        for candidate in mode["candidate_stability"]
    )
    if any_shortlist:
        return "INCONCLUSIVE"
    return "INCONCLUSIVE"
