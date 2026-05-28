# AGENT-RUN-0035 — Exoplanet regime residual scout

- Task: TASK-0370
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**

## Boundary

Sandbox-only scout. Uses only committed snapshot rows. Does not fetch live data, does not refit CK17, does not score reveals, and does not produce habitability / biosignature / target-prioritization output.

## Eligible Slice

- Total rows in snapshot: 6291
- Pre-filter included: 6157
- Post-filter included: 4301
- Eligible (true mass + transit radius): 1207
- Eligible log10 RMSE = 0.158170, log10 MAE = 0.104430, log10 bias = -0.040844

## Thresholds

- Minimum regime row count: 30
- Survival log10 RMSE margin: 0.022
- Shuffle seed: 20260524

## Per-Class CK17 Median Log10 Residuals (eligible set)

| class | median log10 residual |
| --- | --- |
| jovian | -0.009588 |
| neptunian | -0.055182 |
| terran | 0.007782 |

## Generated Hypotheses

- Generated: 6
- Executed: 3

### REGIME-001 — `super_earth_to_sub_neptune_transition` (executed_regime)

FGK-host transit slice (4000 K ≤ Teff ≤ 7200 K), planet mass 1.5 ≤ M/M_earth ≤ 12. Tests CK17 residual structure across the super-Earth / sub-Neptune transition.

- Candidate slice: count 225, log10 RMSE 0.156078, log10 MAE 0.116712, log10 bias -0.046247

| control | count | log10 RMSE | log10 MAE | log10 bias |
| --- | --- | --- | --- | --- |
| per_class_median | 225 | 0.149329 | 0.106315 | 0.007535 |
| shuffled_regime | 225 | 0.132075 | 0.091623 | -0.032767 |
| matched_size_neighbor | 225 | 0.158500 | 0.115578 | -0.043647 |

- **Outcome:** `inconclusive`
- candidate log10 RMSE = 0.15607849239524166; eligible log10 RMSE = 0.15817019267448623; strongest control = shuffled_regime (log10 RMSE = 0.13207458089428595); survival margin = 0.022.

### REGIME-002 — `jovian_radius_plateau` (executed_regime)

Mass slice 100 ≤ M/M_earth ≤ 1000 (sub-Jovian to Jovian). Tests the CK17 jovian-segment near-flat-slope residual.

- Candidate slice: count 515, log10 RMSE 0.128217, log10 MAE 0.081607, log10 bias -0.023834

| control | count | log10 RMSE | log10 MAE | log10 bias |
| --- | --- | --- | --- | --- |
| per_class_median | 515 | 0.124299 | 0.079789 | -0.010794 |
| shuffled_regime | 515 | 0.167062 | 0.109549 | -0.044849 |
| matched_size_neighbor | 515 | 0.120508 | 0.079237 | -0.023646 |

- **Outcome:** `regime_residual_lower_than_eligible_only`
- candidate log10 RMSE = 0.12821737098891156; eligible log10 RMSE = 0.15817019267448623; strongest control = matched_size_neighbor (log10 RMSE = 0.12050795972524343); survival margin = 0.022.

### REGIME-003 — `hot_jupiter_high_irradiation` (executed_regime)

Hot Jupiter slice: M > 30 M_earth AND equilibrium temperature > 1500 K. Tests CK17 residual structure in the hot-Jupiter inflated regime.

- Candidate slice: count 212, log10 RMSE 0.097906, log10 MAE 0.076139, log10 bias 0.049184

| control | count | log10 RMSE | log10 MAE | log10 bias |
| --- | --- | --- | --- | --- |
| per_class_median | 212 | 0.102798 | 0.081621 | 0.061782 |
| shuffled_regime | 212 | 0.184238 | 0.111740 | -0.052698 |
| matched_size_neighbor | 212 | 0.124730 | 0.079201 | -0.022859 |

- **Outcome:** `regime_residual_lower_than_eligible_only`
- candidate log10 RMSE = 0.09790644232520128; eligible log10 RMSE = 0.15817019267448623; strongest control = per_class_median (log10 RMSE = 0.10279764761470823); survival margin = 0.022.

### REGIME-004 — `ultra_short_period_irradiation` (generated_only)

Ultra-short-period slice: orbital_period_days < 1. Tests CK17 residual structure for tidally-stressed planets.

- Candidate slice: count 49, log10 RMSE 0.239983, log10 MAE 0.128452, log10 bias -0.097663

- **Outcome:** `generated_not_executed`
- Hypothesis generated and recorded but not executed; kept for review as part of the bounded scout's candidate slate.

### REGIME-005 — `cold_host_transit_subset` (generated_only)

Cool-host slice: Teff < 4000 K (M dwarfs). Tests CK17 residual structure on the M-dwarf transit sub-population.

- Candidate slice: count 156, log10 RMSE 0.208335, log10 MAE 0.115875, log10 bias -0.085844

- **Outcome:** `generated_not_executed`
- Hypothesis generated and recorded but not executed; kept for review as part of the bounded scout's candidate slate.

### REGIME-006 — `warm_host_long_period_subset` (generated_only)

Long-period FGK-host slice: orbital_period_days > 100, Teff between 5000 and 6500 K. Bounded counter-regime for the hot-Jupiter slice.

- Candidate slice: count 39, log10 RMSE 0.225940, log10 MAE 0.168055, log10 bias -0.057894

- **Outcome:** `generated_not_executed`
- Hypothesis generated and recorded but not executed; kept for review as part of the bounded scout's candidate slate.
