# AGENT-RUN-0059 - Exoplanet second-snapshot baseline replay preflight

- Task: `TASK-0582`
- Campaign profile: `exoplanet-mass-radius`
- Verdict: `BLOCKED_BY_REOPEN_COVERAGE_GATE`
- Baseline replay status: `not_run_gate_failed`

## Method

The preflight reads committed `EXO-0001` and `EXO-0002` snapshots, applies the shared exoplanet loader filters, and evaluates the frozen second-snapshot reopen coverage gate per mass axis and per declared null-baseline slice. True-mass and minimum-mass rows remain separate. No live fetch, baseline refit, parameter tuning, claim promotion, or target-priority output is allowed.

## Loader Counts

| snapshot | total rows | post-filter included | true-mass axis | minimum-mass axis |
| --- | ---: | ---: | ---: | ---: |
| `exo_0001` | 6291 | 4301 | 1207 | 2 |
| `exo_0002` | 6298 | 4308 | 1208 | 2 |

## Gate Evaluation

- Gate id: `EXO-SECOND-SNAPSHOT-REOPEN-COVERAGE-GATE-0001`
- Material snapshot gate: `True`
- Axis separation gate: `True`
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

No axis/slice clears the frozen reopen coverage gate. The true-mass compact and sub-Neptune slices do not grow at all, the true-mass jovian slice grows by only one eligible row, and the minimum-mass axis remains far below the declared floor. Therefore the frozen CK17 baseline replay and null-baseline comparison are intentionally not run on `EXO-0002` in this task.

This preserves the campaign's negative/control memory: the second snapshot does not materially change the benchmark posture enough to reopen residual scoring.

## Limitations

- Only committed EXO-0001 and EXO-0002 snapshots were read; no live archive fetch was performed.
- The frozen CK17 baseline and declared null baselines were not replayed because no lane cleared the reopen coverage gate.
- True-mass and minimum-mass axes are reported separately and never pooled.
- Host-context coverage uses the frozen effective-temperature context field as a coverage preflight, not as a residual claim.
- No canonical RESULT, prediction registry entry, claim, knowledge, habitability, composition, or target-priority output is produced.

## Output Routing

- Task verdict: `BLOCKED_BY_REOPEN_COVERAGE_GATE`.
- Canonical destination: agent_runs/AGENT-RUN-0059/ plus docs/reviews/exoplanet-second-snapshot-baseline-replay-preflight.md.
- Review tier: `none`.
- Gate A: `not_attempted`.
- Gate B: `not_applicable`.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: second-snapshot reopen coverage gate did not clear.
