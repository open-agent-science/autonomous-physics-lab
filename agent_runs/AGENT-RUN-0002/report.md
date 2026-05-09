# Agent Run AGENT-RUN-0002 — Theta2 Negative Baseline

## Scope

This sandbox run tests `HYP-PROPOSAL-0002` and `EXP-PROPOSAL-0002` as a
negative-control pendulum candidate.

It is not a canonical result and does not update the pendulum leaderboard.

## Method

The candidate formula was:

`1 + a*theta^2`.

It was fit on `0.01 <= theta <= 1.10` rad and checked on
`1.10 <= theta <= 1.57` rad, with an additional stress diagnostic over
`1.57 <= theta <= 2.80` rad.

## Metrics

| Slice | Mean relative error | Max relative error |
| --- | ---: | ---: |
| Train | `4.383396e-04` | `1.552664e-03` |
| Test | `6.937606e-03` | `1.515048e-02` |
| Stress | `9.325947e-02` | `2.497787e-01` |

## Verdict

`SANDBOX_FAIL`

The candidate fails the declared `1e-3` test-mean threshold and is retained as
negative sandbox evidence for the first autonomous pendulum pilot.
