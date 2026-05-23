# Exoplanet `PSCompPars` Snapshot Ingestion Plan

**Task:** TASK-0345
**Status:** plan only (no live fetch, no rows committed, no metrics)
**Campaign:** Exoplanet Mass-Radius (planned fourth campaign)
**Inputs reviewed:**

- `docs/campaigns/exoplanet-mass-radius.md`
- `docs/reviews/exoplanet-mass-radius-source-surface-review.md`
- `data/exoplanets/README.md`
- `data/exoplanets/source_manifest_template.yaml`
- `physics_lab/schemas/exoplanet_mass_radius.schema.json`
- `docs/exoplanet-mass-radius-holdout-protocol.md`

## Scope

This document is the **plan** for a future maintainer-approved ingestion
task that pins a NASA Exoplanet Archive `PSCompPars` snapshot. It does
not fetch live data, does not commit any catalog rows, does not run a
loader, does not compute metrics, and does not promote any claim.

The plan locks the query contract, retrieval policy, field list,
provenance mapping, row-class assignment rules, inclusion/exclusion
filters, and stop conditions in advance so that the eventual ingestion
task is deterministic and reviewable. A curator who runs the ingestion
under a different field list or filter without amending this plan
breaks the no-peek discipline of the campaign.

## Source Family

| Field | Value |
| --- | --- |
| Source family id (manifest) | `EXO-SRC-CLASS-001` |
| Source title | NASA Exoplanet Archive — Planetary Systems Composite Parameters (`PSCompPars`) |
| Issuing body | NASA Exoplanet Science Institute (NExScI), Caltech/IPAC |
| Homepage | https://exoplanetarchive.ipac.caltech.edu/ |
| Documentation | https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html |
| Reuse terms | NASA public data; per-row attribution via `pl_refname`, `disc_refname`, `st_refname` must be preserved |
| Access surface | TAP service (Table Access Protocol) at `https://exoplanetarchive.ipac.caltech.edu/TAP/sync` |
| Archive policy (recommended) | `committed_copy` for the raw CSV plus `normalized_artifact_checksum` for the parsed YAML |

## Retrieval Contract

The ingestion task must perform the snapshot retrieval **exactly once**
per pinned task instance. Re-running the retrieval at a later date
produces a different snapshot and requires a new ingestion task with a
new manifest entry. The plan recommends:

1. Pick a single UTC retrieval timestamp at task start. Record it in
   the manifest as `retrieval_date`.
2. Issue the TAP query (see "Query Contract") and capture both:
   - the raw response body as `data/exoplanets/raw/exo-snapshot-<retrieval_date>.csv`
   - the SHA-256 of the raw body as `raw_checksum_sha256` in the
     manifest entry.
3. Parse the raw CSV into a row-level YAML (see "Row-Level Schema
   Mapping") and record `normalized_checksum_sha256`.
4. Commit both the raw CSV and the normalized YAML (or, if redistribution
   is contested, commit only the normalized YAML and record the raw
   checksum with an explicit `not_committed_reason`).

Live external fetches outside the pinned ingestion task are forbidden.
A future agent must run any benchmark against the pinned snapshot, never
against a fresh TAP query.

## Query Contract

The ingestion task should issue exactly one TAP `sync` query. The
recommended ADQL form is reproduced below; the ingestion task should
commit the exact query text (and any version-stamped diff) under
`data/exoplanets/snapshot_plans/pscomppars_query.adql` before running
the retrieval.

```sql
SELECT
    pl_name,
    hostname,
    default_flag,
    soltype,
    disc_year,
    discoverymethod,
    pl_orbper,
    pl_orbsmax,
    pl_orbeccen,
    pl_eqt,
    pl_insol,
    pl_rade, pl_radeerr1, pl_radeerr2,
    pl_radj,
    pl_bmasse, pl_bmasseerr1, pl_bmasseerr2,
    pl_bmassj,
    pl_bmassprov,
    pl_dens,
    st_spectype,
    st_teff, st_tefferr1, st_tefferr2,
    st_rad,
    st_mass,
    st_met, st_meterr1, st_meterr2,
    st_age,
    st_logg,
    sy_dist,
    pl_refname,
    st_refname,
    disc_refname
FROM ps
WHERE default_flag = 1
```

Notes:

- `default_flag = 1` selects the single canonical parameter row per
  planet in the `ps` Planetary Systems table. The composite catalog
  `pscomppars` exposes the same rows as a flat view; the ingestion task
  should choose one of `ps` (with `default_flag` filter) or `pscomppars`
  but **not** mix them within the same snapshot.
- `pl_bmasse` is the "best mass" composite value with provenance
  `pl_bmassprov` indicating whether it is a true mass, an `M sin i`
  minimum mass, or model-inferred. The provenance flag is the gate for
  row-class assignment (see below).
- The query intentionally requests **both** asymmetric uncertainty
  columns (`*err1`, `*err2`) so the loader can preserve asymmetric
  intervals; downstream code may symmetrize, but the raw values must be
  preserved.
- The query intentionally **omits** habitability flags, biosignature
  scores, transit-spectroscopy summaries, and target-prioritization
  fields. These are out of scope for the campaign and must not be
  introduced via a later query change.

## Row-Level Schema Mapping

Each CSV row maps to a single schema entry under
`physics_lab/schemas/exoplanet_mass_radius.schema.json` using the
following mapping:

| Schema field | PSCompPars column | Notes |
| --- | --- | --- |
| `row_id` | derived from `pl_name` (slugified) | one row per planet per snapshot |
| `planet_name` | `pl_name` | canonical |
| `planet_alt_names` | (omitted from snapshot) | left empty |
| `host_star.name` | `hostname` | |
| `host_star.spectral_type` | `st_spectype` | nullable |
| `host_star.effective_temperature_K` | `st_teff` | nullable |
| `host_star.stellar_mass_msun` | `st_mass` | nullable |
| `host_star.stellar_radius_rsun` | `st_rad` | nullable |
| `host_star.metallicity_fe_h` | `st_met` | nullable |
| `host_star.stellar_age_gyr` | `st_age` | nullable |
| `host_star.notes` | composed from `st_refname`, `st_logg` | optional |
| `detection_method` | `discoverymethod` (mapped) | see method mapping below |
| `mass.value` | `pl_bmasse` | always in Earth masses for the schema |
| `mass.unit` | `mearth` if `pl_bmassprov != 'Msini'` else `msini_mearth` | see provenance rule |
| `mass.uncertainty_upper` | `pl_bmasseerr1` | asymmetric upper bound |
| `mass.uncertainty_lower` | `pl_bmasseerr2` | asymmetric lower bound (typically negative) |
| `mass.uncertainty_semantics` | `1-sigma per NASA Exoplanet Archive docs` | recorded explicitly per row |
| `mass.mass_class` | derived from `pl_bmassprov` | see provenance rule |
| `mass.mass_method_label` | `pl_bmassprov` (free text) | preserved verbatim |
| `radius.value` | `pl_rade` | always in Earth radii |
| `radius.unit` | `rearth` | |
| `radius.uncertainty_upper` | `pl_radeerr1` | |
| `radius.uncertainty_lower` | `pl_radeerr2` | |
| `radius.uncertainty_semantics` | `1-sigma per NASA Exoplanet Archive docs` | |
| `radius.radius_class` | `transit_radius` if discovery via transit else `model_inferred` (excluded) | see below |
| `radius.radius_method_label` | composed from `discoverymethod` | optional |
| `equilibrium_temperature_K` | `pl_eqt` | nullable |
| `irradiation_flux_earth_units` | `pl_insol` | nullable |
| `orbital_period_days` | `pl_orbper` | nullable |
| `orbital_semimajor_axis_au` | `pl_orbsmax` | nullable |
| `discovery_year` | `disc_year` | |
| `source_id` | `EXO-SRC-CLASS-001` | constant per snapshot |
| `source_table_ref` | `pl_refname` (planet) and `disc_refname` (discovery) preserved jointly | |
| `inclusion_status` | derived from filters below | every row must carry an explicit decision |
| `inclusion_reason` | filter rule that decided the row | |
| `provenance_notes` | optional free text | parser version + raw column list |

### Detection-Method Mapping

NASA Exoplanet Archive uses a small canonical set in `discoverymethod`.
Map to schema `detection_method` enum:

| `discoverymethod` value | Schema value |
| --- | --- |
| `Transit` | `transit` |
| `Radial Velocity` | `radial_velocity` |
| `Transit Timing Variations` | `transit_timing_variation` |
| `Microlensing` | `microlensing` |
| `Astrometry` | `astrometry` |
| `Imaging` | `direct_imaging` |
| `Pulsar Timing` / `Pulsation Timing Variations` | `pulsar_timing` |
| `Eclipse Timing Variations` / `Orbital Brightness Modulation` / anything else | `other` |

The mapping table is committed verbatim under
`data/exoplanets/snapshot_plans/pscomppars_method_map.yaml` (no row
values; only the mapping).

### Mass-Provenance Rule (the most important rule)

`pl_bmassprov` controls `mass_class`. The mapping is enforced verbatim
and is **the single source of truth** for whether a row contributes to
the true-mass residual axis:

| `pl_bmassprov` value | Schema `mass_class` | Schema `row_class` | Default `inclusion_status` |
| --- | --- | --- | --- |
| `Mass` | `true_mass` | `direct_mass_radius_measurement` (if radius present) or `rv_minimum_mass_only` (if not transit method) | `included` (subject to quality filters) |
| `M-R relationship` | `model_inferred` | `model_inferred` | **`excluded`** (`inclusion_reason: mass_inferred_from_mass_radius_relationship`) |
| `Msini` | `minimum_mass_msini` | `transit_radius_with_rv_minimum_mass` (if transit radius present) or `rv_minimum_mass_only` | `included` for the minimum-mass axis; **excluded from the true-mass residual axis** |
| `Mass Function` or `Msin(i)/sin(i)` | `microlensing_mass` or `astrometric_mass` (per `discoverymethod`) | `microlensing_or_astrometry_mass` | `included` on the alternate-method axis |
| (blank / null) | `not_measured` | row class depends on radius availability | `included` only if `radius` is present and the row is treated as radius-only |
| anything else | `model_inferred` | `model_inferred` | **`excluded`** with `inclusion_reason: unknown_mass_provenance` |

The ingestion task **must refuse to map** any `pl_bmassprov` value not
listed above as a known known-class value. Unknown provenance flags
become `excluded` with an explicit reason; they never silently fall into
`true_mass`.

### Radius-Class Rule

| Condition | `radius_class` | `row_class` modifier |
| --- | --- | --- |
| `discoverymethod` is `Transit` or `Transit Timing Variations` | `transit_radius` | radius is admissible |
| `discoverymethod` is `Imaging` | `direct_imaging_radius` | rare; admissible per case |
| `discoverymethod` is anything else and `pl_rade` is present | `model_inferred` | `inclusion_status: excluded` (`inclusion_reason: radius_inferred_from_non_transit_method`) |
| `pl_rade` is null | `not_measured` | row may still be a mass-only row |

## Inclusion / Exclusion Filters

The first ingestion task must apply these filters in order. Every
filtered-out row is preserved in the snapshot YAML with
`inclusion_status: excluded` and an explicit `inclusion_reason`. No
row is silently dropped.

1. **Solution-type filter.** Keep rows with `soltype` in
   `{Published Confirmed}`. Exclude `soltype = Candidate`, `Controversial`,
   or `Retracted` with `inclusion_reason: solution_type_not_confirmed`.
2. **Mass-provenance gate** (above). Unknown or model-inferred mass
   provenance → excluded.
3. **Radius-class gate** (above). Non-transit-derived radius → excluded.
4. **Mass relative-uncertainty filter** (recommended default). When
   `pl_bmasse` is non-null and asymmetric uncertainties are present,
   compute `sigma_M/M = max(|pl_bmasseerr1|, |pl_bmasseerr2|) / pl_bmasse`.
   Mark `inclusion_status: excluded` with
   `inclusion_reason: mass_relative_uncertainty_above_threshold` when
   `sigma_M/M > 0.30`. The threshold is recorded in the manifest and
   may be relaxed for later analyses; the default snapshot reports
   both pre- and post-filter views.
5. **Radius relative-uncertainty filter** (recommended default).
   Analogous, threshold `sigma_R/R > 0.15`.
6. **Duplicate planet-name filter.** Within a single snapshot, each
   `pl_name` must appear exactly once because the query already filters
   on `default_flag = 1`. The loader must assert this invariant and
   stop with `SOURCE_MANIFEST_INCOMPLETE` if a duplicate is encountered.
7. **Reserved-name filter.** Reject any `pl_name` matching a reserved
   placeholder (e.g. empty string, `TBD`, `Unknown`).

The plan does not introduce a planet-class filter at ingestion time.
Planet-class binning is an analysis-time concern under the holdout
protocol.

## Duplicate / Multi-Solution Handling

The query already filters on `default_flag = 1`, which selects the
single canonical row per planet from the `ps` table. The ingestion task
must not relax this filter to pull alternate solutions in the same
snapshot; alternate solutions belong to a separate per-publication
follow-up (`EXO-SRC-CLASS-002`).

When the same planet later appears in a second snapshot at a different
retrieval date with different parameter values, the new row is recorded
as a separate snapshot under a new manifest entry. The campaign does
**not** average parameters across snapshots.

## What This Plan Does Not Authorize

- The plan does not authorize running the TAP query inside the
  TASK-0345 PR. A separate maintainer-approved ingestion task with its
  own branch and PR is required.
- The plan does not authorize live fetches outside that future
  ingestion task.
- The plan does not authorize habitability, biosignature, or
  prioritization output.
- The plan does not authorize benchmark metrics, residual maps, or
  prediction registry entries.
- The plan does not authorize redistribution of any per-row catalog
  table outside the snapshot YAML governed by the source manifest.

## Recommended Follow-Up Ingestion Task Shape

The next maintainer-approved task after TASK-0345 should be a single
ingestion task with this shape:

- task type: `scientific_dataset`
- task scope:
  - run the committed TAP query exactly once at a recorded retrieval
    timestamp;
  - commit (or archive-and-checksum) the raw CSV;
  - commit the normalized row-level YAML under
    `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`;
  - populate the `source_manifest_template.yaml` placeholders with
    real values for the snapshot;
  - record per-row counts at every filter stage;
  - leave benchmark metric computation to a **separate** later task.
- the ingestion task must reference this plan as its
  `related_objects` entry and must not change the field list, query
  text, mass-provenance mapping, or filter thresholds without an
  amendment PR to this plan.

## Stop Conditions Carried Forward

A future ingestion task must stop and surface a blocker when:

- the TAP service is unreachable (snapshot is not pinned; no scoring);
- the raw response checksum does not match a re-run within the same
  task (snapshot is not deterministic; investigate before committing);
- any row's `pl_bmassprov` value is not in the mapping table above;
- any row's `discoverymethod` is not in the mapping table above;
- a duplicate `pl_name` survives the `default_flag = 1` filter;
- the schema rejects any row (refuse to "fix" by relaxing the schema;
  amend the schema in a separate PR if structurally needed).

## Limitations

- The recommended quality-filter thresholds (0.30 for mass, 0.15 for
  radius) are conservative defaults from the holdout protocol; the
  ingestion task may justify different thresholds as long as the
  manifest records both the threshold and the rationale before
  scoring.
- The plan locks the field list as of `PSCompPars` schema documented at
  https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html
  on the retrieval date. If NASA Exoplanet Archive changes column names
  or semantics later, the next snapshot must amend this plan
  accordingly.
- The plan does not estimate the number of rows that will survive
  filters for any specific retrieval date; that is a per-snapshot
  diagnostic.
- The plan intentionally does not include planet-class labels at
  ingestion time. Class binning is analysis-time only.

## Verdict

`PARTIALLY_VALID` for the ingestion plan. The query contract, retrieval
policy, schema mapping, mass-provenance rule, inclusion/exclusion
filters, and stop conditions are now reviewable in advance. No row has
been ingested. The campaign remains "planned fourth campaign"; the
next allowed step is a maintainer-approved ingestion task that follows
this plan verbatim.
