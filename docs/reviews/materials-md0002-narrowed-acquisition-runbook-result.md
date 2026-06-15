# Materials MD-0002 Narrowed Acquisition Runbook Result

**Task:** `TASK-0738`
**Campaign:** Materials Property Residuals
**Status:** acquired (maintainer accepted the below-target row count)
**Verdict:** `ACQUIRED_MAINTAINER_ACCEPTED_LOW_ROW_COUNT`

## Scope

`TASK-0738` ran the maintainer-gated Materials Project acquisition for the
`TASK-0737`-approved narrowed predicate using `MP_API_KEY` from the local
environment (never committed, written to an artifact, or printed). The selected
predicate returned 362 included rows per axis, below the predeclared 600 lower
target. The maintainer explicitly accepted the 362-row slice (a ~2.1x widening
over MD-0001's 169), recorded via `--accept-row-count 362`, so the acquisition
proceeded and committed the pinned snapshot + normalized combined dataset.

Inclusion is chemistry-only (cation families + axis presence); no
formation-energy or band-gap value was used to include or exclude any row, and
no baseline, residual, ranking, prediction, or claim was produced.

## Source Pin

| Field | Value |
| --- | --- |
| Source | Materials Project summary API |
| Heartbeat `db_version` | `2026.04.13` |
| Query date | `2026-06-15` |
| Endpoint | `https://api.materialsproject.org/materials/summary/` |
| Base predicate | `elements=O`, `nelements=3`, `is_stable=true` |
| Predicate id | `md0002_alkali_alkaline_earth_3d_transition_oxide` |
| Snapshot checksum (sha256, reproducible) | `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567` |
| Tool | `scripts/acquire_md0002_materials_project.py` |

## Count And Acquisition Result

| Quantity | Value |
| --- | ---: |
| Raw stable-ternary-oxide candidates | `3473` |
| Selected predicate included per axis | `362` |
| Fallback predicate included per axis | `225` |
| Predeclared target per axis | `600-1500` |
| Cap per axis | `1500` |
| Maintainer decision | accept 362 (below 600 floor) |
| Committed rows (combined, both axes) | `724` (362 formation-energy + 362 band-gap) |
| Frozen split per axis | train `253`, validation `55`, holdout `54` |

The raw candidate count (`3473`) reproduces the `TASK-0699` run exactly. The
snapshot checksum is deterministic over the data (no retrieval timestamp in the
checksummed snapshot), so a re-fetch of `db_version 2026.04.13` reproduces it.

## Artifacts Committed

- `data/materials/snapshots/materials_project_md0002_2026.04.13.json` — pinned raw snapshot of the 362 included Materials Project records.
- `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml` — normalized **combined** dataset (both axes), passing `physics_lab/datasets/materials_md0002.py`; per-row 70/15/15 split frozen.
- `data/materials/md0002_holdout_manifest.yaml` — pinned `database_version`, `snapshot_checksum_sha256`, `row_count_per_axis`, frozen split counts; status `acquired_pinned_pending_holdout_freeze_validation`.
- `data/DATA_LICENSES.yaml` — new `materials-project-ternary-oxides-md0002` CC BY 4.0 entry.

### File-shape note for review

The MD-0002 loader (`load_md0002_dataset`) requires **both axes in one file**, so
the dataset is a single combined file rather than the two split files named in
the older scaffold/accepted-outputs. This follows the MD-0002-specific loader
design (the fixture is combined). If two split files are preferred, it is a
mechanical reshape.

## Maintainer Decision (resolved)

The `TASK-0737` contract required stopping and reporting when the predicate
returned < 600 rows. The maintainer reviewed the 362 count and chose **accept 362**
(over widening the predicate or lowering the 600 floor). The choice was made
without inspecting formation-energy or band-gap residuals, preserving no-peek
discipline.

## Guardrails Preserved

- `MP_API_KEY` was used only from the local environment and was not committed.
- Inclusion used chemistry only; no value-bearing axis was inspected to select rows.
- Formation energy and band gap are separate axes in the combined file and must not be pooled.
- No baseline, residual, ranking, prediction, recommendation, `RESULT-*`, `PRED-*`, or `CLAIM-*` artifact was created.

## Output Routing Summary

- Task verdict: `ACQUIRED_MAINTAINER_ACCEPTED_LOW_ROW_COUNT`.
- Canonical destination: pinned snapshot + normalized combined dataset + pinned holdout manifest + DATA_LICENSES entry + this runbook; `TASK-0738` → `REVIEW_READY`.
- Review tier: source/data acquisition execution only.
- Gate A status: `not_attempted`. Gate B status: `not_applicable`.
- Claim impact: none. Knowledge impact: workflow memory only.
- Next step: `TASK-0702` validates the acquisition and freezes the holdout binding; then `TASK-0703` runs the formation-energy retest. Band gap stays diagnostic-only.
- Limitations: 362 rows is below the original 600 target (maintainer-accepted); computed DFT only; combined-file shape supersedes the two-file scaffold plan.
