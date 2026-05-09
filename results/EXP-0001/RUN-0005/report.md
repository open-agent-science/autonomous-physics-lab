# Pendulum Formula Discovery — Gauntlet (102 Candidates)

- Result: `RESULT-0013`
- Run: `RUN-0005`
- Hypothesis: `HYP-0001`
- Task: `TASK-0110`
- Train range (rad): `0.0100` to `2.1683`
- Test range (rad): `2.1839` to `3.1000`
- Total candidates evaluated: 102

## Limitations

- This workflow evaluates an ideal mathematical pendulum with no damping or driving force.
- Core gauntlet candidates are linear-in-coefficients models fitted by least squares.
- Verdicts apply only to the configured train and test amplitude ranges.
- Core candidates are drawn from a fixed basis of eleven atoms; other functional forms are not tested unless explicitly configured.
- Configured comparison candidates expand the evaluated set but do not make the search exhaustive.
- The leaderboard ranks by composite score; top candidates may still fail separatrix diagnostics.

## Verification (Best Candidate)

- Best candidate: `model_asymptotic_refined`
- Verification gate passed: `True`
- small_angle_limit: `PASS`
- small_angle_window_accuracy: `PASS`
- small_angle_curvature: `PASS`
- large_angle_window_accuracy: `PASS`
- near_separatrix_extrapolation: `PASS`
- separatrix_asymptotic_alignment: `PASS`
- separatrix_log_growth_rate: `PASS`
- evenness: `PASS`
- monotonicity: `PASS`
- dimensional_consistency: `PASS`
- known_small_angle_coefficients: `PLACEHOLDER`

## Top 10 Leaderboard

| Rank | Model ID | Family | Cpx | Test Mean Err | Test Max Err | Verdict | Failure Mode |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | `model_asymptotic_refined` | asymptotic | 3 | 0.000028 | 0.000044 | VALID | none |
| 2 | `model_t2_t4_l0` | mixed | 3 | 0.001776 | 0.010935 | PARTIALLY_VALID | none |
| 3 | `model_t2_x1_l0` | mixed | 3 | 0.002213 | 0.013248 | OVERFITTED | none |
| 4 | `model_t2_x2_l0` | mixed | 3 | 0.003145 | 0.017668 | OVERFITTED | none |
| 5 | `model_t2_l0` | mixed | 2 | 0.004029 | 0.020468 | OVERFITTED | none |
| 6 | `model_t2_t8_l0` | mixed | 3 | 0.003230 | 0.020850 | OVERFITTED | none |
| 7 | `model_t2_t6_l0` | mixed | 3 | 0.004982 | 0.028181 | OVERFITTED | none |
| 8 | `model_phys_constrained_l1` | cross_domain | 2 | 0.010377 | 0.016857 | OVERFITTED | moderate_error |
| 9 | `model_t6_l0` | mixed | 2 | 0.006361 | 0.049171 | OVERFITTED | moderate_error |
| 10 | `model_x1_l0` | log_enhanced | 2 | 0.010080 | 0.035363 | OVERFITTED | moderate_error |

## Failure Mode Summary

- `high_error`: 73 candidate(s)
- `moderate_error`: 22 candidate(s)
- `none`: 7 candidate(s)

## Verdict

Best candidate: `model_asymptotic_refined` with verdict `VALID_IN_RANGE`.
Formula: `(2/pi) * [ln(4) + 0.5*ln(1/m1) + a*m1 + (pi/2-ln(4)-a)*m1^2 + c*m1*ln(1/m1) + d*m1^2*ln(1/m1)] where m1 = cos^2(theta/2)`

## Conclusion

This report describes approximation behavior only within the configured amplitude ranges. It keeps the interpretation benchmark-scoped and range-limited. The leaderboard identifies the best-performing candidate formula under the current benchmark across 102 evaluated deterministic candidates.

## Physics-Constrained Candidate (c = 1/π fixed)

| Property | Value |
| --- | --- |
| Model ID | `model_phys_constrained_l1` |
| Formula | `1 + a*theta^2 + b*x^4 + (1/pi)*x*log(1/(1-x)) [c=0.318310 fixed]` |
| Test mean relative error | `0.010377` |
| Test max relative error | `0.016857` |
| Verdict | `OVERFITTED` |

### Fitted Coefficients

- `a` = `0.04202458`
- `b` = `-0.46431209`
- `c` = `1/π = 0.31830989` (fixed)

### Physical Interpretation

The log coefficient `c = 1/π` is derived from the exact asymptotic expansion
of `K(k²) ≈ ln(4/√(1-k²))` as `k → 1` (near-separatrix limit).
Fixing this coefficient to its theoretically correct value allows the free
parameters `a` and `b` to capture intermediate-angle corrections without
sacrificing near-separatrix divergence behavior.

## High-Precision Asymptotic Candidate (A&S Inspired)

| Property | Value |
| --- | --- |
| Model ID | `model_asymptotic_refined` |
| Formula | `(2/pi) * [ln(4) + 0.5*ln(1/m1) + a*m1 + (pi/2-ln(4)-a)*m1^2 + c*m1*ln(1/m1) + d*m1^2*ln(1/m1)] where m1 = cos^2(theta/2)` |
| Test mean relative error | `2.751872e-05` |
| Test max relative error | `4.403782e-05` |
| Verdict | `VALID` |

### Fitted Coefficients

- `a` = `0.12063134`
- `b` = `0.06387062` (constrained by small-angle limit)
- `c` = `0.11806652`
- `d` = `0.02310461`

### Physical Interpretation

This model uses a 4-term polynomial in `(1-x)` and `(1-x)ln(1-x)` to refine
the basic logarithmic asymptotic expansion from Abramowitz & Stegun.
The `m1^2` coefficient is constrained so the small-angle limit is exact,
while the fitted log terms preserve the near-separatrix divergence diagnostics.
