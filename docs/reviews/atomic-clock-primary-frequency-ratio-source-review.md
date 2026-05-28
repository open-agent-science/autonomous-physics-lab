# Atomic-Clock Primary Frequency-Ratio Source Review

**Task:** `TASK-0330`  
**Reviewed source class:** `direct_frequency_ratio_measurement`  
**Manifest source family:** `ACLOCK-SRC-CLASS-001`  
**Decision:** `ADMISSIBLE_WITH_SOURCE_REVIEW`  
**Evidence class:** metadata-only source-class review

## Scope

This review defines when a primary atomic-clock frequency-ratio source may be
used later as a direct measurement row in APL. It reads the existing
Atomic-Clock Residuals campaign scaffold, metadata-only source manifest
template, schema sketch, source-candidate note, and fresh-data source policy.

No numerical frequency ratios, clock values, drift values, derived constants
constraints, benchmark metrics, prediction registry entries, claims, or
canonical results are added.

## Source-Class Boundary

`direct_frequency_ratio_measurement` is admissible only for primary measured
clock-comparison evidence whose transition labels, ratio partner, epoch or
campaign window, units, and uncertainty semantics can be recovered from a
source artifact. The class should preserve the measurement as directly as
possible before any later residual, trend, or derived-constraint work.

This source class must stay separate from:

- `drift_bound_or_constants_constraint`, which depends on sensitivity
  coefficients, interval assumptions, or model choices;
- `evaluation_or_review_summary`, which may combine primary papers and hide
  covariance or combination rules;
- synthetic dry-run rows, which are valid only for loader and schema tests.

If a source mixes direct measurements with derived constraints or evaluation
summaries, a future task must split the rows deterministically or stop.

## Candidate Primary-Source Shapes

The existing source-candidate note and source manifest template identify these
metadata-only candidate shapes for future source-specific review:

| Candidate shape | Potential use | Required source-review focus |
| --- | --- | --- |
| Peer-reviewed primary frequency-ratio measurement paper | Direct measurement row when the paper or supplement exposes the measured ratio and uncertainty semantics. | Stable DOI or archive locator, publication date, transition labels, ratio partner, epoch or campaign window, uncertainty budget, covariance notes, and license/citation status. |
| Official supplementary table linked from a primary paper | Deterministic row extraction if table semantics and provenance are explicit. | Table identifier, checksum or archive plan, unit conventions, field definitions, link back to the primary paper, and redistribution limits. |
| Official lab or collaboration release material tied to a primary source | Source locator or provenance trail for a later row seed. | Versioning, retrieval date, whether the release duplicates a paper/evaluation, and whether shared systematics or campaign grouping are documented. |
| Repeated comparison campaign record with separable epochs | Possible direct comparison rows or a campaign-level source family when repeated rows are independently reviewable. | Campaign interval, repeat-group identifier, shared systematic notes, covariance handling, and holdout/reveal boundary. |

No concrete source was inspected for values in this task. These shapes are
admissibility classes only.

## Minimum Provenance For A Direct Row

A future source-specific task must record all of the following before writing a
real direct frequency-ratio row:

| Field | Requirement |
| --- | --- |
| Source locator | Stable DOI, official release page, archive record, or primary paper plus supplement. |
| Publication or release date | Date needed for source-freeze and later source-date split decisions. |
| Retrieval and archive plan | Retrieval date plus checksum, archived copy policy, or a documented reason a checksum is unavailable. |
| Transition labels | Clock species, isotope where applicable, transition label, and reference transition or ratio partner. |
| Unit semantics | Whether the observable is a dimensionless ratio, absolute frequency, residual form, or another declared quantity. |
| Epoch or campaign window | Measurement date, start/end interval, campaign label, or explicit blocker when unavailable. |
| Uncertainty semantics | Total uncertainty plus statistical/systematic split when available; confidence or coverage convention when relevant. |
| Covariance and correlation notes | Shared systematic, common lab, repeated-campaign, or covariance-group notes; unknown covariance must be recorded as a limitation or blocker. |
| License and citation status | Reuse terms, required citations, and whether any source artifact can be committed. |
| Holdout or reveal boundary | Source-manifest-only, train/validation/holdout, or future no-peek split before any model selection. |

## Review-Summary-Only Conditions

A candidate source must not become a direct measurement row when:

- the only accessible value is in a review plot, screenshot, informal summary,
  or combined evaluation table;
- transition labels, isotope labels, ratio partner, or unit semantics are
  ambiguous;
- the source omits epoch, campaign interval, or release-date information needed
  for a freeze/reveal boundary;
- uncertainty components, confidence convention, or systematic-budget meaning
  cannot be recovered;
- covariance, shared-systematic, or repeated-campaign notes are mentioned but
  not available;
- direct measurements and derived constraints are combined without row-class
  labels;
- license or citation requirements are unclear;
- the future task asks for residual fitting, trend fitting, constants-drift
  interpretation, or prediction-registry entries before source review.

Those cases can still be preserved as negative source-review evidence, but they
should not become machine-readable direct rows.

## Relationship To Derived Constraints

This review is independent of `TASK-0331`. A primary frequency-ratio paper can
later support both direct rows and derived-constraint rows, but the two uses
must be represented separately.

Direct rows should preserve the measured comparison and uncertainty trail.
Derived constraints should preserve the transformation through sensitivity
coefficients, model assumptions, and interval semantics. A future benchmark
must not treat a direct row and a derived constraint from the same source chain
as independent evidence unless a later review justifies that treatment.

## Stop Conditions

Stop before ingestion if any of these conditions apply:

- missing stable source locator or source artifact;
- missing retrieval date, checksum, or archive plan;
- unrecoverable transition or ratio-partner labels;
- unclear unit semantics;
- missing epoch or campaign-window metadata;
- uncertainty budget unavailable or ambiguous;
- covariance or shared-systematic notes required but unavailable;
- license or citation status unresolved;
- source mixes direct rows, review summaries, and derived constraints without
  deterministic separation;
- task scope moves from source review into fitting, benchmark metrics, or
  broad constants-anomaly interpretation.

## Verdict

`ADMISSIBLE_WITH_SOURCE_REVIEW`

The primary direct frequency-ratio source class is useful for Atomic Clock
Residuals, but only after a future source-specific task freezes a stable source
artifact and records provenance, transition labels, units, uncertainty,
covariance, license, and holdout semantics. Until then, the campaign remains
pre-ingestion: no real clock values, benchmark rows, prediction entries,
residual metrics, or constants-drift claims are available.
