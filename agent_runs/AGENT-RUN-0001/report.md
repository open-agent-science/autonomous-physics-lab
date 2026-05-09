# Agent Run AGENT-RUN-0001 — Rational X-Pole Candidate

## Scope

This sandbox run tests `HYP-PROPOSAL-0001` and `EXP-PROPOSAL-0001` inside the
pendulum formula falsification campaign.

It is not a canonical result and does not update the pendulum leaderboard.

## Method

The candidate formula was:

`(1 + a*x) / (1 - b*x)`, with `x = sin^2(theta/2)`.

The exact reference was the ideal pendulum period ratio:

`T/T0 = (2/pi) K(sin^2(theta/2))`.

The candidate was fit on `0.01 <= theta <= 1.10` rad and checked on
`1.10 <= theta <= 1.57` rad, with an additional stress diagnostic over
`1.57 <= theta <= 2.80` rad.

## Metrics

| Slice | Mean relative error | Max relative error |
| --- | ---: | ---: |
| Train | `1.119074e-05` | `4.484870e-05` |
| Test | `8.588075e-04` | `2.681596e-03` |
| Stress | `6.102625e-02` | `2.228621e-01` |

The candidate beats the theta2-only negative baseline on the configured test
slice, but it does not beat the current `t4_x1` reference candidate from the
gauntlet note.

## Verdict

`SANDBOX_PASS`

This means the bounded rational candidate is reviewable as sandbox memory. It
does not mean it should be promoted to canonical result evidence.
