# Exoplanet Second Snapshot Source Acquisition

**Task:** `TASK-0565`
**Status:** review (pinned real catalog snapshot acquired)
**Actor:** `akutenyov/codex`
**Approval reference:** `user-request-2026-06-04-TASK-0565`
**Retrieval timestamp:** `2026-06-04T18:50:11Z`
**Verdict:** `VALID` as a pinned source artifact; no benchmark run.

## Scope

This review records the second pinned NASA Exoplanet Archive Planetary Systems snapshot for the Exoplanet Mass-Radius campaign. It commits a raw CSV, normalized YAML dataset, and filled acquisition manifest. It does not compute residuals, plots, baseline metrics, habitability analysis, target prioritization, prediction entries, claims, or canonical results.

## Source And Pinning

- Source family: `EXO-SRC-CLASS-001`
- TAP endpoint: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`
- Query contract: `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- Query SHA-256: `4364d83855a19cfc638f733b4aea32c1873af9b78338f0b84a9b25f51e0de3e4`
- Raw snapshot: `data/exoplanets/raw/exo-pscomppars-second-snapshot-20260604T185011Z.csv`
- Raw SHA-256: `9a12e1e4e09bc2fc1093236494b521e3da9a8a5b4a98f5b66d391e9bba630c2b`
- Normalized snapshot: `data/exoplanets/exo-0002-pscomppars-snapshot.yaml`
- Normalized file SHA-256: `432aa663b916addbf41d38d42efa5b8f6260a097d44c0e3245dbfc2c662fb330`
- Normalized payload SHA-256: `90894e978269c787a89de9ee51709255e3b2eb442b1c957e30a89ed28bfdc8ca`

## Counts

```json
{
  "dataset_id": "exo-0002-pscomppars-snapshot",
  "detection_method_counts": {
    "astrometry": 6,
    "direct_imaging": 97,
    "microlensing": 278,
    "other": 27,
    "pulsar_timing": 10,
    "radial_velocity": 1186,
    "transit": 4653,
    "transit_timing_variation": 41
  },
  "exclusion_reason_counts": {
    "mass_and_radius_absent": 16,
    "mass_provenance_requires_source_specific_review": 10,
    "mass_relative_uncertainty_above_threshold": 578,
    "radius_inferred_from_non_transit_method": 34,
    "radius_relative_uncertainty_above_threshold": 1278,
    "solution_type_not_confirmed": 74
  },
  "mass_class_counts": {
    "minimum_mass_msini": 985,
    "not_measured": 3203,
    "true_mass": 2110
  },
  "post_filter_included_count": 4308,
  "pre_filter_included_count": 6164,
  "radius_class_counts": {
    "direct_imaging_radius": 29,
    "model_inferred": 34,
    "not_measured": 1595,
    "transit_radius": 4640
  },
  "retrieval_date_utc": "2026-06-04T18:50:11Z",
  "row_class_counts": {
    "direct_mass_radius_measurement": 1509,
    "model_inferred": 16,
    "rv_minimum_mass_only": 1579,
    "transit_radius_only": 3187,
    "transit_radius_with_rv_minimum_mass": 7
  },
  "snapshot_kind": "composite_catalog_snapshot",
  "source_family_id": "EXO-SRC-CLASS-001",
  "thresholds": {
    "mass_sigma_threshold": 0.3,
    "radius_sigma_threshold": 0.15
  },
  "total_rows": 6298
}
```

## Raw Source Diagnostics

```json
{
  "raw_detection_method_counts": {
    "Astrometry": 6,
    "Disk Kinematics": 1,
    "Eclipse Timing Variations": 17,
    "Imaging": 97,
    "Microlensing": 278,
    "Orbital Brightness Modulation": 9,
    "Pulsar Timing": 8,
    "Pulsation Timing Variations": 2,
    "Radial Velocity": 1186,
    "Transit": 4653,
    "Transit Timing Variations": 41
  },
  "raw_mass_provenance_counts": {
    "": 3203,
    "Mass": 2110,
    "Msin(i)/sin(i)": 10,
    "Msini": 975
  },
  "solution_type_counts": {
    "Kepler Project Candidate (q1_q17_dr25_koi)": 70,
    "Published Confirmed": 6224,
    "TESS Project Candidate": 4
  },
  "source_row_count": 6298
}
```

## No-Peek Attestation

- The committed ADQL query hash was checked before live acquisition.
- Counts and checksums were recorded before any analysis stage.
- No target scoring, reopen coverage metric, residual metric, prediction, claim, or knowledge promotion was run.
- True-mass, minimum-mass, model-derived, radius-only or mass-only, and excluded rows remain separate through row classes and loader summaries.

## Result-Promotion Routing

The output is intentionally limited to source-acquisition artifacts. Per result-promotion protocol, this task does not create a canonical result, claim, prediction entry, or scientific memory promotion.

## Next Step

A separate review or benchmark task may decide whether this pinned snapshot is eligible for reopen coverage or mass-radius baseline analysis. That future task must not merge true-mass and minimum-mass rows into a single scored axis.
