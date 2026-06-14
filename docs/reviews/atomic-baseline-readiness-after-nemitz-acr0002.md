# Atomic Baseline-Readiness Gate After Nemitz ACR-0002

**Task:** `TASK-0705`
**Campaign:** `atomic-clock-residuals`
**Mode:** planning only (scientific validation gate)
**Gate verdict:** `BASELINE_READY` for the narrow exploratory diagonal-only
Yb/Sr cross-source diagnostic; not a claim, result, or constants-drift analysis.

## Scope

This gate reruns the Atomic baseline-readiness decision after `TASK-0704`
committed the Nemitz 2016 / RIKEN `ACR-0002` direct Yb/Sr row. It uses only
committed repository artifacts and performs no cross-source metric, constants
drift fit, result publication, prediction entry, or claim promotion.

The only decision here is whether the first Atomic Yb/Sr cross-source diagnostic
task (`TASK-0456`) may proceed under the predeclared no-peek and covariance
limits.

## Evidence Reviewed

| Input | Role |
| --- | --- |
| `TASK-0704` | Confirms `TASK-0704` is `DONE`. |
| `data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml` | Committed Nemitz 2016 / RIKEN `ACR-0002-ROW-001` direct Yb/Sr row. |
| `docs/reviews/atomic-nemitz-acr0002-row-curation-gate.md` | Records the `NO_DRIFT` version-of-record check and row curation gate. |
| `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml` | Committed Beloy 2021 / BACON direct rows, including `ACR-0001-ROW-003` Yb/Sr. |
| `data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml` | Source-derived Beloy within-source covariance approximation. |
| `data/atomic_clocks/atomic_holdout_manifest.yaml` | First-benchmark no-peek split and row-role policy. |
| `data/atomic_clocks/source_manifest.yaml` | Current source-family readiness state and next-action mapping. |
| `docs/reviews/atomic-baseline-readiness-after-pizzocaro-covariance.md` | Prior gate: `PINNED_DATASET`, blocked only by the missing second Yb/Sr row. |
| `TASK-0456` | Downstream benchmark/diagnostic task contract. |

## Deterministic Loader Check

The committed direct-row loader was run locally against the Beloy and Nemitz
datasets:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from physics_lab.engines.atomic_clock_residuals import load_atomic_clock_direct_dataset; b=load_atomic_clock_direct_dataset(Path('data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml')); n=load_atomic_clock_direct_dataset(Path('data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml')); print({'beloy_rows': len(b.rows), 'beloy_splits': sorted({r.split for r in b.rows}), 'beloy_roles': sorted({r.row_role for r in b.rows}), 'beloy_covariance_groups': b.covariance_group_counts, 'nemitz_rows': len(n.rows), 'nemitz_splits': sorted({r.split for r in n.rows}), 'nemitz_roles': sorted({r.row_role for r in n.rows}), 'nemitz_covariance_groups': n.covariance_group_counts})"
```

It reported:

```text
{'beloy_rows': 3, 'beloy_splits': ['cross_source_reference', 'train'], 'beloy_roles': ['cross_source_reference', 'training_context'], 'beloy_covariance_groups': {'bacon_2018_campaign': 3}, 'nemitz_rows': 1, 'nemitz_splits': ['cross_source_target'], 'nemitz_roles': ['cross_source_target'], 'nemitz_covariance_groups': {'nemitz_2016_riken_independent': 1}}
```

This confirms that the committed loader sees:

- Beloy `ACR-0001-ROW-003` as the Yb/Sr `cross_source_reference`;
- Nemitz `ACR-0002-ROW-001` as the Yb/Sr `cross_source_target`;
- distinct covariance groups for BACON 2018 and Nemitz 2016.

## Readiness Decision

Atomic moves from `PINNED_DATASET` to `BASELINE_READY` for exactly one narrow
follow-up shape:

```text
Beloy 2021 / BACON ACR-0001-ROW-003
vs.
Nemitz 2016 / RIKEN ACR-0002-ROW-001
```

The prior load-bearing blocker was `SECOND_YB_SR_BENCHMARK_ROW_MISSING`. That
blocker is now cleared because `TASK-0704` is `DONE`, the Nemitz row is
committed, and the row is bound to the no-peek manifest as `cross_source_target`.

The readiness is deliberately narrow:

- use only committed Beloy and Nemitz rows;
- carry the independence / diagonal-only covariance banner from `ACR-0002`;
- treat the cross-source comparison as exploratory diagnostic evidence;
- report uncertainty treatment and limitations before any metric interpretation;
- do not fit constants drift, infer new physics, create predictions, or promote
  claims.

## Decision For TASK-0456

`TASK-0456` may proceed after this gate is reviewed because its explicit unblock
condition has changed: Atomic is now `BASELINE_READY` for the first exploratory
diagonal-only Yb/Sr cross-source diagnostic.

The downstream task should keep its current conservative vocabulary
(`CONSISTENT_WITHIN_UNCERTAINTY`, `INCONCLUSIVE`, or `SOURCE_LIMITED`) and must
not present the output as a canonical result unless a later maintainer-approved
Gate A publication path explicitly allows it.

## Limitations

- No benchmark metric was computed in this task.
- The Nature Photonics version-of-record for Nemitz was locally cross-checked
  but is not committed because it is not redistributable here.
- Cross-source covariance is diagonal-only by independence; this permits an
  exploratory diagnostic, not a headline consistency claim.
- The Beloy within-source covariance approximation remains source-derived and
  sandbox-only; it is relevant to Beloy multi-row combinations, not to claiming
  cross-source physics.
- `TASK-0456` must still do its own predeclared uncertainty treatment before
  computing any diagnostic metrics.

## Output-Routing Summary

- **Task verdict:** `VALID` as a readiness gate; Atomic is `BASELINE_READY` for
  the narrow exploratory diagonal-only Yb/Sr diagnostic.
- **Canonical destination:** this review note,
  `docs/reviews/atomic-baseline-readiness-after-nemitz-acr0002.md`, plus the
  `TASK-0456` status update.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact.
- **Gate A status:** not attempted. **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** campaign routing only; no knowledge entry.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** any future result publication remains blocked until
  `TASK-0456` runs deterministic diagnostics and a maintainer-approved Gate A
  path permits a tiered artifact.
