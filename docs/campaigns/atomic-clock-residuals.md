# Atomic-Clock Residuals

## Goal

Create a conservative source surface for future atomic-clock comparison work:
frequency-ratio measurements, drift constraints, uncertainty budgets, epoch
metadata, and source provenance that could later support freeze/reveal-style
benchmarks.

This campaign is not a constants-drift campaign yet. It is not a broad
new-physics or new-constant search. `TASK-0311` creates only the source and
schema scaffold needed before any future ingestion task can add rows.

## Current Status

Planning scaffold only.

`TASK-0311` adds:

- this campaign orientation page;
- the data-area README at
  [`data/atomic_clocks/README.md`](../../data/atomic_clocks/README.md);
- the row and constraint schema sketch at
  [`data/atomic_clocks/schema.md`](../../data/atomic_clocks/schema.md);
- the source-candidate and stop-condition note at
  [`docs/notes/atomic-clock-source-candidates.md`](../notes/atomic-clock-source-candidates.md).

No atomic-clock dataset has been ingested. No benchmark, residual map,
prediction registry entry, canonical result, claim, or knowledge artifact is
created by this scaffold.

Current next tasks:

- `TASK-0327` adds a metadata-only atomic-clock source manifest template;
- `TASK-0328` adds a synthetic-only loader dry-run with fabricated rows.

Those tasks can run in parallel because one owns source-manifest structure and
the other owns loader mechanics. Neither should ingest real clock values.

## Why This Could Matter Later

Atomic-clock comparisons may become a useful fresh-data axis because they can
offer:

- precise frequency-ratio measurements with explicit uncertainty budgets;
- repeated comparison campaigns across dates or labs;
- drift bounds or constraints that may be frozen before later evaluations;
- clear source-date discipline when primary papers and supplementary tables
  are pinned before analysis.

Those benefits only matter if the repository keeps source provenance,
uncertainty semantics, correlation notes, and direct-vs-derived boundaries
visible. APL should prefer a slow source manifest over a fast but ambiguous
constants-fit table.

## Candidate Observables

Future tasks may propose rows or constraints only after a reviewed source
manifest exists.

Allowed observable families:

- direct frequency-ratio measurements between named clock transitions;
- repeated frequency-ratio comparisons with explicit epoch or campaign window;
- drift bounds quoted with clear interval semantics;
- systematic-shift budget entries only when tied to a primary measurement row;
- sensitivity-coefficient metadata only as a derived-constraint dependency,
  not as a measurement row by itself.

Not allowed in this scaffold:

- inferred constants-drift rows without the underlying measurement trail;
- review-summary values that hide primary-source provenance;
- mixed direct measurements and derived constraints without explicit flags;
- live source fetching;
- benchmark metrics or fitting.

## Data Boundary

Atomic-clock evidence must be split before ingestion into three classes:

| Class | Meaning | Initial status |
| --- | --- | --- |
| Direct measurement row | A primary frequency ratio or measured comparison with source, epoch, units, and uncertainty fields. | Schema-only. |
| Derived constraint | A drift or constants-variation constraint that depends on sensitivity coefficients or model assumptions. | Schema-only and must not be mixed with direct rows. |
| Review-summary value | A value copied from an evaluation, review, or secondary table. | Not ingestible unless provenance and combination rules are reviewable. |

Future tasks must coordinate with the
[Fresh-Data Source Policy](../notes/fresh-data-source-policy.md) before adding
any real rows.

## Minimal Future Schema

The row sketch in [`data/atomic_clocks/schema.md`](../../data/atomic_clocks/schema.md)
requires future tasks to preserve:

- observable id and row class;
- clock species, isotope where applicable, transition, and reference
  transition or ratio partner;
- value or residual form, units, epoch or campaign interval, and uncertainty
  components;
- direct-vs-derived flags plus sensitivity-coefficient dependencies for
  derived constraints;
- source citation, DOI or archive locator, retrieval date, checksum or archive
  policy, license notes, and limitation notes;
- holdout classification and reveal boundary when future freeze/reveal work is
  proposed.

## Coordination With TASK-0309

`TASK-0309` defines the repository-wide fresh-data source policy. Atomic-clock
work must satisfy that policy before ingestion:

- fixed source list before retrieval;
- frozen retrieval date;
- checksum or archive policy;
- license and citation review;
- unit and uncertainty semantics;
- covariance or correlation handling;
- holdout split discipline;
- deterministic loader path;
- negative-result preservation plan.

If any of those are missing, the future task should stay planning-only.

## Recommended Next Task Shapes

Safe future tasks:

- create an atomic-clock source manifest template without values;
- review one source class for admissibility and preserve blockers;
- run a synthetic-only loader dry-run with fabricated rows;
- define a no-peek freeze package for a future source update;
- audit whether derived constraints can be separated from direct measurements.

Unsafe next tasks:

- ingest real frequency ratios directly from a review plot;
- fit constants drift before source and correlation semantics are fixed;
- merge direct rows and derived constraints in one unflagged table;
- add prediction registry entries before a source manifest and holdout policy
  exist.

## What Not To Claim

- Do not claim evidence for constants drift.
- Do not claim evidence for new constants or new physics.
- Do not frame clock comparisons as a broad anomaly explanation surface.
- Do not treat source-surface readiness as benchmark readiness.
- Do not promote any atomic-clock result without a later maintainer-reviewed
  ingestion, benchmark, and claim-promotion path.
