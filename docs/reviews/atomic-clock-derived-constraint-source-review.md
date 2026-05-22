# Atomic-Clock Derived-Constraint Source Review

**Task:** `TASK-0331`  
**Reviewed source class:** `drift_bound_or_constants_constraint`  
**Manifest source family:** `ACLOCK-SRC-CLASS-003`  
**Decision:** `ADMISSIBLE_WITH_SOURCE_REVIEW`  
**Evidence class:** metadata-only source-class review

## Scope

This review defines when atomic-clock drift bounds or constants-variation
constraints may be represented as derived constraints in APL. It reads the
existing campaign scaffold, source manifest template, schema sketch, source
candidate note, and fresh-data source policy.

No numerical drift bounds, constants-variation constraints, frequency ratios,
sensitivity coefficients, benchmark metrics, prediction registry entries,
claims, or canonical results are added.

## Source-Class Boundary

`drift_bound_or_constants_constraint` is admissible only as a derived
constraint source class. It must not be treated as an independent direct
frequency-ratio measurement row.

The class may become a future dataset row only when the future task can
preserve enough provenance to reconstruct the constraint chain:

- which direct measurement sources enter the constraint;
- which sensitivity coefficients or transition-dependence model are used;
- which time interval, campaign window, or epoch comparison defines the bound;
- which assumptions convert measured frequency-ratio behavior into a
  constants-variation statement.

If any of those are hidden, the source remains review-summary-only.

## Minimum Provenance For A Derived Constraint

A future source-specific task must record all of the following before writing a
derived-constraint value:

| Field | Requirement |
| --- | --- |
| Source locator | Stable DOI, official release page, archive record, or primary paper plus supplement. |
| Retrieval and archive plan | Retrieval date plus checksum, archived copy policy, or reason a checksum is not available. |
| Input measurement source list | Explicit list of primary frequency-ratio or comparison measurements used to form the constraint. |
| Sensitivity-coefficient source | Citation or table locator for coefficients, including transition labels and assumptions. |
| Interval semantics | Start/end dates, campaign interval, elapsed time convention, or explicit statement that the interval is unavailable. |
| Units and quantity | Quantity being constrained, unit semantics, and whether the value is a bound, estimate, slope, or fitted coefficient. |
| Uncertainty semantics | Total/statistical/systematic split when available, confidence or coverage convention, and asymmetric-bound handling. |
| Covariance and correlation notes | Shared systematic, repeated-campaign, or coefficient-correlation notes; absence of recoverable covariance must be a limitation or blocker. |
| Model assumptions | Constants allowed to vary, constants fixed, linearization assumptions, and whether multiple constants are fit together. |
| License and citation status | Reuse terms, citation requirements, and whether the source artifact can be committed. |
| Holdout or reveal boundary | Source-manifest-only, train/validation/holdout, or future no-peek split before any model selection. |

## Review-Summary-Only Conditions

A drift-bound or constants-constraint source must stay review-summary-only
instead of becoming an APL dataset row when:

- it quotes a bound but hides the underlying measurement source list;
- sensitivity coefficients are required but not traceable to a reviewed source;
- multiple constants are varied but the model assumptions or fixed-constant
  choices are not recoverable;
- the source combines direct measurements and derived constraints in one table
  without labels that allow deterministic splitting;
- the interval or epoch semantics are missing;
- covariance, shared-systematic, or repeated-campaign notes are referenced but
  not recoverable;
- the value is copied from an evaluation or review table without combination
  rules;
- license or reuse terms are unclear.

Those cases can still be preserved as negative source-review evidence, but
they should not become machine-readable derived-constraint rows.

## Stop Conditions

Stop before ingestion if any of these conditions apply:

- hidden direct input rows;
- unrecoverable sensitivity coefficients;
- mixed direct and derived values without explicit row-class labels;
- missing interval semantics;
- missing uncertainty confidence or coverage convention;
- covariance or shared-systematic notes required but unavailable;
- unclear source license or citation requirements;
- the task asks to fit constants drift or infer a broad constants-anomaly
  interpretation before source review is complete.

## Relationship To Direct Rows

This review is independent of `TASK-0330`. Direct frequency-ratio measurement
rows and derived constraints may cite the same primary literature later, but
they need separate row classes and separate provenance checks.

Direct rows should preserve measured clock comparisons as directly as
possible. Derived constraints should preserve the transformation from those
measurements through sensitivity coefficients and model assumptions. A future
benchmark must not silently treat the two as statistically independent copies
of the same evidence.

## Verdict

`ADMISSIBLE_WITH_SOURCE_REVIEW`

The derived drift-bound source class is useful for Atomic Clock Residuals, but
only as explicitly labeled derived-constraint evidence with recoverable input
measurements, sensitivity coefficients, interval semantics, covariance notes,
model assumptions, and license/citation status. Until a concrete source passes
that review, the campaign remains pre-ingestion and no constants-drift claim is
available.
