# Atomic Real Direct-Row Loader Review

**Task:** `TASK-0453`  
**Campaign:** `atomic-clock-residuals`  
**Loader:** `physics_lab/engines/atomic_clock_residuals.py`  
**Status:** deterministic direct-row validation only; no benchmark consumer

## Scope

This review records the first deterministic loader path for committed
`row_class: direct_measurement` atomic-clock rows. It validates the Beloy 2021
`ACR-0001` seed rows without computing residuals, fitting constants drift,
deriving constraints, writing prediction entries, creating `RESULT-*`
artifacts, or promoting claims.

Synthetic dry-run rows remain on the pre-existing synthetic loader path. The
new direct-row path is intentionally separate so fabricated fixtures cannot
silently masquerade as real measurements and real rows cannot silently use
synthetic field names.

## Implemented Contract

The direct-row loader now requires each committed row to carry:

- `row_id`, `row_class`, `observable_id`;
- `clock_system` and `reference_system` with clock identity, species, and
  transition labels;
- `observable.value_kind: frequency_ratio`, committed value, units, and epoch
  bounds;
- `uncertainty.total`, `confidence_level_label`, `bound_style`, and
  `covariance_reference`;
- `source` with citation, retrieval date, checksum, checksum scope, licence
  note, and either DOI or archive URL;
- `classification` flags with `direct_measurement: true` and
  `derived_constraint`, `review_summary`, and `synthetic` all false;
- `holdout.split`;
- non-empty limitations.

At the dataset level, the loader also enforces that benchmark, drift-fitting,
derived-constraint, claim-promotion, and prediction-registry flags remain
false during validation.

## Source Naming Reconciliation

The loader makes the source-field split explicit:

- synthetic fixtures use `source_metadata`;
- committed real direct rows use `source`;
- a direct row that includes `source_metadata` is rejected.

This preserves the existing synthetic dry-run behavior while matching the
real-row schema sketch and the committed Beloy seed.

## Tests

`tests/test_atomic_clock_real_rows.py` verifies that:

- the committed Beloy 2021 direct-ratio seed loads as three
  `direct_measurement` rows;
- all three rows retain `1_sigma` confidence labels, `measurement` bound
  style, and the shared `bacon_2018_campaign` covariance group;
- a direct row using the synthetic `source_metadata` alias is rejected;
- a direct row missing `uncertainty.covariance_reference` is rejected;
- the existing synthetic dry-run fixture still loads through the synthetic
  path.

## Boundary

This loader clears only the deterministic real-row validation blocker. Atomic
is still not `BASELINE_READY` because future work must still resolve
holdout/no-peek assignment, second-source readiness or waiver, and benchmark
covariance policy acceptance before any real Yb/Sr cross-source benchmark.

## Verdict

`VALID_IN_RANGE`

The committed Beloy direct rows now have a deterministic validation path, and
the synthetic loader behavior remains intact. The loader does not authorize
benchmark metrics, constants-drift fits, predictions, claims, knowledge, or
canonical results.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: loader code, targeted tests, and this review note;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- limitations / blockers: real benchmark work remains blocked on no-peek
  holdout assignment, cross-source readiness, and benchmark covariance policy.
