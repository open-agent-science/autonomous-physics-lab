---
id: CLAIM-0011
title: Range-Limited Adequacy of the Textbook alpha=3.5 Mass-Luminosity Exponent on the DEBCat Main-Sequence Slice
domain: astrophysics
status: DRAFT
hypothesis_id: HYP-0015
evidence:
  experiments:
    - EXP-0015
  results:
    - RESULT-0022
scope: >
  Configured DEBCat main-sequence-compatible slice (stellar mass 0.5-2.0 Msun, 223
  components), controlled baseline benchmark. Range-limited benchmark evidence on a
  heterogeneous-luminosity slice; NOT a universal mass-luminosity law, a
  stellar-evolution claim, a falsification of alpha=3.5, or an application-domain claim.
---

# CLAIM-0011: Range-Limited Adequacy of the Textbook alpha=3.5 Mass-Luminosity Exponent on the DEBCat Main-Sequence Slice

## Statement

On the configured DEBCat main-sequence slice (stellar mass `0.5`-`2.0` Msun, `223`
components), the single textbook mass-luminosity exponent `alpha = 3.5`
(`L` proportional to `M^3.5`), evaluated as a sole frozen baseline, is a
controls-surviving but **materially suboptimal** fit: a train-fitted exponent
(`model_train_fitted_alpha`) fits the slice materially better, while `alpha = 3.5`
still beats the constant null. This is benchmark-scoped, range-limited evidence; it
does **not** falsify `alpha = 3.5` as a textbook relation and makes no universal-law,
stellar-evolution, or application claim.

## Evidence Status

`RESULT-0022` (`EXP-0015`, `AGENT_VALIDATED`, `VALID_IN_RANGE`; an independent Gate B
replay reproduced the metrics and preserved the verdict) supports this bounded
benchmark finding on the frozen DEBCat slice; the evidence is **valid only within the
tested slice**.

| Result | Tier / status | Scope | Outcome |
| --- | --- | --- | --- |
| `RESULT-0022` | `AGENT_VALIDATED` (Gate B replayed) | DEBCat main sequence 0.5-2.0 Msun, 223 components | `VALID_IN_RANGE`; the train-fitted exponent beats the frozen `alpha=3.5` baseline, which in turn beats the constant null |

Luminosities mix catalogue-reported and Stefan-Boltzmann-derived values (per-row
provenance), so residuals inherit that heterogeneity. The DEBCat normalized rows are
CC BY 4.0 (Southworth). A separately-packaged high-mass transfer benchmark
(`TASK-0837` / pending `TASK-0849` Gate-A packaging) indicates the fitted relation
transfers to the disjoint high-mass regime under controls, but it is not yet a
canonical RESULT and is **not** relied on here.

## Review Recommendation

Recommended maintainer Gate C: promote from `DRAFT` to `PARTIALLY_SUPPORTED` at
`review_tier: MAINTAINER_REVIEWED`, keeping the range-limited wording. `RESULT-0022`
is `AGENT_VALIDATED` by independent Gate B replay but **not** maintainer-reviewed, and
the result itself flags that the headline must stay scope-limited
("`alpha=3.5` inadequate as the sole frozen baseline on this slice, NOT falsified").
`PARTIALLY_SUPPORTED` is the ceiling: single-slice, heterogeneous-luminosity,
benchmark-scoped. Do **not** adopt falsification, universal-law, stellar-evolution,
or discovery wording unless future evidence removes those limitations.

## Scope

DEBCat main-sequence-compatible slice (`0.5`-`2.0` Msun, `223` components), controlled
baseline benchmark. Range-limited benchmark evidence, not a discovery, not a
falsification of `alpha = 3.5`, and not a universal mass-luminosity law.

## Caution

This claim is about the configured-benchmark adequacy of a single textbook exponent
on one slice, not about discovering a new stellar law, falsifying `alpha = 3.5`, or
any stellar-structure, evolution, or application conclusion.
