---
id: CLAIM-0001
title: Pendulum Period Depends on Amplitude
domain: classical_mechanics
status: DRAFT
hypothesis_id: HYP-0001
evidence:
  experiments:
    - EXP-0001
  results:
    - RESULT-0001
    - RESULT-0003
scope: Initial scope covers amplitude correction for the ideal pendulum in classical mechanics.
---

# CLAIM-0001: Pendulum Period Depends on Amplitude

## Statement

For an ideal mathematical pendulum, the period increases with amplitude and
cannot be captured exactly by the small-angle approximation alone.

## Evidence Status

`EXP-0001` has produced `RESULT-0001` and `RESULT-0003`. Together they show a
verification-backed benchmark for low-order and theory-aware pendulum
approximations. This claim remains in `DRAFT` until a human or later workflow
explicitly accepts the suggested evidence update.

## Review Recommendation

Keep this claim in `DRAFT` for now.

Reason:

- the current benchmark is still range-limited;
- the best overall verdict remains `VALID_IN_RANGE`;
- the theory-aware candidate improves near-separatrix behavior, but the overall
  evidence is still benchmark-scoped rather than globally valid.

If a maintainer wants to promote it later, the safest next status is
`PARTIALLY_SUPPORTED` with explicit range-aware wording. A later split could
separate:

- a narrow claim about in-range approximation quality;
- a broader claim about large-amplitude or separatrix-aware behavior.

## Scope

Initial scope: amplitude correction for the ideal pendulum in classical
mechanics.

## Caution

This claim file is a scientific placeholder until reproducible experiment
artifacts are reviewed and the claim status is intentionally updated.
