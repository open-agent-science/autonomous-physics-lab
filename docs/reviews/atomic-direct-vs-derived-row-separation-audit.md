# Atomic Direct-Vs-Derived Row Separation Audit

**Task:** `TASK-0487`
**Campaign:** `atomic-clock-residuals`
**Audit class:** scientific validation / source discipline
**Status:** no new measurement values, no derived values, no drift fit, no claim

## Scope

This audit checks the current Atomic-Clock schema sketch, committed Beloy 2021
rows, loader rules, and source-review notes for direct-vs-derived separation.
It records the boundary that future derived-constraint tasks must preserve
before any benchmark consumer runs.

Inputs reviewed:

- `data/atomic_clocks/schema.md`;
- `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`;
- `data/atomic_clocks/atomic_holdout_manifest.yaml`;
- `physics_lab/engines/atomic_clock_residuals.py`;
- `docs/campaigns/atomic-clock-residuals.md`;
- `docs/reviews/atomic-clock-primary-frequency-ratio-source-review.md`;
- `docs/reviews/atomic-clock-derived-constraint-source-review.md`;
- `docs/reviews/atomic-clock-beloy-2021-direct-ratio-row-curation.md`;
- `docs/reviews/atomic-holdout-no-peek-manifest.md`;
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`.

No live source fetch, row ingestion, benchmark metric, prediction-registry
entry, result artifact, claim, or knowledge entry is added.

## Pre-Claim Search

Before implementation, open-PR search found no active implementation PR for:

- `TASK-0487`;
- `atomic direct derived row separation`.

Claim surface for this PR:

- `tasks/TASK-0487-audit-atomic-direct-vs-derived-row-separation.yaml`;
- `docs/reviews/atomic-direct-vs-derived-row-separation-audit.md`;
- `data/atomic_clocks/schema.md`.

## Current Schema Boundary

The schema sketch already names four row classes:

| Row class | Allowed role |
| --- | --- |
| `direct_measurement` | Primary measured frequency ratio or comparison row. |
| `derived_constraint` | Drift or constants-variation constraint derived from measurements plus sensitivity/model assumptions. |
| `review_summary` | Evaluation or review value that combines sources; not ingestible unless provenance and combination rules are explicit. |
| `synthetic_dry_run` | Fabricated loader/schema exercise row only. |

The schema now makes the consistency rule explicit: `row_class` must agree with
the `classification` booleans. Real direct rows must set only
`classification.direct_measurement: true`; the derived, review-summary, and
synthetic flags must be `false`.

## Beloy Row Audit

The committed Beloy seed file contains three rows:

| Row | Observable | Row class | Classification state | Separation verdict |
| --- | --- | --- | --- | --- |
| `ACR-0001-ROW-001` | Al+/Yb frequency ratio | `direct_measurement` | direct `true`; derived/review/synthetic `false` | `PASS` |
| `ACR-0001-ROW-002` | Al+/Sr frequency ratio | `direct_measurement` | direct `true`; derived/review/synthetic `false` | `PASS` |
| `ACR-0001-ROW-003` | Yb/Sr frequency ratio | `direct_measurement` | direct `true`; derived/review/synthetic `false` | `PASS` |

The file-level scope flags also preserve the boundary:

- `benchmark_allowed: false`;
- `drift_fitting_allowed: false`;
- `derived_constants_constraint_allowed: false`;
- `claim_promotion_allowed: false`;
- `prediction_registry_allowed: false`;
- `promotion_boundary.writes_derived_constraint_values: false`.

Verdict: the Beloy seed rows are direct measurement rows only. Their
per-systematic-component notes and covariance-group metadata are uncertainty
context for the direct measurements, not derived constants constraints.

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

This means a future derived-constraint row cannot silently enter the current
real direct-row loader.

## Future Derived-Constraint Requirements

A future task that writes `row_class: derived_constraint` must record at least:

| Requirement | Reason |
| --- | --- |
| `derived_constraint.quantity` | Names the constrained quantity instead of reusing a direct-ratio label. |
| `sensitivity_coefficients.source` and coefficient values | Preserves the model bridge from frequency ratios to constants constraints. |
| `input_measurement_rows` | Prevents treating a derived value and its input direct rows as independent evidence. |
| Interval or epoch semantics | Distinguishes a campaign bound, repeated comparison, slope, or fitted coefficient. |
| Unit and bound semantics | Separates point estimates, limits, confidence intervals, and coverage conventions. |
| Model assumptions | Records which constants vary, which are fixed, and whether multiple constants are fit together. |
| Covariance/correlation notes | Keeps shared measurements, shared clocks, and coefficient correlations visible. |
| Source locator, retrieval date, checksum or archive policy, and license note | Matches the direct-row provenance floor. |
| `holdout.split: excluded` unless a later manifest revision authorizes otherwise | Keeps derived constraints out of scored direct residual axes by default. |

Derived constraints must not be loaded through the direct-row loader, must not be
used as direct benchmark rows, and must not be combined with their own input
measurements as independent evidence without a later reviewed dependency rule.

## Review-Summary Boundary

`review_summary` rows remain review-only unless a future task can recover and
record:

- the primary measurements combined by the review value;
- the combination or evaluation rule;
- uncertainty, covariance, and confidence semantics;
- source artifact provenance and reuse terms;
- whether the value duplicates direct rows or derived constraints already in
  the repository.

Absent those fields, a review summary may be preserved as source-review memory
but must remain excluded from scored residual axes.

## Verdict

`VALID_IN_RANGE`

Atomic's current Beloy seed rows preserve direct-vs-derived separation for the
current source-readiness stage. The repository has direct rows only; no derived
constraint values are committed. The real direct-row loader rejects derived,
review-summary, and synthetic classifications, and the schema now states the
row-class/classification consistency rule explicitly.

## Limitations

- This audit does not add or inspect new source values.
- It does not validate any future derived-constraint source-specific row.
- It does not unblock constants-drift fitting or any new benchmark result.
- The Beloy rows remain sandbox-only first-seed data until the baseline
  readiness gate accepts all source, holdout, loader, and covariance blockers.

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
