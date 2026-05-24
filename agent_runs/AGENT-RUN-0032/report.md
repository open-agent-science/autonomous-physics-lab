# AGENT-RUN-0032 — Exoplanet mass-radius frozen-baseline benchmark

- Task: TASK-0361
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Snapshot retrieval (UTC): 2026-05-23T17:15:49Z
- Verdict: **INCONCLUSIVE**

## Loader summary

- Total rows in snapshot: 6291
- Pre-filter included: 6157
- Post-filter included: 4301
- Quality thresholds: sigma_M/M <= 0.3, sigma_R/R <= 0.15

### Exclusion reasons

| reason | count |
| --- | --- |
| mass_and_radius_absent | 16 |
| mass_provenance_requires_source_specific_review | 10 |
| mass_relative_uncertainty_above_threshold | 578 |
| radius_inferred_from_non_transit_method | 34 |
| radius_relative_uncertainty_above_threshold | 1278 |
| solution_type_not_confirmed | 74 |

## Frozen baseline metadata

- Reference: Chen, J. & Kipping, D. M. (2017), ApJ 834, 17, DOI 10.3847/1538-4357/834/1/17
- No new parameters fit on the snapshot: True

| segment | mass lower (M_earth) | mass upper (M_earth) | slope | prefactor |
| --- | --- | --- | --- | --- |
| terran | 0.000 | 2.040 | 0.279 | 1.008000 |
| neptunian | 2.040 | 131.581 | 0.589 | 0.808119 |
| jovian | 131.581 | 26635.680 | -0.044 | 17.738792 |
| stellar | 26635.680 | infinity | 0.881 | 0.001430 |

## Benchmark axes

### Axis: `true_mass_with_transit_radius`

- Eligible row count: 1207

| metric | Chen-Kipping (frozen) | Per-class median null |
| --- | --- | --- |
| count | 1207 | 1207 |
| log10 MAE | 0.104430 | 0.162637 |
| log10 RMSE | 0.158170 | 0.242713 |
| log10 bias | -0.040844 | 0.034503 |
| median log10 residual | -0.025403 | 0.000000 |
| within factor 1.5 | 0.843413 | 0.712510 |
| within factor 2 | 0.944490 | 0.821872 |

#### Per-class log10 RMSE

| class | CK count | CK log10 RMSE | null count | null log10 RMSE |
| --- | --- | --- | --- | --- |
| jovian | 580 | 0.130933 | 580 | 0.130650 |
| neptunian | 588 | 0.182790 | 588 | 0.320246 |
| terran | 39 | 0.124740 | 39 | 0.151880 |

#### Per-detection-method log10 RMSE (Chen-Kipping)

| detection method | count | log10 RMSE | log10 bias |
| --- | --- | --- | --- |
| transit | 1205 | 0.158272 | -0.040788 |
| transit_timing_variation | 2 | 0.074741 | -0.074548 |

### Axis: `minimum_mass_with_transit_radius`

- Eligible row count: 2

| metric | Chen-Kipping (frozen) | Per-class median null |
| --- | --- | --- |
| count | 2 | 2 |
| log10 MAE | 0.152214 | 0.031917 |
| log10 RMSE | 0.207728 | 0.031917 |
| log10 bias | -0.152214 | 0.000000 |
| median log10 residual | -0.152214 | 0.000000 |
| within factor 1.5 | 0.500000 | 1.000000 |
| within factor 2 | 1.000000 | 1.000000 |

#### Per-class log10 RMSE

| class | CK count | CK log10 RMSE | null count | null log10 RMSE |
| --- | --- | --- | --- | --- |
| neptunian | 2 | 0.207728 | 2 | 0.031917 |

#### Per-detection-method log10 RMSE (Chen-Kipping)

| detection method | count | log10 RMSE | log10 bias |
| --- | --- | --- | --- |
| transit | 2 | 0.207728 | -0.152214 |

## Verdict inputs

| axis | CK log10 RMSE | null log10 RMSE | delta (null - CK) | CK beats null |
| --- | --- | --- | --- | --- |
| true_mass_with_transit_radius | 0.158170 | 0.242713 | 0.084543 | True |
| minimum_mass_with_transit_radius | 0.207728 | 0.031917 | -0.175811 | False |

Negative outcomes — null beating CK on either axis — are preserved as valid review evidence and not retried with a tuned baseline.
