# Pendulum Formula Discovery — Gauntlet (100 Candidates)

- Result: `RESULT-0004`
- Run: `RUN-0003`
- Hypothesis: `HYP-0001`
- Task: `TASK-0010`
- Train range (rad): `0.0100` to `1.1002`
- Test range (rad): `1.1080` to `1.5708`
- Total candidates evaluated: 100

## Limitations

- This workflow evaluates an ideal mathematical pendulum with no damping or driving force.
- All 100 candidates are linear-in-coefficients models fitted by least squares.
- Verdicts apply only to the configured train and test amplitude ranges.
- Candidates are drawn from a fixed basis of ten atoms; other functional forms are not tested.
- The leaderboard ranks by composite score; top candidates may still fail separatrix diagnostics.

## Verification (Best Candidate)

- Best candidate: `model_t4_x1`
- Verification gate passed: `True`
- small_angle_limit: `PASS`
- small_angle_window_accuracy: `PASS`
- small_angle_curvature: `PASS`
- large_angle_window_accuracy: `PASS`
- near_separatrix_extrapolation: `FAIL`
- separatrix_asymptotic_alignment: `FAIL`
- separatrix_log_growth_rate: `FAIL`
- evenness: `PASS`
- monotonicity: `PASS`
- dimensional_consistency: `PLACEHOLDER`
- known_small_angle_coefficients: `PLACEHOLDER`

## Top 10 Leaderboard

| Rank | Model ID | Family | Cpx | Test Mean Err | Test Max Err | Verdict | Failure Mode |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | `model_t4_x1` | cross_domain | 2 | 0.000305 | 0.000948 | VALID | none |
| 2 | `model_t2_x1_x4` | cross_domain | 3 | 0.000021 | 0.000068 | VALID | none |
| 3 | `model_t2_x4_l1` | mixed | 3 | 0.000035 | 0.000061 | VALID | none |
| 4 | `model_t2_t4_x4` | cross_domain | 3 | 0.000023 | 0.000143 | VALID | none |
| 5 | `model_t2_t6_x2` | cross_domain | 3 | 0.000034 | 0.000110 | VALID | none |
| 6 | `model_t2_t6_l1` | mixed | 3 | 0.000047 | 0.000181 | VALID | none |
| 7 | `model_t2_t4` | theta_poly | 2 | 0.000635 | 0.001889 | VALID | none |
| 8 | `model_t4_t8_x1` | cross_domain | 3 | 0.000060 | 0.000215 | VALID | none |
| 9 | `model_t2_t6_x1` | cross_domain | 3 | 0.000065 | 0.000248 | VALID | none |
| 10 | `model_t2_t4_t6` | theta_poly | 3 | 0.000071 | 0.000269 | VALID | none |

## Failure Mode Summary

- `high_error`: 43 candidate(s)
- `moderate_error`: 13 candidate(s)
- `none`: 44 candidate(s)

## Verdict

Best candidate: `model_t4_x1` with verdict `VALID_IN_RANGE`.
Formula: `1 + a*theta^4 + b*x`

## Conclusion

This report describes approximation behavior only within the configured amplitude ranges. It does not claim exact discovery or validity near the separatrix. The leaderboard identifies the best-performing candidate formula under the current benchmark across a systematic search of 100 deterministic candidates.
