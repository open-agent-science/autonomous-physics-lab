# Exoplanet null-baseline family audit

- Agent run: `AGENT-RUN-0050`
- Task: `TASK-0483`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: `INCONCLUSIVE`
- Audit class: `BENCHMARK_CONTROL_PANEL`

This sandbox audit compares the frozen CK17-style baseline with deterministic null baselines.
It does not infer composition, habitability, target priority, or a new mass-radius law.

## Axis and slice summary

| axis | slice | rows | CK17 RMSE | best null | classification |
| --- | --- | ---: | ---: | --- | --- |
| `true_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 92 | 0.263350 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `true_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 340 | 0.204175 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `true_mass_with_transit_radius` | `jovian_radius_8_16Re` | 567 | 0.083354 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `true_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 445 | 0.069788 | `nearest_radius_neighbor` | `null_family_matches_or_beats_ck17` |
| `minimum_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 0 | n/a | `None` | `underpowered_slice` |
| `minimum_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 2 | 0.207728 | `uncertainty_band_median` | `underpowered_slice` |
| `minimum_mass_with_transit_radius` | `jovian_radius_8_16Re` | 0 | n/a | `None` | `underpowered_slice` |
| `minimum_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 0 | n/a | `None` | `underpowered_slice` |

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0050/` plus review note.
- Review tier: `none`.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
