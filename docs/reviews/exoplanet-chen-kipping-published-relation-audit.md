# TASK-0866 - Chen-Kipping Published-Relation Audit

**Outcome:** `CONTROL_SENSITIVE_NEGATIVE`  
**Promotion gate:** `FAIL`  
**Run:** `AGENT-RUN-0088`

## Scope

This audit tests the frozen Chen and Kipping (2017) mass-to-radius median relation on committed EXO-0002 rows, with EXO-0001 as a compatibility snapshot. No relation parameter, breakpoint, subset rule, or control was changed after scoring.

The tested implementation is a deterministic median equation, not the full probabilistic Forecaster model. Interval calibration and predictive coverage were not tested.

## Frozen Inputs And Split

- Primary: `data/exoplanets/exo-0002-pscomppars-snapshot.yaml`.
- Compatibility: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`.
- Primary axis: included direct true-mass plus transit-radius rows below 13 Jupiter masses.
- Minimum-mass rows: reported separately as diagnostic-only.
- Split: stable planet-name SHA-256 bucket, 80% train and 20% test.
- Controls: train-only global median, CK17-regime median, global power law, per-regime power law, and 32 shuffled-label power laws.

## Subset Counts

| snapshot | entries | direct rows | primary rows | uncertainty rows | boundary rows | train | test |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exo-0002-pscomppars-snapshot` | 6298 | 1449 | 1433 | 1294 | 16 | 1137 | 296 |
| `exo-0001-pscomppars-snapshot` | 6291 | 1448 | 1432 | 1294 | 16 | 1136 | 296 |

## Held-Out Point Metrics

Lower log10 MAE and RMSE are better.

| snapshot | model | log10 MAE | log10 RMSE | bias | within factor 2 |
| --- | --- | ---: | ---: | ---: | ---: |
| `exo-0002-pscomppars-snapshot` | `chen_kipping_frozen` | 0.115533 | 0.181050 | -0.032349 | 0.929054 |
| `exo-0002-pscomppars-snapshot` | `global_median` | 0.370662 | 0.457843 | -0.200512 | 0.510135 |
| `exo-0002-pscomppars-snapshot` | `regime_median` | 0.172426 | 0.251227 | 0.033138 | 0.820946 |
| `exo-0002-pscomppars-snapshot` | `global_power_law` | 0.142372 | 0.198083 | -0.000966 | 0.891892 |
| `exo-0002-pscomppars-snapshot` | `regime_power_law` | 0.111762 | 0.173024 | 0.007867 | 0.929054 |
| `exo-0002-pscomppars-snapshot` | `shuffled_label_power_law` | 0.375850 | 0.413874 | -0.018154 | 0.293919 |
| `exo-0001-pscomppars-snapshot` | `chen_kipping_frozen` | 0.115533 | 0.181050 | -0.032349 | 0.929054 |
| `exo-0001-pscomppars-snapshot` | `global_median` | 0.370556 | 0.456705 | -0.197901 | 0.510135 |
| `exo-0001-pscomppars-snapshot` | `regime_median` | 0.172425 | 0.251227 | 0.033102 | 0.820946 |
| `exo-0001-pscomppars-snapshot` | `global_power_law` | 0.142339 | 0.198086 | -0.001123 | 0.891892 |
| `exo-0001-pscomppars-snapshot` | `regime_power_law` | 0.111751 | 0.173019 | 0.007799 | 0.929054 |
| `exo-0001-pscomppars-snapshot` | `shuffled_label_power_law` | 0.373273 | 0.411105 | -0.017777 | 0.297297 |

## Primary Per-Regime MAE

| regime | test rows | CK17 | global median | regime median | global power law | regime power law | shuffled labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `terran` | 13 | 0.156518 | 0.904904 | 0.172821 | 0.164954 | 0.155727 | 0.726285 |
| `neptunian` | 159 | 0.136182 | 0.464095 | 0.240565 | 0.141541 | 0.128992 | 0.351609 |
| `jovian` | 124 | 0.084760 | 0.194848 | 0.085014 | 0.141070 | 0.085058 | 0.370194 |
| `stellar` | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

## Uncertainty-Aware Check

The common complete-uncertainty mask contains 259 EXO-0002 test rows. Inverse-variance log10 MAE is reported as a sensitivity metric; it is not Forecaster calibration.

| model | weighted log10 MAE | reduced chi-square diagnostic |
| --- | ---: | ---: |
| `chen_kipping_frozen` | 0.097865 | 177.048767 |
| `global_median` | 0.287581 | 1429.506997 |
| `regime_median` | 0.190449 | 713.327853 |
| `global_power_law` | 0.101764 | 203.763825 |
| `regime_power_law` | 0.074171 | 124.964144 |
| `shuffled_label_power_law` | 0.316865 | 1208.936835 |

## Verdict

The frozen relation has EXO-0002 held-out log10 MAE `0.115533`. The best declared control is `regime_power_law` at `0.111762`.

The relation does not clear the predeclared all-controls promotion rule. This is a scoped control-sensitive negative for the median-equation audit, not a judgment about the full probabilistic model.

Failed checks: `primary_beats_regime_power_law`.

## Limitations

- The two snapshots are successive composite-catalog snapshots, not independent instruments or surveys.
- The repository implementation exposes only the median relation; probabilistic interval calibration remains untested.
- Catalog errors and source heterogeneity are not a predictive-scatter model.
- Data-derived controls are valid only for this frozen split and audit direction.
- Brown-dwarf-boundary rows and minimum-mass rows do not determine the primary verdict.

## Sources

- Chen, J. and Kipping, D. M. (2017), ApJ 834, 17, DOI `10.3847/1538-4357/834/1/17`.
- Otegi et al. (2020), A&A 634, A43, `arXiv:1911.04745`, used as transition-regime context only.

## Output Routing

- Task verdict: `CONTROL_SENSITIVE_NEGATIVE`.
- Canonical destination: sandbox `agent_runs/AGENT-RUN-0088/` plus this review note.
- Review tier: `none`.
- Gate A: `not_passed`.
- Gate B: `not_attempted`.
- Claim impact: none.
- Knowledge impact: none.
- Residual lane: `monitor_only`.
