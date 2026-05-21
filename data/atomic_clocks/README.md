# Atomic-Clock Data Area

This directory is reserved for future atomic-clock comparison source surfaces.

`TASK-0311` does not ingest any atomic-clock data. The directory currently
contains only a schema sketch and source-boundary notes so future tasks can be
reviewed before any rows are added.

## Current Contents

- [`schema.md`](./schema.md): minimal row and constraint schema sketch for
  future source-manifest or ingestion tasks.

## Allowed Future Contents

A future maintainer-approved task may add:

- source manifests without measured values;
- deterministic loader contracts;
- synthetic-only dry-run rows with fabricated values;
- real direct measurement rows only after source, license, checksum,
  uncertainty, and holdout semantics are reviewed.

## Not Allowed Yet

Do not add:

- real frequency-ratio rows;
- drift-constraint values;
- sensitivity-coefficient tables;
- benchmark outputs;
- prediction registry entries;
- broad constants-fit artifacts.

## Required Coordination

Future tasks must read:

- [Atomic-Clock Residuals Campaign](../../docs/campaigns/atomic-clock-residuals.md)
- [Fresh-Data Source Policy](../../docs/notes/fresh-data-source-policy.md)
- [Atomic-Clock Source Candidates](../../docs/notes/atomic-clock-source-candidates.md)
- [Blind Holdout Benchmark Protocol](../../docs/blind-holdout-benchmark-protocol.md)

If a future task cannot identify source provenance, retrieval date, checksum
or archive policy, unit semantics, uncertainty fields, direct-vs-derived
classification, and stop conditions, it should remain planning-only.

## Synthetic Loader Dry Run

`TASK-0328` adds a synthetic-only loader fixture at
[`synthetic_loader_dry_run.yaml`](./synthetic_loader_dry_run.yaml)
and loader checks in
[`physics_lab/engines/atomic_clock_residuals.py`](../../physics_lab/engines/atomic_clock_residuals.py).
The fixture is fabricated and is not benchmark input.
