# Fresh-Data Intake Protocol Review

**Task:** `TASK-0373`
**Status:** review-ready protocol artifact
**Verdict:** `VALID_SOURCE_POLICY_ARTIFACT`

## Scope

This review records a metadata-only cross-campaign protocol for moving
fresh-data work from source candidate to benchmark-ready state. It standardizes
the handoff stages and admissibility gates used by Nuclear, Quantum, Atomic,
and Exoplanet campaigns.

No source values, rows, benchmark metrics, residuals, predictions, results,
claims, or knowledge entries are added.

## Inputs

- `docs/notes/fresh-data-source-policy.md`
- `docs/campaigns/nuclear-mass-surface.md`
- `docs/campaigns/quantum-size-effects.md`
- `docs/campaigns/atomic-clock-residuals.md`
- `docs/campaigns/exoplanet-mass-radius.md`
- `docs/reviews/campaign-curator-brief-2026-05-24.md`

## Method

The protocol defines standard lifecycle stages:

- `SOURCE_CANDIDATE`
- `SOURCE_ARTIFACT_PINNED`
- `TABLE_OR_FIGURE_EXTRACTED`
- `ROWS_CURATED`
- `ROW_SCHEMA_VALIDATED`
- `BASELINE_READY`
- `BENCHMARK_READY`

For each stage it records entry criteria, exit criteria, mandatory artifacts,
and campaign-specific extensions. It also separates direct measurements,
derived constraints, calibration curves, model-derived rows, and digitised
figure points so future benchmark tasks do not silently mix incompatible data
classes.

## Limitations

- This is a protocol artifact, not a data-ingestion artifact.
- It does not validate any existing campaign manifest.
- It does not make any campaign baseline-ready by itself.
- It intentionally keeps claim promotion outside the protocol.

## Verdict

`VALID_SOURCE_POLICY_ARTIFACT`: the protocol is ready for maintainer review as
shared fresh-data infrastructure. Later tasks may cite it when adding source
artifact packages, extraction ledgers, curated rows, or readiness matrices.
