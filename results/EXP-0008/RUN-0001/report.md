# Quark Koide Cascade — Brannen Phase Extension Test

**Result ID:** `RESULT-0010`
**Run:** `RUN-0001`
**Experiment:** `EXP-0008`
**Hypothesis:** `HYP-0008`
**Task:** `TASK-0088`

---

## Scope

This experiment tests whether the Koide formula Q = 2/3 can be satisfied
by the up-type quark triplet (u, c, t) or the down-type triplet (d, s, b)
using PDG 2024 running masses. Two formulas are evaluated:

1. **Standard Koide** (real, δ = 0): Q = (Σm) / (Σ√m)²
2. **Phase scan** Q(δ) = (Σm) / |√m₁ + √m₂·e^(iδ) + √m₃·e^(2iδ)|², δ ∈ [0, π]
3. **Brannen equal-spacing** Q_B = (Σm) / (Σm − Σ√(mᵢmⱼ))

Key analytic result: for this phase parameterisation, Q(δ) is minimised at
δ = 0, so Q_min = Q_std. If Q_std > 2/3, then no phase brings Q to 2/3.

---

## Up-Type Sector (u, c, t)

| Metric | Value |
| --- | ---: |
| Masses | mu = 2.16 MeV, mc = 1270 MeV, mt = 172,690 MeV |
| Q standard (δ=0) | 0.848981 |
| Q target (2/3) | 0.666667 |
| Gap Δ = Q − 2/3 | 0.182314 |
| Q uncertainty (1σ) | ±0.001145 |
| Gap in σ | **159.2σ** |
| Q phase min (scan) | 0.848981 |
| Q phase max (scan) | 1.195943 |
| Phase achieves Q = 2/3? | **NO** |
| Q Brannen equal-spacing | 1.097624 |
| Brannen fit B/A ratio | 1.7589 |
| Verdict | **INVALID** |

---

## Down-Type Sector (d, s, b)

| Metric | Value |
| --- | ---: |
| Masses | md = 4.67 MeV, ms = 93.4 MeV, mb = 4183 MeV |
| Q standard (δ=0) | 0.731497 |
| Q target (2/3) | 0.666667 |
| Gap Δ = Q − 2/3 | 0.064830 |
| Q uncertainty (1σ) | ±0.007331 |
| Gap in σ | **8.8σ** |
| Q phase min (scan) | 0.731497 |
| Q phase max (scan) | 1.309706 |
| Phase achieves Q = 2/3? | **NO** |
| Q Brannen equal-spacing | 1.224785 |
| Brannen fit B/A ratio | 1.5456 |
| Verdict | **INVALID** |

---

## Physical Interpretation

**Why Q > 2/3 for quarks:**

The Koide formula Q = 2/3 holds for charged leptons because the three lepton
masses satisfy a specific numerical relation. For quarks, the mass hierarchies
are far more extreme: mt/mu ~ 80,000 (up sector) and mb/md ~ 900 (down sector),
compared to mτ/me ~ 3,500 for leptons.

For the standard Koide formula, Q increases as masses become more hierarchical.
The charged-lepton masses happen to sit at the precise hierarchy where Q = 2/3.
Quark masses are more hierarchical, giving Q > 2/3.

**Why the phase scan cannot help:**

For the parameterisation Q(δ) = (Σm)/|√m₁ + √m₂·e^(iδ) + √m₃·e^(2iδ)|²,
the denominator is maximised at δ = 0 (standard real formula), so Q is
minimised at δ = 0. Since Q_min = Q_std > 2/3, no phase δ ∈ [0, π] brings
Q to 2/3.

**Brannen B/A ratio:**

The Brannen parametrization √mₖ = A + B·cos(δ_fit + 2πk/3) always has an
exact solution for any three positive masses. The ratio B/A measures how
"extreme" the mass hierarchy is. For charged leptons B/A ≈ 1.4; for up quarks
B/A ≈ 1.76 and for down quarks B/A ≈ 1.55. These values indicate that the
Brannen parametrization goes through negative values between the three evaluation
points — a sign of large hierarchy.

**Down sector note:**

The down-type sector shows a smaller gap to 2/3 (8.8σ)
compared to up (159.2σ), driven primarily by the large PDG
uncertainties on md (~10%) and ms (~10%). Even with 1σ favourable shifts, Q_std
remains above 2/3 for the down sector.

---

## Limitations

- Quark masses at mixed renormalization scales: mu, md, ms at μ = 2 GeV;
  mc at mc (charm pole), mb at mb (bottom pole), mt from direct measurements.
  No RGE running was applied to bring all masses to a common scale.
- PDG uncertainties on light quark masses are non-Gaussian and asymmetric;
  Gaussian propagation used here is an approximation.
- This test covers only the standard real Koide formula and one class of
  phase-modified formulas. Other extensions (e.g., non-equal phase spacing,
  quark mixing, GUT-scale masses) are not tested.
- The Brannen equal-spacing formula Q_B is also above 2/3 for both sectors,
  but Q_B is a distinct quantity from the phase-scan Q(δ).
