# Quantum Jasieniak 2011 Source Artifact Package

**Task:** `TASK-0334`
**Status:** review (metadata-only source-artifact package)
**Source candidate:** `jasieniak-2011-acs-nano-band-edge`
**Decision:** `BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`
**Retrieval review date:** 2026-05-22

## Scope

This review executes TASK-0334 for the Quantum Size Effects campaign. It
attempts to package deterministic source evidence for Jasieniak, Califano, and
Watkins (2011), DOI `10.1021/nn201681s`, without adding row-level
measurements or redistributing publisher material.

The task is source-artifact work only. It does not create a `qd-*.yaml`
dataset file, does not run the quantum baseline benchmark, and does not
unblock `TASK-0225`, `TASK-0293`, or `TASK-0336`.

## Inputs Reviewed

- `tasks/TASK-0334-package-quantum-jasieniak-source-artifact.yaml`
- `docs/campaigns/quantum-size-effects.md`
- `docs/reviews/quantum-size-direct-band-edge-seed-review.md`
- `docs/reviews/quantum-direct-measurement-digitization-package.md`
- `docs/reviews/quantum-direct-measurement-source-triage.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/digitization/jasieniak-2011-acs-nano-band-edge/README.md`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- ACS article metadata page for DOI `10.1021/nn201681s`
- ACS Supporting Information locator
  `https://pubs.acs.org/doi/suppl/10.1021/nn201681s/suppl_file/nn201681s_si_001.pdf`

## Method

1. Re-read the task contract and the existing TASK-0292/TASK-0325 blocker
   records.
2. Searched the repository for committed `nn201681s` source files,
   extracted tables, axis-calibration artifacts, and extracted-point CSVs.
3. Checked the public ACS metadata surface for whether Supporting Information
   exists and whether it advertises tabulated energy-point data.
4. Created a metadata-only source-artifact README under
   `data/quantum_dots/source_artifacts/jasieniak-2011/`.
5. Updated the source manifest notes to point future curators at the reviewed
   artifact package and preserve the non-redistribution guardrail.

No row values were copied, inferred, digitized, or generated.

## Evidence

### E1. Source locator is concrete

The source remains registered as
`jasieniak-2011-acs-nano-band-edge` in
`data/quantum_dots/source_manifest.yaml`.

Persistent locators:

- DOI: `https://doi.org/10.1021/nn201681s`
- ACS article page: `https://pubs.acs.org/doi/abs/10.1021/nn201681s`
- ACS Supporting Information locator:
  `https://pubs.acs.org/doi/suppl/10.1021/nn201681s/suppl_file/nn201681s_si_001.pdf`

The public ACS metadata surface lists the Supporting Information file
`nn201681s_si_001.pdf` and describes the SI as containing tabulated energy
points, optical band-gap relations, and size-dependent energy-level diagrams.
That is enough to keep Jasieniak 2011 as the correct first source-artifact
target, but not enough to curate rows without inspecting the file itself.

### E2. No deterministic artifact is committed

The repository contains review notes and a TASK-0325 blocker directory, but no
committed source table, checksum-pinned SI file, table extraction, figure image,
axis calibration, or extracted-points artifact for Jasieniak 2011.

The local repository evidence remains:

- `data/quantum_dots/source_manifest.yaml` — source metadata only;
- `data/quantum_dots/digitization/jasieniak-2011-acs-nano-band-edge/README.md`
  — blocker note only;
- no `axis_calibration.csv`;
- no `extracted_points.csv`;
- no verified `nn201681s_si_001.pdf` checksum;
- no row-level `qd-*.yaml` band-edge seed.

### E3. Copyright and provenance constraints block committing the SI file here

The source manifest already uses `checksum_policy: doi_pinned` and states that
ACS tables or figures should not be redistributed without permission. TASK-0334
therefore should not commit the publisher PDF or SI file unless a maintainer
confirms the repository policy and license allow it.

This PR keeps the package metadata-only and records the checksum plan instead:
retrieve the official SI from the ACS locator, store only a SHA-256 digest and
a non-copyrighted extraction log unless redistribution is explicitly allowed.

### E4. Row-level curation remains blocked

The ACS metadata strongly suggests a future curator may be able to produce
`>=6` direct band-edge rows. However, this task did not inspect the SI table
contents or digitize figures. Any row-level output in this PR would therefore
come from memory, inferred source structure, or LLM-estimated values, all of
which are forbidden by the digitization protocol.

## Artifact Package Added

This PR adds:

- `data/quantum_dots/source_artifacts/jasieniak-2011/README.md`

The package records:

- source locator;
- retrieval date;
- expected upstream artifact name;
- checksum/archive plan;
- license/citation notes;
- figure/table identifiers to verify;
- whether future rows should be treated as table-derived or digitized;
- exact unblock conditions before `TASK-0336`.

It is intentionally not a data artifact. It contains no measurements and must
not be used as a source for benchmark rows.

## Decision

`BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED`

Jasieniak 2011 remains admissible as a candidate direct band-edge source, and
the official ACS metadata indicates a Supporting Information path that likely
contains the needed energy-point tables. This PR packages the source locator
and deterministic artifact plan, but the actual table or digitization artifact
is still absent.

Therefore:

- `TASK-0336` remains blocked;
- `TASK-0293` remains blocked;
- `TASK-0225` remains blocked for measurement-versus-model benchmarking;
- no `qd-*.yaml` band-edge seed is created.

## Required Unblock Path

A future row-curation task may proceed only after at least one of these
reviewable inputs exists:

1. A maintainer-provided `nn201681s_si_001.pdf` or equivalent official SI copy
   with retrieval date and SHA-256 digest, plus permission or policy guidance
   on whether the file itself can be committed.
2. A non-copyrighted table extraction from the SI, with table identifiers,
   row locators, units, uncertainty semantics, and source checksum metadata.
3. A deterministic WebPlotDigitizer-class package for the relevant figure,
   including axis calibration, extracted points, tool/version notes, and
   coordinate uncertainty.

Once one of those exists, `TASK-0336` can curate rows while preserving
band-edge semantics: row notes must distinguish valence-band energy,
conduction-band energy, optical gap, and any derived `bandgap_eV` value.

## What This Review Did Not Do

- It did not ingest real quantum-dot values.
- It did not add or edit `data/quantum_dots/qd-*.yaml`.
- It did not commit ACS PDFs, figures, or tables.
- It did not use LLM-estimated coordinates.
- It did not run a baseline residual benchmark.
- It did not promote claims, results, knowledge entries, synthesis guidance,
  device claims, or biomedical claims.

## Limitations

- The conclusion is access-limited, not source-disqualifying.
- The review did not inspect the actual SI table values, so it cannot confirm
  row count, material coverage, units, or uncertainty semantics.
- The artifact package does not replace a checksum-pinned source or
  deterministic extraction.
- A future maintainer may choose a different approved source artifact if it is
  better licensed or easier to verify.

## Verdict

`INCONCLUSIVE` for direct row production.

`VALID` as a source-artifact blocker package: the source locator and
deterministic acquisition plan are now reviewable, while row-level curation
remains correctly blocked until a source table or digitization artifact exists.
