# Pendulum Formula Discovery

- Result: `RESULT-0003`
- Run: `RUN-0002`
- Hypothesis: `HYP-0001`
- Task: `TASK-0003`
- Train range (rad): `0.0100` to `1.1002`
- Test range (rad): `1.1080` to `1.5708`

## Assumptions

- Ideal mathematical pendulum
- No friction
- No driving force
- theta is measured in radians

## Limitations

- This workflow assumes an ideal mathematical pendulum with no damping or driving force.
- Verdicts apply only to the sampled amplitude ranges used in the train and test split.
- Candidate formulas are limited to predefined polynomial, trigonometric, and theory-aware separatrix approximation families.

## Verification

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
- dimensional_consistency: `PASS`
- known_small_angle_coefficients: `PASS`

## Candidate Models

| Model | Formula | Coefficients | Mean Relative Error (test) | Max Relative Error (test) | Complexity | Verdict |
| --- | --- | --- | ---: | ---: | ---: | --- |
| model_theta2_theta4 | `1 + a*theta^2 + b*theta^4` | `a=0.06235952, b=0.00398244` | 0.000635 | 0.001889 | 2 | VALID |
| model_x_x2_log | `1 + a*x + b*x^2 + c*x*log(1/(1 - x)) where x = sin(theta/2)^2` | `a=0.25004437, b=-0.06649689, c=0.20616164` | 0.000115 | 0.000417 | 3 | VALID |
| model_x_x2 | `1 + a*x + b*x^2 where x = sin(theta/2)^2` | `a=0.24631141, b=0.18474229` | 0.003317 | 0.009319 | 2 | PARTIALLY_VALID |
| model_theta2 | `1 + a*theta^2` | `a=0.06582719` | 0.007046 | 0.015181 | 1 | OVERFITTED |
| model_sin2 | `1 + a*sin(theta/2)^2` | `a=0.28298542` | 0.015772 | 0.032912 | 1 | OVERFITTED |

## Verdict

Best candidate: `model_theta2_theta4` with verdict `VALID_IN_RANGE`.

## RUN-0001 vs RUN-0002 Comparison

- Baseline run: `RUN-0001` / `RESULT-0001`
- Baseline best model: `model_theta2_theta4`
- Best theory-aware candidate in this run: `model_x_x2_log`

### In-range accuracy

- Baseline mean/max relative error: `0.000635` / `0.001889`
- Theory-aware mean/max relative error: `0.000115` / `0.000417`

### Near-separatrix behavior

- Baseline end-ratio-to-exact: `0.350001`
- Theory-aware end-ratio-to-exact: `0.754633`
- Baseline asymptotic max relative error: `0.649999`
- Theory-aware asymptotic max relative error: `0.245367`

### Complexity and limitations

- Baseline complexity score: `2`
- Theory-aware complexity score: `3`
- Tradeoff: the theory-aware candidate improves separatrix behavior substantially and also improves in-range error, but it pays a higher complexity penalty and still remains range-limited rather than exact.

## Conclusion

This report describes approximation behavior only within the configured train and test amplitude ranges.
It does not claim exact discovery or validity near the separatrix; it identifies the best-performing candidate formula under the current benchmark.
