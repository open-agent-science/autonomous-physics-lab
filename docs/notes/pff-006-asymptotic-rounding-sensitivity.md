# PFF-006: Coefficient-Rounding Sensitivity for `model_asymptotic_refined`

**Microtask:** PFF-006  
**Campaign:** Pendulum Formula Falsification  
**Candidate:** `model_asymptotic_refined` from `EXP-0001/RUN-0005` (`RESULT-0013`)

## Question

Does the reported error scale for `model_asymptotic_refined` depend materially
on storing coefficients at full floating-point precision, or is ordinary
decimal presentation precision enough to reproduce the benchmark behavior?

This note compares the stored full-precision coefficients against rounded
coefficient interpretations on the same deterministic grid used by
`RUN-0005`.

## Candidate

The candidate formula is:

`(2/pi) * [ln(4) + 0.5*ln(1/m1) + a*m1 + (pi/2-ln(4)-a)*m1^2 + c*m1*ln(1/m1) + d*m1^2*ln(1/m1)]`

where `m1 = cos^2(theta/2)`.

Stored fitted coefficients:

- `a = 0.12063134260560071`
- `c = 0.11806651633743737`
- `d = 0.023104612364090865`

The `m1^2` coefficient is constrained by the small-angle limit:

`b = pi/2 - ln(4) - a`

## Method

Inputs:

- result artifact: `results/EXP-0001/RUN-0005/metrics.json`
- candidate builder: `physics_lab.engines.gauntlet.build_asymptotic_refined_candidate`
- scoring helper: `physics_lab.engines.scoring.score_model`
- verification helper: `physics_lab.engines.verification.verify_candidate_model`

Procedure:

1. Recreated the `RUN-0005` grid: `theta = 0.01..3.10`, `sample_count = 200`.
2. Used the same `train_fraction = 0.7`.
3. Scored the full-precision coefficients.
4. Replaced `a`, `c`, and `d` with rounded values at 8, 6, 4, 3, and 2 decimal places.
5. Compared train/test relative error and full verification-gate status.

## Results

| Coefficient interpretation | Test mean rel. error | Test max rel. error | Verification gate | Max abs prediction delta vs full test |
| --- | ---: | ---: | --- | ---: |
| Full precision | `2.751872e-05` | `4.403782e-05` | `PASS` | `0.000000e+00` |
| Rounded to 8 decimals | `2.751857e-05` | `4.403769e-05` | `PASS` | `3.913785e-10` |
| Rounded to 6 decimals | `2.749321e-05` | `4.401901e-05` | `PASS` | `8.207041e-08` |
| Rounded to 4 decimals | `2.620687e-05` | `4.291536e-05` | `PASS` | `3.480318e-06` |
| Rounded to 3 decimals | `2.372119e-05` | `4.214089e-05` | `PASS` | `2.066424e-05` |
| Rounded to 2 decimals | `5.861220e-05` | `1.341267e-04` | `FAIL` | `2.146375e-04` |

The 2-decimal interpretation fails the verification gate through
`small_angle_window_accuracy`:

- mean relative error: `3.608237e-06`
- max relative error: `1.055102e-05`

The failure threshold for that check is crossed only after very coarse
rounding.

## Interpretation

Rounding to the report-level precision used for the candidate coefficients
(`8` decimals) is negligible relative to the observed residual scale.
Rounding to `6` decimals is also secondary: the max test error changes by less
than `2e-08` in relative-error units.

Rounding to `4` or `3` decimals still passes the configured verification gate
on this grid, but it changes predictions enough that it should be treated as a
presentation shortcut rather than a faithful archival representation.

Rounding to `2` decimals is material. It increases the max test relative error
by roughly `9e-05` and fails the small-angle window check.

## Limitations

- This is a coefficient-rounding audit for one named candidate only:
  `model_asymptotic_refined`.
- The audit uses the `RUN-0005` configured range and sample grid. It does not
  test arbitrary resampling or alternative train/test splits.
- The result does not prove that all pendulum candidates are insensitive to
  coefficient rounding.
- The result does not promote any claim status.

## Verdict

`VALID_IN_RANGE` for ordinary coefficient presentation precision.

For `model_asymptotic_refined`, coefficient rounding is secondary at `6` to
`8` decimals and not material for the reported residual scale. Coarse
`2`-decimal rounding is material and should not be used for reproducible
benchmark interpretation.

`REVIEW_NEEDED` before treating this note as stable campaign memory.
