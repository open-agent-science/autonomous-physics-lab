# Numerical Accuracy and Tolerance Policy

## Purpose

Autonomous Physics Lab must distinguish between:

- numerical error from reference computation;
- error introduced by coefficient rounding or report formatting;
- real model error from an approximation formula.

APL should not treat every non-zero residual as a model failure.
It should report which kind of error is being measured, on what range, and to
what tolerance.

## Core Rules

1. Do not require zero numerical error for a model to be considered valid.
2. Do not describe a model as exact unless exactness is established by symbolic
   proof, formal derivation, or an equivalent deterministic argument.
3. Use range-aware language for approximation results.
4. Report explicit tolerances whenever a validation check depends on numerical
   comparison.
5. Separate reference-computation uncertainty from approximation residuals in
   artifacts, reports, and claim language.

## Preferred Reporting Language

Prefer wording such as:

- "validated in-range to the configured tolerance"
- "mean relative error X on the configured test range"
- "no deviation above tolerance Y observed on the validation grid"
- "approximation residual, not a claim of exact equality"

Avoid wording such as:

- "wrong because error is not zero"
- "100% exact" without symbolic proof
- "identical to the exact solution" based only on floating-point sampling

## Error Categories

### 1. Numerical Reference Error

This is the uncertainty in the reference computation itself, for example from:

- floating-point roundoff;
- quadrature tolerances;
- iterative solver stopping criteria;
- finite sampling grids.

Typical mitigation:

- document the numerical method used for the reference;
- document the tolerance or precision setting;
- compare double-precision references against higher-precision references when
  public claims depend on very small residuals.

### 2. Coefficient-Rounding Error

This is the deviation introduced when fitted coefficients are rounded in human
 reports or compact summaries.

Typical mitigation:

- store full fitted coefficients in machine-readable artifacts;
- treat rounded report coefficients as presentation values only;
- do not recompute benchmark verdicts from shortened coefficients.

### 3. Model Residual

This is the actual approximation gap between the candidate model and the chosen
reference function over the validated range.

This is the quantity that should drive fit-quality verdicts such as
`VALID_IN_RANGE`, `PARTIALLY_VALID`, or `INVALID`.

## Policy for Current Verdicts

APL may keep the existing verdict vocabulary.

For approximation benchmarks, the preferred interpretation is:

- `VALID_IN_RANGE` means the model passed the configured deterministic checks on
  the validated range with the reported residual metrics;
- it does not imply symbolic identity or global validity;
- it should be accompanied by explicit error metrics and validation range.

## Recommended Artifact Fields

When practical, result artifacts should include or evolve toward fields such as:

```yaml
accuracy:
  mean_relative_error: 3.1e-4
  max_relative_error: 9.5e-4
  relative_tolerance: 1.0e-3
  passed_tolerance: true
  validation_range: "configured test range"
  error_interpretation: "approximation residual, not numerical roundoff"
```

This is guidance, not yet a required schema contract.

## High-Precision Audit Rule

When a result is strong enough that public readers may mistake it for an exact
discovery, APL should prefer an explicit audit that compares:

1. the standard reference implementation;
2. a higher-precision reference implementation;
3. the candidate model prediction.

Interpretation rule:

- if the difference between standard and high-precision references is much
  smaller than the model residual, treat the residual as model error;
- if the two are comparable, treat the result as numerically ambiguous until
  the reference computation is strengthened.

## Public Communication Rule

For public summaries, use statements like:

- "Best candidate validated in-range with mean relative error 3.1e-4"
- "No global exactness claim is made"
- "Near-separatrix behavior remains a separate verification problem"

This keeps APL scientifically honest while still communicating strong results.
