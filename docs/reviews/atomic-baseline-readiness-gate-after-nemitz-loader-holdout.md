# Atomic Baseline Readiness Gate After Nemitz, Loader, And Holdout Work

**Task:** `TASK-0455`
**Campaign:** `atomic-clock-residuals`
**Gate verdict:** `PINNED_DATASET`

## Scope

This review reruns the Atomic baseline-readiness gate after the required
source, loader, and holdout tasks landed:

- `TASK-0452` pinned the corrected Nemitz 2016 source artifact but blocked
  value-bearing rows.
- `TASK-0453` added deterministic validation for committed real
  `direct_measurement` rows.
- `TASK-0454` defined the campaign-level holdout/no-peek manifest.
- `TASK-0485` triaged fallback second-source candidates.
- `TASK-0486` defined the first-benchmark covariance policy.

This gate does not fit drift, compare clock values, compute benchmark metrics,
create prediction entries, create `RESULT-*` artifacts, or promote claims.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` | Pinned Beloy 2021 direct rows. |
| `data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml` | Source-derived PSD covariance approximation for Beloy rows. |
| `data/atomic_clocks/atomic_holdout_manifest.yaml` | First-benchmark holdout/no-peek manifest. |
| `data/atomic_clocks/source_manifest.yaml` | Current source-family status and Nemitz blocker list. |
| `data/atomic_clocks/synthetic_cross_source_dry_run.yaml` | Fabricated cross-source fixture proving plumbing only. |
| `physics_lab/engines/atomic_clock_residuals.py` | Deterministic real direct-row and synthetic fixture loaders. |
| `docs/reviews/atomic-beloy-2021-row-readiness-recheck.md` | Prior `PINNED_DATASET` gate and blocker baseline. |
| `docs/reviews/atomic-nemitz-2016-source-artifact-and-row-readiness.md` | Nemitz source artifact pin and row blockers. |
| `docs/reviews/atomic-real-direct-row-loader-review.md` | Real-row loader review. |
| `docs/reviews/atomic-holdout-no-peek-manifest.md` | Holdout manifest review. |
| `docs/reviews/atomic-first-benchmark-covariance-policy.md` | Covariance-state policy for the first benchmark. |
| `docs/reviews/atomic-second-source-fallback-triage.md` | Fallback source ranking if Nemitz remains row-blocked. |

## Method

The gate re-evaluates each `TASK-0401` blocker and the additional
`TASK-0455` requirements using committed repository evidence only. Loader
evidence was checked deterministically with:

```text
python3 -c "from pathlib import Path; from physics_lab.engines.atomic_clock_residuals import load_atomic_clock_direct_dataset, load_atomic_clock_synthetic_cross_source_dataset; direct=load_atomic_clock_direct_dataset(Path('data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml')); synthetic=load_atomic_clock_synthetic_cross_source_dataset(Path('data/atomic_clocks/synthetic_cross_source_dry_run.yaml')); print({'direct_rows': len(direct.rows), 'direct_row_classes': direct.row_class_counts, 'direct_splits': sorted({r.split for r in direct.rows}), 'covariance_groups': direct.covariance_group_counts, 'synthetic_rows': len(synthetic.rows), 'synthetic_covariance_states': synthetic.covariance_states})"
```

The run reported three Beloy `direct_measurement` rows, all still assigned to
`holdout.split: unassigned`, all in the `bacon_2018_campaign` covariance
group, plus three synthetic cross-source dry-run rows.

## Gate Findings

### 1. Source artifact and direct-row surface - `PASS_WITH_BLOCKER`

Beloy 2021 remains a pinned direct-row seed:

- source artifact, checksum, provenance, and version-of-record cross-check are
  recorded for `ACLOCK-SRC-ARTIFACT-2021-BELOY-BACON`;
- `ACR-0001` contains three committed direct frequency-ratio rows;
- all three rows remain sandbox-only and explicitly forbid benchmark,
  drift-fitting, prediction, result, and claim promotion use.

Nemitz 2016 improves the source surface but does not clear the second-source
row gate:

- the corrected `arXiv:1601.04582` artifact is pinned with checksum and
  provenance;
- no `ACR-0002` value-bearing row exists;
- row publication remains blocked by table-level arXiv-vs-Nature review,
  campaign-window lock, and row-level uncertainty transcription.

`TASK-0485` adds a fallback plan, with Pizzocaro 2020 / INRIM Yb/Sr as the
preferred fallback if Nemitz stays blocked. It does not pin a fallback source
or clear the second-source blocker.

### 2. Deterministic real-row loader - `PASS`

`TASK-0453` clears the prior loader blocker for committed Beloy rows. The
current loader validates:

- three `direct_measurement` rows from `ACR-0001`;
- required source, uncertainty, classification, holdout, and limitation
  groups;
- real-row `source` naming as distinct from synthetic `source_metadata`;
- sandbox boundary flags that keep benchmark and promotion actions disabled.

This is a readiness check only. The loader does not authorize residual
metrics, constants-drift fits, predictions, claims, or canonical results.

### 3. Holdout/no-peek boundary - `PARTIAL_PASS_BLOCKER_FOR_SCORING`

`TASK-0454` adds a campaign-level manifest:
`data/atomic_clocks/atomic_holdout_manifest.yaml`.

The manifest defines the first-benchmark roles, including `train`,
`holdout`, `cross_source_reference`, `cross_source_target`, and `excluded`.
It also states that real scoring requires:

- row-level `holdout.split` and `holdout.freeze_manifest` fields populated
  from the manifest;
- a real-row loader for all benchmark rows;
- covariance policy for shared campaign and shared clock groups;
- a second direct source for cross-source replay.

The committed Beloy rows still carry `holdout.split: unassigned` and
`holdout.freeze_manifest: null`. That is acceptable for the current
sandbox-only dataset, but it blocks baseline scoring. No benchmark task should
consume these rows until a follow-up task assigns manifest-backed row roles
without tuning them after benchmark design.

### 4. Covariance policy - `PASS_WITH_LIMITATION`

`TASK-0486` clears the missing policy blocker by defining covariance states for
future benchmark consumers:

- `COV_EXACT_COMMITTED`;
- `COV_SOURCE_DERIVED_PSD_APPROX`;
- `COV_DIAGONAL_ONLY_DECLARED`;
- `COV_SINGLE_ROW_NO_CROSS_ROW_RISK`;
- `COV_BLOCKED_SHARED_SYSTEMATICS`.

Beloy's source-derived PSD approximation can support sensitivity-only
correlated diagnostics, not a paper-published full covariance claim. Any future
benchmark using it must report a diagonal-only comparator and label the
correlated metric as approximate. If diagonal and approximate-covariance
diagnostics disagree materially, the stricter interpretation wins.

This policy is sufficient for a future narrow benchmark design, but it does
not by itself make the current single-source rows `BASELINE_READY`.

### 5. Direct-vs-derived separation - `PASS_WITH_OPEN_FOLLOWUP`

The committed Beloy rows are correctly separated from derived constraints:

- `row_class: direct_measurement`;
- `classification.direct_measurement: true`;
- `classification.derived_constraint: false`;
- `classification.review_summary: false`;
- `classification.synthetic: false`.

Nemitz 2016 is also source-triaged as a direct optical frequency-ratio source,
but the paper's alpha-variation discussion must stay out of direct-row
ingestion. `TASK-0487` remains open as a dedicated direct-vs-derived audit for
future derived-constraint discipline. That open audit does not invalidate the
current Beloy pin, but broad residual or derived-constraint work should wait
for it.

### 6. Second-source replay risk - `BLOCKER`

The load-bearing blocker is unchanged: Atomic does not yet have a second
committed value-bearing direct-ratio source.

The current state is better than the original `TASK-0401` state because:

- the preferred Nemitz source artifact is pinned;
- source identity was corrected;
- fallback candidates are ranked;
- synthetic cross-source plumbing exists.

But none of those are equivalent to a second real row. Cross-source Yb/Sr
consistency scoring remains blocked until Nemitz rows, or a reviewed fallback
source such as Pizzocaro 2020, are committed under the same source,
uncertainty, covariance, and holdout gates.

## Classification

`PINNED_DATASET`.

Atomic is not `SOURCE_BLOCKED` because the Beloy source and rows are pinned,
the real-row loader works, covariance policy exists, a holdout manifest exists,
and the Nemitz/fallback paths are documented. The campaign still has a viable
source-curation route.

Atomic is not `BASELINE_READY` because the benchmark-scoring prerequisites are
not all satisfied:

1. no second value-bearing direct source row is committed;
2. Beloy row-level holdout splits and `freeze_manifest` fields remain
   unassigned;
3. the first cross-source benchmark cannot yet bind a real
   `cross_source_reference` row to a real `cross_source_target` row;
4. dedicated direct-vs-derived follow-up remains open for any broad
   derived-constraint or mixed-axis work.

The previous loader blocker is cleared. The previous covariance-policy blocker
is cleared at the policy level, with the explicit limitation that Beloy
covariance is source-derived and sensitivity-only.

## Recommendation

Do not start `TASK-0456` yet.

The first narrow benchmark shape should remain:

- Beloy 2021 Yb/Sr as `cross_source_reference`;
- a future committed Nemitz 2016 or Pizzocaro 2020 Yb/Sr row as
  `cross_source_target`;
- explicit manifest-backed row splits;
- covariance state declared per source family;
- diagonal-only and approximate-covariance diagnostics reported side by side
  where applicable;
- no drift fit, no constants-variation claim, no prediction entry, and no
  `RESULT-*` artifact unless a later task explicitly authorizes and gates it.

The best next Atomic work is either:

- complete `TASK-0487` so direct-vs-derived policy is explicit before any
  derived-constraint work, or
- open a new row-curation task for Nemitz 2016 or the Pizzocaro 2020 fallback
  that can actually commit the second value-bearing Yb/Sr row if source gates
  pass.

## Limitations

- This review uses committed repository evidence only; it does not fetch live
  papers, publisher pages, supplements, or external datasets.
- It does not re-check the Nature version-of-record PDFs directly; it relies
  on committed provenance and prior review notes.
- It does not assign row-level holdout splits, because doing so is a separate
  no-peek-sensitive task once a concrete first-benchmark surface is selected.
- It does not inspect or add value-bearing Nemitz or fallback rows.

## Output-Routing Summary

- **Task verdict:** `not_applicable` for a scientific claim; campaign gate
  classification is `PINNED_DATASET`.
- **Canonical destination:** this review note,
  `docs/reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact is proposed.
- **Gate A status:** not attempted.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** Atomic baseline scoring remains blocked by missing
  second real direct-source rows and unassigned row-level holdout manifest
  fields.
