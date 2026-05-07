# Koide Null Baseline — Log-Uniform Random Triplet

**Microtask:** `PMR-004`
**Campaign:** `particle-mass-relations`
**Status:** REVIEW_NEEDED
**Date:** 2026-05-07

---

## Method

Baseline 2 from `docs/notes/koide-baseline-planning.md` — log-uniform random
triplet baseline.

- N = 100,000 mass triplets
- Each mass drawn independently from log-uniform over [m_e, m_t] = [0.511, 172,690] MeV
- Sorted within each triplet (m₁ ≤ m₂ ≤ m₃)
- Q computed using `koide_q_real` from `physics_lab/engines/koide_quark.py`
- Random seed: 42 (reproducible)

---

## Results

### Q Distribution Under Log-Uniform Random Masses

| Statistic | Value |
|-----------|------:|
| Mean | 0.6363 |
| Median | 0.6022 |
| Std | 0.1842 |
| Min | 0.3333 |
| Max | 0.9924 |
| 10th percentile | 0.4107 |
| 90th percentile | 0.9139 |

### Q Histogram

| Q bucket | Fraction of random triplets |
|---------|---------------------------|
| [1/3, 0.50) | 30.0% |
| [0.50, 0.60) | 19.7% |
| [0.60, 0.70) | 13.6% |
| [0.70, 0.80) | 12.2% |
| [0.80, 0.90) | 12.6% |
| [0.90, 1.00) | 11.9% |

### Fraction of Random Triplets Within ε of Q = 2/3

| ε (half-width) | Random fraction | Analytic B1 (uniform Q) |
|---------------|----------------|------------------------|
| 0.1 | 27.0% | 30.0% |
| 0.05 | 13.1% | 15.0% |
| 0.01 | 2.72% | 3.0% |
| 0.001 | 0.264% | 0.3% |
| 3×10⁻⁵ (charged leptons) | **0.009%** | 0.009% |

### Charged Lepton Result in Baseline Context

| Metric | Value |
|--------|------:|
| Charged lepton Q | 0.666664 |
| Gap to 2/3 | 2.67×10⁻⁶ |
| Charged lepton percentile in random distribution | 59th |
| Distance from random mean in σ units | 0.16σ |
| Random fraction within charged-lepton precision (ε=3×10⁻⁵) | 0.009% |

---

## Key Findings

### Finding 1: Q = 2/3 is NOT a rare target value

The mean of the log-uniform Q distribution is 0.636 and the median is 0.602.
The value 2/3 = 0.667 sits near the center of the distribution — at the 59th
percentile. This means that **finding a mass triplet with Q near 2/3 is not
intrinsically rare**. Roughly 27% of random log-uniform triplets have
|Q − 2/3| < 0.1.

This partially weakens the naive claim that the charged-lepton result is
surprising "because 2/3 is a special target." The value 2/3 happens to sit
where a large fraction of random triplets also cluster.

### Finding 2: The PRECISION is what is rare

At the actual precision of the charged-lepton result (|Q − 2/3| < 3×10⁻⁵),
only 0.009% of random log-uniform triplets match. This is consistent with
the analytic B1 estimate from TASK-0082 (< 0.01% of the Q range).

The charged-lepton result is not remarkable because Q ≈ 2/3 is a rare value.
It is remarkable because the match is precise to 3×10⁻⁵ while no other
intra-family quark or neutrino triplet comes within 8.8σ.

### Finding 3: The analytic B1 estimate matches B2 closely

The analytic Baseline 1 (uniform Q prior, fraction = 3ε) and the numerical
Baseline 2 (log-uniform masses) agree to within a factor of 1.1 across all ε.
This validates the planning estimate from TASK-0082 for practical use.

---

## Comparison: All Four SM Family Triplets

| Family | Q value | Percentile in random | Gap to 2/3 (σ) |
|--------|--------:|--------------------:|---------------|
| Charged leptons | 0.666664 | 59th | ~0 (VALID) |
| Down quarks | 0.731497 | 68th | 8.8σ above |
| Neutrinos (NH) | ≤ 0.584 | ~49th | 70.7σ below |
| Up quarks | 0.848981 | 78th | 159.2σ above |

All four families sit within the bulk of the random Q distribution (49th–78th
percentile). None is extreme in the random baseline. The charged-lepton
result is special not because its Q value is globally rare, but because it hits
2/3 with a precision that random draws rarely achieve, and while all other
intra-family triplets miss substantially.

---

## Limitations

- Baseline uses central-value masses only; uncertainty propagation is not applied to the random draws.
- Log-uniform over [m_e, m_t] is one reasonable choice; a different range or distribution would shift results.
- The 0.009% random-fraction figure does not account for the number of triplet families examined (4). If interpreted as a p-value, the Bonferroni-corrected p-value would be ~0.036%, still small but larger.
- This baseline does not assess whether Q = 2/3 is physically special (e.g., a fixed point of some RG flow). It only calibrates the numerical observation.
- The finding that 2/3 is not a rare Q value is itself dependent on the log-uniform mass prior. Under a different prior the result could differ.

---

## Claim Ceiling

This result does **not** license:
- "Charged leptons are uniquely determined by some deep principle"
- "Q = 2/3 is the only acceptable value"
- Any promotion of CLAIM-0003 from DRAFT to CONFIRMED

It does support (conservative wording):
> "The charged-lepton Koide quantity matches 2/3 to within 3×10⁻⁵.
> Under a log-uniform random triplet baseline, fewer than 0.01% of random
> SM-scale triplets achieve this precision, though 2/3 itself is not
> a rare value for Q (59th percentile of the random distribution).
> All other SM fermion family triplets miss 2/3 by at least 8.8σ."
