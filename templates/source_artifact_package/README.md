# Source Artifact Package Template

## Purpose

Use this directory shape when a task pins, reviews, or blocks a source artifact
before row curation. The package is designed for PDFs, CSV snapshots,
supplementary tables, figure digitisation artifacts, and API snapshots.

Copy this directory to a campaign-specific path such as:

```text
data/<campaign>/source_artifacts/<source-id>/
```

Then replace template placeholders with source-specific metadata. Do not add
real external values, tables, figures, PDFs, or API responses unless the
canonical task explicitly allows artifact promotion and the license review
permits repository storage.

## File Roles

| File | Purpose | May contain value-bearing data? |
| --- | --- | --- |
| `README.md` | Package purpose, source identity, status, and non-goals. | No |
| `provenance.yaml` | Locator, retrieval, checksum, artifact type, archive, and row-class metadata. | Metadata only by default |
| `license_review.md` | Redistribution, citation, and storage decision. | No |
| `extraction_notes.md` | Planned or executed extraction method, table/figure/API locator, uncertainty notes, and reviewer notes. | Only if the task explicitly authorizes extracted rows |
| `raw_derived_policy.md` | Direct-vs-derived, calibration, model-derived, and digitised-point boundaries. | No |
| `blocker_notes.md` | Stop conditions and failed extraction/reuse notes. | No |
| `raw/` | Optional raw source artifacts such as PDF, CSV, SI, or API response. | Yes, only with task and license approval |
| `derived/` | Optional derived extraction products such as transcription CSV, digitised points, or normalized manifest. | Yes, only with task approval |

## Status Vocabulary

- `METADATA_ONLY_TEMPLATE`: placeholder package, no source-specific artifact.
- `METADATA_ONLY_BLOCKER`: source identified but artifact or license blocks row curation.
- `SOURCE_ARTIFACT_PINNED`: artifact locator, retrieval date, and checksum or archive policy are recorded.
- `EXTRACTION_REVIEW_READY`: extraction notes or ledger are ready for review.
- `ROWS_CURATED_ELSEWHERE`: package supports a separate curated row artifact.

## Guardrails

- LLM-recalled values and prose-only numerical claims are not data.
- A checksum or explicit archive policy is required before value-bearing
  artifacts are used.
- Redistribution status must be decided before committing raw files.
- Direct measurements, derived constraints, calibration curves, model-derived
  rows, and digitised figure points must stay separate.
- This template does not authorize benchmark metrics, residual plots,
  prediction entries, results, claims, or knowledge promotion.
