# Exoplanet compact-radius host-context preflight

- Agent run: `AGENT-RUN-0051`
- Task: `TASK-0481`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**
- Preflight status: `conditional_only_partition_underpowered`

## Scope

This preflight checks host-context metadata coverage before any compact-radius host hypothesis is audited. It uses true-mass rows with transit radii only, defines compact radius as R/Re < 1.5, and reports missingness without fitting a correction model.

No live fetch, baseline refit, correction model, composition, habitability, atmosphere, target-priority, prediction, claim, canonical result, or knowledge output is produced.

## Compact-radius field coverage

| field | present | missing | coverage | interpretable bins | status |
| --- | ---: | ---: | ---: | ---: | --- |
| host Teff | 90 | 2 | 97.8% | 1 | `coverage_usable_partition_underpowered` |
| host metallicity [Fe/H] | 81 | 11 | 88.0% | 1 | `coverage_usable_partition_underpowered` |
| stellar radius | 92 | 0 | 100.0% | 1 | `coverage_usable_partition_underpowered` |
| equilibrium temperature | 70 | 22 | 76.1% | 1 | `conditionally_usable` |
| irradiation flux | 61 | 31 | 66.3% | 0 | `conditionally_usable` |

## Eligible-axis reference coverage

| field | present | missing | coverage | interpretable bins | status |
| --- | ---: | ---: | ---: | ---: | --- |
| host Teff | 1166 | 41 | 96.6% | 4 | `benchmark_usable` |
| host metallicity [Fe/H] | 1093 | 114 | 90.6% | 3 | `benchmark_usable` |
| stellar radius | 1203 | 4 | 99.7% | 4 | `benchmark_usable` |
| equilibrium temperature | 934 | 273 | 77.4% | 3 | `conditionally_usable` |
| irradiation flux | 472 | 735 | 39.1% | 3 | `blocked_by_missingness` |

## Recommendation

- Benchmark-usable compact-radius axes: none.
- Conditional or partition-underpowered axes: ['host_effective_temperature_K', 'host_metallicity_fe_h', 'stellar_radius_rsun', 'equilibrium_temperature_K', 'irradiation_flux_earth_units'].
- Blocked by missingness: none.

No benchmark-axis host-context audit should proceed from this compact slice as-is. A future task would need to explicitly declare a conditional missingness or underpowered-bin analysis. Missingness remains a first-class negative result.

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0051/` and this review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: sandbox-only preflight; no correction model or promoted claim.
