# Atomic-Clock Covariance And Uncertainty Semantics Review

**Task:** TASK-0344
**Status:** review (metadata-only; no clock values; no fits; no claims)
**Campaign:** Atomic-Clock Residuals
**Inputs reviewed:**

- `docs/campaigns/atomic-clock-residuals.md`
- `docs/reviews/atomic-clock-source-manifest-template-review.md`
- `docs/reviews/atomic-clock-primary-frequency-ratio-source-review.md`
- `docs/reviews/atomic-clock-derived-constraint-source-review.md`
- `docs/reviews/atomic-clock-real-row-readiness-gate.md`
- `data/atomic_clocks/schema.md`
- `data/atomic_clocks/source_manifest_template.yaml`
- `TASK-0332`

## Scope

This review locks the rules for how atomic-clock uncertainty fields,
covariance handling, and shared-systematic structure must be represented
**before** any real frequency-ratio, drift-constraint, or derived-row is
ingested. It does not ingest any clock value, does not fit any drift, does
not add any prediction registry entry, and does not promote any claim.

The review is upstream of `TASK-0332` (real-row readiness gate) and any
later row-curation task. The goal is to prevent the most likely
discipline failure for the Atomic-Clock Residuals campaign:

- silently averaging direct measurement rows with derived-constraint
  rows, hiding shared systematics inside a single uncertainty number,
  and producing a misleadingly tight residual that is in fact a
  covariance artefact.

## Required Uncertainty Fields For Direct Frequency-Ratio Rows

A future `direct_frequency_ratio_measurement` row must carry the
following uncertainty fields. Any row whose source artifact cannot
recover them is **not** admissible to the true-measurement axis and
must be excluded with an explicit `inclusion_reason`.

| Field | Required content | Why it is required |
| --- | --- | --- |
| `total_uncertainty` | Combined (statistical + systematic) 1-σ uncertainty as reported by the primary source. | Default residual-axis weight when statistical and systematic are not separable. |
| `total_uncertainty_unit` | Explicit unit (e.g. `Hz`, `relative`, or `parts_per_10^18`). | Mixing units silently is the most common atomic-clock leakage mode. |
| `statistical_uncertainty` | Statistical-only 1-σ when the source separates it. May be `null` when the source reports a single total. | Required to support per-row covariance handling when the same campaign is reused. |
| `systematic_uncertainty` | Systematic-only 1-σ when the source separates it. May be `null` when not separated. | Required for shared-systematic checks across repeated campaigns. |
| `systematic_components` | Optional table of named systematic components when the source reports per-effect contributions. | Lets reviewers spot shared sensitivity coefficients across rows. |
| `confidence_level_label` | Explicit confidence level when the source uses anything other than 1-σ (e.g. `2-sigma`, `k=2`, `95%`). | Mixing 1-σ and 2-σ residuals silently flips fit weights by factors of 2. |
| `asymmetric_upper` / `asymmetric_lower` | Upper and lower uncertainty bounds when the source reports an asymmetric interval. | Atomic-clock asymmetries appear in some systematic budgets and must not be silently symmetrised. |
| `bound_style` | Explicit flag when the source reports a one-sided bound (e.g. `<= 1e-17`) rather than a measurement. | Bounds must not enter the measurement axis. |
| `covariance_reference` | Either a per-row covariance note pointing to a documented matrix, or an explicit `none_documented` marker. | A null here is fine; an undocumented null is a stop condition. |

A row missing any **required** field above is excluded with
`inclusion_reason: uncertainty_semantics_not_recoverable`.

## Required Uncertainty Fields For Derived Constraint Rows

A future `drift_bound_or_constants_constraint` row needs additional
fields because it depends on sensitivity coefficients and interval
assumptions:

| Field | Required content |
| --- | --- |
| `derivation_assumptions` | Named assumptions used in the derivation (e.g. linear-drift, single-coefficient, fixed-epoch). |
| `sensitivity_coefficients` | Per-component sensitivity coefficients used in the derivation, with units. |
| `interval_window_start` / `interval_window_end` | UTC bounds for the campaign window the derivation aggregates over. |
| `combined_with_sources` | Explicit list of primary sources combined into the derivation, with their `source_id`s. |
| `total_uncertainty` (as above) | The reported 1-σ derived bound or constraint. |
| `confidence_level_label` (as above) | Explicit confidence level. |
| `combination_rule` | Named combination rule (e.g. `weighted_mean`, `kolmogorov_smirnov_bound`, `bayes_posterior_mean`). |

A derived-constraint row missing any of these is excluded with
`inclusion_reason: derivation_semantics_not_recoverable`.

## Forbidden Uncertainty Representations

The following representations are **forbidden** anywhere in the
Atomic-Clock Residuals campaign rows. Each is a documented leakage
mode for clock data.

1. **A single uncertainty number with no semantics**. A row that
   records `uncertainty: 1.2e-18` without confidence-level,
   statistical/systematic split, or covariance reference is silently
   1-σ vs k=2 vs combined. Excluded.
2. **Asymmetric bounds silently symmetrised**. A loader that converts
   `(−0.5, +0.8)` to `0.65` average drops the asymmetry signal.
   Forbidden.
3. **One-sided bounds entered as measurements**. A row reporting
   `<= 1e-17` is a bound, not a measurement. It belongs on the
   bound-axis, not the residual-axis.
4. **Cross-campaign averaging of nominally-independent statistical
   uncertainties when the campaigns share systematics**. Two
   measurements from the same lab in the same year share the lab's
   systematic budget; treating them as independent under-states
   uncertainty by `sqrt(2)`.
5. **Confidence-level mixing without explicit conversion**. A 2-σ
   bound and a 1-σ measurement on the same axis must be converted
   to a single confidence level via an explicit rule recorded in
   the manifest.
6. **Derived-constraint rows on the direct-measurement axis**.
   `drift_bound_or_constants_constraint` rows must live on a
   separate axis with their own combination-rule notes.

## Covariance And Shared-Systematic Stop Conditions

The Atomic-Clock Residuals campaign must stop ingestion when any of
the following holds, rather than silently fold the rows into a
residual:

### Stop condition C1 — repeated campaign without separable epochs

When two or more rows come from the same physical campaign (same
clock pair, same lab, overlapping epoch), the rows are **not
independent**. The campaign must be either:

- represented as a single source family with a documented
  combination rule, or
- split into separable per-row epoch windows whose timing makes
  shared systematics negligible (e.g. weeks apart with full
  systematic re-evaluation).

If neither holds, the ingestion stops with
`SOURCE_MANIFEST_INCOMPLETE: shared_campaign_systematics_not_separable`.

### Stop condition C2 — shared sensitivity coefficients

When two derived-constraint rows share a sensitivity coefficient
(e.g. both depend on `α_relativistic_correction`), the rows are not
independent on the residual axis. The manifest must record the
shared coefficient and the combination rule that handles it.

If absent, stop with
`SOURCE_MANIFEST_INCOMPLETE: shared_sensitivity_coefficient_not_handled`.

### Stop condition C3 — direct/derived duplicate evidence

When a derived-constraint row is itself derived from a primary
measurement that is also being curated as a direct row, ingesting
both into the same axis double-counts the same physical evidence.
The manifest must declare which axis owns the evidence (direct,
derived, or both with an explicit combination rule).

If absent, stop with
`SOURCE_MANIFEST_INCOMPLETE: direct_and_derived_double_count_not_resolved`.

### Stop condition C4 — covariance matrix referenced but not committed

When a row's `covariance_reference` points to a matrix the source
publishes but the curator has not committed (typically because the
publisher gates the matrix or the file is too large), the row may
still enter the schema, but only with `inclusion_status: excluded`
and `inclusion_reason: covariance_matrix_not_pinned`. It is **not**
admissible to the residual axis until the matrix or a deterministic
fallback (e.g. diagonal-only approximation with explicit note) is
committed.

## Schema / Manifest Wording Recommendations

Minor metadata-only wording changes are recommended for the
`data/atomic_clocks/source_manifest_template.yaml` template to
surface these requirements. These changes are **not made by this
review** to avoid conflicting with the parallel TASK-0355 source-
artifact review; they should land in a single follow-up task that
holds both reviews' agreed wording.

Recommended additions to the manifest template (for the follow-up
task to apply):

- a top-level `uncertainty_semantics_required` block listing the
  required and forbidden representations from this review;
- a per-source-family `covariance_stop_conditions` field listing
  which of C1–C4 the source-family review evaluated;
- a per-row `confidence_level_label` field with enum values
  `1_sigma`, `2_sigma_k_equals_2`, `95_percent`, `99_percent`,
  `other_documented`.

Schema sketch (`data/atomic_clocks/schema.md`) should grow a short
"Uncertainty Discipline" subsection that points back to this review
for the per-field requirements. Again, not done here.

## How TASK-0332 Should Treat Missing Covariance Notes

`TASK-0332` (atomic-clock real-row readiness gate) currently runs
without a covariance-discipline check. This review recommends:

- **Treat missing covariance notes as a BLOCKER**, not a limitation
  or a review-summary-only annotation, for any source family that
  contains more than one row OR that shares systematics with another
  family. A single isolated direct measurement may proceed with
  `covariance_reference: none_documented_single_row` because no
  cross-row covariance is at risk.

- **Treat missing per-row `confidence_level_label` as a BLOCKER**
  whenever multiple rows enter the residual axis. A single
  hard-coded campaign default in the manifest is not a substitute.

- **Treat missing `derivation_assumptions` on derived-constraint
  rows as a BLOCKER** even on the alternate axis, because without
  the assumptions the row cannot be re-evaluated under a different
  combination rule.

- **Treat asymmetric uncertainty rows with no `asymmetric_upper` /
  `asymmetric_lower` fields as a BLOCKER**, not a limitation, when
  the source artifact reports the asymmetry. Silently symmetrising
  is the most common atomic-clock-discipline failure.

Each "BLOCKER" recommendation here means that the row stays out of
the residual axis (`inclusion_status: excluded`) with the explicit
reason recorded in `inclusion_reason`, and the readiness gate
returns `BLOCKED_VALUE_SEMANTICS`. A maintainer waiver is the only
way to override.

## What This Review Did Not Do

- It did not ingest any clock value, drift constraint, or derived
  bound.
- It did not edit `data/atomic_clocks/source_manifest_template.yaml`
  or `data/atomic_clocks/schema.md`. (Deferred to the follow-up
  task per the "Schema / Manifest Wording Recommendations" section
  to avoid conflict with the parallel TASK-0355 review.)
- It did not authorise a real `TASK-0332` reveal.
- It did not promote any claim, knowledge entry, or canonical
  result.

## Limitations

- The forbidden representations listed here are the ones surveyed
  in the existing atomic-clock review series. A future source may
  expose a new uncertainty representation that requires this
  document to be amended rather than relaxed.
- The recommendations assume the campaign keeps its current
  `direct` / `derived` / `review_summary` / `synthetic_dry_run`
  row-class separation. If a future task collapses these classes,
  the covariance discipline must be re-derived.
- The review does not estimate how many candidate sources are
  likely to pass the discipline gate; that is a per-source-family
  diagnostic owned by source-specific tasks (e.g. TASK-0355).

## Verdict

`PARTIALLY_VALID` for the uncertainty-and-covariance discipline
contract. The required and forbidden representations, the four
covariance stop conditions, and the recommended treatment of
missing covariance notes in TASK-0332 are now reviewable in
advance. No row has been ingested. The next allowed step is the
TASK-0355 source-artifact review (sibling, parallel) followed by
a coordinated follow-up task that applies the schema / manifest
wording recommendations and re-runs TASK-0332 with the new
BLOCKER rules in effect.
