"""Muon g-2 anomaly formula search engine."""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
from typing import Any

import numpy as np

# ── Physical constants (PDG 2024) ─────────────────────────────────────────────

ALPHA = 7.2973525693e-3
MU_OVER_ME = 206.7682830
MU_OVER_MTAU = 0.059462
MW_OVER_MZ = 0.88145
GF_MMU_SQ = 1.302e-7
MU_OVER_MPI0 = 0.7830

ALPHA_OVER_PI = ALPHA / math.pi
EW_SCALE = GF_MMU_SQ / (8.0 * math.pi**2 * math.sqrt(2))

# ── Target ────────────────────────────────────────────────────────────────────────────

DELTA_AMU = 249.0e-11
SIGMA_COMBINED = 48.0e-11


# ── Result dataclasses ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FormulaHit:
    family: str
    label: str
    params: dict[str, Any]
    formula_str: str
    value: float
    z_score: float
    complexity: int
    is_reference: bool = False  # True for optimal-fit hits (not independently predicted)


@dataclass(frozen=True)
class RandomBaseline:
    family: str
    n_samples: int
    seed: int
    hit_rate_1sigma: float
    guardrail_passed: bool


@dataclass(frozen=True)
class FamilyResult:
    family_id: str
    label: str
    n_evaluated: int
    hits: list[FormulaHit]
    random_baseline: RandomBaseline
    verdict: str
    notes: str


# ── Scoring ───────────────────────────────────────────────────────────────────────────

def _z(value: float) -> float:
    return abs(value - DELTA_AMU) / SIGMA_COMBINED


def _hit(value: float, nsigma: float = 1.0) -> bool:
    return _z(value) < nsigma


# ── Family F1 — QED power-law (α/π)^a × (mμ/me)^b ──────────────────────────────

def search_f1() -> FamilyResult:
    a_range = range(1, 5)          # a ∈ {1,2,3,4}
    b_range = range(-3, 4)         # b ∈ {-3,...,3}
    hits: list[FormulaHit] = []
    total = 0
    for a, b in itertools.product(a_range, b_range):
        val = ALPHA_OVER_PI**a * MU_OVER_ME**b
        total += 1
        if _hit(val):
            hits.append(FormulaHit(
                family="F1",
                label=f"(α/π)^{a} × (mμ/me)^{b}",
                params={"a": a, "b": b},
                formula_str=f"(α/π)^{a} × (mμ/me)^{b}",
                value=val,
                z_score=_z(val),
                complexity=0,
            ))
    rng = np.random.default_rng(1001)
    a_samp = rng.integers(1, 5, size=100_000)
    b_samp = rng.integers(-3, 4, size=100_000)
    rand_vals = ALPHA_OVER_PI**a_samp * MU_OVER_ME**b_samp
    hit_rate = float(np.mean(np.abs(rand_vals - DELTA_AMU) / SIGMA_COMBINED < 1.0))
    rb = RandomBaseline("F1", 100_000, 1001, hit_rate, hit_rate < 0.01)
    return FamilyResult(
        family_id="F1",
        label="QED power-law: (α/π)^a × (mμ/me)^b",
        n_evaluated=total,
        hits=hits,
        random_baseline=rb,
        verdict="NULL" if not hits else "HIT",
        notes="Integer exponents a∈[1,4], b∈[-3,3]. C=0 free parameters.",
    )


# ── Family F2 — EW scale × integer coefficient c ───────────────────────────────────
# f2 = c × GF·mμ²/(8π²√2)   for integer c ∈ {1,...,10}

def search_f2() -> FamilyResult:
    hits: list[FormulaHit] = []
    total = 0
    for c in range(1, 11):
        val = c * EW_SCALE
        total += 1
        if _hit(val):
            hits.append(FormulaHit(
                family="F2",
                label=f"{c} × GF·mμ²/(8π²√2)",
                params={"c": c},
                formula_str=f"{c} × EW_scale",
                value=val,
                z_score=_z(val),
                complexity=0,
            ))
    rng = np.random.default_rng(1002)
    c_samp = rng.integers(1, 11, size=100_000)
    rand_vals = c_samp * EW_SCALE
    hit_rate = float(np.mean(np.abs(rand_vals - DELTA_AMU) / SIGMA_COMBINED < 1.0))
    rb = RandomBaseline("F2", 100_000, 1002, hit_rate, hit_rate < 0.01)
    return FamilyResult(
        family_id="F2",
        label="EW scale: c × GF·mμ²/(8π²√2), integer c ∈ [1,10]",
        n_evaluated=total,
        hits=hits,
        random_baseline=rb,
        verdict="NULL" if not hits else "HIT",
        notes="Integer scale factor c. C=0 free parameters. G4 check: not a known SM term.",
    )


# ── Family F2b — EW scale × QED/mass ratio corrections ──────────────────────────
# f2b = GF·mμ²/(8π²√2) × (α/π)^a × ratio^b
# ratio ∈ {mμ/me, mμ/mτ, mW/mZ, mμ/mπ}; a,b ∈ {0,1,2,3}

def search_f2b() -> FamilyResult:
    ratios = {
        "mμ/me": MU_OVER_ME,
        "mμ/mτ": MU_OVER_MTAU,
        "mW/mZ": MW_OVER_MZ,
        "mμ/mπ⁰": MU_OVER_MPI0,
    }
    a_range = range(0, 4)
    b_range = range(0, 4)
    hits: list[FormulaHit] = []
    total = 0
    for ratio_name, ratio_val in ratios.items():
        for a, b in itertools.product(a_range, b_range):
            if a == 0 and b == 0:
                continue  # covered by F2
            val = EW_SCALE * ALPHA_OVER_PI**a * ratio_val**b
            total += 1
            if _hit(val):
                hits.append(FormulaHit(
                    family="F2b",
                    label=f"EW × (α/π)^{a} × ({ratio_name})^{b}",
                    params={"a": a, "b": b, "ratio": ratio_name},
                    formula_str=f"EW_scale × (α/π)^{a} × ({ratio_name})^{b}",
                    value=val,
                    z_score=_z(val),
                    complexity=0,
                ))
    rng = np.random.default_rng(1003)
    n = 100_000
    ratio_choices = rng.integers(0, len(ratios), size=n)
    ratio_arr = np.array(list(ratios.values()))
    a_samp = rng.integers(0, 4, size=n)
    b_samp = rng.integers(0, 4, size=n)
    rand_vals = EW_SCALE * ALPHA_OVER_PI**a_samp * ratio_arr[ratio_choices]**b_samp
    hit_rate = float(np.mean(np.abs(rand_vals - DELTA_AMU) / SIGMA_COMBINED < 1.0))
    rb = RandomBaseline("F2b", 100_000, 1003, hit_rate, hit_rate < 0.01)
    return FamilyResult(
        family_id="F2b",
        label="EW scale with QED/mass corrections: EW × (α/π)^a × ratio^b",
        n_evaluated=total,
        hits=hits,
        random_baseline=rb,
        verdict="NULL" if not hits else "HIT",
        notes="Integer exponents a,b ∈ [0,3] per ratio. C=0 free parameters.",
    )


# ── Family F3 — Hadronic: c × (α/π)^3 × (mμ/mπ⁰)^2 ─────────────────────────────────

def search_f3() -> FamilyResult:
    """F3: one free scale factor c, fitted optimally."""
    f3_base = ALPHA_OVER_PI**3 * MU_OVER_MPI0**2
    c_opt = DELTA_AMU / f3_base

    # Test exact rational candidates
    rational_candidates = [
        (1, 3), (1, 4), (1, 2), (1, 1), (2, 3), (3, 8), (1, 5),
    ]
    hits: list[FormulaHit] = []
    for num, den in rational_candidates:
        c = num / den
        val = c * f3_base
        if _hit(val):
            hits.append(FormulaHit(
                family="F3",
                label=f"({num}/{den}) × (α/π)³ × (mμ/mπ⁰)²",
                params={"c_num": num, "c_den": den, "c": c},
                formula_str=f"({num}/{den}) × (α/π)^3 × (mμ/mπ⁰)^2",
                value=val,
                z_score=_z(val),
                complexity=1,
            ))
    # Also report optimal fit (is_reference=True: fitted to target, not independently predicted)
    val_opt = c_opt * f3_base
    hits.insert(0, FormulaHit(
        family="F3",
        label=f"(optimal c={c_opt:.4f}) × (α/π)³ × (mμ/mπ⁰)² [fitted]",
        params={"c_num": None, "c_den": None, "c": c_opt},
        formula_str=f"({c_opt:.6f}) × (α/π)^3 × (mμ/mπ⁰)^2",
        value=val_opt,
        z_score=_z(val_opt),
        complexity=1,
        is_reference=True,
    ))

    # Random baseline: c drawn from uniform [0, 2]
    rng = np.random.default_rng(1004)
    c_samp = rng.uniform(0.0, 2.0, size=100_000)
    rand_vals = c_samp * f3_base
    hit_rate = float(np.mean(np.abs(rand_vals - DELTA_AMU) / SIGMA_COMBINED < 1.0))
    rb = RandomBaseline("F3", 100_000, 1004, hit_rate, hit_rate < 0.01)
    predicted_hits = [h for h in hits if not h.is_reference]
    return FamilyResult(
        family_id="F3",
        label="Hadronic: c × (α/π)³ × (mμ/mπ⁰)²",
        n_evaluated=len(rational_candidates) + 1,
        hits=hits,
        random_baseline=rb,
        verdict="NULL" if not predicted_hits else "HIT",
        notes=f"One free scale c. Optimal c={c_opt:.4f} ≈ 1/3. C=1 free parameter.",
    )


# ── Family F4 — Lepton mass cascade α^a × (mμ/me)^b × (mμ/mτ)^c ─────────────────────

def search_f4() -> FamilyResult:
    a_range = range(-2, 4)   # -2,...,3
    b_range = range(-2, 4)
    c_range = range(-2, 4)
    hits: list[FormulaHit] = []
    total = 0
    for a, b, c in itertools.product(a_range, b_range, c_range):
        if a == 0 and b == 0 and c == 0:
            continue
        val = ALPHA**a * MU_OVER_ME**b * MU_OVER_MTAU**c
        total += 1
        if _hit(val):
            hits.append(FormulaHit(
                family="F4",
                label=f"α^{a} × (mμ/me)^{b} × (mμ/mτ)^{c}",
                params={"a": a, "b": b, "c": c},
                formula_str=f"α^{a} × (mμ/me)^{b} × (mμ/mτ)^{c}",
                value=val,
                z_score=_z(val),
                complexity=0,
            ))
    rng = np.random.default_rng(1005)
    n = 100_000
    a_samp = rng.integers(-2, 4, size=n)
    b_samp = rng.integers(-2, 4, size=n)
    c_samp = rng.integers(-2, 4, size=n)
    rand_vals = ALPHA**a_samp * MU_OVER_ME**b_samp * MU_OVER_MTAU**c_samp
    finite = np.isfinite(rand_vals)
    hit_rate = float(np.mean(np.abs(rand_vals[finite] - DELTA_AMU) / SIGMA_COMBINED < 1.0))
    rb = RandomBaseline("F4", 100_000, 1005, hit_rate, hit_rate < 0.01)
    return FamilyResult(
        family_id="F4",
        label="Lepton cascade: α^a × (mμ/me)^b × (mμ/mτ)^c",
        n_evaluated=total,
        hits=hits,
        random_baseline=rb,
        verdict="NULL" if not hits else "HIT",
        notes="Integer exponents a,b,c ∈ [-2,3]. C=0 free parameters.",
    )


# ── Family F5 — Mixed EW+QED ───────────────────────────────────────────────────────────
# f5 = (α/π)^a × (mW/mZ)^b × (GF·mμ²)^c

def search_f5() -> FamilyResult:
    a_range = range(1, 5)    # 1,...,4
    b_range = range(0, 4)    # 0,...,3
    c_range = range(0, 4)    # 0,...,3
    hits: list[FormulaHit] = []
    total = 0
    for a, b, c in itertools.product(a_range, b_range, c_range):
        if c == 0 and b == 0:
            continue  # pure QED, no EW factor; handled in F1 overlap
        val = ALPHA_OVER_PI**a * MW_OVER_MZ**b * GF_MMU_SQ**c
        total += 1
        if _hit(val):
            hits.append(FormulaHit(
                family="F5",
                label=f"(α/π)^{a} × (mW/mZ)^{b} × (GF·mμ²)^{c}",
                params={"a": a, "b": b, "c": c},
                formula_str=f"(α/π)^{a} × (mW/mZ)^{b} × (GF·mμ²)^{c}",
                value=val,
                z_score=_z(val),
                complexity=0,
            ))
    rng = np.random.default_rng(1006)
    n = 100_000
    a_samp = rng.integers(1, 5, size=n)
    b_samp = rng.integers(0, 4, size=n)
    c_samp = rng.integers(0, 4, size=n)
    rand_vals = ALPHA_OVER_PI**a_samp * MW_OVER_MZ**b_samp * GF_MMU_SQ**c_samp
    hit_rate = float(np.mean(np.abs(rand_vals - DELTA_AMU) / SIGMA_COMBINED < 1.0))
    rb = RandomBaseline("F5", 100_000, 1006, hit_rate, hit_rate < 0.01)
    return FamilyResult(
        family_id="F5",
        label="Mixed EW+QED: (α/π)^a × (mW/mZ)^b × (GF·mμ²)^c",
        n_evaluated=total,
        hits=hits,
        random_baseline=rb,
        verdict="NULL" if not hits else "HIT",
        notes="Integer exponents. c=0,b=0 excluded (overlap with F1). C=0 free params.",
    )


# ── Main search ────────────────────────────────────────────────────────────────────────────

def run_formula_search() -> dict[str, Any]:
    families = [search_f1(), search_f2(), search_f2b(), search_f3(), search_f4(), search_f5()]
    # Exclude reference (fitted) hits from global verdict logic
    all_hits = [h for fr in families for h in fr.hits if not h.is_reference]
    # Credible hits: C≤1 AND guardrail passed AND z<1
    credible = [
        h for h in all_hits
        if h.complexity <= 1
        and any(
            fr.random_baseline.guardrail_passed
            for fr in families
            if fr.family_id == h.family
        )
    ]
    # Interesting: z < 0.5
    interesting = [h for h in all_hits if h.z_score < 0.5]
    best_overall_hit = min(all_hits, key=lambda h: h.z_score) if all_hits else None
    best_credible_hit = min(credible, key=lambda h: h.z_score) if credible else None
    primary_hit = best_credible_hit or best_overall_hit
    return {
        "target_value": DELTA_AMU,
        "sigma": SIGMA_COMBINED,
        "constants": {
            "alpha": ALPHA,
            "alpha_over_pi": ALPHA_OVER_PI,
            "mu_over_me": MU_OVER_ME,
            "mu_over_mtau": MU_OVER_MTAU,
            "mW_over_mZ": MW_OVER_MZ,
            "GF_mmu_sq": GF_MMU_SQ,
            "mu_over_mpi0": MU_OVER_MPI0,
            "EW_scale": EW_SCALE,
        },
        "families": [
            {
                "family_id": fr.family_id,
                "label": fr.label,
                "n_evaluated": fr.n_evaluated,
                "n_hits_1sigma": len([h for h in fr.hits if not h.is_reference]),
                "hits": [
                    {
                        "formula": h.formula_str,
                        "params": h.params,
                        "value": h.value,
                        "value_1e11": h.value / 1e-11,
                        "z_score": h.z_score,
                        "complexity": h.complexity,
                        "is_reference": h.is_reference,
                    }
                    for h in sorted(fr.hits, key=lambda x: x.z_score)
                ],
                "random_baseline": {
                    "hit_rate_1sigma": fr.random_baseline.hit_rate_1sigma,
                    "guardrail_passed": fr.random_baseline.guardrail_passed,
                    "n_samples": fr.random_baseline.n_samples,
                },
                "verdict": fr.verdict,
                "notes": fr.notes,
            }
            for fr in families
        ],
        "summary": {
            "total_formulas_evaluated": sum(fr.n_evaluated for fr in families),
            "total_hits_1sigma": len(all_hits),
            "credible_hits": len(credible),
            "interesting_hits_half_sigma": len(interesting),
            # None when no hits (avoids float("inf") which breaks JSON serialization)
            "best_formula_basis": (
                "credible_hit" if best_credible_hit else "closest_hit" if best_overall_hit else None
            ),
            "best_z_score": primary_hit.z_score if primary_hit else None,
            "best_formula": primary_hit.formula_str if primary_hit else None,
            "best_value": primary_hit.value if primary_hit else None,
            "best_credible_z_score": best_credible_hit.z_score if best_credible_hit else None,
            "best_credible_formula": best_credible_hit.formula_str if best_credible_hit else None,
            "best_credible_value": best_credible_hit.value if best_credible_hit else None,
            "closest_hit_z_score": best_overall_hit.z_score if best_overall_hit else None,
            "closest_hit_formula": best_overall_hit.formula_str if best_overall_hit else None,
            "closest_hit_value": best_overall_hit.value if best_overall_hit else None,
        },
        "global_verdict": (
            "VALID_EMPIRICAL" if credible else
            "NUMEROLOGY_ONLY" if all_hits else
            "NULL"
        ),
    }
