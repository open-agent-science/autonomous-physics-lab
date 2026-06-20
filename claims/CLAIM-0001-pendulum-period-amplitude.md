---
id: CLAIM-0001
title: Pendulum Period Depends on Amplitude
domain: classical_mechanics
status: PARTIALLY_SUPPORTED
review_tier: MAINTAINER_REVIEWED
hypothesis_id: HYP-0001
evidence:
  experiments:
    - EXP-0001
  results:
    - RESULT-0001
    - RESULT-0003
    - RESULT-0013
scope: >
  Ideal mathematical pendulum (undamped, undriven) benchmarked against the exact
  elliptic-integral period reference, over the sampled EXP-0001 amplitudes up to
  3.10 rad. Range-limited approximation evidence only: valid only within the
  tested range, not exact, not valid at the separatrix theta = pi, and not a
  result for non-ideal (damped, driven, finite-size, elastic, or laboratory)
  pendulums.
---

# CLAIM-0001: Pendulum Period Depends on Amplitude

## Statement

For the ideal mathematical pendulum benchmarked against the exact
elliptic-integral reference, the period is amplitude-dependent, and the
small-angle approximation alone is not exact away from its limiting regime.
Within the sampled `EXP-0001` amplitude ranges up to `3.10` rad, range-limited
correction formulas improve approximation accuracy and are **valid only within
the tested range**. The strongest referenced held-out result has maximum
relative error `4.4038e-5` for `model_asymptotic_refined` on `2.1839`-`3.1000`
rad. This does not establish a globally exact approximation, validity at
`theta = pi`, or a result for non-ideal pendulums.

## Status

`PARTIALLY_SUPPORTED` — `review_tier: MAINTAINER_REVIEWED`.

Promoted from `DRAFT` by a maintainer Gate C decision following Option 4 of
[`docs/reviews/claim-0001-pendulum-scoped-decision-options.md`](../docs/reviews/claim-0001-pendulum-scoped-decision-options.md)
(TASK-0796). `PARTIALLY_SUPPORTED` is the ceiling: the evidence is benchmark-,
model-, and range-limited.

## Evidence

| Result | Scope | Outcome |
| --- | --- | --- |
| `RESULT-0001` | test 1.1080-1.5708 rad | `VALID_IN_RANGE`; best-model test max relative error 1.8887e-3 |
| `RESULT-0003` | test 1.1080-1.5708 rad | `VALID_IN_RANGE`; theory-aware candidate test max relative error 4.1721e-4 |
| `RESULT-0013` | train 0.0100-2.1683 rad; test 2.1839-3.1000 rad | Strongest positive: `VALID_IN_RANGE`; `model_asymptotic_refined` test max relative error 4.4038e-5 |
| `RESULT-0017` | train 0.0100-2.0985 rad; test 2.1135-3.0000 rad | Negative boundary: `OVERFITTED`; test max relative error 2.1261e-2; Gate B replay PASS (verdict unchanged) |

The held-out tolerance belongs to the named approximation
(`model_asymptotic_refined`) and its held-out range; it is not transferable to
other models, amplitudes, or the broader qualitative law. `RESULT-0017` is
negative boundary evidence, not positive support for a formula, and its Gate B
PASS validates only the reproducibility of the `OVERFITTED` result, not the
positive `RESULT-0013` metrics.

## Limitations

- Valid only within the tested amplitude range (up to 3.10 rad); not exact and
  not valid at the separatrix `theta = pi`.
- Ideal mathematical pendulum only; excludes damped, driven, finite-size,
  elastic, and laboratory pendulums.
- The candidate search was not exhaustive.
- The strongest positive result (`RESULT-0013`) is legacy-untiered and has not
  received an independent Gate B replay; the maintainer accepted its
  reproducible, verification-passing evidence for this Gate C decision. An
  independent `RESULT-0013` replay would further strengthen the claim.

## Scope

Ideal mathematical pendulum, undamped and undriven, benchmarked against the
exact elliptic-integral period reference over the sampled `EXP-0001` amplitudes
up to 3.10 rad. Range-limited approximation evidence, not a discovery of a new
or exact pendulum law.
