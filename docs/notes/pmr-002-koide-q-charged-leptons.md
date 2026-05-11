# PMR-002: Koide Q for Charged Lepton Triplet

**Microtask ID:** PMR-002  
**Queue:** particle-mass-relations  
**Run:** MICROTASK-RUN-0019  
**Verdict:** REVIEW_NEEDED  
**Review state:** UNREVIEWED  

---

## Input Masses

All values from `data/particle_masses/charged_leptons.yaml` (PDG 2025, pole masses):

| Particle | Mass (MeV) | Uncertainty (MeV) |
|---|---|---|
| electron (e) | 0.51099895000 | ±1.5×10⁻¹⁰ |
| muon (μ) | 105.6583755 | ±2.3×10⁻⁶ |
| tau (τ) | 1776.93 | ±0.09 |

Source: S. Navas et al. (PDG), Phys. Rev. D 110, 030001 (2024) and 2025 update.

---

## Koide Q Definition

For a mass triplet (m₁, m₂, m₃), the Koide Q parameter is defined as:

```
Q = (m₁ + m₂ + m₃) / (√m₁ + √m₂ + √m₃)²
```

By the Cauchy-Schwarz inequality, Q lies in [1/3, 1] for positive masses.

---

## Computation

```
sum_mass  = me + mμ + mτ = 0.51099895000 + 105.6583755 + 1776.93
          = 1883.09937445 MeV

sum_sqrt  = √me + √mμ + √mτ
sum_sqrt² = 2824.65839683 MeV

Q = 1883.09937445 / 2824.65839683 = 0.6666644634

2/3       = 0.6666666667

|Q − 2/3| = 2.20e-06
```

The computed Q deviates from 2/3 by approximately 2.2×10⁻⁶.

---

## Uncertainty Propagation (Tau-Dominated)

The tau mass uncertainty ±0.09 MeV dominates. Evaluating Q at the tau mass bounds:

```
τ lower bound: mτ − 0.09 MeV = 1776.84 MeV  →  Q_lo = 0.6666593823
τ upper bound: mτ + 0.09 MeV = 1777.02 MeV  →  Q_hi = 0.6666695442

Q range width = Q_hi − Q_lo = 1.02e-05
σ_Q ≈ (range width) / 2 ≈ 5.1×10⁻⁶
```

The current central value deviation |Q − 2/3| = 2.2×10⁻⁶ is smaller than σ_Q ≈ 5.1×10⁻⁶, meaning Q is consistent with 2/3 within the tau mass uncertainty.

---

## Limitation

Numeric closeness to 2/3 is not explanatory evidence. This is a narrow numerical observation for pole masses from PDG 2025. No theoretical derivation exists within this repository that predicts Q = 2/3 from first principles. Using MS-bar quark masses instead of pole lepton masses yields different Q values for other triplets (see PMR-003, PMR-011). The observation is narrow in scope: it applies to this specific mass triplet, in this specific scheme (pole masses), at this specific PDG edition. It does not generalize to quarks or neutrinos without separate analysis.

---

## Verdict

REVIEW_NEEDED — Q = 0.6666644634 for the charged lepton pole mass triplet is numerically consistent with 2/3 at the ~2.2×10⁻⁶ level. This is within the tau mass uncertainty (σ_Q ≈ 5.1×10⁻⁶). The observation is noted as a narrow numerical coincidence requiring further theoretical context before any physical interpretation can be assigned.
