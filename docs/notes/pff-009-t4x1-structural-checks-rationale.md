# PFF-009: Why model_t4_x1 Should Pass Evenness and Monotonicity Checks

## Model

`model_t4_x1` from EXP-0001/RUN-0003 (best composite-score model, complexity 2):

```
T/T0 = 1 + a·θ⁴ + b·sin²(θ/2)
```

Fitted coefficients: a ≈ 0.008923, b ≈ 0.249792 (both positive).

## Evenness Check

Both atoms are even in θ:
- `θ⁴` is even by polynomial parity: (−θ)⁴ = θ⁴.
- `sin²(θ/2)` satisfies sin²(−θ/2) = (−sin(θ/2))² = sin²(θ/2).

The pendulum period depends only on amplitude magnitude, not sign of initial
displacement — so evenness is physically required. Both atoms satisfy this
without explicit enforcement.

## Monotonicity Check

For θ ∈ (0, π/2), both atoms are strictly increasing:
- d(θ⁴)/dθ = 4θ³ > 0 for θ > 0.
- d(sin²(θ/2))/dθ = sin(θ/2)cos(θ/2) = (1/2)sin(θ) > 0 for θ ∈ (0, π).

With a > 0 and b > 0, T/T0 is monotonically increasing in amplitude — correct
for a pendulum period.

## What Remains Untested

- No symbolic proof that global monotonicity holds beyond θ = π/2.
- The sign of fitted coefficients is empirical; a different amplitude range
  could in principle yield negative coefficients.
- No formal proof that the sum of these atoms matches the Maclaurin expansion
  of K(sin²(θ/2)).

## Limitation Statement

Rationale applies to fitted coefficients from EXP-0001/RUN-0003 only.
Configured range: 0.01–1.57 rad. No full benchmark validation claimed.
