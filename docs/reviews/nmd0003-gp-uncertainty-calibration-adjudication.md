# NMD-0003 GP Uncertainty Calibration Adjudication

**Task:** `TASK-0844`
**Source task:** `TASK-0824`
**Source metrics:** `agent_runs/AGENT-RUN-0080/metrics.json`
**Verdict:** `POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED`

## Executive Decision

The TASK-0824 GP correction remains useful as point-estimator evidence,
but its uncertainty envelope is not ready for prediction freeze. The
holdout has a split personality: central coverage is already too wide
at 1 sigma, while a small tail produces a large RMS standardized
residual. A single train-only interval inflation rule therefore cannot
make the envelope both calibrated and sharp enough for future PRED
interval semantics.

## Source Consistency

- Holdout rows: `295` (source metrics `295`).
- GP-corrected MAE: `0.462129` MeV (source `0.462129`).
- Calibration verdict: `HEAVY_TAILED_MISCALIBRATED` (source `HEAVY_TAILED_MISCALIBRATED`).

## Standardized Residual Diagnostics

| diagnostic | train-only LOO | post-AME2020 holdout |
| --- | ---: | ---: |
| count | `2309` | `295` |
| RMS standardized residual | `1.08951` | `2.826769` |
| abs p68 | `0.652357` | `0.725497` |
| abs p95 | `1.705723` | `1.707069` |
| abs p99 | `4.10063` | `3.457904` |
| abs max | `19.017237` | `46.302384` |
| fraction beyond 2 sigma | `0.038545` | `0.033898` |
| fraction beyond 3 sigma | `0.018623` | `0.016949` |

The holdout's nominal 1-sigma coverage is high, but the RMS standardized
residual is also high. That combination is the calibration blocker:
uniformly inflating intervals can suppress the tail RMS only by making
the already-overcovered central region even less calibrated.

## Train-Only Interval Scale Sensitivity

| scale rule | scale | 1-sigma coverage | 2-sigma coverage | RMS z | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `none` | `1.0` | `0.823729` | `0.966102` | `2.826769` | `HEAVY_TAILED_MISCALIBRATED` |
| `loo_rms_scale` | `1.08951` | `0.850847` | `0.972881` | `2.594532` | `HEAVY_TAILED_MISCALIBRATED` |
| `loo_95_abs_quantile_to_2sigma` | `1.0` | `0.823729` | `0.966102` | `2.826769` | `HEAVY_TAILED_MISCALIBRATED` |
| `loo_9545_abs_quantile_to_2sigma` | `1.0` | `0.823729` | `0.966102` | `2.826769` | `HEAVY_TAILED_MISCALIBRATED` |
| `loo_99_abs_quantile_to_3sigma` | `1.366877` | `0.911864` | `0.983051` | `2.06805` | `HEAVY_TAILED_MISCALIBRATED` |

## Per-Region Unscaled Coverage

### `a_band`

| region | count | 1 sigma | 2 sigma | RMS z |
| --- | ---: | ---: | ---: | ---: |
| `light_A_lt_60` | `47` | `0.574468` | `0.893617` | `1.422583` |
| `medium_60_le_A_lt_140` | `162` | `0.839506` | `0.975309` | `3.712929` |
| `heavy_A_ge_140` | `86` | `0.930233` | `0.988372` | `0.57881` |

### `neutron_excess_band`

| region | count | 1 sigma | 2 sigma | RMS z |
| --- | ---: | ---: | ---: | ---: |
| `low_eta_lt_0_15` | `114` | `0.763158` | `0.947368` | `1.033658` |
| `mid_0_15_le_eta_lt_0_25` | `150` | `0.86` | `0.986667` | `0.713972` |
| `high_eta_ge_0_25` | `31` | `0.870968` | `0.935484` | `8.345306` |

### `magic_neighborhood`

| region | count | 1 sigma | 2 sigma | RMS z |
| --- | ---: | ---: | ---: | ---: |
| `near_magic_within_2` | `116` | `0.689655` | `0.948276` | `1.075064` |
| `not_near_magic` | `179` | `0.910615` | `0.977654` | `3.524191` |

## Outlier Ledger

| rank | nuclide | Z | N | A | residual MeV | sigma MeV | z | bands |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `Ga-84` | 31 | 53 | 84 | `26.33775` | `0.568821` | `46.302384` | medium_60_le_A_lt_140; high_eta_ge_0_25; not_near_magic |
| 2 | `Si-23` | 14 | 9 | 23 | `4.121917` | `1.019401` | `4.043471` | light_A_lt_60; low_eta_lt_0_15; near_magic_within_2 |
| 3 | `P-26` | 15 | 11 | 26 | `2.722282` | `0.718036` | `3.791288` | light_A_lt_60; low_eta_lt_0_15; not_near_magic |
| 4 | `Si-24` | 14 | 10 | 24 | `2.317138` | `0.674248` | `3.436624` | light_A_lt_60; low_eta_lt_0_15; near_magic_within_2 |
| 5 | `Sc-51` | 21 | 30 | 51 | `-1.498195` | `0.482504` | `-3.105043` | light_A_lt_60; mid_0_15_le_eta_lt_0_25; near_magic_within_2 |
| 6 | `In-133` | 49 | 84 | 133 | `-1.386253` | `0.531756` | `-2.606935` | medium_60_le_A_lt_140; high_eta_ge_0_25; near_magic_within_2 |
| 7 | `S-27` | 16 | 11 | 27 | `2.699856` | `1.090115` | `2.476669` | light_A_lt_60; low_eta_lt_0_15; not_near_magic |
| 8 | `Zr-80` | 40 | 40 | 80 | `1.658594` | `0.748833` | `2.214905` | medium_60_le_A_lt_140; low_eta_lt_0_15; not_near_magic |
| 9 | `In-129` | 49 | 80 | 129 | `-0.977808` | `0.476479` | `-2.052155` | medium_60_le_A_lt_140; mid_0_15_le_eta_lt_0_25; near_magic_within_2 |
| 10 | `Yb-152` | 70 | 82 | 152 | `1.286418` | `0.636808` | `2.020102` | heavy_A_ge_140; low_eta_lt_0_15; near_magic_within_2 |
| 11 | `Ti-52` | 22 | 30 | 52 | `-0.961791` | `0.482672` | `-1.992639` | light_A_lt_60; mid_0_15_le_eta_lt_0_25; near_magic_within_2 |
| 12 | `P-27` | 15 | 12 | 27 | `0.951716` | `0.517849` | `1.837825` | light_A_lt_60; low_eta_lt_0_15; not_near_magic |

## TASK-0827 Implication

- Prediction freeze impact: `blocked_for_uncertainty`; the GP may be carried
  forward as a point-estimator candidate only.
- A future freeze task would need a predeclared uncertainty model that handles
  the tail/central-coverage mismatch without optimizing on the post-AME2020
  holdout.
- No PRED, CLAIM, RESULT, or KNOW artifact is created by this adjudication.

## Output-Routing Summary

- Canonical destination: `docs/reviews/nmd0003-gp-uncertainty-calibration-adjudication.md`.
- Calibration verdict: `POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED`.
- Result impact: `none`.
- Prediction impact: `none`; prediction freeze remains blocked.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Gate A / Gate B: not applicable; this is an adjudication note, not a RESULT/PRED promotion.
