# Exoplanet second-snapshot reopen coverage check

- Task: `TASK-0580`
- Campaign profile: `exoplanet-mass-radius`
- Gate: `EXO-SECOND-SNAPSHOT-REOPEN-COVERAGE-GATE-0001`
- Verdict: `RESIDUAL_LANE_REMAINS_CLOSED`

## Method

Committed snapshots are loaded through the exoplanet dataset loader. EXO-0002 row counts are compared with frozen EXO-0001 reference counts only where the gate requires material growth.

## Loader Counts

| snapshot | total rows | pre-filter included | post-filter included | true-mass axis | minimum-mass axis |
| --- | ---: | ---: | ---: | ---: | ---: |
| `EXO-0001` | 6291 | 6157 | 4301 | 1207 | 2 |
| `EXO-0002` | 6298 | 6164 | 4308 | 1208 | 2 |

## Gate Evaluation

- Gate status: `BLOCKED`
- Material snapshot gate: `True`
- Axis separation gate: `True`
- Null-baseline competition: `not_attempted_coverage_gate_failed`
- Reopening lanes: `0`

| axis | slice | EXO-0001 rows | EXO-0002 rows | growth | floor pass | host bins pass | lane reopens | blockers |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `true_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 92 | 92 | 0.000000 | False | False | False | gate_2_per_axis_slice_floor, gate_3_material_growth, gate_5_host_context_coverage |
| `true_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 340 | 340 | 0.000000 | True | True | False | gate_3_material_growth |
| `true_mass_with_transit_radius` | `jovian_radius_8_16Re` | 567 | 568 | 0.001764 | True | True | False | gate_3_material_growth |
| `true_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 445 | 445 | 0.000000 | True | True | False | gate_3_material_growth |
| `minimum_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 0 | 0 | n/a | False | False | False | gate_2_per_axis_slice_floor, gate_3_material_growth, gate_5_host_context_coverage |
| `minimum_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 2 | 2 | 0.000000 | False | False | False | gate_2_per_axis_slice_floor, gate_3_material_growth, gate_5_host_context_coverage |
| `minimum_mass_with_transit_radius` | `jovian_radius_8_16Re` | 0 | 0 | n/a | False | False | False | gate_2_per_axis_slice_floor, gate_3_material_growth, gate_5_host_context_coverage |
| `minimum_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 0 | 0 | n/a | False | False | False | gate_2_per_axis_slice_floor, gate_3_material_growth, gate_5_host_context_coverage |

## Decision

No declared axis/slice clears the frozen coverage gate. EXO-0002 adds seven post-filter rows overall, but the true-mass transit-radius axis grows by only one eligible row and the minimum-mass transit-radius axis remains at two eligible rows. The compact-radius slice remains at 92 rows, below the 150-row floor and with zero material growth.

The Exoplanet residual lane therefore remains closed. The current negative/control memory is preserved, and this task does not authorize residual scoring, CK17 replay, null-baseline competition, claim promotion, or canonical result publication.

## Limitations

- Coverage check only; no CK17 residual metric or null-baseline metric is run.
- EXO-0001 is used only as the frozen reference surface for gate_3 material growth.
- Host-context coverage uses effective-temperature bins as the frozen context field.
- No live fetch, fit tuning, prediction, claim, knowledge, or canonical RESULT artifact is produced.

## Output Routing

- Task verdict: `RESIDUAL_LANE_REMAINS_CLOSED`.
- Canonical destination: `docs/reviews/exoplanet-second-snapshot-reopen-coverage-check.md`.
- Review tier: `none`.
- Gate A: `not_attempted`.
- Gate B: `not_applicable`.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: no axis/slice clears the frozen reopen coverage gate.
