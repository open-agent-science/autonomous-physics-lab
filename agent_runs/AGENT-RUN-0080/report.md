# AGENT-RUN-0080 - NMD-0003 Calibrated GP Residual Extrapolation

**Task:** `TASK-0824`
**Benchmark:** `nmd0003-calibrated-uncertainty-residual-gp`
**Verdict:** `CONTROL_SURVIVING_GAIN_MISCALIBRATED_UNCERTAINTY`
**Calibration verdict:** `UNDERCONFIDENT_HEAVY_TAILED`

## Summary

A deterministic Gaussian-process correction is fit on the frozen NMD-0003 audit baseline (`nmd0003_train_fitted_ols`) residuals over the training split only (no post-AME2020 holdout leakage), then evaluated on the post-AME2020 time-split holdout for extrapolation accuracy AND uncertainty calibration. The deliverable is a calibrated residual model and its diagnostics; no prediction, claim, knowledge entry, or discovery is promoted.

## Model

- Feature basis: `Z, N` standardized on the training split.
- Kernel: `rbf_plus_white_noise`; hyperparameters by `deterministic_marginal_likelihood_lbfgsb_fixed_init`.
- Fitted hyperparameters: sigma_f = `20.742879` MeV, length-scale = `0.136302` (standardized), sigma_n = `0.432527` MeV.
- Training rows: `2309`; holdout rows: `295`; post-AME2020 rows used for fitting: `0`.

## Extrapolation Accuracy (post-AME2020 holdout)

| Model | MAE (MeV) | RMS (MeV) | median abs (MeV) | max abs (MeV) |
| --- | ---: | ---: | ---: | ---: |
| Frozen baseline | `2.979273` | `4.028345` | `2.424405` | `30.134672` |
| GP-corrected | `0.462129` | `1.638935` | `0.243094` | `26.33775` |

GP MAE improvement over baseline: `2.517144` MeV; RMS improvement: `2.38941` MeV.

## Uncertainty Calibration

- Empirical 1 sigma coverage: `0.823729` (expected `0.682689`).
- Empirical 2 sigma coverage: `0.966102` (expected `0.9545`).
- RMS standardized residual: `2.826769` (well-calibrated ~ 1.0).
- Mean predictive sigma: `0.615737` MeV; fraction beyond 2 sigma: `0.033898`.

## Controls-First Decision

| Lane | holdout MAE (MeV) | MAE improvement vs baseline (MeV) |
| --- | ---: | ---: |
| GP correction | `0.462129` | `2.517144` |
| null_shuffled_target_gp | `4.444398` | `-1.465125` |
| smooth_a_gp | `2.331441` | `0.647832` |

- Predeclared survival margin: `0.25` MeV (fixed before reading holdout scores; the established NMD-0003 bounded-sprint convention).
- Best control: `smooth_a_gp` (MAE improvement `0.647832` MeV).
- GP minus best control: `1.869312` MeV; clears margin: `True`.

## Limitations

- Retrospective post-AME2020 time-split evaluation; not a strict blind prediction reveal.
- Single dataset (NMD-0003 / post-AME2020 holdout) and a single model class (RBF Gaussian process on [Z, N] residuals); no model-class sweep.
- The frozen liquid-drop audit baseline is the residual reference; a different frozen baseline would shift the residual surface the GP learns.
- Predictive uncertainty is the GP posterior plus white-noise variance; it does not separately model heavy-tailed exotic-nuclide structure, so tail coverage is the primary calibration limitation.
- Methodology contribution only: no PRED, CLAIM, KNOW, or discovery artifact is created, and improved fit/calibration is not a discovery.

## Output-routing summary

- Task verdict: `CONTROL_SURVIVING_GAIN_MISCALIBRATED_UNCERTAINTY`.
- Calibration verdict: `UNDERCONFIDENT_HEAVY_TAILED`.
- Gate A status: mechanical conditions are met (deterministic replay, verification, input hashes, limitations, pinned engine version/commit, schema-valid, no protected rewrite, no overclaim, dataset provenance); the result is routed to SANDBOX (this agent run plus the review note) rather than a published RESULT, because linking the result into hypothesis evidence is outside this benchmark task's authorized change surface.
- Extrapolation: baseline holdout MAE `2.979273` MeV / RMS `4.028345` MeV vs GP-corrected MAE `0.462129` MeV / RMS `1.638935` MeV (MAE improvement `2.517144` MeV).
- Calibration coverage: 1 sigma `0.823729` (expected `0.682689`), 2 sigma `0.966102` (expected `0.9545`), RMS standardized residual `2.826769`.
- Control-survival margin: GP minus best control (`smooth_a_gp`) MAE improvement = `1.869312` MeV vs predeclared `0.25` MeV (clears: `True`).
- Claim impact: `none` (methodology contribution; no PRED/CLAIM/KNOW/discovery).
- Limitations: retrospective time-split, single dataset, single model class (RBF GP on `[Z, N]` residuals), frozen-baseline-dependent residual surface.
