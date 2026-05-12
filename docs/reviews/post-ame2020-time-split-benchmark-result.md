# Post-AME2020 Time-Split Benchmark Result

## Scope

`TASK-0197` evaluates the reviewed row-level post-AME2020 holdout from
`TASK-0196` against the frozen `RESULT-0015` baseline and the frozen sandbox
families `HYP-PROPOSAL-0020`, `HYP-PROPOSAL-0021`, and `HYP-PROPOSAL-0022`.

This is retrospective time-split validation. It is not strict blind prediction
and it does not promote any candidate to a claim, canonical result, or
knowledge artifact.

## Method

- Holdout target: `data/nuclear_masses/post_ame2020_holdout.yaml`
- Primary evaluation rows: `295`
- Excluded overlap rows: `1` (`U-238` audit-only)
- Audit-inclusive rows: `296` recorded as non-active metrics only
- Training surface for candidate coefficients: frozen `NMD-0002`
- Baseline: `RESULT-0015::model_fitted_semi_empirical`
- Post-AME2020 rows used for fitting: `0`

Candidate formulas remain frozen. Linear coefficients are fitted once on the
pre-existing NMD-0002 residual surface, then evaluated on the post-AME2020
rows.

## Primary Metrics

Negative `delta_mae_mev` means improvement over the frozen baseline.

| Model | MAE (MeV) | RMSE (MeV) | mean abs error/sigma | delta MAE vs baseline (MeV) |
| --- | ---: | ---: | ---: | ---: |
| `RESULT-0015` frozen baseline | 4.552569 | 5.879637 | 257.318876 | 0.000000 |
| `HYP-PROPOSAL-0020` | 4.552569 | 5.879637 | 257.318876 | 0.000000 |
| `HYP-PROPOSAL-0021` | 4.632212 | 6.049872 | 266.306348 | 0.079643 |
| `HYP-PROPOSAL-0022` | 4.164014 | 5.404950 | 239.392617 | -0.388555 |
| `AME2020 comparison sanity` | 0.196367 | 1.614778 | 6.634150 | -4.356202 |

## Result Summary

- `HYP-PROPOSAL-0020` ties the frozen baseline on this holdout because its
  active shell features do not fire on any primary post-AME2020 row.
- `HYP-PROPOSAL-0021` regresses primary MAE by
  `0.079643` MeV.
- `HYP-PROPOSAL-0022`, the prior overfit negative control, improves primary MAE
  by `0.388555` MeV.
- This mixed outcome is useful negative/diagnostic evidence, not a candidate
  promotion.
- The 296-row audit-inclusive metrics are present in `metrics.json` with
  `active_time_split_metric: false`; active comparisons use the 295-row primary
  holdout so `U-238` remains audit-only.

## Feature Activation

- `HYP-PROPOSAL-0020`: `{'magic_both': 0, 'heavy_double_magic': 0}`
- `HYP-PROPOSAL-0021`: `{'magic_both': 0, 'heavy_double_magic': 0, 'odd_a': 156}`
- `HYP-PROPOSAL-0022`: `{'isospin_asymmetry': 292, 'isospin_asymmetry_sq': 292}`

## Verdict

`INCONCLUSIVE`

The time-split surface does not support the prior lead-candidate story for
`HYP-PROPOSAL-0021`. The negative control's improvement is preserved as a
review-needed signal because it conflicts with earlier structured-holdout
behavior and must not be promoted without a separate task.
