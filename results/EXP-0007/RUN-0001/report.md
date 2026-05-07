# Neutrino Koide Consistency Test

- Result: `RESULT-0009`
- Run: `RUN-0001`
- Hypothesis: `HYP-0007`
- Task: `TASK-0093`

## Scientific Question

Does the Koide relation Q = 2/3 have a physically admissible solution
for neutrino masses consistent with oscillation data and mass bounds?

The Koide formula for charged leptons:

`Q = (m₁ + m₂ + m₃) / (√m₁ + √m₂ + √m₃)² = 2/3`

holds to 9 significant figures. We test whether the same Q = 2/3 is
achievable for any neutrino mass triplet satisfying the measured Δm².

## Input Data (PDG 2024 / NuFIT 5.3)

| Parameter | Value | Unit |
| --- | ---: | --- |
| Δm²₂₁ (solar) | 7.53e-05 | eV² |
| Δm²₃₁ (NH, atmospheric) | 2.45e-03 | eV² |
| \|Δm²₃₂\| (IH, atmospheric) | 2.54e-03 | eV² |
| Planck 2018 sum bound | < 0.12 | eV |
| KATRIN 2022 direct bound | < 0.45 | eV |

## Method

For each hierarchy, parameterize masses via the lightest eigenstate:

- **NH**: m₁ ∈ [0, ∞), m₂ = √(m₁² + Δm²₂₁), m₃ = √(m₁² + Δm²₃₁)
- **IH**: m₃ ∈ [0, ∞), m₁ = √(m₃² + |Δm²₃₂| − Δm²₂₁), m₂ = √(m₃² + |Δm²₃₂|)

Q is monotonically decreasing from Q_max (at m_lightest = 0) toward 1/3
(degenerate limit). Q = 2/3 is achievable only if Q_max ≥ 2/3.

## Results

### Normal Hierarchy (NH)

| Metric | Value |
| --- | ---: |
| Q at m₁ = 0 (maximum) | 0.583994 |
| Koide target (2/3) | 0.666667 |
| Gap Δ = 2/3 − Q_max | 0.082672 |
| Gap in σ (1σ from Δm²) | 70.7σ |
| Q_max uncertainty (1σ) | ±0.001169 |
| Solution Q = 2/3 exists? | NO |
| Verdict | **INCONSISTENT** |

Masses at m₁ = 0 (NH boundary):
- m₁ = 0, m₂ = 8.678 meV, m₃ = 49.528 meV, Σ = 58.205 meV

### Inverted Hierarchy (IH)

| Metric | Value |
| --- | ---: |
| Q at m₃ = 0 (maximum) | 0.500007 |
| Koide target (2/3) | 0.666667 |
| Gap Δ = 2/3 − Q_max | 0.166660 |
| Gap in σ (1σ from Δm²) | 421889.0σ |
| Q_max uncertainty (1σ) | ±0.000000 |
| Solution Q = 2/3 exists? | NO |
| Verdict | **INCONSISTENT** |

## Physical Interpretation

Q is a measure of mass hierarchy spread. For three equal masses: Q = 1/3.
For one dominant mass (m₃ >> m₁, m₂): Q → 1.
The charged-lepton value Q = 2/3 falls at a specific intermediate spread.

The neutrino oscillation data strongly constrain the mass ratios:
- NH: m₂/m₃ ≈ 0.175 at m₁ → 0
- IH: m₁/m₂ ≈ 0.985 at m₃ → 0

These mass ratios are set by nature and cannot be tuned. The maximum
achievable Q is determined by them, not by a free parameter.

## Verdict

- NH: Q_max = 0.5840 < 2/3 = 0.6667 → **INCONSISTENT**
- IH: Q_max = 0.5000 < 2/3 = 0.6667 → **INCONSISTENT**

The Koide relation Q = 2/3, as defined for charged leptons, is
**inconsistent with neutrino oscillation data under both hierarchies**.

The gap is not marginal: Q_max(NH) falls 70.7σ below 2/3.
This is a clean falsification, not a near-miss.

## Limitations

- This test applies the Koide formula in its original charged-lepton form (Q = 2/3).
- Phase-modified variants (Brannen cascade with δ ≠ 0) are not tested here.
- The analysis uses PDG 2024 / NuFIT 5.3 best-fit values; tension between
  oscillation experiments is not modelled.
- Majorana vs Dirac nature does not affect this mass-eigenvalue test.
- The claim does not extend to future data with significantly different Δm² values.

## Conclusion

The Koide relation Q = 2/3 is a feature of the charged-lepton sector only.
It does not generalise to neutrinos in its original form. A different
value of Q, or a modified formula family, would be required to define
an analogous neutrino relation — if one exists at all.

This result does not promote any claim. CLAIM-0003 (charged-lepton
Koide reproduction) remains unaffected.
