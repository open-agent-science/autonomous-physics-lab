# Materials MD-0002 Acquisition Validation And Holdout Freeze (TASK-0702)

**Task:** `TASK-0702`
**Campaign:** Materials Property Residuals
**Mode:** validation gate; no residual, baseline, or metric scored
**Verdict:** `ACQUISITION_VALID__HOLDOUT_FROZEN` — `TASK-0703` may proceed.

## Scope

`TASK-0738` committed the MD-0002 dataset (362 stable alkali/alkaline-earth +
3d-transition ternary oxides). This gate verifies, before any scoring, that the
acquisition is source-pinned, attribution-complete, and that the holdout/no-peek
split was frozen deterministically. It scores no baseline, residual, or metric.

Note: the original `TASK-0702` blocker text referenced `TASK-0699` landing the
dataset; the cap-stopped `TASK-0699` produced no dataset, and the value-bearing
acquisition actually landed via `TASK-0738`. The dependency is corrected to
`TASK-0738` in the task file.

## Deterministic Checks (all pass)

Re-run from the repository root over the committed artifacts:

| Check | Result |
| --- | --- |
| Snapshot SHA-256 recomputed from `data/materials/snapshots/materials_project_md0002_2026.04.13.json` | `5bfb3e7f86c0afcd…349567` |
| — matches dataset `snapshot_checksum_sha256` | ✅ |
| — matches holdout manifest `scope.snapshot_checksum_sha256` | ✅ |
| Row count | `724` = 362 formation-energy + 362 band-gap (matches header `row_count`) |
| All rows `inclusion_status: included`, `provenance_class: computed_dft` | ✅ |
| License / source version | `CC BY 4.0` / `database_version 2026.04.13` |
| DATA_LICENSES declaration | ✅ `materials-project-ternary-oxides-md0002` (CC BY 4.0, attribution) |
| Committed split counts per axis | train `253`, validation `55`, holdout `54` |
| — match holdout manifest `frozen_split_counts_per_axis` | ✅ |
| **Holdout-freeze re-derivation** (sorted `material_id`, deterministic 70/15/15) | **0 mismatches vs committed `split`** |

## Holdout / No-Peek Freeze

The per-row `split` is reproduced exactly by the frozen rule (cumulative
fraction over sorted `material_id`), so the freeze is deterministic and depends
**only on material_id ordering, never on formation-energy or band-gap values**.
That satisfies the no-peek requirement: the split is fixed before any scoring and
cannot be tuned to residuals. Formation energy and band gap remain separate axes
and must not be pooled.

## Decision

`ACQUISITION_VALID__HOLDOUT_FROZEN`. The MD-0002 acquisition is source-pinned,
checksum-consistent, attribution-complete, and holdout-frozen. The formation-energy
retest (`TASK-0703`) may proceed under the frozen split; band gap stays
diagnostic-only.

## Limitations

- 362 included rows per axis is below the original 600 pre-fetch target
  (maintainer-accepted in `TASK-0738`); the retest holdout (54 rows) is larger
  than MD-0001's (33) but still small.
- Computed DFT only; no experimental measurements.
- This gate scores nothing; durability of the formation-energy signal on the
  wider slice is decided by `TASK-0703` (baseline + null controls +
  split-sensitivity), reusing the MD-0001 engines.

## Output-Routing Summary

- **Task verdict:** `ACQUISITION_VALID__HOLDOUT_FROZEN`.
- **Canonical destination:** this validation review; `TASK-0702` → `REVIEW_READY`;
  `TASK-0703` unblocked.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` created.
- **Gate A status:** not attempted. **Gate B status:** not applicable.
- **Claim impact:** no claim change. **Knowledge impact:** campaign routing only.
- **Limitations / blockers:** none for proceeding to `TASK-0703`; the retest must
  declare its baselines/controls before inspecting residuals.
