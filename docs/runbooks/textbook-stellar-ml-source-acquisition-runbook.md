# Runbook: Textbook Stellar M-L Pinned-Source Acquisition

**Task:** `TASK-0564`
**Campaign:** Textbook Formula Audit
**Lane:** `T4_snapshot_approval` / `T1_access` depending on source
**Operates under:** [Source Acquisition, Pinning, and Extraction Lane](../source-acquisition-lane.md)
and the [Published-Source and Reusable-Dataset Standard](../published-source-dataset-standard.md)

## Scope

This runbook prepares the first pinned-source package for a future empirical
audit of the textbook stellar mass-luminosity relation. It does not fetch Gaia
or literature rows, cross-match catalogs, fit exponents, inspect residuals, or
run metrics.

The future acquisition must keep source acquisition, row curation, baseline
freezing, holdout declaration, and residual scoring as separate gates.

## Candidate Source Surfaces

### Surface A: Gaia DR3 archive surface

- Candidate role: astrometry, photometry, and derived luminosity context for a
  main-sequence slice.
- Locator shape: Gaia Archive ADQL query against pinned Gaia DR3 tables such as
  `gaiadr3.gaia_source` and reviewed DR3 astrophysical-parameter tables.
- Acquisition lane: `T4_snapshot_approval`.
- Redistribution posture: metadata and query are committable; row
  redistribution must follow Gaia archive terms and attribution requirements.
- Primary caution: any model-derived mass, luminosity, radius, or evolutionary
  classification must be tagged as derived/model context, not direct
  measurement evidence.

### Surface B: literature benchmark-star anchors

- Candidate role: dynamical-mass and luminosity anchors for calibration and
  source sanity checks.
- Locator shape: DOI/VizieR/source-catalog records for reviewed main-sequence
  binaries or benchmark stars.
- Acquisition lane: `T1_access` until license and redistribution posture are
  reviewed.
- Redistribution posture: metadata-only until the source license permits
  committing curated facts or a maintainer supplies an approved artifact.
- Primary caution: copied tables, PDFs, or copyrighted supplemental files are
  not committable unless a compatible license or permission is documented.

### Surface C: curated normalized ingestion surface

- Candidate role: future APL-owned normalized row table after source approval.
- Locator shape: `data/textbook_formula_audit/stellar_ml/<snapshot-id>.yaml`.
- Acquisition lane: row-curation task after Surface A/B source gates pass.
- Redistribution posture: committable only after per-source license,
  attribution, checksum, row-role, and uncertainty semantics are recorded.

## Selected Field Contract

Future source acquisition must preserve at least these fields or record why a
field is unavailable:

- `source_id`, `source_table`, `source_version`, `source_locator`
- `source_row_id` and source-row checksum scope
- `star_name` or catalog alias when available
- `mass_solar`, `mass_uncertainty`, `mass_provenance_class`
- `luminosity_solar`, `luminosity_uncertainty`,
  `luminosity_provenance_class`
- `parallax_mas`, `parallax_uncertainty_mas`, and distance method when used
- `photometric_band`, magnitude/flux inputs, extinction correction notes, and
  bolometric-correction notes when luminosity is derived
- `effective_temperature_k`, `radius_solar`, `spectral_type` when available
- `main_sequence_flag`, `evolutionary_class_source`, `multiplicity_flag`
- `row_role`: `direct_observation`, `derived_luminosity`,
  `model_derived_mass`, `holdout`, or `excluded`
- `exclusion_reason` for every excluded row

Units must remain explicit. Solar-normalized values may be used in later
benchmarks, but source units and conversion notes must remain auditable.

## Baseline Convention Frozen For The First Audit Slice

The planning baseline remains:

```text
L / L_sun = (M / M_sun)^alpha
```

For the first empirical audit, freeze the classroom baseline as a declared
input before any residual inspection:

- `alpha = 3.5`
- primary audit slice: single-star or well-resolved main-sequence rows with
  `0.5 <= M / M_sun <= 2.0`
- rows below 0.5 solar masses, above 2.0 solar masses, unresolved multiples,
  giants/subgiants, and rows with missing uncertainty/provenance semantics are
  exclusions or diagnostic rows, not failures of the formula.

No exponent fitting, mass-range tuning, row filtering, or slice selection may
be changed after holdout inspection.

## Acquisition Procedure

1. Select one source surface and record the exact query, DOI, catalog id, or
   archive locator before fetching.
2. Record source license and attribution text. Stop if redistribution status is
   unknown or restricted and no metadata-only path is acceptable.
3. Retrieve the source artifact only in an approved acquisition task. Do not
   fetch inside a benchmark runner.
4. Compute SHA-256 for raw and normalized artifacts, or record why the raw
   artifact is external-only.
5. Fill `data/textbook_formula_audit/stellar_ml/source_manifest.yaml` with
   retrieval timestamp, selected fields, row counts, checksums, row-role rules,
   and no-peek attestation.
6. Hand off to a separate row-curation task. Do not compute mass-luminosity
   residuals in the acquisition task.

## Stop Conditions

Stop before row curation or scoring if any of these are true:

- source license or redistribution posture is unknown;
- selected fields cannot distinguish direct observations, derived luminosities,
  model-derived masses, and excluded rows;
- checksum, retrieval timestamp, or source version cannot be recorded;
- no-peek attestation cannot be made;
- the source slice is too sparse after main-sequence and multiplicity
  exclusions;
- the baseline exponent or slice boundary would need to be changed after row
  inspection.

## Guardrails

- No live Gaia fetch, cross-match, residual metric, fitted exponent, prediction,
  result, claim, or knowledge artifact is produced by this runbook.
- Do not mix direct observations, derived luminosities, model-derived masses,
  and excluded rows.
- Do not claim that the mass-luminosity relation is validated, falsified,
  universal, or newly discovered.
