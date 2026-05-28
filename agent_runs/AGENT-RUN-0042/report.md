# AGENT-RUN-0042 - Exoplanet compact/sub-Neptune matched-control audit

- Task: TASK-0427
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **SANDBOX_PASS**
- Pilot reproduction status: `match`

## Boundary

Sandbox-only matched-control audit on committed snapshot rows. The primary axis is true-mass/transit-radius rows; minimum-mass rows are diagnostic-only. The frozen CK17 baseline is not refit.

## Eligible baseline + pilot reproduction

- Eligible true-mass/transit-radius rows: 1207
- Diagnostic minimum-mass/transit-radius rows: 2
- Current eligible log10 RMSE: 0.158170
- Pilot eligible log10 RMSE (AGENT-RUN-0036): 0.158170
- Eligible log10 RMSE delta vs pilot: -0.000000
- Reproduces pilot eligible baseline within 1e-09: `yes`

## Per-slice summary

| slice | label | count | log10 RMSE | pilot RMSE | reproduces | outcome | adverse control | delta vs adverse |
| --- | --- | ---: | ---: | ---: | :-: | --- | --- | ---: |
| CSN-001 | compact_radius_lt1p5Re | 92 | 0.263350 | 0.263350 | yes | residual_stress_above_eligible_and_controls | per_class_median | 0.025680 |
| CSN-002 | sub_neptune_radius_1p5_4Re | 340 | 0.204175 | 0.204175 | yes | control_sensitive_residual_stress | nearest_radius_outside_slice | 0.007627 |
| CSN-003 | compact_or_sub_neptune_radius_lt4Re | 432 | 0.218126 | 0.218126 | yes | control_sensitive_residual_stress | per_class_median | 0.018476 |

## Per-slice control tables

### CSN-001 - compact_radius_lt1p5Re

- Target count: 92
- Target log10 RMSE: 0.263350
- Delta vs eligible: 0.105180

| control | kind | status | count | log10 RMSE | delta target-control |
| --- | --- | --- | ---: | ---: | ---: |
| nearest_radius_outside_slice | matched_cohort | usable_control | 92 | 0.196087 | 0.067263 |
| host_temperature_outside_slice | matched_cohort | usable_control | 90 | 0.158252 | 0.105098 |
| detection_method_outside_slice | matched_cohort | usable_control | 92 | 0.127368 | 0.135982 |
| uncertainty_band_outside_slice | matched_cohort | usable_control | 92 | 0.147538 | 0.115812 |
| sample_size_random_outside | sample_size_matched_random | usable_control | 92 | 0.115060 | 0.148290 |
| per_class_median | residual_shift | usable_control | 92 | 0.237670 | 0.025680 |
| shuffled_radius_label | negative_control_shuffle | usable_control | 92 | 0.748190 | -0.484840 |
| uncertainty_equalized_subset | negative_control_uncertainty | partial_control | 70 | 0.297241 | -0.033891 |
| adverse_nearest_radius_outside_slice | negative_control_adverse | usable_control | 92 | 0.196087 | 0.067263 |

### CSN-002 - sub_neptune_radius_1p5_4Re

- Target count: 340
- Target log10 RMSE: 0.204175
- Delta vs eligible: 0.046004

| control | kind | status | count | log10 RMSE | delta target-control |
| --- | --- | --- | ---: | ---: | ---: |
| nearest_radius_outside_slice | matched_cohort | usable_control | 340 | 0.196548 | 0.007627 |
| host_temperature_outside_slice | matched_cohort | usable_control | 324 | 0.153261 | 0.050914 |
| detection_method_outside_slice | matched_cohort | usable_control | 340 | 0.186336 | 0.017839 |
| uncertainty_band_outside_slice | matched_cohort | partial_control | 336 | 0.172835 | 0.031340 |
| sample_size_random_outside | sample_size_matched_random | usable_control | 340 | 0.156117 | 0.048058 |
| per_class_median | residual_shift | usable_control | 340 | 0.188046 | 0.016128 |
| shuffled_radius_label | negative_control_shuffle | usable_control | 340 | 0.562397 | -0.358222 |
| uncertainty_equalized_subset | negative_control_uncertainty | partial_control | 178 | 0.231909 | -0.027735 |
| adverse_nearest_radius_outside_slice | negative_control_adverse | usable_control | 340 | 0.196548 | 0.007627 |

### CSN-003 - compact_or_sub_neptune_radius_lt4Re

- Target count: 432
- Target log10 RMSE: 0.218126
- Delta vs eligible: 0.059956

| control | kind | status | count | log10 RMSE | delta target-control |
| --- | --- | --- | ---: | ---: | ---: |
| nearest_radius_outside_slice | matched_cohort | usable_control | 432 | 0.131343 | 0.086783 |
| host_temperature_outside_slice | matched_cohort | usable_control | 414 | 0.118057 | 0.100069 |
| detection_method_outside_slice | matched_cohort | usable_control | 432 | 0.125929 | 0.092197 |
| uncertainty_band_outside_slice | matched_cohort | partial_control | 428 | 0.130406 | 0.087721 |
| sample_size_random_outside | sample_size_matched_random | usable_control | 432 | 0.111664 | 0.106463 |
| per_class_median | residual_shift | usable_control | 432 | 0.199651 | 0.018476 |
| shuffled_radius_label | negative_control_shuffle | usable_control | 432 | 0.610140 | -0.392013 |
| uncertainty_equalized_subset | negative_control_uncertainty | partial_control | 248 | 0.252071 | -0.033944 |
| adverse_nearest_radius_outside_slice | negative_control_adverse | usable_control | 432 | 0.131343 | 0.086783 |

## Output Routing

- Task verdict: `SANDBOX_PASS`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0042/` and review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: task scope authorizes sandbox evidence only.
