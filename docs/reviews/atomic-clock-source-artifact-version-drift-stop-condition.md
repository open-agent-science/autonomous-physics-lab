# Atomic-Clock Source Artifact Version-Drift Stop Condition

**Task:** `TASK-0372`
**Campaign:** Atomic-Clock Residuals
**Status:** metadata-only stop-condition update
**Verdict:** `VALID_AS_BLOCKER_POLICY`

## Scope

This review records the `SOURCE_ARTIFACT_VERSION_DRIFT` stop condition
recommended by the TASK-0363 Beloy 2021 source-artifact preflight.

The task is source-intake policy only. It does not fetch source artifacts,
commit PDFs, copy clock ratios, record uncertainties, curate real rows, run
fits, add prediction entries, or promote claims.

## Inputs Reviewed

- `tasks/TASK-0372-add-atomic-source-artifact-version-drift-stop-condition.yaml`
- `docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md`
- `data/atomic_clocks/source_manifest_template.yaml`
- `data/atomic_clocks/source_artifacts/2021-beloy-bacon/README.md`
- `docs/campaigns/atomic-clock-residuals.md`
- `docs/reviews/atomic-clock-real-row-readiness-gate.md`

## Stop Condition

`SOURCE_ARTIFACT_VERSION_DRIFT` fires when two reviewed versions of the same
source artifact disagree on any value-bearing or row-defining field needed for
curation.

Examples:

- an arXiv preprint and version-of-record table disagree on a frequency-ratio
  value;
- uncertainty totals or uncertainty decomposition differ across source
  versions;
- campaign windows, epoch labels, or row inclusion boundaries change across
  versions;
- the table shape differs enough that row identity is ambiguous.

When the condition fires, row curation is blocked until a separate review
resolves the discrepancy.

## Required Curator Behavior

The future row-curation task must:

1. stop before committing any real row;
2. preserve the discrepancy in a source-specific review;
3. identify the compared source versions and artifact locators;
4. record checksum or archive status for each reviewed version when available;
5. ask for maintainer review before selecting one version, representing both as
   separate source artifacts, or rejecting the source for the first row seed.

The row-curation task must not silently choose one source version, average
across versions, copy values from memory, or normalize the discrepancy inside
the dataset file.

## Repository Changes

- `data/atomic_clocks/source_manifest_template.yaml` now lists
  `SOURCE_ARTIFACT_VERSION_DRIFT` under `global_stop_conditions` and defines
  the blocker behavior in `stop_condition_definitions`.
- `data/atomic_clocks/source_artifacts/2021-beloy-bacon/README.md` now makes
  the Beloy arXiv-versus-Nature comparison an explicit halt condition before
  any row can be committed.

## Impact

This strengthens atomic-clock source intake before value-bearing rows exist.
The campaign stays at source-specific review readiness, not real-row readiness.

Blocked states remain blocked:

- no real atomic-clock row is added;
- no benchmark is run;
- no drift fit or constants-variation constraint is recorded;
- no prediction registry entry, result, claim, or knowledge file is promoted.

## Limitations

- This task does not inspect the Beloy 2021 source artifacts or determine
  whether a version drift actually exists.
- It does not define a full source-artifact schema.
- It does not decide whether an arXiv preprint or version-of-record table
  should dominate when a discrepancy is found.
- A future source-specific task still needs retrieval dates, checksums or
  archive policy, license review, covariance treatment, row-class labels, and
  real-row validation before any value-bearing row can be accepted.
