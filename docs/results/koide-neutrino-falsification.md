# Koide Neutrino Consistency Test — Falsification Result

## Scope

`TASK-0093` extends the Koide track from charged leptons to the neutrino sector.
The original Koide formula holds for charged leptons (e, μ, τ) to nine significant
figures. This experiment tests whether the same relation Q = 2/3 can be satisfied
by any physically admissible neutrino mass triplet under current oscillation data.

This result is narrow:

- neutrino mass eigenstates only (not flavour basis);
- oscillation parameters from PDG 2024 / NuFIT 5.3;
- tests the unmodified Koide formula Q = (m₁+m₂+m₃)/(√m₁+√m₂+√m₃)² = 2/3;
- does not test modified or extended Koide variants (Brannen, Koide's own neutrino proposals).
- should be read as one scoped part of the broader [Koide campaign summary](./koide-campaign-summary.md).

## Canonical Result

- Result: `RESULT-0009`
- Run: `RUN-0001`
- Experiment: `EXP-0007`
- Hypothesis: `HYP-0007`
- Overall verdict: `INVALID`

### Normal Hierarchy (NH: m₁ < m₂ < m₃)

| Metric | Value |
| --- | ---: |
| Q at m₁ → 0 (maximum achievable) | 0.5840 |
| Koide target (2/3) | 0.6667 |
| Gap Δ = 2/3 − Q_max | 0.0827 |
| Q_max uncertainty (1σ from Δm²) | ±0.00117 |
| Gap in units of 1σ | **70.7σ** |
| Solution Q = 2/3 exists? | **NO** |

### Inverted Hierarchy (IH: m₃ < m₁ < m₂)

| Metric | Value |
| --- | ---: |
| Q at m₃ → 0 (maximum achievable) | 0.5000 |
| Koide target (2/3) | 0.6667 |
| Gap Δ = 2/3 − Q_max | 0.1667 |
| Q_max uncertainty (1σ from Δm²) | ±3.95 × 10⁻⁷ |
| Gap in units of 1σ | **421,889σ** |
| Solution Q = 2/3 exists? | **NO** |

## Physical Interpretation

Q is a monotonically decreasing function of the lightest neutrino mass.
Its maximum is achieved when the lightest eigenstate → 0, giving Q_max.
Since Q_max < 2/3 for both hierarchies, there is **no physically admissible
neutrino mass triplet** consistent with oscillation data that satisfies Q = 2/3.

The IH result has an analytic explanation: when m₃ → 0 and m₁ ≈ m₂ (from
the atmospheric mass difference), the Koide formula reduces to a two-body
system giving Q → 1/2 exactly. The large sigma gap (421,889σ) reflects the
extreme precision of the atmospheric oscillation measurement.

This is a clean falsification in scope, not a marginal or inconclusive result.

## What This Does and Does Not Mean

**What it means:**
- The original Koide formula Q = 2/3, applied directly to the three neutrino
  mass eigenstates, is mathematically incompatible with PDG 2024 oscillation data.
- This holds for both known mass orderings (NH and IH) without exception.

**What it does not mean:**
- It does not rule out modified Koide relations (different exponents, phases,
  or sector-mixing extensions).
- It does not address whether a deeper symmetry underlies the charged-lepton
  Koide relation.
- It does not constrain absolute neutrino masses beyond what oscillation data
  already provides.

## Input Data

| Parameter | Value | Source |
| --- | ---: | --- |
| Δm²₂₁ (solar) | (7.53 ± 0.18) × 10⁻⁵ eV² | PDG 2024 / NuFIT 5.3 |
| Δm²₃₁ (NH, atmospheric) | (2.453 ± 0.033) × 10⁻³ eV² | PDG 2024 / NuFIT 5.3 |
| \|Δm²₃₂\| (IH, atmospheric) | (2.536 ± 0.034) × 10⁻³ eV² | PDG 2024 / NuFIT 5.3 |
| KATRIN direct bound | < 0.45 eV (90% CL) | KATRIN 2022 |
| Planck 2018 sum bound | < 0.12 eV (95% CL) | Planck 2018 + BAO |

## Canonical Artifacts

- [result.yaml](../../results/EXP-0007/RUN-0001/result.yaml)
- [report.md](../../results/EXP-0007/RUN-0001/report.md)
- [metrics.json](../../results/EXP-0007/RUN-0001/metrics.json)
- [review_summary.md](../../results/EXP-0007/RUN-0001/review_summary.md)
- [review_metadata.yaml](../../results/EXP-0007/RUN-0001/review_metadata.yaml)
- [Koide campaign summary](./koide-campaign-summary.md)
