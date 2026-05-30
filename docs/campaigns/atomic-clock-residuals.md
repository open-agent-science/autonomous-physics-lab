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

Pinned-dataset source surface with one committed direct-ratio seed, a
source-derived covariance approximation, and a triaged second-source path. No
real-row benchmark yet.

## Public Monitoring Snapshot

**Current question:** can high-precision atomic-clock comparison data be
curated with source provenance, covariance, and version-drift semantics intact
before any residual analysis?

**Shareable result:** APL has pinned Beloy 2021 / BACON as a sandbox-only
direct-frequency-ratio seed (`PINNED_DATASET`), reconstructed a positive-
semidefinite source-derived covariance approximation, and selected Nemitz 2016
RIKEN Yb/Sr as the next independent source candidate. The campaign is
deliberately not fitting constants drift yet.

**Not a claim:** no atomic-clock residual benchmark, constants-drift result,
new constant, or anomaly explanation exists in APL.

**Active next work:** `TASK-0452` ingests the Nemitz 2016 source if gates pass,
`TASK-0453` adds a real direct-row loader, and the `TASK-0485`-`TASK-0488`
wave closes second-source fallbacks, covariance policy, direct-vs-derived
row separation, and synthetic cross-source dry-run boundaries before any
benchmark consumer runs.

**Expected next result:** a `BASELINE_READY` go/no-go path: second source
committed or blocked, real-row loader available, holdout/no-peek manifest
declared, and then a readiness gate deciding whether a first Yb/Sr
cross-source consistency benchmark can run.

`TASK-0311` adds:

- this campaign orientation page;
- the data-area README at
  [`data/atomic_clocks/README.md`](../../data/atomic_clocks/README.md);
- the row and constraint schema sketch at
  [`data/atomic_clocks/schema.md`](../../data/atomic_clocks/schema.md);
- the source-candidate and stop-condition note at
  [`docs/notes/atomic-clock-source-candidates.md`](../notes/atomic-clock-source-candidates.md).

One atomic-clock direct-row seed has been ingested as sandbox-only data:
Beloy 2021 / BACON (`ACR-0001`). No benchmark, residual map, prediction
registry entry, canonical result, claim, or knowledge artifact has been
created from it.

Current next tasks:

- `TASK-0327` added a metadata-only atomic-clock source manifest template:
  [`data/atomic_clocks/source_manifest_template.yaml`](../../data/atomic_clocks/source_manifest_template.yaml)
  and
  [`docs/reviews/atomic-clock-source-manifest-template-review.md`](../reviews/atomic-clock-source-manifest-template-review.md);
- `TASK-0328` added a synthetic-only loader dry-run with fabricated rows:
  [`data/atomic_clocks/synthetic_loader_dry_run.yaml`](../../data/atomic_clocks/synthetic_loader_dry_run.yaml),
  [`physics_lab/engines/atomic_clock_residuals.py`](../../physics_lab/engines/atomic_clock_residuals.py),
  and
  [`docs/reviews/atomic-clock-synthetic-loader-dry-run.md`](../reviews/atomic-clock-synthetic-loader-dry-run.md).
- `TASK-0330` and `TASK-0331` reviewed the two most important source classes:
  direct frequency-ratio measurements and derived drift/constraint sources;
- `TASK-0332` ran the real-row readiness gate before any real clock value can
  be added;
- `TASK-0344` locked the uncertainty and covariance semantics required before
  direct rows or derived constraints can enter a residual axis;
- `TASK-0355` and `TASK-0363` continue the Beloy 2021 source-artifact and
  covariance hardening path;
- `TASK-0372` added the `SOURCE_ARTIFACT_VERSION_DRIFT` stop condition so
  arXiv, version-of-record, or supplement disagreements halt row curation
  before any value-bearing row is committed;
- `TASK-0371` added the first Beloy 2021 / BACON direct-ratio seed under
  sandbox-only flags;
- `TASK-0401` re-ran the row-readiness gate and classified Atomic as
  `PINNED_DATASET`, not `BASELINE_READY`;
- `TASK-0402` reconstructed a source-derived, positive-semidefinite
  cross-ratio covariance approximation for the Beloy rows;
- `TASK-0403` triaged Nemitz 2016 / RIKEN Yb/Sr as the recommended second
  independent direct-ratio source, but left ingestion to a follow-up task;
- `TASK-0452`, `TASK-0453`, and the `TASK-0485` through `TASK-0488` wave are
  the next executable blockers to close before a later baseline-readiness gate
  can honestly run.

`TASK-0401` records `PINNED_DATASET`: the Beloy rows are pinned and
source-reviewed, but Atomic is not `BASELINE_READY`. The remaining blockers are
second-source ingestion or waiver, holdout/no-peek boundary, deterministic
real-row loader, and benchmark-time covariance policy acceptance.

The next tasks can run in parallel because they own separate surfaces:
Nemitz source ingestion, real-row loader, and holdout/no-peek manifest. None
should fit drift, derive constants constraints, or promote a claim.

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
They should also follow the
[Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md) so direct
frequency-ratio rows, derived constraints, covariance blockers, and reveal
boundaries are reviewed before row curation.

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
- run a real-row readiness gate before any future row seed;
- curate a single source-specific row seed only when covariance, confidence
  level, direct-vs-derived, and version-drift stop conditions are satisfied;
- ingest Nemitz 2016 as the second direct Yb/Sr source if arXiv/Nature
  version-drift, checksum, license, and uncertainty gates pass;
- add a deterministic real-row loader for committed direct_measurement rows;
- define a holdout/no-peek manifest before any benchmark consumer touches
  atomic rows;
- rerun the baseline-readiness gate after source, loader, and holdout blockers
  are closed;
- define a no-peek freeze package for a future source update;
- audit whether derived constraints can be separated from direct measurements.

Unsafe next tasks:

- ingest real frequency ratios directly from a review plot;
- fit constants drift before source and correlation semantics are fixed;
- merge direct rows and derived constraints in one unflagged table;
- add prediction registry entries before a source manifest and holdout policy
  exist.
- run the Yb/Sr cross-source consistency benchmark before `TASK-0455` declares
  Atomic `BASELINE_READY`.

## What Not To Claim

- Do not claim evidence for constants drift.
- Do not claim evidence for new constants or broad anomaly explanations.
- Do not frame clock comparisons as a broad anomaly explanation surface.
- Do not treat source-surface readiness as benchmark readiness.
- Do not promote any atomic-clock result without a later maintainer-reviewed
  ingestion, benchmark, and claim-promotion path.
