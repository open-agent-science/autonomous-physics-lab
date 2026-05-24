# Source Artifact Package Template Review

**Task:** `TASK-0374`
**Status:** review-ready template artifact
**Verdict:** `VALID_SOURCE_PACKAGE_TEMPLATE`

## Scope

This task adds a reusable metadata-only source artifact package template for
cross-campaign fresh-data work. It is intended for future source-specific
packages before agents pin PDFs, CSV snapshots, supplementary tables, figure
digitisation artifacts, or API responses.

No live source artifacts are fetched. No source values, rows, benchmark
metrics, residuals, predictions, results, claims, or knowledge entries are
added.

## Added Template Files

- `templates/source_artifact_package/README.md`
- `templates/source_artifact_package/provenance.yaml`
- `templates/source_artifact_package/license_review.md`
- `templates/source_artifact_package/extraction_notes.md`
- `templates/source_artifact_package/raw_derived_policy.md`
- `templates/source_artifact_package/blocker_notes.md`
- `templates/source_artifact_package/raw/.gitkeep`
- `templates/source_artifact_package/derived/.gitkeep`

## Method

The template was shaped from existing campaign needs:

- Atomic clock source-artifact preflight requires redistribution, covariance,
  and extraction-shape notes before real rows.
- Quantum direct-source curation needs checksum-pinned SI/table or deterministic
  figure digitisation artifacts before row curation.
- Exoplanet snapshot ingestion showed the value of raw and normalized checksum
  pairs with explicit live-fetch boundaries.

The template separates metadata-only files from optional raw and derived
value-bearing directories, and it records which file types may contain values
only after task and license approval.

## Limitations

- This is a template, not a campaign-specific source package.
- It does not validate or rewrite existing campaign manifests.
- It intentionally avoids linking to unmerged task artifacts.
- Future source-specific tasks must replace placeholders and run their own
  source, checksum, license, and extraction review.

## Verdict

`VALID_SOURCE_PACKAGE_TEMPLATE`: the template is ready for maintainer review as
shared source-artifact infrastructure.
