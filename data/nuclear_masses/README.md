# Nuclear Mass Datasets

This directory stores pinned input datasets for the nuclear mass surface
campaign.

The purpose of these files is to make future baseline residual benchmarks,
holdout splits, and sandbox-only correction tests source-aware and reviewable
before any mass-surface interpretation is attempted.

## Scope

These files are input data only.

They do not, by themselves:

- establish a nuclear benchmark result;
- justify a correction family;
- support a broad physical conclusion;
- authorize mixing measured and extrapolated entries silently.

## Source Policy

Primary source policy:

- use a pinned AME-style source release with explicit edition or version
  wording;
- record the exact table, extraction method, and checksum used for the
  committed dataset file;
- record access date and any redistribution notes;
- preserve whether an entry is measured, extrapolated, or explicitly
  unspecified in the source layer.

If a later post-baseline update batch is added for holdout use, it must be
stored as a separate, versioned dataset surface rather than silently merged
into the original file.

## Field-Semantics Policy

Every entry must record:

- `Z`
- `N`
- `A`
- `evaluation`

Rules:

- `A` must equal `Z + N`;
- `evaluation` must be explicit: `measured`, `extrapolated`, or
  `unspecified`;
- do not collapse measured and extrapolated entries into one unlabeled pool;
- keep units explicit when storing atomic masses or mass excess values;
- use deterministic derived conversions instead of handwritten secondary
  fields.

## Supported Value Shapes

The current loader supports either of these primary value shapes per entry:

- `atomic_mass_u` plus `atomic_mass_uncertainty_u`
- `mass_excess_keV` plus `mass_excess_uncertainty_keV`

Entries may store both, but at least one complete pair must be present.

The engine normalizes both representations so later baseline tasks can use:

- `atomic_mass_u`
- `mass_excess_keV`
- `binding_energy_mev`
- `binding_energy_per_nucleon_mev`

without re-encoding conversion logic in every workflow.

## Current State

The repository includes one small measured benchmark slice:

- `nmd-0002-curated-measured-slice.yaml`

This file exists to support the first baseline residual benchmark under
`TASK-0168`. It is intentionally narrow:

- measured entries only;
- no silent extrapolated merge;
- no claim that this slice substitutes for a full AME2020 import.

The repository also includes a broader source-gated AME2020 measured-row
training surface:

- `nmd-0003-source-manifest.yaml`
- `nmd-0003-ame2020-measured-training.yaml`
- `nmd-0003-split-manifest.yaml`

`NMD-0003` is intended to supersede `NMD-0002` for larger Nuclear Research
Factory training after maintainer review. It excludes AME2020 estimated rows
and primary post-AME2020 holdout nuclide ids, preserving the time-split
validation boundary.

The repository also includes a reviewed source manifest for the future
post-AME2020 time-split lane:

- `post_ame2020_sources.yaml`
- `post_ame2020_sources.md`
- `post_ame2020_holdout.yaml`
- `post_ame2020_checksums.md`

The holdout dataset commits the reviewed row-level post-AME2020 values and
provenance needed for time-split evaluation. `TASK-0197` activates
retrospective benchmark metrics from committed rows only; it still does not
promote candidate claims or strict blind-prediction language.
