# Atomic Beloy Freeze-Manifest Row Roles

**Task:** `TASK-0526`
**Campaign:** Atomic-Clock Residuals
**Status:** review-ready protocol definition (no benchmark scoring)
**Verdict:** `ROW_ROLES_DEFINED_SCHEMA_EXPRESSION_BLOCKED`

## Scope

This review defines the no-peek row roles and freeze-manifest binding for the
three committed Beloy 2021 / BACON direct-ratio rows before any second-source
row is scored. It makes the first Atomic benchmark no-peek boundary explicit at
the row level.

It does **not** select success thresholds, fit drift, compute residual metrics,
combine rows, add measurement values, or unlock `TASK-0456`. It keeps the
campaign at `PINNED_DATASET` (per `TASK-0455`).

## Inputs Reviewed

- `TASK-0526`
- `docs/reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md`
- `docs/reviews/atomic-holdout-no-peek-manifest.md`
- `docs/reviews/atomic-direct-vs-derived-row-separation-audit.md`
- `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`
- `data/atomic_clocks/atomic_holdout_manifest.yaml`
- `data/atomic_clocks/schema.md`
- `physics_lab/engines/atomic_clock_residuals.py`
- `tests/test_atomic_clock_real_rows.py`

## Committed Beloy Rows

`data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` contains three
`direct_measurement` rows, all currently `holdout.split: unassigned` and
`holdout.freeze_manifest: null`:

| Row | Observable | Clock / reference | Intended role |
| --- | --- | --- | --- |
| `ACR-0001-ROW-001` | `frequency_ratio_al27plus_yb171_beloy2021` | Al+/Yb | context (non-primary) |
| `ACR-0001-ROW-002` | `frequency_ratio_al27plus_sr87_beloy2021` | Al+/Sr | context (non-primary) |
| `ACR-0001-ROW-003` | `frequency_ratio_yb171_sr87_beloy2021` | Yb/Sr | primary axis: cross-source reference |

## Row-Role Assignment (No-Peek, Pre-Inspection)

These roles are fixed **before** any second-source row is inspected, so the
target axis cannot be tuned after the fact.

### Primary axis — Yb/Sr (`ACR-0001-ROW-003`)

- **Role:** `cross_source_reference` (reference side of the first cross-source
  Yb/Sr consistency check).
- **Rationale:** Yb/Sr is the only Beloy species pair that a ranked, fully
  independent second source can directly cross-check (Nemitz 2016 / RIKEN and
  the Pizzocaro 2020 / INRIM fallback both publish Yb/Sr). This matches the
  `beloy_reference_family` mapping in `atomic_holdout_manifest.yaml`, which
  states the Yb/Sr row may move to `cross_source_reference` once a second
  source lands.
- **Binding:** when a second-source Yb/Sr row is committed, that row takes role
  `cross_source_target` and is compared 1:1 against this reference row. The
  target axis (Yb/Sr) is frozen now and must not be re-selected after seeing the
  second source's values, uncertainties, or residual direction.

### Context rows — Al+/Yb and Al+/Sr (`ACR-0001-ROW-001`, `ACR-0001-ROW-002`)

- **Role:** context / non-primary. They are **not** part of the first
  cross-source Yb/Sr axis because no ranked second source provides an
  independent Al+/Yb or Al+/Sr direct ratio for a 1:1 cross-check.
- **Default split intent:** `train`-like (single-source display / readiness
  diagnostics only). They must not be silently combined with the Yb/Sr axis,
  and they must not be promoted to a scored cross-source target.
- **Shared-clock caution:** ROW-001 (Yb) and ROW-002 (Sr) share physical clocks
  with the Yb/Sr reference row (`shared_clock_systems` in the dataset). Per the
  first-benchmark covariance policy, combining any of these rows in one metric
  requires an explicit covariance state; this review does not authorize such a
  combination.

### Freeze-manifest binding (intended)

Per the future-row guidance in `atomic-holdout-no-peek-manifest.md`, each Beloy
row's intended binding is:

```yaml
holdout:
  split: <train | cross_source_reference>   # Yb/Sr -> cross_source_reference; Al+ rows -> train
  freeze_manifest: data/atomic_clocks/atomic_holdout_manifest.yaml
```

## Schema-Expression Check (Why The Roles Are Not Yet Written To Data)

`TASK-0526` requires assigning these fields to the dataset only **if the schema
supports the fields cleanly**, and otherwise writing the blocker and proposing a
minimal schema follow-up. The current active surface cannot express the roles
cleanly:

1. **`holdout.split` value vocabulary is unvalidated, and a committed test pins
   the current value.** `physics_lab/engines/atomic_clock_residuals.py`
   (`_validate_direct_row`) reads `holdout.split` as a non-empty string but does
   not validate it against the manifest's split vocabulary
   (`train`, `holdout`, `cross_source_reference`, `cross_source_target`,
   `excluded`). Worse, `tests/test_atomic_clock_real_rows.py` asserts
   `{row.split for row in dataset.rows} == {"unassigned"}`. Changing the split
   on the committed seed would break that test and would set a value that nothing
   validates.
2. **`holdout.freeze_manifest` is not read or validated by the loader.** Setting
   it from `null` to the manifest path would be a silently-ignored field with no
   path-existence or content check — not a clean schema expression.
3. **There is no `row_role` concept in the loader or active schema.** Adding a
   `row_role` field would be unvalidated free text. `data/atomic_clocks/schema.md`
   is explicitly a "planning schema sketch, not an active dataset schema," so it
   cannot make `row_role` authoritative on its own.

Writing roles into `acr-0001` now would therefore be either test-breaking
(item 1) or unvalidated/silent (items 2-3), and it would mutate a
maintainer-reviewed `sandbox_first_seed` for a no-peek-sensitive decision
without an enforcement gate. This review intentionally adds **no** data edit.

## Minimal Schema Follow-Up Proposal

A separate, narrowly-scoped task (not this one) should make the roles
schema-clean, then assign them:

1. Extend `_validate_direct_row` to validate `holdout.split` against the
   manifest's allowed split vocabulary, treating `unassigned` as the only
   pre-assignment value.
2. Read and validate `holdout.freeze_manifest`: when a row's split is a scored
   role, require `freeze_manifest` to point at an existing manifest file.
3. Optionally add a validated `row_role` enum
   (`primary_cross_source_axis | context_non_primary`) if the maintainer wants a
   role field distinct from the split.
4. Update `tests/test_atomic_clock_real_rows.py` to expect the manifest-backed
   splits once they are assigned, replacing the `{"unassigned"}` assertion.
5. Only then assign the roles in `acr-0001` (Yb/Sr -> `cross_source_reference`,
   Al+ rows -> `train`, all rows ->
   `freeze_manifest: data/atomic_clocks/atomic_holdout_manifest.yaml`).

Keeping this as a separate task preserves the no-peek boundary (roles are fixed
in this review before any second-source inspection) while ensuring the eventual
data edit is enforced by code, not asserted by prose.

## Boundaries Preserved

- No success thresholds, residual metrics, drift fits, or constants-variation
  values are selected or computed.
- No rows are combined; no covariance state is exercised.
- `TASK-0456` stays blocked; the campaign stays `PINNED_DATASET`.
- The dataset's `benchmark_allowed`, `drift_fitting_allowed`,
  `claim_promotion_allowed`, and `prediction_registry_allowed` flags remain
  `false`.

## Limitations

- This review fixes role *intent*; it does not write role *fields* to the
  dataset because the active schema cannot express them cleanly yet.
- Role assignment assumes the ranked second-source path (Yb/Sr via Nemitz 2016
  or the Pizzocaro 2020 fallback). If the maintainer selects a different second
  source pair, the primary axis must be re-fixed in a new no-peek review before
  inspection, not after.
- This review does not inspect the Beloy PDF or recompute any row value.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for a scientific claim;
  `ROW_ROLES_DEFINED_SCHEMA_EXPRESSION_BLOCKED` for the protocol artifact.
- **Canonical destination:** this review note,
  `docs/reviews/atomic-beloy-freeze-manifest-row-roles.md`.
- **Review tier:** `none` (no `RESULT-*` or `PRED-*` artifact).
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change. **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified; no
  `acr-*.yaml` data edit.
- **Limitations / blockers:** row roles are defined but not written to data
  because the active loader/test cannot express manifest-backed
  `holdout.split` / `freeze_manifest` / `row_role` cleanly; a minimal schema
  follow-up task is required before assignment, and the second-source row that
  would activate the `cross_source_target` binding is still blocked
  (see `TASK-0525`).
