# Pendulum Formula Discovery

- Result: `RESULT-0001`
- Run: `RUN-0001`
- Hypothesis: `HYP-0001`
- Task: `TASK-0001`
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
- Candidate formulas are limited to predefined low-order approximation families.

## Verification

- Verification gate passed: `True`
- small_angle_limit: `PASS`
- small_angle_window_accuracy: `PASS`
- evenness: `PASS`
- monotonicity: `PASS`
- dimensional_consistency: `PASS`
- known_small_angle_coefficients: `PASS`

## Candidate Models

| Model | Formula | Coefficients | Mean Relative Error (test) | Max Relative Error (test) | Complexity | Verdict |
| --- | --- | --- | ---: | ---: | ---: | --- |
| model_theta2_theta4 | `1 + a*theta^2 + b*theta^4` | `a=0.06235952, b=0.00398244` | 0.000635 | 0.001889 | 2 | VALID |
| model_x_x2 | `1 + a*x + b*x^2 where x = sin(theta/2)^2` | `a=0.24631141, b=0.18474229` | 0.003317 | 0.009319 | 2 | PARTIALLY_VALID |
| model_theta2 | `1 + a*theta^2` | `a=0.06582719` | 0.007046 | 0.015181 | 1 | OVERFITTED |
| model_sin2 | `1 + a*sin(theta/2)^2` | `a=0.28298542` | 0.015772 | 0.032912 | 1 | OVERFITTED |

## Verdict

Best candidate: `model_theta2_theta4` with verdict `VALID`.

## Conclusion

This report describes approximation behavior within the tested amplitude ranges.
It does not claim exact discovery; it identifies the best-performing candidate formula under the current benchmark.
