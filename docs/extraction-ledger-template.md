# Fresh-Data Extraction Ledger Template

## Purpose

`templates/extraction_ledger.yaml` defines a reusable ledger for source rows
that are extracted from tables or digitised from figures before they enter any
campaign benchmark dataset.

The ledger is a review surface, not a dataset. It records where a value came
from, how it was extracted, what uncertainty semantics were available, who
reviewed it, and whether it is admissible for benchmark use.

## Required Entry Fields

Each ledger entry must include:

- `source_artifact_id`
- `source_location`
- `extraction_method`
- `extracted_by`
- `reviewed_by`
- `value_fields`
- `uncertainty_fields`
- `unit`
- `row_class`
- `provenance_mode`
- `accepted_for_benchmark`
- `reviewer_notes`
- `blocker_fields`

`accepted_for_benchmark` defaults to `false`. It should remain false until a
reviewer verifies source artifact provenance, exact source location, units,
uncertainty semantics, row class, and campaign-specific admissibility.

## Provenance Modes

The template defines five provenance modes:

- `direct_table_value` for central values and uncertainties transcribed from a
  primary table.
- `digitised_figure_point` for deterministic figure-digitisation outputs with
  axis calibration and raw extracted coordinates.
- `independently_reviewed_observation` for values checked by an independent
  reviewer against source evidence.
- `calibration_derived_value` for values computed from a calibration curve,
  empirical relation, or sizing formula.
- `rejected_value` for candidates preserved as negative extraction evidence.

Only provenance is recorded here. A later campaign task must still decide
whether a reviewed row is allowed into a benchmark dataset.

## Review Discipline

Reviewer notes are required because the common failure mode is not just a
wrong number; it is an unverifiable number. Table rows need row/cell
verification, unit review, and uncertainty review. Figure rows also need axis
calibration artifacts and raw extraction exports.

Blocker fields should stay explicit. A row with missing uncertainty, unresolved
license status, inaccessible source artifacts, ambiguous axes, or incomplete
review should remain `accepted_for_benchmark: false` and carry blocker codes
instead of silently disappearing.

## Scope Limits

This task adds a template only. It does not curate real rows, ingest new
sources, run benchmark metrics, alter canonical result artifacts, or promote
scientific claims.
