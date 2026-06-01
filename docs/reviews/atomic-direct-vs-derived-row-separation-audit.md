# Atomic Direct-vs-Derived Row Separation Audit

**Task:** `TASK-0487`
**Campaign:** Atomic Clock Residuals
**Verdict:** `DIRECT_DERIVED_BOUNDARY_INTACT_WITH_FUTURE_DERIVED_CONSTRAINT_REQUIREMENTS`

## Scope

This audit reviews the current Atomic Clock Residuals schema sketch and the
committed Beloy 2021 / BACON direct-ratio seed rows for direct-vs-derived row
separation.

This task does not add measurement values, derived constants constraints,
review-summary values, benchmark metrics, drift fits, prediction-registry
entries, claims, or knowledge artifacts.

## Reviewed Surfaces

- `data/atomic_clocks/schema.md`
- `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`
- `docs/campaigns/atomic-clock-residuals.md`

## Schema Boundary Check

`data/atomic_clocks/schema.md` already separates future Atomic evidence into
four row classes:

| Row class | Ingestion status in current repo | Boundary result |
| --- | --- | --- |
| `direct_measurement` | Allowed only after source-manifest review. | Acceptable for Beloy 2021 rows. |
| `derived_constraint` | Must not be mixed with direct rows without explicit flags. | No current rows use this class. |
| `review_summary` | Not ingestible unless provenance and combination rules are explicit. | No current rows use this class. |
| `synthetic_dry_run` | Allowed only when clearly marked synthetic. | Separate from real Beloy rows. |

The schema also requires classification flags:

```yaml
classification:
  direct_measurement: true
  derived_constraint: false
  review_summary: false
  synthetic: false
```

This is sufficient for the current seed dataset because the committed real rows
are all direct frequency-ratio measurements, not constraints on drift or
fundamental constants.

## Beloy 2021 Row Check

`data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` contains three
committed rows:

| Row | Observable | Declared `row_class` | Direct flag | Derived flag | Review-summary flag | Synthetic flag |
| --- | --- | --- | --- | --- | --- | --- |
| `ACR-0001-ROW-001` | `frequency_ratio_al27plus_yb171_beloy2021` | `direct_measurement` | true | false | false | false |
| `ACR-0001-ROW-002` | `frequency_ratio_al27plus_sr87_beloy2021` | `direct_measurement` | true | false | false | false |
| `ACR-0001-ROW-003` | `frequency_ratio_yb171_sr87_beloy2021` | `direct_measurement` | true | false | false | false |

Each row records:

- a primary frequency-ratio observable;
- named clock and reference systems;
- dimensionless-ratio units;
- epoch start/end campaign window;
- total, statistical, and systematic uncertainty fields;
- a reviewed source citation, DOI, archive locator, retrieval date, checksum,
  checksum scope, and license note;
- direct-vs-derived classification flags;
- sandbox-only limitations that prohibit benchmarks, drift fits, derived
  constants constraints, and claim promotion.

No committed Beloy row is misclassified as a derived constraint or review
summary value.

## Dataset-Level Promotion Boundary

The Beloy dataset includes dataset-level scope flags:

```yaml
benchmark_allowed: false
drift_fitting_allowed: false
derived_constants_constraint_allowed: false
claim_promotion_allowed: false
prediction_registry_allowed: false
```

It also records a promotion boundary stating that real clock values are written
as a first seed, while derived constraint values, benchmark metrics,
prediction-registry entries, canonical results, and claim promotion remain
blocked.

This boundary is consistent with the row-level classification flags and should
remain in force until a separate baseline-readiness gate explicitly changes the
campaign state.

## Direct Measurement Boundary

A direct measurement row is allowed to contain information needed to interpret
that measurement, including:

- source citation and checksum/provenance metadata;
- clock species, isotope, charge state, and transition labels;
- frequency-ratio value and unit semantics;
- measurement campaign interval;
- uncertainty components and covariance/correlation notes;
- holdout or freeze-manifest status;
- limitations and benchmark prohibitions.

Those fields do not make the row a derived constraint as long as the observable
is still the primary reported measurement and no constants-drift quantity is
computed or copied as the row value.

## Derived Constraint Boundary

A derived constraint row must not reuse the Beloy direct-ratio row shape without
additional fields. Any future task that adds `row_class: derived_constraint`
must include at least:

```yaml
row_class: derived_constraint
observable:
  value_kind: derived_constraint
  residual_form: null
classification:
  direct_measurement: false
  derived_constraint: true
  review_summary: false
  synthetic: false
derived_constraint:
  quantity: null
  sensitivity_coefficients:
    source: null
    values: []
    assumptions: []
  input_measurement_rows: []
  model_dependency_notes: []
  derivation_source:
    citation: null
    doi: null
    archive_url: null
    retrieval_date: null
    checksum_sha256: null
    checksum_scope: null
  interval_semantics: null
  confidence_level_label: null
  bound_style: null
```

The `input_measurement_rows` field must list all direct measurement rows that
feed the constraint, or explicitly state that the source paper/review does not
publish enough information to map the constraint to source rows. A constraint
without this mapping is not benchmark-ready.

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

Without that metadata, the value should remain a review note, not an Atomic row.

## Required Future Derived-Constraint Fields

Any future derived-constraint task must provide these fields or stop as blocked:

| Field family | Required content | Stop condition if missing |
| --- | --- | --- |
| Constraint identity | `quantity`, value kind, units, confidence/bound style | Cannot distinguish drift bound from direct ratio. |
| Sensitivity model | coefficient source, coefficient values, assumptions | Cannot audit model dependency. |
| Measurement provenance | input rows or primary source measurements | High risk of direct/derived double counting. |
| Time interval | epoch or interval semantics | Drift bounds are not comparable. |
| Uncertainty semantics | confidence level, covariance/correlation notes | Constraint cannot be benchmarked. |
| Source artifact | DOI/archive locator, retrieval date, checksum or archive policy | Fails fresh-data source policy. |
| Promotion boundary | claim/result/prediction status and limitations | Overclaim risk. |

## Stop Conditions For Future Atomic Work

Stop before ingestion or benchmark consumption when:

- a task mixes `direct_measurement` and `derived_constraint` rows in one table
  without explicit `row_class` and classification flags;
- a constants-drift bound is copied as if it were a primary frequency ratio;
- a direct frequency-ratio row is used as an independent row after it has already
  contributed to a derived constraint in the same benchmark surface;
- sensitivity coefficients are used without source citation, values, and
  assumptions;
- a review-summary value hides which primary measurements were combined;
- a benchmark consumer ignores the dataset's `benchmark_allowed: false` or
  `derived_constants_constraint_allowed: false` flags;
- a task proposes prediction-registry, claim, or knowledge promotion before a
  reviewed baseline-readiness gate.

## Impact On Baseline-Readiness Gates

This audit provides the direct-vs-derived boundary check used by Atomic
baseline-readiness gates such as `TASK-0455`.

Baseline-readiness reviews should treat direct-vs-derived separation as
currently intact for Beloy `ACR-0001`, but still blocked for any benchmark that
requires derived constraints, because no derived-constraint rows exist and no
separate source-gated derived-constraint ingestion task has passed.

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
use, drift fitting, prediction registry, and claim promotion disabled. Future
Atomic derived-constraint work must use a distinct row class, explicit
sensitivity-model metadata, input-measurement provenance, interval semantics,
and source checksums before it can be considered for benchmark or scientific
memory routing.
