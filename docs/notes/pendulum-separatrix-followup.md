# Pendulum Separatrix Follow-up

## Purpose

This note explains why the pendulum benchmark received a second canonical run
after the initial public-alpha release candidate state.

## RUN-0001 Failure Mode

`RUN-0001` established a strong in-range pendulum benchmark, but its best
low-order polynomial candidate still failed the non-gating separatrix
diagnostics:

- `near_separatrix_extrapolation`
- `separatrix_asymptotic_alignment`

That was not a bug in the benchmark. It was a real signal that the current
candidate family behaved well on the configured train/test amplitude range while
still breaking down as `theta -> pi`.

## Why TASK-0003 Existed

`TASK-0003` was created to test whether a more theory-aware candidate family
could improve large-angle behavior without rewriting the benchmark around a new
physics problem.

The task intentionally did not broaden the scope to a new benchmark. Instead,
it focused on strengthening the first benchmark where the failure mode was
already visible.

## RUN-0002 Improvement

`RUN-0002` added a theory-aware candidate family with logarithmic structure
near the separatrix.

The most important outcome was not that the new candidate became the global
winner. It did not. The overall best candidate in the configured benchmark
remained `model_theta2_theta4` with verdict `VALID_IN_RANGE`.

The improvement was more precise:

- theory-aware candidate `model_x_x2_log` improved near-separatrix behavior;
- `RUN-0002` documented that improvement explicitly against the `RUN-0001`
  baseline;
- the benchmark now exposes both in-range success and large-angle limitations
  more clearly.

## Remaining Limits

The pendulum benchmark is still range-aware rather than globally exact.

Current limits:

- the best overall verdict remains `VALID_IN_RANGE`;
- non-gating separatrix diagnostics still fail for the best overall candidate;
- the theory-aware candidate improves separatrix behavior but does not solve the
  full exact large-angle problem;
- claim promotion should remain conservative until maintainers intentionally
  review scope language.

## Takeaway

This is a good example of the intended APL loop:

`result -> failure mode -> follow-up task -> improved result -> narrower and clearer knowledge`

The benchmark is stronger now not because it claims a discovery, but because it
describes more honestly where the approximation works and where it still fails.
