# Pendulum Gauntlet 100 — Public Scientific Result Summary

## Scope

This package summarizes the current strongest measurable APL result from
`EXP-0001/RUN-0003` (`RESULT-0004`).

It describes:

- what APL tested;
- what passed and what failed;
- what the result means scientifically;
- what remains out of scope.

It does not make the repository public, promote claims automatically, or make a
global exactness claim.

## What Was Tested

APL evaluated 100 deterministic candidate formulas for the ideal pendulum
period ratio `T/T0`, using the exact complete-elliptic-integral reference as
the benchmark target.

The gauntlet used:

- 10 basis atoms drawn from `theta` powers, `x = sin^2(theta/2)` powers, and
  separatrix-aware log terms;
- 100 linear-in-coefficients candidate formulas built from 1-, 2-, and selected
  3-atom subsets;
- deterministic least-squares fitting;
- a fixed train/test split over amplitude in radians;
- deterministic verification checks plus non-gating separatrix diagnostics.

Canonical evidence:

- [result.yaml](../../results/EXP-0001/RUN-0003/result.yaml)
- [leaderboard.md](../../results/EXP-0001/RUN-0003/leaderboard.md)
- [metrics.json](../../results/EXP-0001/RUN-0003/metrics.json)
- [precision_audit.md](../../results/EXP-0001/RUN-0003/precision_audit.md)
- [pendulum-gauntlet-100.md](../notes/pendulum-gauntlet-100.md)

## Why This Benchmark Matters

Pendulum period approximation is a good benchmark for APL because it combines:

- a known exact reference function;
- physically meaningful small-angle structure;
- a nontrivial large-angle regime;
- clear failure modes near the separatrix;
- deterministic reproduction from stored inputs and code.

This makes the benchmark more than a toy demo. It exercises the full APL loop:

- candidate generation;
- deterministic fitting;
- verification checks;
- leaderboard ranking;
- failure-mode interpretation;
- numerical-accuracy audit;
- limitation reporting.

## Main Result

The top leaderboard candidate in `RUN-0003` is `model_t4_x1`:

`1 + a*theta^4 + b*x`, where `x = sin^2(theta/2)`

Stored coefficients from the canonical artifact:

- `a = 0.008923301235509813`
- `b = 0.24979180460285416`

Configured ranges:

- train range: `0.0100` to `1.1002` rad
- test range: `1.1080` to `1.5708` rad

Key interpretation:

- the top leaderboard candidate is chosen by composite score, not by raw test
  error alone;
- some 3-term models have lower raw test residuals;
- `model_t4_x1` ranks first because it achieves strong configured-range
  accuracy with lower complexity.

## Key Numbers

For the top leaderboard candidate `model_t4_x1`:

| Metric | Value |
| --- | ---: |
| Total candidates tested | 100 |
| Complexity score | 2 |
| Train mean relative error | `3.580313074575558e-06` |
| Test mean relative error | `3.0524596412228103e-04` |
| Test max relative error | `9.480571262666894e-04` |
| Best verdict in canonical result | `VALID_IN_RANGE` |

Important nuance:

- the lowest raw test mean residual in the score table is
  `model_t2_x1_x4` at about `2.14e-05`;
- that model has complexity score `3` and ranks below `model_t4_x1` once the
  benchmark's composite score penalizes complexity;
- the public headline should therefore refer to the top leaderboard candidate,
  not imply that `3.1e-4` is the minimum raw residual across all 100 formulas.

## Leaderboard Summary

Verdict counts from the canonical score table:

| Verdict | Count |
| --- | ---: |
| `VALID` | 32 |
| `PARTIALLY_VALID` | 8 |
| `OVERFITTED` | 60 |

Failure-mode summary:

| Failure mode | Count |
| --- | ---: |
| `none` | 44 |
| `moderate_error` | 13 |
| `high_error` | 43 |

Interpretation:

- many candidates are usable in the configured range;
- only a subset stay accurate enough to clear the strongest in-range threshold;
- most poor performers fail by direct test-range error magnitude, not by any
  claim of surprising or novel physics.

## Verification and Failure Modes

For the top leaderboard candidate:

- gating checks passed for small-angle limit, small-angle window accuracy,
  curvature, large-angle window accuracy, evenness, and monotonicity;
- separatrix diagnostics failed, but they are explicitly non-gating for the
  current in-range verdict;
- symbolic dimensional and known-coefficient checks remain `PLACEHOLDER` for
  gauntlet model IDs, because the current symbolic registry does not map these
  generated model names directly.

This means the current result is best described as:

- validated in the configured range;
- not validated near the separatrix;
- not a symbolic exactness result.

## Precision Audit Interpretation

`TASK-0011` added an explicit audit for `RUN-0003`:

- model vs standard reference mean relative error:
  `3.0524596412228103e-04`
- standard vs independent reference mean discrepancy:
  `7.22351219135287e-17`
- full vs rounded prediction mean discrepancy:
  `8.38410000988178e-07`

Audit classification:

- `model_residual`

Interpretation:

- the reported `~3.1e-4` scale is not explained by elliptic-reference numerical
  noise;
- it is also not primarily a rounding artifact from the shortened coefficients
  shown in human-readable docs;
- it should be interpreted as approximation residual on the configured test
  range.

This is the key reason the gauntlet can support a public-facing measurable
result without claiming symbolic exactness.

## What This Result Means

The current honest headline is:

APL evaluated 100 deterministic candidate formulas for the ideal pendulum
period ratio. The top leaderboard candidate validated in the configured range
with about `3.1e-4` mean relative residual on the test split. A dedicated
precision audit classified that error as model residual, not numerical
reference noise. No symbolic exactness claim and no global validity claim are
made.

Why this is useful:

- it demonstrates that APL can run a systematic deterministic search rather
  than a one-off handpicked fit;
- it shows that APL stores evidence, limitations, and failure modes alongside
  the best score;
- it provides a reproducible benchmark artifact that outside reviewers can
  inspect and rerun.

## Limitations

- this benchmark uses an ideal mathematical pendulum only;
- the candidate family is limited to 10 predefined basis atoms;
- all 100 models are linear-in-coefficients least-squares fits;
- verdicts are range-aware and apply only to the configured train/test split;
- all candidates fail the near-separatrix diagnostic checks;
- no symbolic exactness claim is made;
- no global validity claim is made.

## How To Reproduce

Re-run the gauntlet into a temporary output directory:

```bash
python3 -m physics_lab.cli run examples/pendulum_gauntlet.yaml --output-dir /tmp/apl-pendulum-gauntlet
```

Inspect the canonical repository artifacts:

```bash
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

Review the canonical evidence bundle:

- [result.yaml](../../results/EXP-0001/RUN-0003/result.yaml)
- [leaderboard.md](../../results/EXP-0001/RUN-0003/leaderboard.md)
- [metrics.json](../../results/EXP-0001/RUN-0003/metrics.json)
- [precision_audit.md](../../results/EXP-0001/RUN-0003/precision_audit.md)
- [report.md](../../results/EXP-0001/RUN-0003/report.md)

## Bottom Line

APL already has one strong, honest, measurable result:

- a 100-candidate deterministic pendulum gauntlet;
- a top leaderboard model validated to tolerance in the configured range;
- an explicit audit showing the reported error is model residual;
- explicit failure modes and limits;
- no symbolic exactness claim and no global validity claim.
