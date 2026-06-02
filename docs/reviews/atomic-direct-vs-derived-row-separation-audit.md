# Atomic Direct-vs-Derived Row Separation Audit

**Task:** `TASK-0487`
**Campaign:** Atomic Clock Residuals
**Verdict:** `DIRECT_DERIVED_BOUNDARY_INTACT_WITH_FUTURE_DERIVED_CONSTRAINT_REQUIREMENTS`

## Scope

This audit reviews the current Atomic Clock Residuals schema sketch, committed
Beloy 2021 / BACON direct-ratio seed rows, loader rules, and campaign review
notes for direct-vs-derived row separation.

This task does not add measurement values, derived constants constraints,
review-summary values, benchmark metrics, drift fits, prediction-registry
entries, claims, results, or knowledge artifacts.

## Reviewed Surfaces

- `data/atomic_clocks/schema.md`
- `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`
- `data/atomic_clocks/atomic_holdout_manifest.yaml`
- `physics_lab/engines/atomic_clock_residuals.py`
- `docs/campaigns/atomic-clock-residuals.md`
- `docs/reviews/atomic-clock-primary-frequency-ratio-source-review.md`
- `docs/reviews/atomic-clock-derived-constraint-source-review.md`
- `docs/reviews/atomic-clock-beloy-2021-direct-ratio-row-curation.md`
- `docs/reviews/atomic-holdout-no-peek-manifest.md`
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`

## Schema Boundary Check

`data/atomic_clocks/schema.md` separates future Atomic evidence into four row
classes:

| Row class | Current boundary |
| --- | --- |
| `direct_measurement` | Primary measured frequency-ratio or comparison row. |
| `derived_constraint` | Drift or constants-variation constraint derived from measurements plus sensitivity/model assumptions. |
| `review_summary` | Evaluation or review value that combines sources; not ingestible unless provenance and combination rules are explicit. |
| `synthetic_dry_run` | Fabricated loader/schema exercise row only. |

`row_class` and the `classification` booleans must agree. For real direct
measurement rows, only `classification.direct_measurement` may be `true`; the
derived, review-summary, and synthetic flags must be `false`.

## Beloy 2021 Row Check

`data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` contains three
committed direct rows:

| Row | Observable | Declared `row_class` | Direct flag | Derived flag | Review-summary flag | Synthetic flag |
| --- | --- | --- | --- | --- | --- | --- |
| `ACR-0001-ROW-001` | `frequency_ratio_al27plus_yb171_beloy2021` | `direct_measurement` | true | false | false | false |
| `ACR-0001-ROW-002` | `frequency_ratio_al27plus_sr87_beloy2021` | `direct_measurement` | true | false | false | false |
| `ACR-0001-ROW-003` | `frequency_ratio_yb171_sr87_beloy2021` | `direct_measurement` | true | false | false | false |

Each row records source provenance, clock/reference systems, dimensionless
ratio units, campaign interval, uncertainty components, covariance notes,
holdout status, and limitations. These interpretation fields do not make the
row a derived constraint as long as the row value remains the primary reported
frequency-ratio measurement and no constants-drift quantity is computed or
copied as the observable value.

## Dataset-Level Boundary

The Beloy dataset preserves the boundary with file-level flags:

```yaml
benchmark_allowed: false
drift_fitting_allowed: false
derived_constants_constraint_allowed: false
claim_promotion_allowed: false
prediction_registry_allowed: false
```

Its promotion boundary writes real clock values only as a first seed. Derived
constraint values, benchmark metrics, prediction-registry entries, canonical
results, and claim promotion remain blocked.

## Loader Boundary

`physics_lab/engines/atomic_clock_residuals.py` keeps real direct rows separate
from synthetic fixtures and derived synthetic rows:

- real direct datasets accept only `row_class: direct_measurement`;
- real direct rows must use `source`, not `source_metadata`;
- real direct rows must use `observable.value_kind: frequency_ratio`;
- real direct rows must have positive `uncertainty.total`,
  `confidence_level_label`, `bound_style`, and `covariance_reference`;
- real direct rows must set `classification.direct_measurement: true`;
- real direct rows must set `classification.derived_constraint`,
  `classification.review_summary`, and `classification.synthetic` to `false`;
- synthetic dry-run rows are accepted only through the synthetic loader path,
  and derived synthetic rows require `derived_constraint` metadata.

A future derived-constraint row therefore cannot silently enter the current
real direct-row loader.

## Future Derived-Constraint Requirements

Any future task that adds `row_class: derived_constraint` must include at
least:

| Field family | Required content | Stop condition if missing |
| --- | --- | --- |
| Constraint identity | Quantity, value kind, units, confidence or bound style. | Cannot distinguish drift bound from direct ratio. |
| Sensitivity model | Coefficient source, coefficient values, assumptions. | Cannot audit model dependency. |
| Measurement provenance | Input rows or primary source measurements. | High risk of direct/derived double counting. |
| Time interval | Epoch or interval semantics. | Drift bounds are not comparable. |
| Uncertainty semantics | Confidence level, covariance/correlation notes. | Constraint cannot be benchmarked. |
| Source artifact | DOI/archive locator, retrieval date, checksum or archive policy. | Fails fresh-data source policy. |
| Promotion boundary | Claim/result/prediction status and limitations. | Overclaim risk. |

The `input_measurement_rows` field must list all direct measurement rows that
feed the constraint, or explicitly state that the source does not publish
enough information to map the constraint to source rows. A constraint without
this mapping is not benchmark-ready.

## Review-Summary Boundary

A `review_summary` value must not be promoted as a direct row. Future review or
evaluation values are admissible only as planning metadata unless they carry:

- the primary measurements used in the summary;
- the combination rule;
- covariance or correlation assumptions;
- interval semantics;
- source checksums or archive policy;
- an explicit reason why the review summary is not double-counting rows already
  present in the repository.

Without that metadata, the value should remain a review note, not an Atomic
row.

## Stop Conditions For Future Atomic Work

Stop before ingestion or benchmark consumption when:

- a task mixes `direct_measurement` and `derived_constraint` rows in one table
  without explicit `row_class` and classification flags;
- a constants-drift bound is copied as if it were a primary frequency ratio;
- a direct frequency-ratio row is used as an independent row after it has
  already contributed to a derived constraint in the same benchmark surface;
- sensitivity coefficients are used without source citation, values, and
  assumptions;
- a review-summary value hides which primary measurements were combined;
- a benchmark consumer ignores the dataset's `benchmark_allowed: false` or
  `derived_constants_constraint_allowed: false` flags;
- a task proposes prediction-registry, claim, result, or knowledge promotion
  before a reviewed baseline-readiness gate.

## Impact On Baseline-Readiness Gates

Baseline-readiness reviews should treat direct-vs-derived separation as intact
for Beloy `ACR-0001`, but still blocked for any benchmark that requires
derived constraints. No derived-constraint rows exist and no separate
source-gated derived-constraint ingestion task has passed.

## Limitations

- This audit does not inspect the original Beloy PDF or recompute row values.
- This audit does not add or validate a derived-constraint schema in code.
- This audit does not run an Atomic benchmark.
- This audit does not decide whether single-source Beloy rows are enough for a
  baseline; that remains a separate source/replay/holdout decision.
- This audit does not promote the Atomic campaign to `BASELINE_READY`.

## Verdict

`DIRECT_DERIVED_BOUNDARY_INTACT_WITH_FUTURE_DERIVED_CONSTRAINT_REQUIREMENTS`

The current Beloy `ACR-0001` rows are consistently represented as sandbox-only
`direct_measurement` rows with derived constraints, review summaries, benchmark
use, drift fitting, prediction registry, result publication, and claim
promotion disabled. Future Atomic derived-constraint work must use a distinct
row class, explicit sensitivity-model metadata, input-measurement provenance,
interval semantics, and source checksums before it can be considered for
benchmark or scientific-memory routing.

## Output Routing Summary

- Task verdict: `VALID_IN_RANGE`.
- Canonical destination:
  `docs/reviews/atomic-direct-vs-derived-row-separation-audit.md`.
- Review tier: `none`.
- Gate A status: not attempted.
- Gate B status: not attempted.
- Claim impact: no claim status transition.
- Knowledge impact: no knowledge promotion.
- Result artifact impact: no `results/` artifact modified.
