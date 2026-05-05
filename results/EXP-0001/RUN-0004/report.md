# Pendulum Formula Discovery — Gauntlet (100 Candidates)

- Result: `RESULT-0008`
- Run: `RUN-0004`
- Hypothesis: `HYP-0001`
- Task: `TASK-0086`
- Train range (rad): `0.0100` to `2.0985`
- Test range (rad): `2.1135` to `3.0000`
- Total candidates evaluated: 100

## Limitations

- This workflow evaluates an ideal mathematical pendulum with no damping or driving force.
- All 100 candidates are linear-in-coefficients models fitted by least squares.
- Verdicts apply only to the configured train and test amplitude ranges.
- Candidates are drawn from a fixed basis of ten atoms; other functional forms are not tested.
- The leaderboard ranks by composite score; top candidates may still fail separatrix diagnostics.

## Verification (Best Candidate)

- Best candidate: `model_t2_x4_l2`
- Verification gate passed: `False`
- small_angle_limit: `PASS`
- small_angle_window_accuracy: `FAIL`
- small_angle_curvature: `PASS`
- large_angle_window_accuracy: `FAIL`
- near_separatrix_extrapolation: `PASS`
- separatrix_asymptotic_alignment: `FAIL`
- separatrix_log_growth_rate: `PASS`
- evenness: `PASS`
- monotonicity: `PASS`
- dimensional_consistency: `PLACEHOLDER`
- known_small_angle_coefficients: `PLACEHOLDER`

## Top 10 Leaderboard

| Rank | Model ID | Family | Cpx | Test Mean Err | Test Max Err | Verdict | Failure Mode |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | `model_t2_x4_l2` | mixed | 3 | 0.004347 | 0.021261 | OVERFITTED | none |
| 2 | `model_t2_t8_x2` | cross_domain | 3 | 0.013831 | 0.027170 | OVERFITTED | moderate_error |
| 3 | `model_t2_t8_l1` | mixed | 3 | 0.008078 | 0.063770 | OVERFITTED | moderate_error |
| 4 | `model_x1_l2` | log_enhanced | 2 | 0.015348 | 0.077104 | OVERFITTED | moderate_error |
| 5 | `model_t2_t8_x1` | cross_domain | 3 | 0.014010 | 0.097797 | OVERFITTED | moderate_error |
| 6 | `model_t2_t6` | theta_poly | 2 | 0.015322 | 0.100917 | OVERFITTED | moderate_error |
| 7 | `model_t2_t4_t8` | theta_poly | 3 | 0.018573 | 0.112545 | OVERFITTED | moderate_error |
| 8 | `model_t4_t8_x1` | cross_domain | 3 | 0.024291 | 0.129910 | OVERFITTED | moderate_error |
| 9 | `model_t2_x2_l1` | mixed | 3 | 0.029290 | 0.115307 | OVERFITTED | moderate_error |
| 10 | `model_t2_t4_x3` | cross_domain | 3 | 0.025089 | 0.137474 | OVERFITTED | moderate_error |

## Failure Mode Summary

- `high_error`: 69 candidate(s)
- `moderate_error`: 30 candidate(s)
- `none`: 1 candidate(s)

## Verdict

Best candidate: `model_t2_x4_l2` with verdict `OVERFITTED`.
Formula: `1 + a*theta^2 + b*x^4 + c*x^2*log(1/(1-x))`

## Conclusion

This report describes approximation behavior only within the configured amplitude ranges. It does not claim exact discovery or validity near the separatrix. The leaderboard identifies the best-performing candidate formula under the current benchmark across a systematic search of 100 deterministic candidates.

## Physics-Constrained Candidate (c = 1/π fixed)

| Property | Value |
| --- | --- |
| Model ID | `model_phys_constrained_l1` |
| Formula | `1 + a*theta^2 + b*x^4 + (1/pi)*x*log(1/(1-x)) [c=0.318310 fixed]` |
| Test mean relative error | `0.013608` |
| Test max relative error | `0.020779` |
| Verdict | `OVERFITTED` |

### Fitted Coefficients

- `a` = `0.04267610`
- `b` = `-0.48560645`
- `c` = `1/π = 0.31830989` (fixed)

### Comparison with Best Unconstrained Log Candidate

| Metric | Unconstrained (`model_t2_x4_l1`) | Constrained (`model_phys_constrained_l1`) |
| --- | ---: | ---: |
| Test mean relative error | `0.072166` | `0.013608` |
| Test max relative error | `0.252768` | `0.020779` |
| Verdict | `OVERFITTED` | `OVERFITTED` |

### Physical Interpretation

The log coefficient `c = 1/π` is derived from the exact asymptotic expansion
of `K(k²) ≈ ln(4/√(1-k²))` as `k → 1` (near-separatrix limit).
Fixing this coefficient to its theoretically correct value allows the free
parameters `a` and `b` to capture intermediate-angle corrections without
sacrificing near-separatrix divergence behavior.
