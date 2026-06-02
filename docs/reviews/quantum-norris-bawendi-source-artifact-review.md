# Quantum Norris-Bawendi Source Artifact Review

**Task:** `TASK-0489`
**Status:** review (metadata-only source-artifact package)
**Campaign:** Quantum Size Effects
**Source candidate:** `norris-bawendi-1996-prb-cdse-band-edge`
**DOI:** `10.1103/PhysRevB.53.16338`
**Decision:** `BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`
**Review date:** 2026-06-02

## Scope

This review executes `TASK-0489` for the Quantum Size Effects campaign. It
packages deterministic source evidence for Norris, D. J.; Bawendi, M. G.
(1996), DOI `10.1103/PhysRevB.53.16338`, without adding row-level measurements
or redistributing publisher material.

The task is source-artifact work only. It does not create a `qd-*.yaml` dataset
file, does not estimate figure coordinates, does not run the quantum baseline
benchmark, and does not unblock `TASK-0225`, `TASK-0293`, or `TASK-0336`.

It is the fuller source-artifact review that `TASK-0398` deferred to a later
source-package task (see the "Relationship To TASK-0489" section of
`docs/reviews/quantum-norris-bawendi-1996-digitization-preflight.md`).

## Inputs Reviewed

- `tasks/TASK-0489-package-quantum-norris-bawendi-source-artifact-review.yaml`
- `tasks/TASK-0398-package-norris-bawendi-1996-digitization-preflight.yaml`
- `docs/reviews/quantum-norris-bawendi-1996-digitization-preflight.md`
- `docs/reviews/quantum-open-direct-table-source-triage.md`
- `docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/quantum-direct-source-artifact-intake.md`
- `docs/reviews/quantum-jasieniak-2011-source-artifact-package.md`
- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/source_artifacts/jasieniak-2011/README.md`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- APS article landing page for DOI `10.1103/PhysRevB.53.16338`

## Method

1. Re-read the task contract, the `TASK-0398` digitization preflight, and the
   `TASK-0364` direct-table verification record.
2. Searched the repository for committed Norris-Bawendi source files, extracted
   tables, axis-calibration artifacts, and extracted-point CSVs.
3. Confirmed the verified provenance class recorded by `TASK-0364` rather than
   re-asserting the original `TASK-0347` triage prediction.
4. Created a metadata-only source-artifact package under
   `data/quantum_dots/source_artifacts/norris-bawendi-1996-prb-cdse-band-edge/`
   following the intake metadata schema.
5. Added a pointer in the source manifest notes to the reviewed artifact
   package while preserving the non-redistribution guardrail.

No row values were copied, inferred, digitized, or generated. No live external
fetch was performed.

## Evidence

### E1. Source locator is concrete

The source is registered as `norris-bawendi-1996-prb-cdse-band-edge` in
`data/quantum_dots/source_manifest.yaml` with `inclusion_decision: excluded`.

Persistent locators:

- DOI: `https://doi.org/10.1103/PhysRevB.53.16338`
- Journal: Physical Review B 53, 16338-16346 (1996)
- Material: CdSe; candidate axes `absorption_peak_eV` and `bandgap_eV`.

The `TASK-0347` open-direct-table triage ranked this candidate first of six
because APS public-access policy is more reliable than ACS supporting-
information routes and the article was expected to expose a `table_derived`
first-exciton surface.

### E2. The expected table-derived path is already falsified

The `TASK-0347` triage prediction of `table_derived` did **not** survive
inspection. `TASK-0364` checked a maintainer-provided sandbox PDF copy (held
only under a local `/tmp` path; no publisher PDF committed) using `pdftotext`
and recorded:

- printed `Table N` headers found: 0
- inline body-text (size -> energy) value pairs found: 0
- verified provenance class: `figure_derived`
- outcome: `not_admissible_for_table_derived_curation`

This is preserved in `data/quantum_dots/source_manifest.yaml` under the
`attempted_verifications` round `TASK-0364-2026-05-25` and in
`docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md`.

This review accepts that finding and does not reclassify the source as
table-derived. The consequence for source-artifact packaging is concrete: the
only admissible future artifact is a deterministic figure-digitization package,
not a printed-table extraction.

### E3. No deterministic artifact is committed

The repository contains review notes and manifest metadata, but no committed
source table, checksum-pinned PDF, table extraction, figure image, axis
calibration, or extracted-points artifact for Norris-Bawendi 1996. In
particular:

- no `data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`
  artifact directory with `axis_calibration.csv` / `extracted_points.csv`;
- no verified PDF SHA-256 digest;
- no row-level `qd-*.yaml` CdSe direct-measurement seed.

### E4. Copyright and provenance constraints block committing the article here

The manifest uses `checksum_policy: doi_pinned` and states that APS tables or
figures must not be redistributed without compliance with APS copyright terms.
This review therefore keeps the package metadata-only: record the locator,
verified evidence class, figure-panel checklist, and checksum plan, but do not
commit the publisher PDF or a rasterized figure.

### E5. Row-level curation is blocked by the LLM-agent tool gap

Under `docs/quantum-direct-measurement-digitization-protocol.md`, a
`figure_derived` source may produce rows only through a WebPlotDigitizer-class
extraction with axis calibration and per-point provenance. The protocol is
explicit that an LLM agent without such a tool must not estimate figure
coordinates by eye. This task is executed by an LLM agent with no deterministic
digitization tool and no live-fetch permission, so no compliant artifact can be
produced here. Any row-level output would come from memory, eyeballing, or a
calibration polynomial — all forbidden.

## Artifact Package Added

This review adds:

- `data/quantum_dots/source_artifacts/norris-bawendi-1996-prb-cdse-band-edge/README.md`

The package records the 13 intake metadata fields, the source locator, the
verified `figure_derived` evidence class, the figure-panel verification
checklist, the checksum/archive plan, and the current blocker. It contains no
measurements and must not be used as a source for benchmark rows.

It also adds a pointer in the `norris-bawendi-1996-prb-cdse-band-edge` manifest
`notes` field to this reviewed package, mirroring the Jasieniak 2011 pattern.

## Decision

`BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`

Norris-Bawendi 1996 remains a scientifically promising CdSe direct-measurement
candidate, but it is **not** a table-derived source: `TASK-0364` verified that
the relevant data live in figures, not printed tables. This review packages the
source locator, the verified evidence class, and the deterministic acquisition
plan, but the required digitization artifact is still absent.

Therefore:

- `TASK-0336` remains blocked;
- `TASK-0293` remains blocked;
- `TASK-0225` remains blocked for measurement-versus-model benchmarking;
- no `qd-*.yaml` CdSe seed is created.

## Required Unblock Path

A future row-curation task may proceed only after a deterministic
WebPlotDigitizer-class package for the relevant Norris-Bawendi 1996 figure
exists under
`data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`,
including:

- axis calibration anchors (>= 4, preferably two per axis);
- per-point extracted coordinates and converted physical values;
- extraction-tool name and version;
- per-point provenance and coordinate uncertainty (digitization read error
  combined with the publication's stated measurement uncertainty);
- explicit inclusion/exclusion status per point, with >= 6 surviving rows;
- separation of `absorption_peak_eV` and `bandgap_eV` semantics, and of
  assignment-derived or model values from direct spectroscopic measurements.

A maintainer-provided, license-cleared file with a recorded SHA-256 digest may
substitute for the access step, but it does not remove the digitization step
because the source is figure-derived.

## What This Review Did Not Do

- It did not ingest real quantum-dot values.
- It did not add or edit `data/quantum_dots/qd-*.yaml`.
- It did not commit APS PDFs, figures, or tables.
- It did not use LLM-estimated coordinates.
- It did not run a baseline residual benchmark.
- It did not change any task status other than its own (`TASK-0489`).
- It did not promote claims, results, knowledge entries, synthesis guidance,
  device claims, or biomedical claims.

## Limitations

- The conclusion is access- and tool-limited, not source-disqualifying.
- The review relied on the `TASK-0364` verified provenance class rather than a
  fresh inspection of the article; a future digitization pass should confirm
  the exact figure panel and point count.
- The artifact package does not replace a checksum-pinned source or
  deterministic extraction.
- A future maintainer may prefer a different approved source artifact if it is
  better licensed or easier to verify.

## Output Routing Summary

Per `docs/result-promotion-protocol.md`:

- **Task verdict:** `INCONCLUSIVE` for direct row production; `VALID` as a
  source-artifact blocker package (the locator, verified evidence class, and
  deterministic acquisition plan are now reviewable, while row-level curation
  remains correctly blocked).
- **Canonical destination:** `docs/reviews/` note plus a metadata-only
  source-artifact package under `data/quantum_dots/source_artifacts/`; no
  `results/`, `prediction_registry/`, `claims/`, or `knowledge/` change.
- **Review tier:** `none` (no tiered RESULT/PRED artifact produced).
- **Gate status:** Gate A not attempted, Gate B not attempted (no measurement
  rows or benchmark metrics produced).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations and blockers:** no live fetch and no deterministic digitization
  tool available to this LLM agent; the source is verified `figure_derived`, so
  the remaining admissible path is a WebPlotDigitizer-class digitization
  artifact or a maintainer-provided, license-cleared file plus that artifact.

## Verdict

`BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`

The Norris-Bawendi 1996 candidate stays excluded from curated `qd-*.yaml` rows
and must not be used to unblock the quantum size-effect baseline benchmark
until a deterministic figure-digitization artifact is committed and reviewed.
