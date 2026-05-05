# PFF-002: Near-Separatrix Failure Mode — model_t2_x1

**Microtask:** PFF-002  
**Campaign:** Pendulum Formula Falsification  
**Candidate:** `model_t2_x1` (gauntlet rank 24, complexity 2)

## Candidate Formula

`T/T0 = 1 + a·θ² + b·x`, where `x = sin²(θ/2)`

Fitted coefficients from `EXP-0001/RUN-0003` (`RESULT-0004`):
- `a = 0.11260889746783385`
- `b = -0.20127850122572450`

## Gauntlet Context

- Verdict within test range: `VALID`
- Test range: `1.108 – 1.571 rad`
- Test mean relative error: `0.000902`
- Test max relative error: `0.002651`

The candidate passes the gauntlet benchmark comfortably within the test range.

## Near-Separatrix Behaviour

The exact pendulum period ratio is:

`T/T0 = (2/π) · K(sin²(θ/2))`

where `K` is the complete elliptic integral of the first kind. As `θ → π`
(the separatrix), `K(k²) → ∞` logarithmically — the exact period diverges.

`model_t2_x1` cannot reproduce this divergence. At `θ = π`:
- `θ²` → `π² ≈ 9.87` (finite)
- `sin²(θ/2)` → `sin²(π/2) = 1` (finite, bounded)

The model approaches a finite limit `1 + a·π² + b·1 ≈ 1.910`, while the
exact period diverges to infinity.

## Numerical Evidence

Relative error `|model - exact| / exact` beyond the test range:

| θ (rad) | Exact T/T0 | Model T/T0 | Rel. error |
|---|---|---|---|
| 1.571 (test edge) | 1.180342 | 1.177213 | 0.27% |
| 1.800 | 1.250665 | 1.241348 | 0.74% |
| 2.000 | 1.328904 | 1.307916 | 1.58% |
| 2.200 | 1.428790 | 1.385162 | 3.05% |
| 2.500 | 1.642982 | 1.522540 | 7.33% |
| 2.800 | 2.020804 | 1.687390 | 16.5% |
| 3.000 | 2.571234 | 1.813209 | 29.5% |
| 3.100 | 3.348496 | 1.880980 | 43.8% |
| 3.130 | 4.161505 | 1.901946 | 54.3% |
| 3.1415 | 7.235874 | 1.910061 | 73.6% |

At `θ → π`: exact → ∞, model → **1.910** (finite, fixed).

## Failure Mode Classification

**Type:** missing logarithmic divergence

The candidate family `1 + a·θ² + b·sin²(θ/2)` is a linear combination of
bounded functions. Neither `θ²` nor `sin²(θ/2)` can diverge as `θ → π`,
so no linear combination of them can reproduce the logarithmic growth of
`K(sin²(θ/2))` near the separatrix.

This is a structural limitation of the polynomial/trig-power basis, not a
fitting failure. Better coefficients cannot fix it.

Candidates with this failure mode can only be `VALID_IN_RANGE` — they work
within a training window that avoids the separatrix but degrade predictably
as `θ` approaches `π`.

## Mechanism

The exact `K(k²)` near `k → 1` behaves as:

`K(k²) ≈ ln(4 / sqrt(1 - k²))` = `ln(4 / |cos(θ/2)|)`

This logarithmic term grows without bound. A basis without `log(1/(1-x))` or
equivalent separatrix-aware atoms cannot approximate it.

The gauntlet does include log-enhanced atoms (e.g. `model_x1_l1`, rank 26;
`model_t2_x4_l1`, rank 3). Those candidates carry a `l1 = x·log(1/(1-x))`
term that can track the divergence — at the cost of higher complexity.

## Limitations

- Analysis is restricted to `model_t2_x1` from `EXP-0001/RUN-0003`; other
  polynomial candidates have the same structural failure mode but different
  error magnitudes.
- Numerical values use the stored coefficients from the canonical run artifact;
  re-fitting on a different range may shift the crossover point but not the
  asymptotic failure.
- This note does not claim that polynomial candidates are globally wrong;
  they are useful within their training range.

## Verdict

`VALID_IN_RANGE` for `θ ≤ ~1.8 rad` (rel. error below 1%).  
Structural failure beyond that: missing log divergence makes the model
approach a finite asymptote while the exact period diverges.
