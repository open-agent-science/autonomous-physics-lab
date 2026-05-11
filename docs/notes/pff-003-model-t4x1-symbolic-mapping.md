# PFF-003: Model `model_t4_x1` — Symbolic Structure and Check Coverage

## Model Identity and Explicit Formula

**Model ID:** `model_t4_x1`

**Gauntlet formula (as stored):**

```
T/T0 = 1 + a*theta^4 + b*x
```

where the atom `x` is defined as:

```
x = sin²(θ/2)
```

**Substitution unpacked:**

```
T/T0 = 1 + a·θ⁴ + b·sin²(θ/2)
```

**Fitted coefficients (EXP-0001/RUN-0003):**

- `a = 0.008923301235509813`
- `b = 0.24979180460285416`

### Why the formula is even in θ

Both atoms in this model produce functions that are even in θ:

- `θ⁴` is even by polynomial parity.
- `sin²(θ/2)` is even in θ because `sin²(−θ/2) = sin²(θ/2)`.

This symmetry is physically appropriate: the pendulum period depends on amplitude magnitude, not direction of initial displacement. Both candidate atoms respect this constraint without requiring explicit enforcement.

### Atom decomposition

The model has two non-constant atoms beyond the baseline offset of 1:

| Atom | Expression | Complexity contribution |
|------|-----------|------------------------|
| `theta^4` | θ⁴ | 1 |
| `x` | sin²(θ/2) | 1 |
| constant | 1 | 0 (baseline) |

Total complexity score: **2** (as recorded in result.yaml).

---

## Structural Check Coverage

All structural checks recorded for this model come from EXP-0001/RUN-0003 (`results/EXP-0001/RUN-0003/result.yaml`). The following checks were run against the best-model verdict:

| Check | Status | Key Metric |
|-------|--------|-----------|
| `small_angle_limit` | PASS | predicted T/T0 ≈ 1.000000000 at θ → 0, deviation ≈ 6.24×10⁻¹⁴ |
| `small_angle_window_accuracy` | PASS | MRE ≈ 6.58×10⁻⁷ on θ ∈ [0.001, 0.200] rad |
| `small_angle_curvature` | PASS | estimated second derivative ≈ 0.12490, expected 0.12500, abs error ≈ 1.04×10⁻⁴ |
| `large_angle_window_accuracy` | PASS | MRE ≈ 5.56×10⁻⁴ on θ ∈ [1.371, 1.571] rad |
| `near_separatrix_extrapolation` | FAIL | MRE ≈ 0.140, max RE ≈ 0.630 on θ ∈ [2.356, 3.141] rad |
| `separatrix_asymptotic_alignment` | FAIL | MRE ≈ 0.380 near θ → π (diagnostic only) |

Notes on gating:
- The four PASS checks above are the checks that gate the `VALID_IN_RANGE` verdict.
- `near_separatrix_extrapolation` and `separatrix_asymptotic_alignment` are diagnostic-only; they do **not** gate the current in-range verdict. Their FAIL status means extrapolation beyond π/2 is not supported.

---

## Remaining Symbolic Checks — Placeholder or Unavailable

The following analyses were **not** performed in EXP-0001/RUN-0003 and are not claimed:

- **Symbolic closure:** No derivation has been attempted to show that `1 + a·θ⁴ + b·sin²(θ/2)` is algebraically equivalent to, or a truncation of, any closed-form elliptic-integral expression. This mapping remains an open question.
- **Jacobi/elliptic series derivation:** The exact pendulum period is `T = 4K(sin(θ/2)) · √(L/g)`, where `K` is the complete elliptic integral of the first kind. No term-by-term derivation has been performed to connect the fitted model to the Maclaurin expansion of `K`.
- **Coefficient physical interpretation:** The fitted values `a ≈ 0.00892` and `b ≈ 0.24979` have not been matched to any known rational or closed-form analytic coefficients from elliptic-function theory.
- **Sensitivity to atom basis:** The model was selected from a fixed basis of ten atoms. No analysis has been done to establish whether a different or larger atom set would produce a simpler or more accurate model.

---

## Limitation Statement

All results cited here are valid only within the configured amplitude range of the EXP-0001/RUN-0003 gauntlet:

- Train range: 0.01–1.10 rad
- Test range: 1.11–1.57 rad (≈ π/2)

The verdict `VALID_IN_RANGE` does not extend beyond this range. The separatrix diagnostic failures confirm that the model degrades substantially for θ approaching π. No symbolic closure has been achieved, no complete proof is offered, and this note makes no universal formula identification claim.
