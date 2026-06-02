# Exoplanet PSCompPars Snapshot Ingestion

**Task:** `TASK-0353`
**Status:** review (pinned real catalog snapshot ingested)
**Retrieval timestamp:** `2026-05-23T17:15:49Z`
**Verdict:** `VALID` as a pinned dataset artifact; no benchmark run.

## Scope

This review records the first pinned NASA Exoplanet Archive Planetary Systems snapshot for the Exoplanet Mass-Radius campaign. It commits a raw CSV and normalized YAML dataset, but does not compute residuals, plots, baseline metrics, habitability analysis, target prioritization, prediction entries, claims, or canonical results.

## Source And Pinning

- Source family: `EXO-SRC-CLASS-001`
- TAP endpoint: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`
- Query contract: `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- Raw snapshot: `data/exoplanets/raw/exo-pscomppars-20260523T171549Z.csv`
- Raw SHA-256: `a86aefd7d0fd7c2e93aaad87f97adb4c96f1246d8fc00abae7d7c43082ba4e54`
- Normalized snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Normalized file SHA-256: `bd7c919e4ba1de5acb01e45c78f64aa2b5af859edd62f0e88eaa62a44fb54c2d`
- Embedded canonical-payload SHA-256: `dc4d8df2d0860f87d6384a1a1bebbe8e3e51a400175593f2b48e6c64a33ae5ee`

## Counts

```json
{
  "dataset_id": "exo-0001-pscomppars-snapshot",
  "detection_method_counts": {
    "astrometry": 6,
    "direct_imaging": 97,
    "microlensing": 278,
    "other": 27,
    "pulsar_timing": 10,
    "radial_velocity": 1181,
    "transit": 4651,
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
    "minimum_mass_msini": 986,
    "not_measured": 3202,
    "true_mass": 2103
  },
  "post_filter_included_count": 4301,
  "pre_filter_included_count": 6157,
  "radius_class_counts": {
    "direct_imaging_radius": 29,
    "model_inferred": 34,
    "not_measured": 1590,
    "transit_radius": 4638
  },
  "retrieval_date_utc": "2026-05-23T17:15:49Z",
  "row_class_counts": {
    "direct_mass_radius_measurement": 1508,
    "model_inferred": 16,
    "rv_minimum_mass_only": 1574,
    "transit_radius_only": 3186,
    "transit_radius_with_rv_minimum_mass": 7
  },
  "snapshot_kind": "composite_catalog_snapshot",
  "source_family_id": "EXO-SRC-CLASS-001",
  "thresholds": {
    "mass_sigma_threshold": 0.3,
    "radius_sigma_threshold": 0.15
  },
  "total_rows": 6291
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
    "Radial Velocity": 1181,
    "Transit": 4651,
    "Transit Timing Variations": 41
  },
  "raw_mass_provenance_counts": {
    "": 3202,
    "Mass": 2103,
    "Msin(i)/sin(i)": 10,
    "Msini": 976
  },
  "solution_type_counts": {
    "Kepler Project Candidate (q1_q17_dr25_koi)": 70,
    "Published Confirmed": 6217,
    "TESS Project Candidate": 4
  },
  "source_row_count": 6291
}
```

## Method

1. Read the committed TASK-0345 ADQL query and mapping files.
2. Retrieved the TAP CSV once for this task branch and recorded the UTC timestamp and checksum.
3. Normalized each row into the exoplanet mass-radius schema.
4. Preserved every row with explicit `inclusion_status` and `inclusion_reason` instead of silently dropping rows.
5. Ran the existing loader filter chain to produce pre/post quality-filter counts.

## Limitations

- The dataset is a catalog snapshot, not a benchmark result.
- Composite rows preserve source references but are not per-publication primary-table extractions.
- Model-inferred masses and non-transit-derived radii are explicitly excluded from the production residual axis.
- True-mass and `M sin i` rows remain separated by `mass_class` and must not be averaged in a future benchmark.
- Planet-class labels are intentionally not assigned at ingestion time; class binning belongs to a later benchmark task.

## What This Review Did Not Do

- It did not run Chen-Kipping or other mass-radius baselines.
- It did not compute residuals, metrics, or plots.
- It did not add prediction registry entries.
- It did not promote claims or knowledge entries.
- It did not add habitability, biosignature, or target-priority fields.

## Next Step

A later benchmark task may consume this pinned snapshot only after maintainer review. That task must keep true-mass, minimum-mass, radius-only, and model-inferred rows on separate diagnostic axes per the baseline protocol.
