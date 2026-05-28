# Fresh-Data Stop-Condition Vocabulary Review

**Task:** TASK-0377
**Status:** vocabulary review; no rows; no metrics; no claims
**Output:** `docs/fresh-data-stop-conditions.md`

## Inputs Reviewed

- `tasks/TASK-0377-add-fresh-data-stop-condition-vocabulary.yaml`
- `docs/fresh-data-intake-protocol.md`
- `docs/notes/fresh-data-source-policy.md`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `docs/reviews/atomic-clock-beloy-2021-source-artifact-covariance-preflight.md`
- `docs/reviews/exoplanet-pscomppars-snapshot-ingestion.md`

## Method

The vocabulary was assembled from blocker patterns already present in fresh-data
campaign work: inaccessible tables, non-redistributable artifacts, figure-only
values, covariance ambiguity, calibration-derived rows, source-version drift,
uncertainty ambiguity, row-class ambiguity, and license review gaps.

No external sources were fetched. No source values were copied. No benchmark or
claim artifact was changed.

## Accepted Output Check

- `docs/fresh-data-stop-conditions.md` defines named source and row-curation
  stop conditions.
- The required ten codes are included:
  `SOURCE_PAYWALLED_NO_TABLE`, `SOURCE_ARTIFACT_NOT_REDISTRIBUTABLE`,
  `FIGURE_DIGITIZATION_REQUIRED`, `COVARIANCE_NOT_SEPARABLE`,
  `DIRECT_ROWS_NOT_PRESENT`, `CALIBRATION_DERIVED_ONLY`,
  `SOURCE_ARTIFACT_VERSION_DRIFT`, `UNCERTAINTY_SEMANTICS_MISSING`,
  `ROW_CLASS_AMBIGUOUS`, and `LICENSE_REVIEW_REQUIRED`.
- Each required code records meaning, halt condition, allowed follow-up, and
  whether rows may be committed.
- Existing Quantum, Atomic, Exoplanet, and generic source-artifact blockers are
  mapped to the shared vocabulary where possible.
- Link-only references were added to the intake/source-policy docs so future
  agents can find the vocabulary during source review.

## Limitations

- This is a documentation vocabulary, not an enforced schema or validator.
- Campaign-specific tasks may add narrower subcodes when the shared vocabulary
  is not precise enough.
- The vocabulary does not clear any existing blocker by itself.
- No `tasks/ACTIVE.md` or `docs/task-views/*.md` generated snapshots are
  committed from this task branch.

## Verdict

`VALID` as a shared blocker vocabulary for fresh-data source and row-curation
work. It preserves negative results and admissibility limits without promoting
any scientific claim.
