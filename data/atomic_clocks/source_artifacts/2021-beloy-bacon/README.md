# Source artifact directory — Beloy et al. 2021 / BACON

**Task:** TASK-0363
**Campaign:** Atomic-Clock Residuals
**Source candidate:** Beloy, K., et al. (2021), *Frequency ratio
measurements at 18-digit accuracy using an optical clock network*,
**Nature 591, 564**, Boulder Atomic Clock Optical Network
(BACON) Collaboration.

## Purpose

This directory is the metadata-only home of the Beloy 2021 / BACON
direct frequency-ratio source artifact. The raw arXiv PDF is **not**
redistributed in the repository; instead this package records the DOI/arXiv
locator, expected SHA-256 sidecar, and provenance needed for a maintainer to
re-fetch and verify the same source locally.

The companion review at
`docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md`
records which TASK-0355 blockers (B1 covariance, B2 redistribution,
B3 extraction-shape lock) this task cleared and which remain gated
on the future row-curation task.

## Planned files

This directory may grow only with artifacts whose redistribution rights are
explicitly recorded. The default source-PDF route is metadata-only.

| Path | Status | Notes |
| --- | --- | --- |
| `README.md` | committed | This file. |
| `arxiv-2005.14694.sha256` | committed | Expected SHA-256 for a local maintainer-fetched arXiv preprint copy. |
| `arxiv-2005.14694.pdf` | not committed | Fetch locally only; do not redistribute unless explicit compatible permission is recorded. |
| `supplementary_information.pdf` | not committed | Optional. Only if separately released by the authors under a redistributable licence. |
| `supplementary_information.sha256` | optional | Optional expected checksum for a non-redistributed or explicitly permitted artifact. |
| `covariance_matrix.yaml` | not committed by TASK-0363 | Optional. Only if a covariance matrix is actually present in the SI; otherwise the row-curation task records a documented diagonal approximation. |
| `provenance.yaml` | committed | Per-artifact provenance fields, redistribution status, expected checksum, and local fetch helper. |

## Retrieval policy (TASK-0363)

- The artifact locator is the arXiv preprint
  ([arXiv:2005.14694](https://arxiv.org/abs/2005.14694)), not the
  Nature version-of-record PDF. The arXiv non-exclusive distribution route is
  not treated as automatic third-party redistribution permission for this
  repository, so the PDF bytes are not committed.
- The Nature DOI
  ([10.1038/s41586-021-03253-4](https://doi.org/10.1038/s41586-021-03253-4))
  remains the publication-of-record reference and must be cited
  alongside the arXiv locator in any future per-row source field.
- A local retrieval/recheck should record `retrieval_date_utc`,
  `source_locator: https://arxiv.org/abs/2005.14694`,
  `archive_url: https://arxiv.org/pdf/2005.14694`,
  `checksum_sha256: <expected-sha256>`,
  `checksum_scope: expected_arxiv_preprint_pdf_sha256_not_committed`, and
  `license_or_reuse_notes: metadata-only; PDF bytes are not redistributed.`
- The retrieval task must verify that the arXiv preprint matches the
  Nature-published ratio table values **before** extracting any row.
- If the arXiv preprint and Nature version-of-record disagree on a ratio
  value, uncertainty, campaign window, table shape, or row inclusion boundary,
  the row-curation task must halt with
  `SOURCE_ARTIFACT_VERSION_DRIFT`. The discrepancy must be preserved in a
  separate review before any row is committed.

## Covariance handling policy (TASK-0363)

Locked by the covariance preflight review:

- The future row-curation task must read the Beloy 2021
  supplementary information for the covariance / shared-systematic
  section before any row is extracted.
- If a full 3×3 covariance matrix is published, commit it as
  `covariance_matrix.yaml` and set
  `covariance_reference: covariance_matrix.yaml#full_three_by_three`
  per row.
- If only per-ratio totals are published with explicit text stating
  that shared-systematic contributions are already folded into each
  total, set
  `covariance_reference: diagonal_per_paper_explicit_<paragraph_cite>`
  per row and document the paragraph cite in `provenance.yaml`.
- If neither condition holds, the row-curation task must halt with
  `SOURCE_MANIFEST_INCOMPLETE: shared_campaign_systematics_not_separable`
  per the TASK-0344 covariance contract (stop condition C1) and
  must not commit any row.

## Extraction shape policy (TASK-0363)

The first row-curation task is **locked to per-ratio totals**:

- Commit three direct rows (Al⁺/Yb, Al⁺/Sr, Yb/Sr) carrying
  `total_uncertainty`, `statistical_uncertainty`,
  `systematic_uncertainty`, `confidence_level_label`, and
  `bound_style: measurement`.
- Do **not** expand the per-systematic-component table on the first
  curation pass. A per-component extraction may follow under a
  separate maintainer-approved task once the per-ratio rows have
  passed the TASK-0344 discipline gate and the TASK-0332 readiness
  gate.
- Rationale: the per-component table multiplies the row count and
  changes the schema shape; locking the simpler shape first keeps
  the first batch reviewable and reversible.

## Local fetch and verify

From the repository root, a maintainer can re-fetch the non-redistributed
preprint copy into a local working tree and verify it against the pinned
sidecar:

```bash
python3 scripts/fetch_source_artifact.py \
  --url https://arxiv.org/pdf/2005.14694 \
  --output data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf \
  --sha256-file data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.sha256
```

The fetched PDF remains local and must not be committed unless a compatible
redistribution marker is added and reviewed.

## Non-goals (TASK-0363 / TASK-0731)

- This task does **not** fetch the arXiv preprint.
- This package does **not** commit any PDF bytes.
- This task does **not** ingest any frequency-ratio value,
  uncertainty number, drift fit, or derived constants constraint.
- This task does **not** edit
  `data/atomic_clocks/source_manifest_template.yaml` row values.
- This task does **not** add any prediction registry entry, RESULT-*,
  CLAIM-*, or knowledge file edit.

## See also

- `docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md`
  (this task's preflight review).
- `docs/reviews/atomic-clock-direct-ratio-source-artifact-review.md`
  (TASK-0355 selection and B1/B2/B3 blocker definitions).
- `docs/reviews/atomic-clock-covariance-uncertainty-semantics.md`
  (TASK-0344 covariance and uncertainty contract).
- `data/atomic_clocks/source_manifest_template.yaml`
  (campaign source manifest template).
