# Post-AME2020 Holdout Protocol Note

## Purpose

This note defines the conservative import boundary for a future post-AME2020
nuclear-mass holdout surface.

The goal is retrospective time-split validation:

- older baseline: AME2020 and APL's frozen `NMD-0002` benchmark surface;
- later source: measured masses from reviewed publications after AME2020;
- evidence class: retrospective validation, not prospective prediction.

## Source Manifest

The reviewed source manifest is:

- `data/nuclear_masses/post_ame2020_sources.yaml`

The manifest records:

- the 2025 Nuclear Science and Techniques compilation of 296 newly measured
  masses from 2021-2024;
- AME2020 paper and AMDC source references;
- access date and stable identifiers;
- source-level measured-versus-extrapolated semantics;
- overlap exclusions for the current APL baseline slice.

## Import Rules For A Later Row-Level Dataset

A future `post_ame2020_holdout.yaml` import must:

1. Pin the exact source artifact and checksum.
2. Preserve source units exactly before converting values for APL workflows.
3. Record `source_reference` and measurement method per row when available.
4. Preserve uncertainty values and units.
5. Flag whether the AME2020 comparison value was extrapolated.
6. Exclude `NMD-0002` nuclides from primary holdout scoring unless a row is
   explicitly labeled as an overlap-audit row.
7. Avoid live fetches during validation and CI.

## Claim Boundary

Post-AME2020 evaluation should be described as:

> retrospective time-split validation against later measurements

It should not be described as strict blind prediction unless a prediction was
registered before the later measurement was known.

## Current Status

`TASK-0187` provides the source manifest and protocol. It does not yet commit
row-level holdout values, and it does not create a benchmark result.
