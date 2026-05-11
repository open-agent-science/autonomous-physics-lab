# PMR-008: Uncertainty Propagation for Koide Q

**Microtask ID:** PMR-008  
**Queue:** particle-mass-relations  
**Run:** MICROTASK-RUN-0022  
**Verdict:** REVIEW_NEEDED  
**Review state:** UNREVIEWED  

---

## Input Masses and Uncertainties

From `data/particle_masses/charged_leptons.yaml` (PDG 2025, pole masses):

| Particle | Mass (MeV) | Uncertainty δm (MeV) |
|---|---|---|
| electron (e) | 0.51099895000 | ±1.5×10⁻¹⁰ |
| muon (μ) | 105.6583755 | ±2.3×10⁻⁶ |
| tau (τ) | 1776.93 | ±0.09 |

---

## Dominant Uncertainty Source

The tau mass uncertainty dominates by several orders of magnitude:

| Comparison | Ratio |
|---|---|
| δm_τ / δm_μ | 0.09 / 2.3×10⁻⁶ ≈ 3.9×10⁴ |
| δm_τ / δm_e | 0.09 / 1.5×10⁻¹⁰ ≈ 6.0×10⁸ |

The tau mass is the overwhelmingly dominant source of uncertainty in Q.

Fractional uncertainty on tau mass: σ_τ / m_τ = 0.09 / 1776.93 ≈ 5.1×10⁻⁵.

---

## Uncertainty Estimate for Q

From the PMR-002 computation, evaluating Q at the tau mass bounds:

```
mτ − 0.09 MeV = 1776.84 MeV  →  Q_lo = 0.6666593823
mτ + 0.09 MeV = 1777.02 MeV  →  Q_hi = 0.6666695442

Q range width = Q_hi − Q_lo = 1.02×10⁻⁵
σ_Q ≈ (Q range width) / 2 = 5.1×10⁻⁶
```

This is a first-order finite-difference estimate of the partial derivative ∂Q/∂m_τ × δm_τ.

---

## Approximation Validity

The first-order Taylor expansion is used:

```
σ_Q ≈ |∂Q/∂m_τ| × δm_τ
```

Second-order corrections are proportional to (σ_τ/m_τ)² ≈ (5.1×10⁻⁵)² ≈ 2.6×10⁻⁹, which is negligible compared to the first-order term σ_Q ≈ 5.1×10⁻⁶.

The first-order approximation is adequate.

---

## Comparison with Central Value Deviation

From PMR-002:

```
|Q − 2/3| = 2.20×10⁻⁶
σ_Q        ≈ 5.1×10⁻⁶
```

The deviation from 2/3 is smaller than σ_Q. The charged lepton Q is consistent with 2/3 within the tau mass uncertainty at the ~0.4σ level.

---

## Limitations

- The tau mass uncertainty used here is the PDG 2025 combined experimental average. The combination procedure and correlations between experiments are not modelled in this propagation.
- Correlations between the tau and muon mass measurements (e.g., from shared systematic effects or electroweak radiative corrections) are not included. These are expected to be negligible given the completely different experimental methods used.
- The electron and muon uncertainties contribute to σ_Q at the 10⁻¹² and 10⁻⁸ level respectively, and are entirely negligible.
- This propagation does not address theoretical uncertainties (QED radiative corrections to the measured masses), which are also small for charged leptons.

---

## Verdict

REVIEW_NEEDED — the tau mass uncertainty dominates Q by 4+ orders of magnitude over the muon and electron contributions. σ_Q ≈ 5.1×10⁻⁶. The observed deviation |Q − 2/3| = 2.2×10⁻⁶ is within σ_Q, making the central value numerically consistent with Q = 2/3.
