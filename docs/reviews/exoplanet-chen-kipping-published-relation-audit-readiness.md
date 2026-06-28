# TASK-0859 - Exoplanet Chen-Kipping Published-Relation Audit Readiness

**Verdict:** `READY`

## Scope Boundary

This task opens a new **published-relation-audit** lane for the exoplanet
mass-radius campaign. It does not reopen the residual-discovery lane, does not
run a benchmark metric, does not refit any relation, and does not create a
RESULT, PRED, CLAIM, or KNOW artifact. The residual lane remains monitor-only
under `campaign_profiles/exoplanet-mass-radius.yaml`.

## Published Relations

- Chen & Kipping 2017, "Probabilistic Forecasting of the Masses and Radii of
  Other Worlds", ApJ 834, 17, DOI `10.3847/1538-4357/834/1/17`,
  arXiv:1603.08614. The frozen hypothesis under test is the published
  Forecaster mass-radius relation, including its regime boundaries and
  probabilistic interpretation.
- Otegi et al. 2020, "Revisiting the mass-radius relations for exoplanets below
  120 M_Earth", A&A 634, A43, arXiv:1911.04745. This source is useful as an
  explicit comparator and caveat for the transition between rocky, volatile-rich,
  and giant-planet regimes, especially around the debated super-Earth /
  sub-Neptune boundary.

The repository already contains a deterministic Chen-Kipping-style median
implementation in `physics_lab/engines/exoplanet_mass_radius.py` with frozen
Terran, Neptunian, Jovian, and stellar piecewise constants. That implementation
is adequate for a first point-estimate audit if the audit states that it is
testing the frozen median relation only. A later full Forecaster audit should
pin the official package/version/license or a frozen-equation reproduction and
must test calibration/coverage intervals, not only point error.

## Implementation Route

Recommended route for the next benchmark task: use the deterministic frozen
equation route as the primary path.

Reasons:

- It is already committed, deterministic, and reviewable.
- It avoids a live dependency on the Forecaster package until licensing,
  versioning, stochastic sampling behavior, and reproducible quantile handling
  are explicitly pinned.
- It matches the repository's published-source standard: the relation under
  test is frozen before touching holdout metrics.

If the official Forecaster package is used later, the audit must record the
exact source, license, package or commit version, random seed strategy, and the
quantiles or credible intervals being judged. The median-only route is not a
substitute for testing Forecaster's probabilistic calibration.

## Pinned Snapshot Compatibility

Use `data/exoplanets/exo-0002-pscomppars-snapshot.yaml` as the current primary
snapshot and `data/exoplanets/exo-0001-pscomppars-snapshot.yaml` as a dated
compatibility/replay snapshot. Both are sufficient for a controlled audit with
no live fetch.

Field mapping:

- Mass input: `entries[].mass.value` in `mearth`, only when
  `entries[].mass.mass_class == true_mass`.
- Radius input: `entries[].radius.value` in `rearth`, only when
  `entries[].radius.radius_class == transit_radius`.
- Uncertainties: `uncertainty_upper`, `uncertainty_lower`, and
  `uncertainty_semantics` under both `mass` and `radius`.
- Exclusions and controls: `row_class`, `inclusion_status`,
  `detection_method`, `host_star`, `source_id`, `source_table_ref`, and
  `provenance_notes`.

Readiness counts from the pinned snapshots:

| snapshot | entries | direct true-mass + transit-radius rows | rows with mass/radius uncertainties | below 13 Mjup | below 13 Mjup with uncertainties | boundary rows at or above 13 Mjup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `exo-0001` | 6291 | 1448 | 1306 | 1432 | 1294 | 16 |
| `exo-0002` | 6298 | 1449 | 1306 | 1433 | 1294 | 16 |

Detection-method mix in the direct true-mass + transit-radius subset is nearly
all transit with a small transit-timing-variation component. That is sufficient
for a first readiness-gated audit but should be documented in any benchmark
result before interpreting regime-level residuals.

## Clean Subset Definition

Primary audit subset:

- `inclusion_status: included`.
- `row_class: direct_mass_radius_measurement`.
- `mass.mass_class: true_mass`; never use `minimum_mass_msini`.
- `radius.radius_class: transit_radius`.
- Require finite positive mass and radius values.
- For uncertainty-weighted scoring or calibration, require nonzero
  `uncertainty_upper` and `uncertainty_lower` on both mass and radius.
- Exclude rows at or above 13 Jupiter masses (`13 * 317.828 M_Earth`) from the
  primary planet audit. These rows may be reported as a boundary diagnostic, but
  they should not determine the primary Chen-Kipping planet relation verdict.

Excluded from the primary audit:

- `rv_minimum_mass_only`, `transit_radius_only`,
  `transit_radius_with_rv_minimum_mass`, and `model_inferred` rows.
- Upper-limit-only or lower-limit-only records.
- Brown-dwarf/stellar-boundary rows at or above the 13 Mjup primary cap.
- Any row requiring a live archive lookup to interpret the mass or radius class.

## No-Refit Rule And Controls

The Chen-Kipping relation, regime boundaries, coefficients, and uncertainty
interpretation must be frozen before scoring. Snapshot-specific tuning,
re-estimating breakpoints, and excluding difficult rows after reading residuals
are not allowed.

Required controls for a future benchmark task:

- Global median radius or mass baseline, matched to the predicted direction.
- Chen-Kipping-regime median baseline with frozen regime assignment.
- Shuffled mass/radius-label controls with deterministic seeds.
- Simple power-law controls fit only on a declared train split, then scored on
  a held-out split.
- Uncertainty-weighted control using the same row-quality mask as the candidate.
- Matched controls by discovery method, host-star grouping, and measurement
  precision where the subset size permits.

For a probabilistic Forecaster audit, also evaluate interval calibration:
coverage of reported intervals, over/under-dispersion, and whether misses
cluster by mass regime. A point-MAE-only result would be incomplete.

## Output-Routing Summary

- Canonical destination for this task: this readiness note under `docs/reviews/`.
- Review tier: not applicable; no RESULT was created.
- Gate A status: not applicable; this is a planning/readiness artifact.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: none for launching the next benchmark task. A future
  benchmark must still pin the exact relation implementation route and must not
  create a headline claim that Chen-Kipping is "wrong" from one snapshot score.
