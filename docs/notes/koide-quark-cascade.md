# Koide Quark Cascade — Notes

**Task:** `TASK-0088`
**Experiment:** `EXP-0008` / `RUN-0001`
**Result:** `RESULT-0010`
**Verdict:** `INVALID`

---

## Summary

The Koide formula Q = 2/3 does not hold for up-type (u, c, t) or down-type
(d, s, b) quark mass triplets using PDG 2024 running masses. The phase-modified
formula Q(δ) also cannot reach 2/3 for either sector.

| Sector | Q standard | Gap to 2/3 | Gap (σ) | Phase scan reaches 2/3? |
|--------|----------:|-----------|--------|------------------------|
| Up (u, c, t) | 0.848981 | 0.182314 | **159.2σ** | NO |
| Down (d, s, b) | 0.731497 | 0.064830 | **8.8σ** | NO |

---

## Analytic Explanation

For the parameterisation Q(δ) = (Σm) / |√m₁ + √m₂·e^{iδ} + √m₃·e^{2iδ}|²,
the denominator is maximised at δ = 0 (standard real formula). This means Q is
**minimised** at δ = 0, so Q_min = Q_std. If Q_std > 2/3, no phase rotation can
lower Q to 2/3.

For charged leptons, Q_std = 2/3 exactly. For quarks, Q_std > 2/3 because the
mass hierarchies are more extreme:
- Up sector: mt/mu ≈ 80,000 (vs mτ/me ≈ 3,500 for leptons)
- Down sector: mb/md ≈ 900

Larger mass ratios → larger Q_std → larger gap to 2/3.

---

## Brannen Equal-Spacing Formula

The Brannen formula Q_B = (Σm) / (Σm − Σ_{i<j}√(mᵢmⱼ)) gives fixed values:
- Up: Q_B ≈ 1.098 (even further from 2/3)
- Down: Q_B ≈ 1.225 (even further from 2/3)

For charged leptons, Q_B = 4/3 (since Q_std = 2/3 implies Q_B = 4/3 algebraically).

---

## Comparison with Neutrino Result

| Sector | Formula type | Gap to 2/3 |
|--------|-------------|-----------|
| Neutrinos NH | Q_max vs 2/3 (Q < 2/3) | 70.7σ below |
| Neutrinos IH | Q_max vs 2/3 (Q < 2/3) | 421,889σ below |
| Up quarks | Q_std vs 2/3 (Q > 2/3) | 159.2σ above |
| Down quarks | Q_std vs 2/3 (Q > 2/3) | 8.8σ above |

The neutrino result (EXP-0007) found Q too LOW to reach 2/3. The quark result
finds Q too HIGH to reach 2/3. Charged leptons sit at the special point Q = 2/3.

---

## Scope and Limitations

- PDG 2024 running masses at mixed scales (μ = 2 GeV for light quarks,
  self-consistent pole for c, b, top quark from direct measurement).
- No renormalization-group running applied to bring masses to a common scale.
- Only one class of phase-modified formulas tested; other extensions (non-equal
  phase spacing, quark mixing, GUT-scale masses) are not tested.
- The Brannen equal-spacing formula gives Q_B ≠ 2/3 for quarks, but this is a
  distinct quantity from the phase-scan formula.

---

## Relation to Existing Koide Track

| Experiment | Hypothesis | Result | Verdict |
|------------|-----------|--------|---------|
| EXP-0004 | Charged leptons (e, μ, τ) | Q = 0.666664 | VALID |
| EXP-0005 | Tau holdout prediction | Δm = 0.039 MeV | VALID |
| EXP-0007 | Neutrinos (NH/IH) | Q_max < 2/3 | INVALID |
| EXP-0008 | Quarks (up/down) | Q_std > 2/3 | INVALID |

The Koide formula Q = 2/3 appears to be specific to charged leptons. It fails
for both neutrinos (Q too small) and quarks (Q too large).
