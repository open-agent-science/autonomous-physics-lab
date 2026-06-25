---
id: CLAIM-0009
title: Anharmonic Oscillator Period Benchmark
domain: classical_mechanics
status: PARTIALLY_SUPPORTED
review_tier: MAINTAINER_REVIEWED
hypothesis_id: HYP-0011
evidence:
  experiments:
    - EXP-0011
  results:
    - RESULT-0014
    - RESULT-0016
scope: >
  Partially supported on the configured conservative 1D quartic oscillator
  benchmark V(x) = 1/2 k x^2 + lambda x^4 with lambda >= 0; valid only within the
  tested weak/nonlinear range and the predeclared holdout/stress boundaries. Not
  a discovery, not exact, not a universal anharmonic formula, and not valid for
  softening/double-well, damped, driven, chaotic, or strong-anharmonic regimes.
---

# CLAIM-0009: Anharmonic Oscillator Period Benchmark

## Statement

On the configured conservative 1D quartic oscillator benchmark
`V(x) = 1/2 k x^2 + lambda x^4` with `lambda >= 0`, the anharmonic period surface
is partially supported on the configured benchmark: the leading perturbative
correction is valid only within the tested weak range, and the train-fitted
empirical quadratic correction improves the predeclared holdout slice over both
the perturbative and harmonic baselines. The strongest Gate-B-validated evidence
(`RESULT-0016`) reports a holdout mean relative error of `1.10e-3` for the
empirical quadratic model versus `1.85e-2` for the leading perturbative baseline,
with expected stress-slice degradation beginning at anharmonicity ratio `0.1014`.
This does not claim exactness, broad-range validity, or a universal anharmonic
formula.

## Evidence Status

`RESULT-0014` and the Gate-B-validated `RESULT-0016` together support a bounded,
verification-backed benchmark for the configured weak-regime anharmonic period
surface; the evidence is **valid only within the tested range**.

| Result | Tier / status | Scope | Outcome |
| --- | --- | --- | --- |
| `RESULT-0014` | legacy canonical | train ratio 0.0008-0.0490; holdout 0.0512-0.1000 | `VALID_IN_RANGE`; original cited benchmark run, verification PASS |
| `RESULT-0016` | `AGENT_VALIDATED` (Gate B `PASS`) | same configured benchmark | `VALID_IN_RANGE`; empirical-quadratic holdout MRE `1.10e-3` vs perturbative `1.85e-2`; Gate B replay 36 metrics, max absolute drift `0.0`, tolerance `1.0e-09` |

The holdout tolerances belong to the named `model_empirical_quadratic` correction
on its configured benchmark and holdout slice; they are not transferable to other
models, potentials, amplitudes, or regimes. Out-of-range behavior degrades as
expected (stress max relative error `1.13e-1` at anharmonicity `> 0.1014`), which
bounds the claim to the weak regime.

## Review Recommendation

Promoted from `DRAFT` to `PARTIALLY_SUPPORTED` at `review_tier:
MAINTAINER_REVIEWED` by a maintainer Gate C decision following
`docs/reviews/claim-0009-anharmonic-gatec-ratification-packet.md` (TASK-0818).

`PARTIALLY_SUPPORTED` is the current ceiling. Reason:

- the support is range-limited, model-limited, and configured-benchmark-limited
  (`VALID_IN_RANGE`), with known out-of-range stress degradation;
- the strongest evidence (`RESULT-0016`) is `AGENT_VALIDATED` with a Gate B
  replay (max absolute drift `0.0`), which is agent validation, not external
  replication or maintainer-run measurement;
- softening/double-well, damped, driven, chaotic, and strong-anharmonic regimes
  are out of scope.

Do not promote beyond `PARTIALLY_SUPPORTED`, and do not adopt discovery,
exactness, broad-range, or universal-anharmonic-formula wording, unless future
evidence removes those limitations. An independent external replication of
`RESULT-0016` would further strengthen the claim.

## Scope

Conservative 1D oscillator with `V(x) = 1/2 k x^2 + lambda x^4`, non-negative
`lambda`, train anharmonicity ratio `0.0008`-`0.0490`, predeclared holdout
`0.0512`-`0.1000`, and stress boundary from `0.1014`. Range-limited benchmark
evidence, not a discovery of a new or exact anharmonic law.

## Caution

This claim is about configured-benchmark behavior in the weak anharmonic regime,
not about discovering a new physical law or validating softening/double-well,
driven, damped, chaotic, or strong-anharmonic regimes.
