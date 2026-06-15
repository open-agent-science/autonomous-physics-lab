# Materials MD-0002 Narrowed Acquisition Runbook Result

**Task:** `TASK-0738`
**Campaign:** Materials Property Residuals
**Status:** stopped below the predeclared lower target
**Verdict:** `BELOW_TARGET_ROW_COUNT__MAINTAINER_DECISION_REQUIRED`

## Scope

`TASK-0738` executed the maintainer-gated Materials Project count check for the
`TASK-0737`-approved narrowed predicate using `MP_API_KEY` from the local
environment. The key was not committed, written to an artifact, or printed.

No dataset files were committed because the selected predicate returned fewer
than the predeclared 600-row-per-axis lower target, and the narrowed-predicate
contract requires stopping and reporting rather than auto-broadening,
subsampling, or silently committing.

Inclusion is chemistry-only (cation families + axis presence); no formation-energy
or band-gap value was used to include or exclude any row.

## Source Pin

| Field | Observed value |
| --- | --- |
| Source | Materials Project summary API |
| Heartbeat `db_version` | `2026.04.13` |
| Query date | `2026-06-15` |
| Query endpoint | `https://api.materialsproject.org/materials/summary/` |
| Base predicate | `elements=O`, `nelements=3`, `is_stable=true` |
| Tool | `scripts/acquire_md0002_materials_project.py --mode count` |

## Count Result

| Quantity | Value |
| --- | ---: |
| Raw stable-ternary-oxide candidates | `3473` |
| Selected predicate included per axis (alkali/alkaline-earth + 3d-transition) | `362` |
| Fallback predicate included per axis (alkali-only + 3d-transition) | `225` |
| Predeclared target per axis | `600-1500` |
| Cap per axis | `1500` |
| Selected in target | `false` (below 600) |
| Fallback in target | `false` (below 600) |

The raw candidate count (`3473`) reproduces the `TASK-0699` cap-exceeded run
exactly, confirming the same pinned snapshot. The `TASK-0737` narrowing
(2738 cation-oxide rows → 362 alkali/alkaline-earth + 3d-transition rows)
over-shot the 600-1500 target on the low side.

For scale: MD-0001 has 169 rows, so the selected 362-row slice is ~2.1x MD-0001.

## Artifacts Not Created

The following were intentionally **not** created because the count is below the
predeclared lower target:

- `data/materials/snapshots/materials_project_md0002_2026.04.13.json`
- `data/materials/md-0002-materials-project-*.yaml`
- populated value-bearing split assignments in
  `data/materials/md0002_holdout_manifest.yaml`

## Maintainer Decision Required

The `TASK-0737` contract states: "If the primary predicate returns fewer than
600 included rows per axis, do not auto-broaden in the same run. Report the
count and let the maintainer decide." Options:

1. **Accept the 362-row selected predicate.** It is a real ~2.1x widening over
   MD-0001 (169 rows), stays well under the 1500 cap, and gives a 70/15/15 split
   of roughly 253/54/54. If accepted, a follow-up acquire run commits the pinned
   snapshot, normalized combined dataset, checksums, attribution, and frozen
   holdout. (Curator-advisory: this is the pragmatic path; 362 already beats the
   MD-0001 row power that produced the split-robust formation-energy signal.)
2. **Widen the predicate** via a new planning task — e.g. add a second cation
   family (alkaline-earth + p-block, rare-earth + transition, or p-block +
   transition) to reach the 600-1500 band. Must be chosen blind, before
   inspecting values, to preserve no-peek discipline.
3. **Lower the predeclared 600 floor** (a frozen-target revision), keeping the
   1500 cap. This is a contract amendment and should be explicit.

Do not select among these by inspecting formation-energy or band-gap residuals.

## Guardrails Preserved

- `MP_API_KEY` was used only from the local environment and was not committed.
- No raw Materials Project rows, normalized MD-0002 rows, residuals, baselines,
  predictions, recommendations, `RESULT-*`, `PRED-*`, or `CLAIM-*` artifacts were
  committed.
- Formation energy and band gap remain separate planned axes.
- Inclusion used chemistry only; no value-bearing axis was inspected.

## Output Routing Summary

- Task verdict: `BELOW_TARGET_ROW_COUNT__MAINTAINER_DECISION_REQUIRED`.
- Canonical destination: this runbook result plus the committed deterministic
  count tool `scripts/acquire_md0002_materials_project.py`.
- Review tier: source/data acquisition count-check execution only.
- Gate A status: `not_attempted`; no dataset artifact was created.
- Gate B status: `not_applicable`.
- Claim impact: no claim change.
- Knowledge impact: workflow memory only; MD-0002 needs a maintainer row-count
  decision before a value-bearing acquisition.
- Publication blocker: MD-0002 remains unpublished because the narrowed predicate
  fell below the predeclared 600-row lower target.
