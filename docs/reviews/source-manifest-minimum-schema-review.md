# Source Manifest Minimum Schema Review

**Task:** `TASK-0375`
**Status:** review-ready schema extension
**Verdict:** `VALID` as a metadata-only provenance contract.

## Scope

This task adds a shared minimum source-manifest schema for cross-campaign
fresh-data work. It standardizes source locator, retrieval, checksum,
redistribution, row-admissibility, blocker, and extraction-review fields before
any campaign consumes source artifacts as row data.

## Added Artifacts

- `physics_lab/schemas/source_manifest_minimum.schema.json`
- `templates/source_manifest_minimum.yaml`
- `docs/source-manifest-minimum-schema.md`
- `tests/test_source_manifest_minimum_schema.py`

## Method

The schema was designed from existing campaign source surfaces:

- Exoplanet PSCompPars pinned snapshot manifests.
- Quantum size-effect source manifests and source-artifact blockers.
- Atomic clock metadata-only source manifest templates.
- Nuclear source manifests and reveal-source templates.

It preserves campaign-specific extension room while requiring a common minimum
set of fields for DOI/arXiv/archive/source locators, retrieval date, checksum
state, redistribution review, row class, inclusion state, blocker reason,
extraction method, and uncertainty semantics.

## Limitations

- Existing campaign manifests are not rewritten in this task.
- The template is metadata-only and intentionally contains no external measured
  values, table rows, benchmark metrics, residuals, predictions, claims, or
  knowledge updates.
- The schema is a minimum contract. Campaign tasks may require stricter local
  schemas before row curation or benchmark use.

## Validation Intent

The included tests validate the metadata-only template, reject accidental extra
top-level properties, require the locator surface, and register
`source_manifest_minimum` with the shared validation registry.
