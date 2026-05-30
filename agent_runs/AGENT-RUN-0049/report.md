# AGENT-RUN-0049 - Exoplanet compact-radius mass-quartile scout

- Task: TASK-0480
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Source slice: `CSN-001` (AGENT-RUN-0042)
- Verdict: **INCONCLUSIVE**
- Scout outcome: `compact_slice_underpowered_for_mass_quartile_localization`
- Reproduction status: `match`

## Boundary

Sandbox-only scout on committed snapshot rows. The primary axis is true-mass/transit-radius rows. The frozen CK17 baseline is not refit. Mass-quartile and mass-half partitions are predeclared before metrics; bin edges are derived deterministically from the mass-sorted compact slice.

## Baseline reproduction

- Eligible true-mass/transit-radius rows: 1207
- Eligible log10 RMSE: 0.158170 (anchor 0.158170, reproduces: `yes`)
- Compact slice (R/Re < 1.5) rows: 92
- Compact slice log10 RMSE: 0.263350 (anchor 0.263350, reproduces: `yes`)
- Outside-compact eligible rows (control pool): 1115

## Partition results

### Partition `mass_quartile` (primary, 4 bins)

Predeclared primary partition: 4 equal-count contiguous bins of the compact slice ordered by ascending true mass. Headline scout question (mass-subrange localization) is decided on this partition.

- Partition outcome: `underpowered_no_interpretable_bin`
- Interpretable bins (>= 30 rows): 0 / 4
- Survivor bins: none

| bin | mass min (Me) | mass max (Me) | count | log10 RMSE | delta vs eligible | delta vs compact | interpretable | outcome | adverse control |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :-: | --- | --- |
| Q1 | 0.0700 | 1.4800 | 23 | 0.136054 | -0.022116 | -0.127296 | no | under_minimum_bin | None |
| Q2 | 1.5400 | 2.4400 | 23 | 0.086787 | -0.071383 | -0.176563 | no | under_minimum_bin | None |
| Q3 | 2.4600 | 4.2800 | 23 | 0.172656 | 0.014486 | -0.090694 | no | under_minimum_bin | None |
| Q4 | 4.3000 | 99.2000 | 23 | 0.470702 | 0.312532 | 0.207352 | no | under_minimum_bin | None |

### Partition `mass_half` (fallback_diagnostic, 2 bins)

Predeclared coarse fallback partition: 2 equal-count contiguous bins by ascending true mass. Reported as a supporting diagnostic when the quartile resolution is underpowered; does not drive the headline verdict.

- Partition outcome: `localized_residual_stress_in_subrange`
- Interpretable bins (>= 30 rows): 2 / 2
- Survivor bins: ['H2']

| bin | mass min (Me) | mass max (Me) | count | log10 RMSE | delta vs eligible | delta vs compact | interpretable | outcome | adverse control |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :-: | --- | --- |
| H1 | 0.0700 | 2.4400 | 46 | 0.114111 | -0.044059 | -0.149239 | yes | residual_below_eligible | sample_size_random_outside_compact |
| H2 | 2.4600 | 99.2000 | 46 | 0.354521 | 0.196351 | 0.091171 | yes | residual_stress_above_eligible_and_controls | per_class_median |

## Interpretation

The compact slice has 92 eligible rows. At quartile resolution each bin holds roughly 23 rows, below the 30-row interpretation floor; the quartile partition is therefore reported but not interpreted. The coarser mass-half partition is a supporting diagnostic only and does not drive the verdict.

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0049/` and review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: task scope authorizes sandbox evidence only.
