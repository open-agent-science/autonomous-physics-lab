# Exoplanet null-baseline family audit

**Task:** `TASK-0483`  
**Agent run:** `AGENT-RUN-0050`  
**Campaign:** Exoplanet Mass-Radius  
**Evidence class:** sandbox-only null-family audit  
**Verdict:** `INCONCLUSIVE`

## Scope

This review packages a deterministic null-baseline family audit on the committed PSCompPars snapshot. It compares frozen CK17 log-radius residuals with simple residual-shift controls and keeps true-mass and minimum-mass rows separate.

No TAP query was run. No live archive row was fetched or inspected. No second snapshot was inspected. No composition, habitability, biosignature, target-priority, prediction, canonical result, claim, or knowledge artifact is produced.

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

## Interpretation

The null-family audit is intentionally conservative. A slice whose CK17 residual RMSE is reduced by a simple null baseline is treated as control-sensitive. That makes the output useful as a benchmark diagnostic, not as a planet-composition or planet-law claim.

The compact-radius result is especially bounded by this rule: it remains a sandbox benchmark diagnostic unless a future maintainer-approved task defines and passes a stronger independent-control or fresh-snapshot reveal.

## Limitations

- The audit uses only the committed PSCompPars snapshot and frozen CK17 residuals.
- Null baselines are same-snapshot controls, not independent physical models.
- The nearest-radius baseline uses observed radius to choose a neighbor and is an oracle-like diagnostic, not a deployable predictor.
- The minimum-mass axis is sparse and remains diagnostic-only.
- Slice counts below the interpretation floor are preserved as underpowered rather than retried with tuned cuts.
- No live archive fetch, second-snapshot inspection, CK17 refit, composition inference, habitability inference, target-priority output, prediction entry, canonical result, claim update, or knowledge edit is authorized.

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0050/` and this review note.
- Review tier: `none`.
- Gate A status: not attempted; no canonical RESULT/PRED artifact is produced.
- Gate B status: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
