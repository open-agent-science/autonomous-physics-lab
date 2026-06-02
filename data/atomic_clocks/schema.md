# Atomic-Clock Row Schema Sketch

This is a planning schema sketch, not an active dataset schema. It defines the
minimum fields future tasks should preserve before atomic-clock rows or
constraints can be ingested.

## Row Classes

Future rows must declare one of:

| Row class | Meaning | Ingestion rule |
| --- | --- | --- |
| `direct_measurement` | Primary frequency-ratio or comparison measurement. | Allowed only after source-manifest review. |
| `derived_constraint` | Drift or constants-variation constraint derived from one or more measurements and sensitivity assumptions. | Must not be mixed with direct rows without explicit flags. |
| `review_summary` | Evaluation or review value that combines sources. | Not ingestible unless provenance and combination rules are explicit. |
| `synthetic_dry_run` | Fabricated row for testing schema or loaders. | Allowed only when clearly marked synthetic. |

`row_class` and the booleans in `classification` must agree. For real direct
measurement rows, `classification.direct_measurement` must be `true` and
`classification.derived_constraint`, `classification.review_summary`, and
`classification.synthetic` must all be `false`. Future derived-constraint or
review-summary rows must use their own row class and must not be ingested into
a direct-frequency-ratio residual axis unless a later task defines an explicit,
reviewed separation rule.

## Minimal Fields

```yaml
row_id: ACLOCK-ROW-0001
row_class: direct_measurement
observable_id: frequency_ratio_sr_yb_YYYY
clock_system:
  species: Sr
  isotope: "87"
  transition_label: optical_lattice_clock_transition
reference_system:
  species: Yb
  isotope: "171"
  transition_label: optical_lattice_clock_transition
observable:
  value_kind: frequency_ratio
  value: null
  residual_form: null
  units: dimensionless_ratio
  epoch_start: YYYY-MM-DD
  epoch_end: YYYY-MM-DD
uncertainty:
  total: null
  statistical: null
  systematic: null
  covariance_group: null
  correlation_notes: "not reviewed"
source:
  citation: "primary source required"
  doi: null
  archive_url: null
  retrieval_date: null
  checksum_sha256: null
  checksum_scope: null
  license_note: "not reviewed"
classification:
  direct_measurement: true
  derived_constraint: false
  review_summary: false
  synthetic: false
holdout:
  split: unassigned
  freeze_manifest: null
limitations:
  - "Planning placeholder; no value ingested."
```

## Derived Constraint Additions

Rows with `row_class: derived_constraint` must additionally record:

```yaml
derived_constraint:
  quantity: alpha_drift_bound
  sensitivity_coefficients:
    source: null
    values: []
    assumptions: []
  input_measurement_rows: []
  model_dependency_notes: []
```

Derived constraints cannot be treated as independent direct measurements.

## Required Validation Ideas For Future Tasks

Future ingestion work should add deterministic validation that checks:

- every row has a source citation or reviewed archive locator;
- every non-synthetic value has unit semantics and uncertainty fields;
- direct measurements and derived constraints are not silently mixed;
- rows with shared covariance groups are visible to downstream benchmarks;
- holdout and training classifications are explicit;
- no row lacks source retrieval date and checksum or archive policy;
- synthetic dry-run rows cannot be promoted to benchmark inputs.

## Stop Conditions

Stop before ingestion when:

- only a review plot or secondary summary is available;
- the transition or reference system is ambiguous;
- epoch semantics are missing;
- uncertainty or covariance language is incomplete;
- derived constants constraints hide sensitivity assumptions;
- source reuse or citation requirements are unclear;
- the task asks for constants-drift fitting before source review.
