# PFF-008: Large-Angle Breakdown Probe for `model_t2_t4_l0`

**Microtask:** PFF-008  
**Campaign:** Pendulum Formula Falsification  
**Probe type:** approximation-breakdown design  
**Candidate:** `model_t2_t4_l0` from `EXP-0001/RUN-0005` (`RESULT-0009`)

## Question

Can a narrow follow-up probe make the large-angle degradation of a strong
non-asymptotic pendulum candidate explicit without turning the observation
into a broad claim about pendulum theory?

This note designs one threshold-style probe for the second-ranked candidate in
`RUN-0005`, `model_t2_t4_l0`.

## Candidate

The candidate formula is:

`1 + a*theta^2 + b*theta^4 + c*log(1/(1-x))`

where:

- `x = sin(theta/2)^2`
- `theta` is the pendulum amplitude in radians
- fitted coefficients on the `RUN-0005` training slice are:
  - `a = -0.02038714090642516`
  - `b = 0.00014338296739137673`
  - `c = 0.3314946278458545`

`RUN-0005` reports this candidate as rank 2 with:

- test mean relative error: `0.001776`
- test max relative error: `0.010935`
- verdict: `PARTIALLY_VALID`

## Proposed Probe

**Approximation under test:** `model_t2_t4_l0` period-ratio prediction.

**Exact reference:** ideal-pendulum period ratio
`T/T0 = (2/pi) * K(sin(theta/2)^2)`, using
`scipy.special.ellipk`.

**Threshold metric:** absolute relative period-ratio error:

`abs(model(theta) - exact(theta)) / exact(theta)`

**Large-angle target interval:** `theta = 2.18..3.10 rad`
(`124.9..177.6 deg`), matching the approximate `RUN-0005` test window.

**Primary threshold:** `1%` relative period-ratio error.

**Secondary calibration thresholds:** `0.1%` and `0.5%` relative error, used
only to understand where degradation begins inside the interval.

## Calibration

The deterministic calibration refit the candidate on the same grid used by
`RUN-0005`:

- amplitude grid: `theta = 0.01..3.10 rad`
- sample count: `200`
- train fraction: `0.7`
- code references:
  - `physics_lab.engines.gauntlet.build_gauntlet_candidates`
  - `physics_lab.engines.formula_discovery.fit_candidate_model`
  - `scipy.special.ellipk`
  - `scipy.optimize.brentq`

Observed signed relative errors:

| Theta (rad) | Theta (deg) | Signed relative error |
| ---: | ---: | ---: |
| `2.18` | `124.905` | `1.012136e-05` |
| `2.60` | `148.969` | `4.635448e-04` |
| `2.80` | `160.428` | `1.529272e-03` |
| `3.00` | `171.887` | `5.060180e-03` |
| `3.10` | `177.617` | `1.093507e-02` |

Threshold crossings inside the large-angle interval:

| Relative-error threshold | First crossing (rad) | First crossing (deg) |
| ---: | ---: | ---: |
| `0.1%` | `2.726997704479` | `156.245459` |
| `0.5%` | `2.998168941613` | `171.782427` |
| `1.0%` | `3.090751749111` | `177.087031` |

## Interpretation

The proposed probe is useful because it separates two facts that can otherwise
blur together in a leaderboard:

1. `model_t2_t4_l0` is strong across much of the configured large-angle test
   window.
2. Its error approaches and then crosses the 1% threshold only near the upper
   edge of that window.

That makes the candidate a good target for a future deterministic
approximation-breakdown artifact: the probe has a clear exact reference, a
single threshold metric, a bounded angle interval, and a concrete crossing
point.

## Limitations

- This note designs and calibrates a probe; it does not add a canonical
  `approximation_probes/` artifact.
- The crossing values depend on the `RUN-0005` training grid and fitted
  coefficients.
- The result is candidate-specific and should not be generalized to all
  logarithmic pendulum candidates.
- The 1% threshold is methodological, not a physical law.
- This note does not promote any claim status.

## Verdict

`PROBE_DESIGNED`.

Recommended future probe: record the first angle at which
`model_t2_t4_l0` exceeds `1%` relative period-ratio error against the exact
elliptic-integral reference over `2.18..3.10 rad`.

`REVIEW_NEEDED` before treating this note as stable campaign memory.
