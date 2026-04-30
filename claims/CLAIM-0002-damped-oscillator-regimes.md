---
id: CLAIM-0002
title: Damped Oscillator Regime Structure
domain: classical_mechanics
status: DRAFT
hypothesis_id: HYP-0002
evidence:
  experiments:
    - EXP-0002
  results:
    - RESULT-0002
scope: Initial scope covers exact regime verification for the linear damped harmonic oscillator.
---

# CLAIM-0002: Damped Oscillator Regime Structure

## Statement

The linear damped harmonic oscillator admits analytically distinct underdamped,
critically damped, and overdamped regimes, and these regimes can be verified
with deterministic checks.

## Evidence Status

`RESULT-0002` now exists for the configured benchmark, but this claim remains
`DRAFT` until the result is reviewed and the scope wording is confirmed.

## Review Recommendation

This claim can remain `DRAFT` until a maintainer explicitly reviews the public
wording, but it is a good candidate for eventual promotion to `SUPPORTED`.

Reason:

- `RESULT-0002` passes exact, in-scope verification checks;
- the claim is already scoped to the linear, unforced damped oscillator;
- no known failing verification checks remain within that benchmark scope.

This claim does not currently need to be split. The better next step is a
deliberate maintainer review rather than automatic promotion.

## Scope

Initial scope: linear, unforced damped oscillator dynamics in classical
mechanics.

## Caution

This claim must not be promoted until a result artifact is generated and
reviewed.
