# Atomic Pizzocaro Source Artifact Review

**Task:** `TASK-0542`
**Campaign:** Atomic-Clock Residuals
**Source artifact:** `ACLOCK-SRC-ARTIFACT-2020-PIZZOCARO-VLBI`
**Verdict:** `SOURCE_ARTIFACT_PINNED_ROWS_BLOCKED`

## Scope

This task pins the source artifact package for the Pizzocaro et al. optical
clock intercontinental-comparison dataset as an Atomic Yb/Sr fallback source.
It does not curate ACR rows, copy publisher PDFs, run a cross-source benchmark,
fit drift, create predictions, promote claims, or mark `TASK-0456` unblocked.

## Inputs Reviewed

- `tasks/TASK-0542-pin-atomic-pizzocaro-source-artifact.yaml`
- `docs/reviews/atomic-second-source-yb-sr-row-gate.md`
- `data/atomic_clocks/source_manifest.yaml`
- `docs/fresh-data-intake-protocol.md`
- `docs/extraction-ledger-template.md`
- Zenodo record `10.5281/zenodo.5592085`
- Related publication DOI `10.1038/s41567-020-01038-6`

## Artifact Decision

The Zenodo record is the appropriate source-artifact surface for this task:

- it is linked to the target Nature Physics publication;
- it is an open dataset with Creative Commons Attribution 4.0 International
  licensing;
- it exposes three CSV files and Zenodo md5 hashes;
- two files are explicitly Yb/Sr ratio-measurement source data, and one is
  supporting delay-resolution source data.

The Nature Physics publisher PDF is not committed. The committed files are the
Zenodo CSV artifacts only:

- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/galav-delay-resolution-function.csv`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measurements-IPPP.csv`
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv`

The local md5 hashes matched the Zenodo record, and SHA-256 checksums are
recorded in `provenance.yaml`.

## Row-Admissibility Status

The source artifact is pinned, but rows remain blocked. A future
row-admissibility task must still review:

- exact source-file-to-row mapping;
- ratio orientation and transition labels;
- campaign-window semantics from the CSV source fields;
- uncertainty and covariance semantics;
- direct-measurement versus derived/link-analysis row class;
- holdout or reveal-freeze binding;
- extraction-ledger shape for preserving source values before ACR row creation.

This review therefore improves Atomic from "Pizzocaro planning-only" to
"Pizzocaro source artifact pinned, rows blocked." It does not produce a
benchmark-ready second source.

## Manifest Update

`data/atomic_clocks/source_manifest.yaml` now records Pizzocaro/VLBI as a
member of the direct frequency-ratio source family with:

- `status: source_artifact_pinned_rows_blocked`
- `value_status: source_artifact_pinned_no_values`
- `readiness_state: SOURCE_ARTIFACT_PINNED_ROWS_BLOCKED`
- provenance at
  `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/provenance.yaml`

## Output Routing Summary

- Task verdict: `SOURCE_ARTIFACT_PINNED_ROWS_BLOCKED`
- Canonical destination:
  `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/`,
  `data/atomic_clocks/source_manifest.yaml`, and this review note.
- Review tier: `none`
- Gate A status: not attempted; no result artifact was produced.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Dataset impact: source artifacts pinned only; no `data/atomic_clocks/acr-*.yaml`
  row dataset was added or changed.
- Publication blocker: future row curation still needs source-file mapping,
  row-class, uncertainty, covariance, campaign-window, and holdout-binding
  review before any values become benchmark rows.

## Limitations

- The source CSV files contain value-bearing source material by design, but the
  repository still treats them as raw source artifacts, not curated rows.
- The source record includes a filename spelling variant
  `Yb-Sr-ratio-measuremets.csv`; this package preserves the original filename.
- The row gate must decide whether the supporting GALA-V delay-resolution file
  is required for any row-level uncertainty/covariance review.
