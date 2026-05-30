# Exoplanet compact-radius mass-quartile scout

- Agent run: `AGENT-RUN-0049`
- Task: `TASK-0480`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Source slice: `CSN-001` (`AGENT-RUN-0042` / `TASK-0427`)
- Verdict: **INCONCLUSIVE**
- Scout outcome: `compact_slice_underpowered_for_mass_quartile_localization`
- Reproduction status: `match`

## Scope

This scout tests whether the compact-radius residual stress (`CSN-001`, R/Re < 1.5; the only matched-control survivor of the TASK-0427 audit) is concentrated in a mass subrange. It uses only the committed PSCompPars snapshot and frozen CK17 residuals. Mass-quartile (primary) and mass-half (fallback diagnostic) partitions are predeclared before any metric is computed.

No live fetch, baseline refit, composition inference, atmospheric inference, habitability wording, target-priority output, new mass-radius law, prediction entry, canonical result, claim update, or knowledge edit is authorized.

## Result summary

- Compact slice rows: 92 (reproduces `CSN-001` anchor: `yes`).
- Compact slice log10 RMSE: 0.263350; eligible log10 RMSE: 0.158170.

| partition | role | bins | interpretable | survivors | outcome |
| --- | --- | ---: | ---: | --- | --- |
| mass_quartile | primary | 4 | 0 | none | underpowered_no_interpretable_bin |
| mass_half | fallback_diagnostic | 2 | 2 | ['H2'] | localized_residual_stress_in_subrange |

## Interpretation

The compact slice holds 92 eligible rows. At quartile resolution each bin holds roughly 23 rows, below the 30-row interpretation floor, so the predeclared primary partition is underpowered and the headline verdict is `INCONCLUSIVE`: the scout cannot localize the compact-radius residual stress to a mass *quartile* at the current data coverage.

As a coarse supporting diagnostic only (not a verdict driver), the mass-half partition shows the residual stress carried by the upper-mass half: H2 (2.46-99.20 Me, log10 RMSE 0.354521) survives the per-class median and outside-compact matched controls, while the lower-mass half sits at or below the eligible baseline. This is a directional hint that the compact-slice stress concentrates toward higher mass, but it is not established: it rests on a two-bin split and the quartile resolution that would test it is underpowered.

Recommended (not authorized by this run): a data-coverage expansion that lifts the compact slice above ~120 eligible rows would make a predeclared mass-quartile audit interpretable; until then, only a predeclared mass-half audit can be powered, and any such follow-up must keep the upper-mass concentration framed as a benchmark diagnostic rather than a planet-physics conclusion.

## Controls per interpreted bin

- `per_class_median` - per-class CK17 median residual shift on the bin's own rows (controls for mass-class bias).
- `nearest_radius_outside_compact` - radius-matched cohort drawn from eligible rows with R/Re >= 1.5.
- `nearest_mass_outside_compact` - log-mass-matched cohort drawn from eligible rows with R/Re >= 1.5; the key control for a mass-subrange interpretation.
- `sample_size_random_outside_compact` - deterministic seeded same-size random outside-compact draw.

## Limitations

- The compact slice is small; quartile bins fall below the 30-row interpretation floor, so the primary partition is underpowered.
- The mass-half partition is a coarse fallback diagnostic only and does not establish a localized subrange.
- Controls are diagnostic slices, not causal adjustments.
- Bin edges are equal-count contiguous chunks of the mass-sorted compact slice; they are deterministic but not fixed physical mass boundaries.
- No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0049/` and this review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: sandbox-only validation task.
