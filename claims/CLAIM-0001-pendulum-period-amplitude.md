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

## Evidence Status

`RESULT-0001`, `RESULT-0003`, and `RESULT-0013` together support a bounded,
verification-backed, amplitude-dependent ideal-pendulum benchmark; the evidence
is **valid only within the tested range**.

| Result | Scope | Outcome |
| --- | --- | --- |
| `RESULT-0001` | test 1.1080-1.5708 rad | `VALID_IN_RANGE`; best-model test max relative error 1.8887e-3 |
| `RESULT-0003` | test 1.1080-1.5708 rad | `VALID_IN_RANGE`; theory-aware candidate test max relative error 4.1721e-4 |
| `RESULT-0013` | train 0.0100-2.1683 rad; test 2.1839-3.1000 rad | Strongest positive: `VALID_IN_RANGE`; `model_asymptotic_refined` test max relative error 4.4038e-5 |

The held-out tolerance belongs to the named approximation
(`model_asymptotic_refined`) and its held-out range; it is not transferable to
other models, amplitudes, or the broader qualitative law. The validated negative
boundary `RESULT-0017` (`OVERFITTED`, Gate B PASS) is documented separately and
is not positive support for a formula; it is kept out of this evidence map
because its verdict fails the in-range verification gate.

## Review Recommendation

Promoted from `DRAFT` to `PARTIALLY_SUPPORTED` at `review_tier:
MAINTAINER_REVIEWED` by a maintainer Gate C decision following Option 4 of
`docs/reviews/claim-0001-pendulum-scoped-decision-options.md` (TASK-0796).

`PARTIALLY_SUPPORTED` is the ceiling. Reason:

- the support is range-limited, model-limited, and benchmark-limited
  (`VALID_IN_RANGE`);
- the strongest positive result (`RESULT-0013`) is legacy-untiered and has not
  received an independent Gate B replay; the maintainer accepted its
  reproducible, verification-passing evidence for this Gate C decision;
- near-separatrix behavior and non-ideal pendulums are out of scope.

Do not promote beyond `PARTIALLY_SUPPORTED`, and do not adopt discovery,
exactness, all-amplitude, separatrix-inclusive, or non-ideal wording, unless
future evidence removes those limitations. An independent `RESULT-0013` replay
would further strengthen the claim.

## Scope

Ideal mathematical pendulum, undamped and undriven, benchmarked against the
exact elliptic-integral period reference over the sampled `EXP-0001` amplitudes
up to 3.10 rad. Range-limited approximation evidence, not a discovery of a new
or exact pendulum law.
