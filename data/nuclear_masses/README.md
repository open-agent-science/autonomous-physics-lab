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
- `binding_energy_meV`
- `binding_energy_per_nucleon_meV`

without re-encoding conversion logic in every workflow.

## Current State

`TASK-0167` adds the schema and loader layer only.

No canonical nuclear mass dataset file is committed yet. A later reviewed task
should add a pinned source file once source packaging, checksum policy, and
field semantics are finalized.
