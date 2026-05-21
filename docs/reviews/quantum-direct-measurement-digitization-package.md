# Quantum Direct-Measurement Digitization Package

**Task:** `TASK-0325`
**Status:** review (blocker package; no row-level dataset produced)
**Selected source path:** `jasieniak-2011-acs-nano-band-edge`
**Verdict:** `INCONCLUSIVE` for row-level curation; `VALID` as a documented
blocker package.

## Scope

This review executes TASK-0325 as a bounded direct-measurement
digitization/table-value package attempt. It chooses exactly one source path
from the existing triage/review notes and asks whether the repository already
contains enough committed evidence to curate `>=6` compliant direct rows.

The selected source is Jasieniak 2011 because the existing TASK-0298 and
TASK-0292 notes identify it as the strongest band-edge table path, while
Yu 2003 absorption remains figure-only without a committed WebPlotDigitizer
artifact.

This pass does not run the quantum baseline benchmark, does not add a
`qd-*.yaml` dataset file, does not fetch live external data, and does not
promote a claim, result, or knowledge artifact.

## Inputs Reviewed

- `tasks/TASK-0325-prepare-quantum-direct-measurement-digitization-package.yaml`
- `docs/campaigns/quantum-size-effects.md`
- `docs/reviews/quantum-direct-measurement-source-triage.md`
- `docs/reviews/quantum-size-direct-band-edge-seed-review.md`
- `docs/reviews/quantum-size-direct-absorption-seed-review.md`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/digitization/README.md`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`

## Method

1. Re-read the TASK-0325 contract and direct-measurement digitization protocol.
2. Re-read the source triage and the two prior direct-seed investigations.
3. Selected exactly one source path: `jasieniak-2011-acs-nano-band-edge`.
4. Searched the committed repository for source files, Supporting Information
   table artifacts, `nn201681s` files, and existing digitization outputs.
5. Compared the local evidence against the row-admission requirements in the
   digitization protocol.

No live external fetch was performed. The task explicitly permits a blocker
when source access or digitization quality is insufficient, and the local
repository has no committed source table or deterministic digitization
artifact for this source.

## Evidence Audit

### E1. Source path is registered and scientifically plausible

`data/quantum_dots/source_manifest.yaml` registers
`jasieniak-2011-acs-nano-band-edge` as an accepted band-edge source for CdSe,
CdTe, PbS, and PbSe. The source is scoped to `bandgap_eV` and
`electrical_transport` style provenance, with an explicit caveat that rows
must preserve the derivation from valence and conduction band-edge
measurements.

The TASK-0298 triage marks Jasieniak 2011 as the first-attempt source for a
band-edge seed. The TASK-0292 review records that a table path likely exists
in Supporting Information, but that the table itself was not available to the
agent and no dataset was produced.

### E2. No committed source table or SI extraction exists

The repository contains metadata and review notes for DOI `10.1021/nn201681s`,
but no committed Supporting Information PDF, table extraction, or row-level
source table for this publication. A local filename search for `nn201681s`
found no committed source file.

Because no table values are available locally, this pass cannot verify row
count, material coverage, table identity, units, uncertainty semantics, or
the source-specific definition of `bandgap_eV`.

### E3. No deterministic digitization artifact exists

Before this PR, `data/quantum_dots/digitization/` contained only the shared
README. It did not contain a
`data/quantum_dots/digitization/jasieniak-2011-acs-nano-band-edge/`
artifact directory with `axis_calibration.csv`, `extracted_points.csv`, or
tool/version notes.

This PR adds only a blocker README for that source path. It does not add
axis calibration or extracted points, so it still does not authorize any
figure-derived rows.

### E4. The `>=6` direct-row threshold cannot be met honestly

The row threshold is not a math problem here; it is an evidence problem.
Without a committed table extraction or deterministic digitization artifact,
any six rows would have to come from memory, LLM-estimated graph coordinates,
or inferred values. The digitization protocol explicitly forbids those
provenance modes.

## Decision

No `data/quantum_dots/qd-0003-*.yaml` or equivalent band-edge seed is
produced.

The correct TASK-0325 output is a blocker package:

- `data/quantum_dots/digitization/jasieniak-2011-acs-nano-band-edge/README.md`
- this review artifact

This preserves the negative result while giving the next curator an exact
source path and evidence checklist.

## Required Unblock Path

A future row-producing pass should start from one of these inputs:

- a reviewed extraction of the Jasieniak 2011 Supporting Information table
  with at least six source-located rows;
- a deterministic WebPlotDigitizer-class package for the relevant figure,
  including calibration anchors, extracted points, tool/version metadata, and
  uncertainty notes;
- maintainer-provided row values with citation, units, derivation semantics,
  uncertainty policy, and redistribution constraints.

After such evidence exists, the future curator may add a `qd-*.yaml` seed and
then run the readiness gate task. Until then, `TASK-0293` and `TASK-0225`
remain blocked on direct-measurement evidence or an explicit maintainer waiver.

## What This Review Did Not Do

- It did not run the quantum baseline benchmark.
- It did not add, edit, or remove any `qd-*.yaml` dataset file.
- It did not fetch live external data or redistribute source tables.
- It did not use LLM-estimated coordinates.
- It did not promote a claim, result, knowledge entry, synthesis claim,
  device claim, or biomedical claim.

## Limitations

- The conclusion is access-limited, not source-disqualifying.
- The review does not prove that Jasieniak 2011 lacks enough rows; it only
  shows that the current repository lacks the committed evidence needed to
  curate them.
- The blocker package contains no reusable coordinate data.
- A future curator must still decide the exact band-edge semantic for
  `bandgap_eV` before committing rows.
