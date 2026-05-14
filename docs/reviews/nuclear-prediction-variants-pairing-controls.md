# Nuclear Prediction Variants: Pairing and Odd-Even Controls

**Task:** TASK-0229
**Entries:** PRED-0023, PRED-0024
**Status:** REGISTERED (prospective; not a claim or result)

## Summary

This review note documents the model choice, deterministic calculation path,
target batch, and limitations for the two pairing/odd-even control variants
registered in TASK-0229.

## Model Variants

Both entries derive from the same frozen baseline:
`RESULT-0015::model_fitted_semi_empirical`

Baseline coefficients (from `results/EXP-0012/RUN-0001/result.yaml`):

| Term | Coefficient |
|------|-------------|
| volume | 15.51423612106804 MeV |
| surface | 17.29318120951770 MeV |
| coulomb | 0.68781560915689 MeV |
| asymmetry | 23.84655788394849 MeV |
| pairing | 15.99084511339891 MeV |

### PRED-0023: Pairing +10% sensitivity control

Pairing coefficient multiplied by 1.10:
`aP_023 = 15.990845113398912 × 1.10 = 17.589929624738804 MeV`

**Purpose:** Measures how much a 10% upward perturbation in pairing strength
shifts predictions for nuclei of different parity classes. Odd-A targets
(Co-59, Ni-61) are pairing-insensitive and serve as internal negative controls.

### PRED-0024: Null-pairing control

Pairing coefficient set to zero: `aP_024 = 0.0`

**Purpose:** Measures the contribution of the pairing term by removing it
entirely. Acts as an ablation baseline: the difference between PRED-0024 and
the base model quantifies the full pairing contribution per target nuclide.

## Deterministic Calculation

All predicted values are computed by the following closed-form path:

```
B(Z, N) = aV·A − aS·A^(2/3) − aC·Z·(Z−1)·A^(−1/3) − aA·(N−Z)²/A + δ

δ = +aP/√A   for even-even (Z even, N even)
δ = −aP/√A   for odd-odd  (Z odd,  N odd)
δ = 0         for odd-A    (exactly one of Z, N is odd)

atomic_mass_u = Z·m_H + N·m_n − B / 931.494013
mass_excess_mev = (atomic_mass_u − A) · 931.494013
```

Physical constants used:
- m_H = 1.00782503207 u
- m_n = 1.00866491600 u
- 1 u = 931.494013 MeV

## Target Batch

All four targets are absent from both NMD-0002 and the post-AME2020 holdout
dataset at registration time.

| Nuclide | Z | N | A | Parity | PRED-0023 (MeV) | PRED-0024 (MeV) | Δ (MeV) |
|---------|---|---|---|--------|-----------------|-----------------|---------|
| Co-59 | 27 | 32 | 59 | odd-A | −64.036113 | −64.036113 | 0.000 |
| Ni-60 | 28 | 32 | 60 | even-even | −66.529991 | −64.259140 | −2.271 |
| Ni-61 | 28 | 33 | 61 | odd-A | −66.081026 | −66.081026 | 0.000 |
| Cu-64 | 29 | 35 | 64 | odd-odd | −67.104960 | −69.303702 | +2.199 |

**Key observations (pre-reveal, no measurement comparison):**

- Odd-A targets show zero difference between PRED-0023 and PRED-0024; this
  confirms correct implementation of the pairing delta formula.
- Even-even Ni-60 is ~2.27 MeV more bound in PRED-0023 than in PRED-0024;
  the difference equals `(aP_023 − 0)/√60 = 17.590/7.746 ≈ 2.271 MeV`.
- Odd-odd Cu-64 is ~2.20 MeV less bound in PRED-0023 than in PRED-0024;
  the difference equals `(aP_023 − 0)/√64 = 17.590/8.000 ≈ 2.199 MeV`.
- The sign reversal between even-even and odd-odd is physically expected.

## Limitations

- Prospective registry entries only; no claim or result promotion.
- No TASK-0201 pairing sandbox candidate is being promoted.
- The +10% perturbation and null-pairing ablation are deliberate control
  probes, not fitted improvements.
- The target batch is small (four nuclides); broader coverage requires a
  separate task.
- True prospective prediction status requires later maintainer source-state
  review to confirm the target nuclides were not measured in any committed
  dataset at registration time.

## Verdict

Both entries are correctly structured prospective control variants.
They are registered for future reveal comparison only.
No claim, result, or knowledge promotion is implied.
