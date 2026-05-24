# Fresh-Data Extraction Ledger Template Review

**Task:** TASK-0376
**Status:** template review; no new rows; no benchmarks; no claims
**Template:** `templates/extraction_ledger.yaml`

## Inputs Reviewed

- `tasks/TASK-0376-add-fresh-data-extraction-ledger-template.yaml`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/notes/fresh-data-source-policy.md`
- `docs/reviews/quantum-size-direct-absorption-seed-review.md`
- `docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md`

## Method

The template was designed from the repeated source-gating failures seen across
fresh-data campaigns:

1. figure-derived points need deterministic axis calibration and raw exports;
2. table-derived values need exact table, row, cell, unit, and uncertainty
   provenance;
3. calibration-derived values must not be relabelled as direct measurements;
4. rejected candidate values should be preserved with explicit blockers.

No external data were fetched. No source table, figure, or benchmark row was
curated.

## Accepted Output Check

- `templates/extraction_ledger.yaml` defines the required entry format with
  source artifact id, source location, extraction method, extracted/reviewed
  attribution, value fields, uncertainty fields, unit, row class, provenance
  mode, reviewer notes, blocker fields, and `accepted_for_benchmark`.
- The template includes explicit provenance modes for direct table values,
  digitised figure points, independently reviewed observations,
  calibration-derived values, and rejected values.
- The template includes placeholder-only examples for table extraction and
  figure digitisation.
- `docs/extraction-ledger-template.md` summarizes the review discipline and
  scope limits.

## Limitations

- The schema is a template, not a validator. A future task can add JSON Schema
  or YAML schema validation once at least one reviewed ledger has been used.
- The examples intentionally contain no real scientific values.
- The template does not decide campaign-specific admissibility thresholds.
- The optional link from `docs/fresh-data-intake-protocol.md` is omitted
  because that protocol is not yet present on `main` in this task branch.

## Verdict

`VALID` as a reusable metadata template for reviewable fresh-data extraction.
It does not promote any result or claim and does not authorize benchmark use
without a later campaign-specific review.
