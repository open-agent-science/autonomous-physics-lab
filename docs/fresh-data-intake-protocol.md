# Fresh-Data Intake Protocol

> Sits under the [Published-Source and Reusable-Dataset Standard](published-source-dataset-standard.md),
> which adds the published≠redistributable rule, the `blocker_type` routing
> vocabulary, and the reusable-dataset publication standard. Read that standard
> first for source admissibility and dataset-publication rules.

## Purpose

This protocol defines the shared source-to-row workflow for fresh-data work
across active APL campaigns. It is a guardrail for moving from a candidate
source to pinned artifacts, extracted tables or figures, curated rows,
validated row schemas, baseline readiness, and benchmark readiness.

It is not a data-ingestion task. It does not add source values, benchmark
metrics, residual plots, prediction entries, results, claims, or knowledge
promotion.

Use it with:

- [Fresh-Data Source Policy](notes/fresh-data-source-policy.md)
- [Fresh-Data Stop Conditions](fresh-data-stop-conditions.md)
- [Source Manifest Minimum Schema](source-manifest-minimum-schema.md)
- [Research Quality Gate](research-quality-gate.md)
- [Claim Promotion Policy](claim-promotion-policy.md)

## Non-Admissible Inputs

The following are never admissible as committed data:

- LLM-recalled numerical values.
- Prose-only numerical claims without a pinned source artifact.
- Screenshot-only or plot-only values without deterministic extraction
  records.
- Central values copied from a review when the primary-source trail is hidden.
- Rows whose unit, uncertainty, covariance, source version, or row class cannot
  be reviewed.

These inputs may be preserved as blockers or source-candidate notes, but they
must not become benchmark rows.

## Source-Selection Preference Order (Open-Licensed-First)

When a campaign needs a new source, rank candidates by **both** redistribution
license and extraction cost, and exhaust higher tiers before lower ones. The
goal is to land table-derived rows from open-licensed data rather than to mass-
digitize closed figures.

- **Tier 1 — Open tabulated data (preferred).** CC0 / CC BY / open-data-licensed
  datasets or repository releases (e.g. Zenodo, Figshare, OSF, government or
  materials databases) that publish the numerical per-row values directly.
  Table-derived; no digitization; no permission; lowest provenance risk.
- **Tier 2 — Open-licensed article with a tabulated table or SI.** A CC BY (or
  equivalently open) article whose primary or supplementary table contains the
  per-sample values. Table-derived; attribution only.
- **Tier 3 — Open-licensed article with figure-only data.** A CC BY / open
  article whose values live in figures and require a WebPlotDigitizer-class tool
  run. The license is clear, but extraction cost and digitization uncertainty are
  higher. Acceptable, not preferred.
- **Tier 4 — Closed or permission-required (last resort).** Subscription/closed
  sources, or any source needing per-figure digitization without an open
  license. Admissible only with explicit author/publisher redistribution
  permission recorded in `data/DATA_LICENSES.yaml`, and never via mass-
  digitization of closed figures.

Rules:

- Record each candidate's tier in the source manifest or review note.
- Do not open a Tier 3/4 figure-digitization lane while an untried Tier 1/2
  candidate plausibly exists for the same campaign axis.
- Prefer one Tier 1/2 source that lands table-derived rows over several Tier 3/4
  lanes that each preserve a blocker.
- The preference order is additive: it does not weaken the source, license,
  checksum, holdout, or overclaim gates below.

This rule encodes the Quantum Size Effects lesson, where repeated closed
figure-PDF scouts (Tier 4) stalled the campaign while open tabular alternatives
(Tier 1/2) were not exhausted first. See
[Quantum open-licensed-first application](reviews/quantum-open-licensed-first-source-selection-application.md).

## Lifecycle Stages

### SOURCE_CANDIDATE

Meaning: a publication, archive record, API endpoint, supplementary file,
repository release, figure, or review table may contain relevant data.

Entry criteria:

- The campaign need is explicit.
- The source has a stable locator candidate such as DOI, arXiv id, archive URL,
  release page, repository tag, or API endpoint.
- The intended row class is named, even if provisional.

Exit criteria:

- The source has an admissibility decision: continue, halt, or split by source
  class.
- Known blockers are named using the
  [Fresh-Data Stop Conditions](fresh-data-stop-conditions.md) vocabulary when
  available.
- The next step is one of source review, artifact pinning, extraction planning,
  or blocker preservation.

Mandatory artifacts:

- Source-candidate note, manifest entry, or review section.
- Locator and citation notes.
- Intended row class and campaign axis.

Campaign-specific artifacts:

- Nuclear: measured/extrapolated boundary and no-peek or reveal boundary.
- Quantum: material, property kind, size axis, and table or figure target.
- Atomic: transition labels, ratio partner, epoch, and direct-vs-derived class.
- Exoplanets: catalog table, query contract, mass/radius provenance class, and
  detection method axis.

### SOURCE_ARTIFACT_PINNED

Meaning: the source artifact or stable source locator is frozen for review.

Entry criteria:

- A source candidate passed source review.
- Retrieval date or archive date is recorded.
- Redistribution and license posture is reviewed.
- A checksum, archive policy, or metadata-only locator policy is chosen.

Exit criteria:

- Every value-bearing artifact has a checksum or a documented reason it cannot
  be redistributed.
- The manifest says whether validation may use live external fetches. The
  default is no.
- The source has an explicit next step: table extraction, figure digitisation,
  row curation, or blocker preservation.

Mandatory artifacts:

- Source manifest entry or source artifact package.
- Retrieval date.
- Checksum or archive policy.
- License and citation notes.
- Live-fetch policy.

Optional validation:

- Run `python3 -m physics_lab.cli validate-source-artifact-package <package-dir>`
  on packages that use the reusable source-artifact package shape.
  Use `--json` when automation needs machine-readable issue output.

Campaign-specific artifacts:

- Query contracts for API snapshots.
- Supplementary table locator and checksum for publication tables.
- Figure image provenance and digitisation plan for plot-derived points.
- Covariance or correlation locator when rows are not independent.

### TABLE_OR_FIGURE_EXTRACTED

Meaning: source values have been extracted from a pinned table, API snapshot,
supplementary artifact, or figure using a deterministic, reviewable process.

Entry criteria:

- The source artifact is pinned or the task explicitly records a blocker for
  why only metadata can be preserved.
- Extraction method is declared before values are trusted.
- The extraction surface is specific: table name, page, figure panel, API
  query, file path, or release artifact.

Exit criteria:

- Extracted values have a ledger, script output, or reviewable transcription
  record.
- Units, uncertainty semantics, and row class are attached to every extracted
  value or to an explicit shared source-level field.
- Figure-derived values include digitisation settings, calibration points, and
  precision limitations.
- Failed extraction attempts are preserved as negative memory.

Mandatory artifacts:

- Extraction ledger, deterministic script output, or transcription review. Use
  [`templates/extraction_ledger.yaml`](../templates/extraction_ledger.yaml) as
  the shared starter template when a task needs a ledger-shaped review surface.
- Source location for every extracted value group.
- Extracted-by and reviewed-by fields or equivalent review notes.
- Unit and uncertainty semantics.

Campaign-specific artifacts:

- Quantum: digitisation calibration, axis transform, point-level provenance,
  material and property-kind labels.
- Atomic: covariance notes, uncertainty budget mapping, transition and epoch
  fields.
- Exoplanets: catalog column map, row-class provenance, threshold policy, and
  exclusion reasons.
- Nuclear: measured/extrapolated flag, source release boundary, and no-peek
  reveal status.

### ROWS_CURATED

Meaning: extracted values have been transformed into campaign row objects with
reviewable provenance and explicit inclusion status.

Entry criteria:

- Extracted values exist or the task is explicitly a blocker-only curation.
- Every row maps to a campaign schema or schema sketch.
- Row-class semantics are not ambiguous.

Exit criteria:

- Every row has source id, row class, inclusion status, unit, uncertainty
  semantics, and limitation notes.
- Direct measurements, derived constraints, calibration curves, model-derived
  rows, and digitised figure points are separated.
- Excluded or blocked rows remain visible with reasons.
- The task does not silently mix incompatible axes into one benchmark surface.

Mandatory artifacts:

- Curated row file or blocker review.
- Row-class and inclusion-status fields.
- Source references back to the pinned artifact or extraction ledger.
- Negative-result or blocker notes for rejected rows.

Campaign-specific artifacts:

- Campaign row schema files.
- Holdout or reveal labels.
- Source-specific exclusion thresholds.
- Domain-specific unit conversion notes.

### ROW_SCHEMA_VALIDATED

Meaning: curated rows pass deterministic schema and loader validation.

Entry criteria:

- Curated rows or metadata-only blocker rows are committed.
- The schema validator or loader path exists.

Exit criteria:

- Schema validation passes.
- Loader validation verifies row counts, row classes, exclusion reasons, and
  source ids.
- Validation uses committed artifacts only unless a task explicitly allows a
  reviewed live fetch.
- Any stale generated board or task-view diffs remain out of the task PR.

Mandatory artifacts:

- Tests or validation commands.
- Review note with row counts or blocker counts.
- Loader limitations and failure modes.

Campaign-specific artifacts:

- Snapshot checksum tests for catalog snapshots.
- Digitisation reproducibility checks for figure-derived rows.
- Covariance review tests when correlations matter.

### BASELINE_READY

Meaning: the dataset is mature enough for a conservative baseline task, but no
benchmark has been run by the intake task itself.

Entry criteria:

- Row schema validation passed.
- The campaign has a declared baseline scope.
- Training, holdout, reveal, or source-date boundary is explicit.
- Direct, derived, calibration, model-derived, and figure-derived axes are
  separated or intentionally scoped.

Exit criteria:

- A future baseline task can cite the source artifacts and row validation
  without re-litigating source admissibility.
- Remaining limitations are explicit enough to decide whether the baseline is
  full, partial, or blocked.

Mandatory artifacts:

- Baseline readiness review.
- Allowed baseline axes.
- Excluded axes and blocker reasons.
- Validation command list.

Campaign-specific artifacts:

- Null baseline or reference model policy.
- Holdout or reveal split.
- Minimum row-count or uncertainty policy.
- Negative-control requirements.

### BENCHMARK_READY

Meaning: a baseline has landed and the campaign can run benchmark, residual,
or failure-map tasks under bounded scientific language.

Entry criteria:

- Baseline artifact exists and is reviewed.
- Result, residual, and limitation surfaces are deterministic.
- Claim-promotion rules remain separate from benchmark execution.

Exit criteria:

- Future benchmark tasks can compute metrics without changing source data.
- Benchmark tasks know which rows and axes are admissible.
- Public wording remains conservative and does not treat benchmark readiness as
  claim readiness.

Mandatory artifacts:

- Baseline result or reviewed baseline package.
- Benchmark-ready review note.
- Claim-impact statement that keeps promotion blocked until maintainer review.

Campaign-specific artifacts:

- Residual map scope.
- Prediction-freeze or reveal-readiness protocol if applicable.
- Failure-map and negative-control checklist.

## Row-Class Handling

Direct measurements:

- May become benchmark rows only when source, unit, uncertainty, and row-class
  semantics are explicit.
- Must retain source id and extraction trail.

Derived constraints:

- Must remain separate from direct rows.
- Must record the model, sensitivity coefficients, combination rules, or input
  measurements that make the row derived.

Calibration curves:

- May support a calibration-consistency benchmark only when explicitly scoped.
- Must not silently unblock a direct measurement-versus-model benchmark.

Model-derived rows:

- Are not direct observations.
- May be retained for diagnostics or excluded axes, but must not be averaged
  with direct measurements.

Figure digitisation:

- Requires deterministic calibration, point-level provenance, uncertainty or
  precision notes, and reviewer notes.
- Eyeballed plot values without an extraction record are blockers, not data.

## Required Handoff Summary

Every fresh-data intake PR should include:

- task id;
- source references;
- lifecycle stage reached;
- method;
- artifact paths;
- row counts or blocker counts;
- validation commands;
- limitations;
- verdict;
- explicit claim-impact statement.

Recommended verdicts:

- `VALID_SOURCE_CANDIDATE`
- `PINNED_ARTIFACT_READY`
- `EXTRACTION_REVIEW_READY`
- `ROWS_CURATED`
- `ROW_SCHEMA_VALIDATED`
- `BASELINE_READY`
- `BENCHMARK_READY`
- `BLOCKED_WITH_NEGATIVE_MEMORY`
- `INCONCLUSIVE_SOURCE_REVIEW`

## Promotion Boundary

This protocol does not authorize claim promotion. A campaign may be
`BENCHMARK_READY` and still not be claim-ready. Claim or knowledge promotion
requires separate maintainer review under the claim-promotion and research
quality-gate policies.
