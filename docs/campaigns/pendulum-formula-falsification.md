# Pendulum Formula Falsification

## Goal

Use the ideal pendulum period ratio as a falsification-friendly benchmark for
candidate approximation formulas. The aim is to test many candidate forms
against an exact elliptic-integral reference, classify their failure modes, and
keep verdicts explicitly range-aware.

## Why It Matters

This is APL's clearest demonstration benchmark because it combines:

- a known exact reference function;
- a meaningful small-angle regime;
- a hard large-angle regime;
- obvious approximation breakdown near the separatrix;
- deterministic reruns from stored inputs and code.

It shows what APL is for: not "inventing physics," but testing candidate
formulas under reproducible constraints.

## Current Results

Core evidence already exists:

- `EXP-0001/RUN-0001` established the baseline low-order pendulum benchmark.
- `EXP-0001/RUN-0002` added a theory-aware near-separatrix follow-up and made
  the failure mode around the separatrix more explicit.
- `EXP-0001/RUN-0003` evaluated 100 deterministic candidate formulas and
  produced the current strongest public-style result package.
- `TASK-0011` added a precision audit showing the `~3.1e-4` test residual scale
  for the top leaderboard model is model residual, not reference-noise drift.

Current headline result:

- top leaderboard candidate: `model_t4_x1`
- configured test mean relative residual: about `3.052e-4`
- canonical verdict: `VALID_IN_RANGE`
- no symbolic exactness claim
- no global-validity claim

Latest review state:

- `RESULT-0017`, the pendulum gauntlet negative/overfit result, has passed
  independent Gate B replay and is now `AGENT_VALIDATED`.
- `CLAIM-0001` has passed maintainer Gate C as `PARTIALLY_SUPPORTED` at
  `MAINTAINER_REVIEWED`, with narrowed range-limited wording. The status does
  not convert `RESULT-0017` into positive evidence; the overfit run remains
  negative boundary memory.

Start here:

- [Pendulum Gauntlet 100 Summary](../results/pendulum-gauntlet-100-summary.md)
- [Pendulum Gauntlet design note](../notes/pendulum-gauntlet-100.md)
- [Pendulum separatrix follow-up](../notes/pendulum-separatrix-followup.md)

## Open Questions

- Can a future candidate beat the current score while also improving
  near-separatrix behavior?
- Should generated gauntlet model IDs map more directly onto symbolic registry
  checks instead of leaving some checks at `PLACEHOLDER`?
- Which approximation-breakdown probes should become reusable benchmark
  patterns beyond pendulum?
- How should future public wording keep the distinction between approximation
  residual, configured-range validation, and exact reference behavior?

## Recommended Tasks

- public-safe negative-memory packaging of `RESULT-0017`, keeping the
  relationship to the narrowed `CLAIM-0001` wording explicit;
- documentation or validation tasks that tighten pendulum wording without
  changing canonical result artifacts;
- future benchmark tasks only when they preserve range-aware verdict
  discipline and non-gating separatrix diagnostics.

## Recommended Contributor Types

- numerical methods contributors;
- scientific validation and testing contributors;
- documentation contributors who can explain limitations clearly;
- scientific safety reviewers focused on overclaim resistance.

## What Not To Claim

- Do not say the best pendulum formula is exact.
- Do not say the best candidate is valid outside the configured benchmark
  range.
- Do not treat non-gating separatrix diagnostics as passed.
- Do not present this benchmark as a real-world damped or driven pendulum
  result.
- Do not use pendulum accuracy as evidence of "new physics."

## Visualization Ideas

- residual vs amplitude curves for the top models;
- leaderboard scatter plot: error vs complexity score;
- verification-check heatmap for top-ranked candidates;
- train/test range strip with separatrix diagnostics marked separately;
- side-by-side comparison of `RUN-0001`, `RUN-0002`, and `RUN-0003`.
