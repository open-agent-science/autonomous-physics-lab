# Atomic Row-Role Schema And Beloy Assignments

**Task:** `TASK-0538`
**Campaign:** Atomic-Clock Residuals
**Status:** review-ready schema/data assignment; no benchmark scoring
**Verdict:** `ROW_ROLES_ASSIGNED_SCHEMA_VALIDATED`

## Scope

This task turns the row-role intent fixed by
`docs/reviews/atomic-beloy-freeze-manifest-row-roles.md` into loader-validated
dataset fields. It only covers the three committed Beloy 2021 / BACON direct
frequency-ratio rows in
`data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`.

It does not add a second-source row, run cross-source metrics, fit constants
drift, write predictions, promote claims, or unblock `TASK-0456`.

## Loader Contract

`physics_lab/engines/atomic_clock_residuals.py` now validates real direct-row
holdout fields against the committed Atomic holdout manifest:

- `holdout.split` must be one of the manifest split values
  (`train`, `holdout`, `cross_source_reference`, `cross_source_target`,
  `excluded`) or `unassigned`.
- `unassigned` remains valid only for pre-assignment rows with
  `holdout.freeze_manifest: null` and `holdout.row_role: unassigned`.
- Assigned rows must set
  `holdout.freeze_manifest: data/atomic_clocks/atomic_holdout_manifest.yaml`,
  and the referenced manifest path must exist.
- `holdout.row_role` is restricted to the narrow split-compatible vocabulary:
  `training_context`, `cross_source_reference`, `cross_source_target`,
  `excluded`, or `unassigned`.

## Beloy Assignments

The committed Beloy rows now carry manifest-backed roles:

| Row | Observable | Split | Row role | Interpretation |
| --- | --- | --- | --- | --- |
| `ACR-0001-ROW-001` | Al+/Yb | `train` | `training_context` | non-primary context/train row |
| `ACR-0001-ROW-002` | Al+/Sr | `train` | `training_context` | non-primary context/train row |
| `ACR-0001-ROW-003` | Yb/Sr | `cross_source_reference` | `cross_source_reference` | first cross-source Yb/Sr reference row |

All three rows are bound to
`data/atomic_clocks/atomic_holdout_manifest.yaml`.

## Tests Updated

`tests/test_atomic_clock_real_rows.py` now asserts the manifest-backed Beloy
splits, row roles, and freeze-manifest binding. It also rejects:

- unknown direct-row `holdout.split` values;
- assigned rows without `holdout.freeze_manifest`;
- split/row-role mismatches.

## Boundaries Preserved

- The dataset scope flags still prohibit benchmark scoring, drift fitting,
  derived-constants constraints, claim promotion, and prediction registry writes.
- The target axis is not reselected in this task; it follows the TASK-0526
  Yb/Sr decision.
- No covariance metric, residual metric, or second-source target row is created.
- `TASK-0456` remains blocked by the missing reviewed second-source target.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `ROW_ROLES_ASSIGNED_SCHEMA_VALIDATED`; not a scientific
  claim or benchmark result.
- **Canonical destination:** this review note plus the loader, schema sketch,
  test, and Beloy direct-row YAML updates listed by `TASK-0538`.
- **Review tier:** none; no `RESULT-*`, `PRED-*`, or claim artifact is created.
- **Gate A status:** not attempted.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge promotion.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** row roles are now schema-validated for Beloy, but
  Atomic cross-source scoring still requires a reviewed second-source Yb/Sr
  target row and a separate benchmark task.
