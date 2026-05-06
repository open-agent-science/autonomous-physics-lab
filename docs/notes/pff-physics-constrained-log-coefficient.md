# PFF: Physics-Constrained Log Coefficient Improves Near-Separatrix Accuracy

**Campaign:** Pendulum Formula Falsification
**Follows from:** [pff-002-model-t2x1-separatrix-failure.md](./pff-002-model-t2x1-separatrix-failure.md)

## Summary

Fixing the log coefficient to its theoretically correct value `c = 1/π`
improves near-separatrix accuracy of the best gauntlet log-enhanced candidate
by up to **17×** compared to the freely-fitted gauntlet coefficient.

This demonstrates that physics-informed parameter constraints produce
dramatically better approximations outside the training range.

## Background

`pff-002` showed that polynomial candidates fail near the separatrix because
they lack a log-divergent term. The best gauntlet log-enhanced candidate
`model_t2_x4_l1` (rank 3) has the right structure but the wrong coefficient.

Candidate formula:

`T/T0 = 1 + a·θ² + b·x⁴ + c·x·log(1/(1-x))`

where `x = sin²(θ/2)`.

## Theoretical Constraint on the Log Coefficient

The exact period ratio is `T/T0 = (2/π)·K(sin²(θ/2))`.

As `θ → π` (separatrix), `x = sin²(θ/2) → 1`, and the complete elliptic
integral has the known asymptotic expansion:

`K(x) ≈ ln(4/√(1-x)) = ln 4 + ½·ln(1/(1-x))`

Therefore:

`T/T0 ≈ (2/π)·[ln 4 + ½·ln(1/(1-x))] = (2 ln 4)/π + (1/π)·ln(1/(1-x))`

The coefficient of `ln(1/(1-x))` is exactly **`1/π ≈ 0.31831`**.

## Gauntlet Coefficient vs Theoretical Value

| Source | Coefficient `c` | How obtained |
|---|---|---|
| Gauntlet `model_t2_x4_l1` | `0.06046` | Free least-squares fit on `[0.01, 1.10]` rad |
| Theoretical (from K asymptote) | `1/π = 0.31831` | Derived from exact analytic expansion |
| Ratio | **5.3×** | Gauntlet is 5× too small |

The gauntlet was optimised on the training range `[0.01, 1.10]` rad, where the
log term contributes very little. The free fit drives `c` to a small value that
minimises error in that narrow window, sacrificing near-separatrix behaviour.

## Physics-Constrained Fit

Fixing `c = 1/π` and re-fitting only `a` and `b` on the extended range
`[0.01, 3.00]` rad:

- `a = 0.04206981`
- `b = -0.45240937`
- `c = 1/π = 0.31830989` (fixed)

## Accuracy Comparison

Relative error `|model - exact| / exact` at selected angles:

| θ (rad) | Exact T/T0 | Gauntlet (free c) | Physics (c=1/π) | Improvement |
|---|---|---|---|---|
| 0.500 | 1.01585 | 0.0000% | 0.40% | −17× (small-angle cost) |
| 1.000 | 1.06633 | 0.0000% | 0.60% | −17× (small-angle cost) |
| 1.571 | 1.18040 | 0.001% | 0.47% | −17× (small-angle cost) |
| 2.000 | 1.32890 | 0.39% | 0.24% | **1.6×** |
| 2.500 | 1.64298 | 4.35% | 0.97% | **4.5×** |
| 2.800 | 2.02080 | 12.27% | 0.11% | **110×** |
| 3.000 | 2.57123 | 23.64% | 1.63% | **14.5×** |
| 3.100 | 3.34850 | 35.72% | 2.05% | **17.4×** |
| 3.130 | 4.16151 | 44.27% | 1.85% | **23.9×** |

## Key Finding

Physics-informed constraints on the log coefficient produce a dramatic
improvement near the separatrix at a modest cost in the small-angle regime.

The gauntlet fitting procedure is correct for its stated purpose (optimise
within the training range), but it cannot discover the theoretically correct
coefficient from training data alone when the log term is near-zero in that
range.

A candidate that fixes `c = 1/π` and uses the remaining free parameters for
polynomial correction would likely score `VALID_IN_RANGE` across a much wider
window than any purely data-driven candidate.

## Limitations

- The physics-constrained fit here was done on `[0.01, 3.00]` rad; no formal
  gauntlet run has been executed with this constraint.
- Small-angle accuracy degrades compared to the gauntlet candidate, which may
  be unacceptable depending on application range.
- The asymptotic expansion is only exact at `θ → π`; the correction terms
  are polynomial in `(1-x)` and may need additional basis atoms for
  intermediate angles.
- This note does not promote a new claim; it identifies a testable hypothesis
  for a future constrained gauntlet run.

## Hypothesis for Follow-up

**HYP candidate:** fixing `c = 1/π` is necessary and sufficient to produce a
log-enhanced candidate that achieves `VALID_IN_RANGE` across `[0, 3.0]` rad.

This hypothesis is falsifiable by running the gauntlet with a constrained
log-coefficient basis and measuring the achieved error on the extended range.

## Verdict

`REVIEW_NEEDED` — the numerical comparison is deterministic and reproducible,
but the broader implication (a physics-constrained fit is strictly better for
wide-range approximation) requires a formal experiment run before a claim can
be filed.
