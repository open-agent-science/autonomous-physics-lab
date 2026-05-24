# Source artifact directory — Beloy et al. 2021 / BACON

**Task:** TASK-0363
**Campaign:** Atomic-Clock Residuals
**Source candidate:** Beloy, K., et al. (2021), *Frequency ratio
measurements at 18-digit accuracy using an optical clock network*,
**Nature 591, 564**, Boulder Atomic Clock Optical Network
(BACON) Collaboration.

## Purpose

This directory is the pinned-on-disk home of the Beloy 2021 / BACON
direct frequency-ratio source artifact. It is **metadata-only at the
time of this TASK-0363 commit** — no frequency-ratio values, no
uncertainty numbers, no drift fits, no derived constants
constraints, no prediction registry entries, and no claim updates
are recorded here.

The companion review at
`docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md`
records which TASK-0355 blockers (B1 covariance, B2 redistribution,
B3 extraction-shape lock) this task cleared and which remain gated
on the future row-curation task.

## Planned files

This directory is **expected** to grow as follows when the future
row-curation task is approved. None of these files exist yet.

| Path | Status | Notes |
| --- | --- | --- |
| `README.md` | committed by TASK-0363 | This file. |
| `arxiv-2005.14694.pdf` | not committed by TASK-0363 | arXiv preprint. The row-curation task fetches, archives, and records SHA-256. |
| `arxiv-2005.14694.sha256` | not committed by TASK-0363 | One-line SHA-256 hex string of the committed PDF. |
| `supplementary_information.pdf` | not committed by TASK-0363 | Optional. Only if separately released by the authors under a redistributable licence. |
| `supplementary_information.sha256` | not committed by TASK-0363 | Optional. |
| `covariance_matrix.yaml` | not committed by TASK-0363 | Optional. Only if a covariance matrix is actually present in the SI; otherwise the row-curation task records a documented diagonal approximation. |
| `provenance.yaml` | not committed by TASK-0363 | Per-artifact provenance fields (retrieval date, source locator, license note, sha256 cross-reference). |

## Retrieval policy (TASK-0363)

- The artifact **must** be the arXiv preprint
  ([arXiv:2005.14694](https://arxiv.org/abs/2005.14694)), not the
  Nature version-of-record PDF. The arXiv perpetual licence allows
  archival redistribution of the author's accepted manuscript; the
  Nature-published PDF is not redistributable here.
- The Nature DOI
  ([10.1038/s41586-021-03253-4](https://doi.org/10.1038/s41586-021-03253-4))
  remains the publication-of-record reference and must be cited
  alongside the arXiv locator in any future per-row source field.
- The retrieval task must record `retrieval_date_utc`,
  `source_locator: https://arxiv.org/abs/2005.14694`,
  `archive_url: https://arxiv.org/pdf/2005.14694`,
  `checksum_sha256: <sha256-of-committed-pdf>`,
  `checksum_scope: arxiv_preprint_pdf`, and
  `license_or_reuse_notes: arXiv perpetual licence; verbatim redistribution of the Nature PDF is forbidden.`
- The retrieval task must verify that the arXiv preprint matches the
  Nature-published ratio table values **before** extracting any row.

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

## Non-goals (TASK-0363)

- This task does **not** fetch the arXiv preprint.
- This task does **not** commit any PDF or SHA-256.
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
