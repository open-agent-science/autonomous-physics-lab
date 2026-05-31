# AGENT-RUN-0050 - Exoplanet null-baseline family audit

- Task: `TASK-0483`
- Snapshot: `data\exoplanets\exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**
- Audit outcome: `control_sensitive_null_family_audit`

## Boundary

Sandbox-only audit on committed snapshot rows. The runner compares frozen CK17 log-radius residuals against deterministic null-family controls and does not fetch live archive data, refit CK17, inspect a second snapshot, or promote claims.

## Null Baseline Family

| null baseline | status | interpretation |
| --- | --- | --- |
| `per_class_median_residual_shift` | `same_sample_control` | Subtracts the median CK17 residual for rows in the same frozen CK17 mass class on the same axis. |
| `nearest_mass_residual_shift` | `leave_one_neighbor_control` | Subtracts the CK17 residual of the nearest other row in log mass on the same axis. |
| `nearest_radius_residual_shift` | `oracle_like_non_predictive_control` | Subtracts the CK17 residual of the nearest other row in observed log radius; this uses the target coordinate and is diagnostic, not a deployable predictor. |
| `uncertainty_band_median_residual_shift` | `same_sample_control` | Subtracts the median CK17 residual among rows in the same combined mass/radius uncertainty band on the same axis. |

## Slice Summary

| slice | count | CK17 RMSE | best null | best null RMSE | delta CK17-null | status |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `axis_true_mass_with_transit_radius` | 1207 | 0.158170 | uncertainty_band_median_residual_shift | 0.147488 | 0.010683 | weak_null_family_improvement |
| `axis_minimum_mass_with_transit_radius` | 2 | 0.207728 | n/a | n/a | n/a | underpowered |
| `compact_radius_lt1p5Re` | 92 | 0.263350 | per_class_median_residual_shift | 0.237670 | 0.025680 | control_sensitive_null_family_explains |
| `sub_neptune_radius_1p5_4Re` | 340 | 0.204175 | uncertainty_band_median_residual_shift | 0.181152 | 0.023022 | control_sensitive_null_family_explains |
| `jovian_radius_8_16Re` | 567 | 0.083354 | uncertainty_band_median_residual_shift | 0.080421 | 0.002933 | weak_null_family_improvement |
| `hot_jupiter_high_irradiation` | 212 | 0.097906 | nearest_radius_residual_shift | 0.055184 | 0.042723 | control_sensitive_null_family_explains |

## Slice Details

### `axis_true_mass_with_transit_radius`

- Axis: `true_mass_with_transit_radius`
- Rows: 1207
- Classification: `weak_null_family_improvement`
- Explanation: Best null uncertainty_band_median_residual_shift lowers RMSE by 0.010683, below the 0.022 margin.

| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CK17 frozen` | 1207 | 0.104430 | 0.158170 | -0.040844 | 0 |
| `per_class_median_residual_shift` | 1207 | 0.099321 | 0.151360 | -0.009606 | 0 |
| `nearest_mass_residual_shift` | 1207 | 0.139946 | 0.207316 | 0.000514 | 0 |
| `nearest_radius_residual_shift` | 1207 | 0.114761 | 0.193071 | 0.001786 | 0 |
| `uncertainty_band_median_residual_shift` | 1207 | 0.098999 | 0.147488 | -0.015250 | 0 |

### `axis_minimum_mass_with_transit_radius`

- Axis: `minimum_mass_with_transit_radius`
- Rows: 2
- Classification: `underpowered`
- Explanation: Slice has 2 rows, below the 30-row interpretation floor.

| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CK17 frozen` | 2 | 0.152214 | 0.207728 | -0.152214 | 0 |
| `per_class_median_residual_shift` | 2 | 0.141356 | 0.141356 | 0.000000 | 0 |
| `nearest_mass_residual_shift` | 2 | 0.282712 | 0.282712 | 0.000000 | 0 |
| `nearest_radius_residual_shift` | 2 | 0.282712 | 0.282712 | 0.000000 | 0 |
| `uncertainty_band_median_residual_shift` | 2 | 0.000000 | 0.000000 | 0.000000 | 0 |

### `compact_radius_lt1p5Re`

- Axis: `true_mass_with_transit_radius`
- Rows: 92
- Classification: `control_sensitive_null_family_explains`
- Explanation: Best null per_class_median_residual_shift lowers RMSE by 0.025680, at or above the 0.022 margin.

| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CK17 frozen` | 92 | 0.162467 | 0.263350 | -0.146837 | 0 |
| `per_class_median_residual_shift` | 92 | 0.138324 | 0.237670 | -0.116977 | 0 |
| `nearest_mass_residual_shift` | 92 | 0.184035 | 0.283265 | -0.099304 | 0 |
| `nearest_radius_residual_shift` | 92 | 0.175577 | 0.248786 | 0.015352 | 0 |
| `uncertainty_band_median_residual_shift` | 92 | 0.152618 | 0.247852 | -0.121817 | 0 |

### `sub_neptune_radius_1p5_4Re`

- Axis: `true_mass_with_transit_radius`
- Rows: 340
- Classification: `control_sensitive_null_family_explains`
- Explanation: Best null uncertainty_band_median_residual_shift lowers RMSE by 0.023022, at or above the 0.022 margin.

| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CK17 frozen` | 340 | 0.140835 | 0.204175 | -0.100080 | 0 |
| `per_class_median_residual_shift` | 340 | 0.124063 | 0.188046 | -0.046610 | 0 |
| `nearest_mass_residual_shift` | 340 | 0.162126 | 0.233169 | -0.047747 | 0 |
| `nearest_radius_residual_shift` | 340 | 0.195126 | 0.262924 | -0.004084 | 0 |
| `uncertainty_band_median_residual_shift` | 340 | 0.125621 | 0.181152 | -0.072126 | 0 |

### `jovian_radius_8_16Re`

- Axis: `true_mass_with_transit_radius`
- Rows: 567
- Classification: `weak_null_family_improvement`
- Explanation: Best null uncertainty_band_median_residual_shift lowers RMSE by 0.002933, below the 0.022 margin.

| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CK17 frozen` | 567 | 0.061255 | 0.083354 | -0.021209 | 0 |
| `per_class_median_residual_shift` | 567 | 0.061604 | 0.086300 | -0.002454 | 0 |
| `nearest_mass_residual_shift` | 567 | 0.104772 | 0.160061 | 0.008133 | 0 |
| `nearest_radius_residual_shift` | 567 | 0.053272 | 0.107388 | 0.002278 | 0 |
| `uncertainty_band_median_residual_shift` | 567 | 0.058406 | 0.080421 | 0.003185 | 0 |

### `hot_jupiter_high_irradiation`

- Axis: `true_mass_with_transit_radius`
- Rows: 212
- Classification: `control_sensitive_null_family_explains`
- Explanation: Best null nearest_radius_residual_shift lowers RMSE by 0.042723, at or above the 0.022 margin.

| baseline | count | log10 MAE | log10 RMSE | log10 bias | missing predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CK17 frozen` | 212 | 0.076139 | 0.097906 | 0.049184 | 0 |
| `per_class_median_residual_shift` | 212 | 0.081621 | 0.102798 | 0.061782 | 0 |
| `nearest_mass_residual_shift` | 212 | 0.120504 | 0.172495 | 0.070984 | 0 |
| `nearest_radius_residual_shift` | 212 | 0.027069 | 0.055184 | 0.001160 | 0 |
| `uncertainty_band_median_residual_shift` | 212 | 0.090717 | 0.111217 | 0.072518 | 0 |

## Interpretation

The audit is control-oriented. When a simple null baseline lowers RMSE by the declared margin, the slice is treated as control-sensitive rather than stronger physical evidence. Underpowered and minimum-mass outcomes are preserved.

## Limitations

- The audit uses only the committed PSCompPars snapshot and frozen CK17 residuals.
- Null baselines are same-snapshot controls, not independent physical models.
- The nearest-radius baseline uses observed radius to choose a neighbor and is an oracle-like diagnostic, not a deployable predictor.
- The minimum-mass axis is sparse and remains diagnostic-only.
- Slice counts below the interpretation floor are preserved as underpowered rather than retried with tuned cuts.
- No live archive fetch, second-snapshot inspection, CK17 refit, composition inference, habitability inference, target-priority output, prediction entry, canonical result, claim update, or knowledge edit is authorized.
