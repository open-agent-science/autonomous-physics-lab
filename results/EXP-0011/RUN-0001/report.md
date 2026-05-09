# Anharmonic Oscillator Period Benchmark

- Result: `RESULT-0014`
- Run: `RUN-0001`
- Hypothesis: `HYP-0011`
- Task: `TASK-0159`
- Train anharmonicity ratio: `0.0008` to `0.0490`
- Holdout anharmonicity ratio: `0.0512` to `0.1000`
- Stress anharmonicity ratio: `0.1014` to `0.1960`

## Assumptions

- The system is 1D, conservative, undamped, and undriven.
- Quartic coefficients are non-negative; no double-well or softening cases are included.
- The benchmark uses a deterministic period-integral reference rather than an inferred zero-crossing estimate.
- Any fitted empirical correction is benchmark-only and does not imply a canonical physical law.

## Dataset

- Mass: `1.0`
- Stiffness: `1.0`
- Amplitude range: `0.200` to `1.400`
- Quartic coefficients: `0.020, 0.040, 0.060, 0.080, 0.100`
- Sample count: `65`

## Limitations

- This benchmark covers the conservative 1D quartic anharmonic oscillator with V(x) = 1/2 k x^2 + lambda x^4.
- Only non-negative quartic coefficients are included; softening and double-well cases are outside scope.
- Reported verdicts are benchmark-slice statements, not claims about driven, damped, chaotic, or large-parameter regimes.

## Verification

- Verification gate passed: `True`
- harmonic_limit: `PASS`
- perturbative_train_window: `PASS`
- holdout_generalization: `PASS`
- monotonic_hardening: `PASS`
- perturbative_breakdown_mapping: `PASS`

## Candidate Models

| Model | Formula | Complexity | Train mean rel. error | Holdout mean rel. error | Verdict |
| --- | --- | ---: | ---: | ---: | --- |
| model_empirical_quadratic | `T = T0 * (1 + a*epsilon + b*epsilon^2), fit on train slice` | 2 | 0.000023 | 0.001102 | VALID |
| model_perturbative_leading | `T = T0 * (1 - 3/2 * epsilon), epsilon = lambda*A^2/k` | 1 | 0.001960 | 0.018457 | PARTIALLY_VALID |
| model_harmonic | `T = 2*pi*sqrt(m/k)` | 1 | 0.028087 | 0.104330 | OVERFITTED |

## Verdict

`model_empirical_quadratic` is the best model on the configured holdout slice, reported as `VALID`.

## Conclusion

The benchmark establishes a deterministic nonlinear mechanics surface with a reference integral, a perturbative baseline, and an explicit breakdown region.
