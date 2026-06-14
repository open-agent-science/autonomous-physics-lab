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

Pinned-dataset source surface with two committed direct-ratio seeds (Beloy
2021 `ACR-0001` and Nemitz 2016 `ACR-0002`), a deterministic real-row loader, a
source-derived covariance approximation, synthetic cross-source dry-run
plumbing, a first-benchmark covariance policy, manifest-backed Beloy row-role
assignments, a Pizzocaro per-window diagnostic ledger, and baseline-readiness
gate reruns that have kept the campaign at `PINNED_DATASET`. `TASK-0704`
(DONE) curated and committed the Nemitz `ACR-0002` Yb/Sr row, so the
second-source blocker that previously held the campaign is now cleared.
Pizzocaro remains diagnostic-only: its post-PSD row-admissibility review
preserved the aggregation blocker. The primary path to the first Yb/Sr
benchmark is now the `TASK-0705` baseline-readiness gate rerun, which decides
whether Atomic moves from `PINNED_DATASET` to `BASELINE_READY` and unblocks the
`TASK-0456` benchmark. No real-row benchmark yet.

## Public Monitoring Snapshot

**Current question:** can high-precision atomic-clock comparison data be
curated with source provenance, covariance, and version-drift semantics intact
before any residual analysis?

**Shareable result:** APL has pinned Beloy 2021 / BACON as a sandbox-only
direct-frequency-ratio seed (`PINNED_DATASET`), reconstructed a positive-
semidefinite source-derived covariance approximation, pinned the correct
Nemitz 2016 RIKEN Yb/Sr arXiv source artifact, and defined conservative
covariance states for the first benchmark. `TASK-0453` also landed a
deterministic loader for committed `direct_measurement` rows, and `TASK-0488`
landed a synthetic-only cross-source fixture. `TASK-0455` reran the
baseline-readiness gate and kept Atomic below `BASELINE_READY` because no
second value-bearing direct source row is committed and the Beloy row-level
holdout assignments remain unpopulated. The campaign is deliberately not
fitting constants drift yet.

**Not a claim:** no atomic-clock residual benchmark, constants-drift result,
new constant, or anomaly explanation exists in APL.

**Active next work:** `TASK-0704` (DONE) committed the Nemitz `ACR-0002` Yb/Sr
row, completing the second-source curation step. The immediate Atomic path is
now the `TASK-0705` baseline-readiness gate rerun, which uses only the
committed Beloy and Nemitz row/source/covariance artifacts to classify Atomic
as `BASELINE_READY` or not and to state whether `TASK-0456` may proceed. A
secondary Pizzocaro path (`TASK-0742`, row-admissibility extraction ledger
gate) may define a sensitivity-only observable-harmonization contract, but it
should not be used as a benchmark row without that contract. `TASK-0652` also
pinned Lange/PTB Yb+ metadata, but that source is a separate Yb+ family (E3/Cs
and E3/E2), not a Yb/Sr benchmark unblocker.

**Expected next result:** a `TASK-0705` baseline-readiness verdict. If it
returns `BASELINE_READY`, the first narrow Yb/Sr cross-source consistency
benchmark (`TASK-0456`) can be unblocked and run on the committed Beloy and
Nemitz rows. If it stays below readiness, the review preserves the exact
remaining blocker (for example row-level holdout/no-peek assignment or
covariance treatment) and Atomic stays source-gated.

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
  independent direct-ratio source;
- `TASK-0452` pinned the correct Nemitz 2016 arXiv artifact
  (`arXiv:1601.04582`) with checksum/provenance and corrected the older
  locator error, but rows remain blocked by version-of-record table review and
  campaign-window lock;
- `TASK-0453` added the deterministic real direct-row loader and
  source-field split (`source` for real rows, `source_metadata` for synthetic
  fixtures);
- `TASK-0488` added a synthetic-only cross-source dry run that exercises row
  roles, covariance-state labels, and no-peek flags without unblocking real
  benchmark work;
- `TASK-0485` ranked second-source fallback candidates if Nemitz remains
  row-blocked;
- `TASK-0486` defines the first-benchmark covariance policy:
  [`docs/reviews/atomic-first-benchmark-covariance-policy.md`](../reviews/atomic-first-benchmark-covariance-policy.md).
  Exact committed covariance can support correlated diagnostics,
  source-derived PSD approximations are sensitivity-only, diagonal-only
  assumptions are exploratory, and shared-systematic ambiguity blocks
  high-precision interpretation.
- `TASK-0455` reran the baseline-readiness gate:
  [`docs/reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md`](../reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md).
  The verdict remains `PINNED_DATASET`, not `BASELINE_READY`.
- `TASK-0538` assigned Beloy row roles through the manifest-backed schema,
  removing the old row-role assignment blocker for the current seed rows.
- `TASK-0542` pinned the Pizzocaro source artifacts with matched hashes and
  provenance; rows remain blocked pending table-to-row mapping, ratio
  orientation, campaign window, uncertainty/covariance, and direct-vs-derived
  row classification.
- `TASK-0567` is now the row-admissibility gate that decides whether a
  Pizzocaro row can be committed or whether the source remains blocker memory.
- `TASK-0636` created a deterministic Pizzocaro per-window diagnostic ledger
  for 10 VLBI campaign windows while preserving the shared-systematics blocker.
- `TASK-0651` found Pizzocaro covariance reconstruction feasible as a
  `COV_SOURCE_DERIVED_PSD_APPROX` approximation, under-specified for an exact
  committed covariance matrix.
- `TASK-0652` pinned Lange/PTB Yb+ metadata and reuse blockers; it is a
  separate Yb+ source-family path, not a Yb/Sr benchmark unblocker.
- `TASK-0666` committed a source-derived Pizzocaro PSD covariance
  approximation for sensitivity-only diagnostics.
- `TASK-0686` re-gated Pizzocaro after that covariance work and preserved the
  aggregation blocker; Pizzocaro remains diagnostic-only until a separate
  aggregation or observable-harmonization contract lands.

`TASK-0401` records `PINNED_DATASET`: the Beloy rows are pinned and
source-reviewed, but Atomic is not `BASELINE_READY`. After `TASK-0455`, the
remaining blockers are second-source value-bearing row ingestion or waiver,
row-level holdout/no-peek assignment from the manifest, and direct-vs-derived
separation for broad derived-constraint or mixed-axis work. The real-row
loader and first-benchmark covariance policy blockers are cleared at the
policy/validation level.

The next tasks can run in parallel only when they own separate surfaces:
Nemitz `ACR-0002` row curation, Pizzocaro observable harmonization, or a
separate-family Lange/PTB artifact route. None should fit drift, derive
constants constraints, or promote a claim.

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
- curate Nemitz 2016 value-bearing rows only after arXiv/Nature version-drift,
  table-level uncertainty, campaign-window, checksum, and license gates pass;
- populate row-level holdout/no-peek fields from the manifest before any
  benchmark consumer touches atomic rows;
- rerun the baseline-readiness gate only after a second value-bearing source
  row is committed or explicitly waived;
- rerun the baseline-readiness gate after a Nemitz `ACR-0002` row package
  passes, while preserving any failed source as blocker memory;
- define a no-peek freeze package for a future source update;
- audit whether derived constraints can be separated from direct measurements.
- define a narrow Pizzocaro observable-harmonization contract only if the
  campaign still needs diagnostic cross-source consistency after Nemitz;
- keep Lange/PTB metadata-only until maintainer license approval before any
  source copy, checksum, or value extraction task.

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
