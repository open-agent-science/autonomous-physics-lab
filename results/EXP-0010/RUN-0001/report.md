# Muon g-2 Formula-Search Stress Test

- Result: `RESULT-0012`
- Run: `RUN-0001`
- Experiment: `EXP-0010`
- Hypothesis: `HYP-0010`
- Task: `TASK-0127`
- Global verdict: `STRESS_TEST_HIT`

## Target

Δaμ = 249 × 10⁻¹¹  (σ = 48 × 10⁻¹¹)

Significance: ~5.1σ (data-driven HVP, 2023 BNL+FNAL combined).

## Results by Formula Family

### F1 — QED power-law: (α/π)^a × (mμ/me)^b

- Formulas evaluated: 28
- Hits within 1σ: 0
- Random baseline hit-rate: 0.00%  (guardrail P<1%: ✓ PASS)
- Notes: Integer exponents a∈[1,4], b∈[-3,3]. C=0 free parameters.

No hits within 1σ.

### F2 — EW scale: c × GF·mμ²/(8π²√2), integer c ∈ [1,10]

- Formulas evaluated: 10
- Hits within 1σ: 1
- Random baseline hit-rate: 10.08%  (guardrail P<1%: ✗ FAIL)
- Notes: Integer scale factor c. C=0 free parameters. G4 check: not a known SM term.

| Formula | Value (×10⁻¹¹) | z-score | C | Role | Screened? |
|---|---:|---:|---|---|---|
| `2 × EW_scale` | 233.2 | 0.329 | 0 | Predicted | No |

### F2b — EW scale with QED/mass corrections: EW × (α/π)^a × ratio^b

- Formulas evaluated: 60
- Hits within 1σ: 0
- Random baseline hit-rate: 0.00%  (guardrail P<1%: ✓ PASS)
- Notes: Integer exponents a,b ∈ [0,3] per ratio. C=0 free parameters.

No hits within 1σ.

### F3 — Hadronic: c × (α/π)³ × (mμ/mπ⁰)²

- Formulas evaluated: 8
- Hits within 1σ: 2
- Random baseline hit-rate: 6.25%  (guardrail P<1%: ✗ FAIL)
- Notes: One free scale c. Optimal c=0.3241 ≈ 1/3. C=1 free parameter.

| Formula | Value (×10⁻¹¹) | z-score | C | Role | Screened? |
|---|---:|---:|---|---|---|
| `(0.324063) × (α/π)^3 × (mμ/mπ⁰)^2` | 249.0 | 0.000 | 1 | Reference fit | No |
| `(1/3) × (α/π)^3 × (mμ/mπ⁰)^2` | 256.1 | 0.148 | 1 | Predicted | No |
| `(3/8) × (α/π)^3 × (mμ/mπ⁰)^2` | 288.1 | 0.815 | 1 | Predicted | No |

Reference-fit rows are shown for calibration only and are excluded from hit counts, guardrail checks, and the global verdict.

### F4 — Lepton cascade: α^a × (mμ/me)^b × (mμ/mτ)^c

- Formulas evaluated: 215
- Hits within 1σ: 1
- Random baseline hit-rate: 0.49%  (guardrail P<1%: ✓ PASS)
- Notes: Integer exponents a,b,c ∈ [-2,3]. C=0 free parameters.

| Formula | Value (×10⁻¹¹) | z-score | C | Role | Screened? |
|---|---:|---:|---|---|---|
| `α^3 × (mμ/me)^-2 × (mμ/mτ)^-2` | 257.1 | 0.168 | 0 | Predicted | Yes |

### F5 — Mixed EW+QED: (α/π)^a × (mW/mZ)^b × (GF·mμ²)^c

- Formulas evaluated: 60
- Hits within 1σ: 0
- Random baseline hit-rate: 0.00%  (guardrail P<1%: ✓ PASS)
- Notes: Integer exponents. c=0,b=0 excluded (overlap with F1). C=0 free params.

No hits within 1σ.

## Summary

| Metric | Value |
|---|---|
| Total formulas evaluated | 381 |
| Hits within 1σ | 4 |
| Guardrail-screened hits (C≤1, P<1%) | 1 |
| Interesting hits (z<0.5σ) | 3 |
| Best z-score | 0.168σ |
| Best guardrail-screened formula | `α^3 × (mμ/me)^-2 × (mμ/mτ)^-2` |
| Closest unscreened formula | `(1/3) × (α/π)^3 × (mμ/mπ⁰)^2` (0.148σ) |

## Stress-Test Guardrail Assessment

A result is **guardrail-screened** only if these first-pass mechanical filters hold:
1. z < 1.0 (within 1σ)
2. C ≤ 1 free real-valued parameter
3. P(random match) < 1% within the family
4. Not a fitted reference row or known SM contribution

This screen is not a discovery, anomaly-resolution, or physical-mechanism test.
Before any stronger interpretation, EXP-0010 needs multiple-testing correction,
bootstrap stability under target/constant uncertainty, alternate-target comparison,
cross-observable checks, and a pre-registered physical-motivation review.

**Global verdict: STRESS_TEST_HIT**

At least one predicted formula passes the first-pass mechanical screen.
The result remains an inconclusive stress-test observation; no physical
mechanism, anomaly resolution, or theoretical explanation is claimed.

## Limitations

- This search uses the data-driven HVP baseline (~5.1σ). The BMW lattice-QCD result
  reduces the discrepancy to ~1.5σ; matching a formula to a contested target is not
  itself evidence for BSM physics.
- Integer/rational exponent constraints exclude smooth BSM contributions from
  non-trivial loop integrals.
- A null result within these families does not exclude all possible BSM formulas.
- F3 with c≈1/3 has physical motivation (HLbL leading-log estimate) but the
  random baseline for continuous c fails the P<1% threshold.
- The F4 lepton-cascade screen-passing formula has no known SM loop-diagram
  motivation and should remain a stress-test hit, not a public success story.
