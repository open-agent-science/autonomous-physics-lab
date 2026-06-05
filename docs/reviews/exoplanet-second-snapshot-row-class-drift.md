# Exoplanet EXO-0002 overlapping-row mass-class drift

- Task: `TASK-0598`
- Campaign: `exoplanet_mass_radius`
- Protocol class: committed-snapshot row-class drift inspection
- Inputs:
  - `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
  - `data/exoplanets/exo-0002-pscomppars-snapshot.yaml`
- Code reference: `physics_lab/datasets/exoplanets.py`

## Scope

This inspection follows the two overlapping planet-name rows flagged by the
`TASK-0581` EXO-0001/EXO-0002 delta audit as having changed `mass_class`.
It reports source-reference, mass-field, uncertainty, and inclusion-state
details only.

It does not fetch live archive data, compute residuals, refit baselines, alter
row filters, merge true-mass and minimum-mass axes, create prediction entries,
or promote claims.

## Method

The inspection loaded both committed snapshots with
`load_exoplanet_snapshot`, applied the committed inclusion filters with
`apply_inclusion_filters`, joined rows by exact `planet_name`, and selected
overlapping rows whose `mass.mass_class` differed between snapshots.

The deterministic query found exactly two rows:

```text
HD 141937 b
HD 96127 b
```

## Drift rows

| Planet | EXO-0001 row | EXO-0001 mass class | EXO-0001 mass | EXO-0001 post-filter | EXO-0002 row | EXO-0002 mass class | EXO-0002 mass | EXO-0002 post-filter |
| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |
| HD 141937 b | `EXO-0001-04273-hd-141937-b` | `minimum_mass_msini` | 3079.7727 `msini_mearth` | yes | `EXO-0002-00380-hd-141937-b` | `true_mass` | 3591.4609991 `mearth` | yes |
| HD 96127 b | `EXO-0001-03539-hd-96127-b` | `minimum_mass_msini` | 6661.7168 `msini_mearth` | no | `EXO-0002-00652-hd-96127-b` | `true_mass` | 1207.7479466 `mearth` | no |

Both rows keep:

- `row_class: rv_minimum_mass_only`;
- `detection_method: radial_velocity`;
- `radius.radius_class: not_measured`;
- `radius.value: null`;
- `inclusion_status: included`;
- `inclusion_reason: pre_quality_filter_included`.

## Source-reference change

Both `mass_class` changes are accompanied by a source-reference change in the
planet table reference:

| Planet | EXO-0001 planet reference | EXO-0002 planet reference | Discovery reference |
| --- | --- | --- | --- |
| HD 141937 b | Stassun et al. 2017 | Piccinini et al. 2026 | Udry et al. 2002 in both snapshots |
| HD 96127 b | Stassun et al. 2017 | Piccinini et al. 2026 | Gettel et al. 2012 in both snapshots |

The normalized provenance notes mirror the catalog-side provenance flag
change: EXO-0001 records `pl_bmassprov=Msini`, while EXO-0002 records
`pl_bmassprov=Mass`.

## Inclusion interpretation

`HD 141937 b` remains post-filter included in both snapshots. Its row therefore
can enter loader summaries, but the changed `mass_class` must remain visible to
any later replay and must not be pooled with the old minimum-mass axis.

`HD 96127 b` remains excluded after the quality filter in both snapshots. In
EXO-0001 the maximum mass uncertainty ratio is about `0.62`; in EXO-0002 it is
about `0.34`. Both exceed the loader's `0.30` mass-sigma threshold.

The drift is best treated as benign source-catalog metadata drift rather than a
deterministic loader-classification bug. The loader is preserving the committed
snapshot values and not silently rewriting them.

## Verdict

`VALID_IN_RANGE`

The two overlapping `mass_class` changes are explained by catalog source
reference/provenance changes from `Msini` to `Mass`, not by a loader error.
They do not justify altering filters, computing residuals, or merging true-mass
and minimum-mass axes. Later EXO-0002 replay work should keep these rows
auditable in axis-specific diagnostics.

## Limitations

- The inspection uses exact `planet_name` joins only.
- No live NASA Exoplanet Archive fetch was performed.
- No source-paper semantic review was performed beyond the committed
  `source_table_ref` and provenance fields.
- No residual, baseline, or model-performance metric was computed.

## Output routing

- Task verdict: `VALID_IN_RANGE`.
- Canonical destination:
  `docs/reviews/exoplanet-second-snapshot-row-class-drift.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified.
- Publication blocker: none for this review note; any later benchmark replay
  remains blocked on a separate task with axis-specific metrics and null
  controls.
