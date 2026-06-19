# Materials MD-0002 Descriptor-Ablation Control Audit (TASK-0790)

**Verdict:** `DESCRIPTOR_AUDIT_RUN` — a single predeclared descriptor-granularity
ablation (coarse cation-**group** mean vs exact cation-**pair** mean vs null) was run on
the frozen MD-0002 formation-energy split. The RESULT-0021 advantage is specific to the
**exact cation-pair** granularity; coarsening the composition descriptor to the cation
group removes essentially all of it. Control/sandbox memory only — no RESULT, claim, or
materials-design statement.

## Scope and inputs

- Data: committed `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`,
  formation-energy rows, **frozen** train/holdout split (train 253 / holdout 54). No live
  fetch, no row changes, same primary metric as RESULT-0021 (holdout MAE, eV/atom).
- Engine: the existing frozen TASK-0703 benchmark engine
  (`physics_lab/engines/materials_md0002_baseline.py`), which already fits the global,
  cation-group, and cation-pair baselines deterministically.

## Predeclared ablation (one family, chosen before reading metrics)

**Composition-descriptor granularity.** Hold the model class fixed (group-mean lookup)
and vary only the grouping descriptor: exact unordered non-oxygen cation **pair** (the
RESULT-0021 baseline) vs the coarser cation **group/family**, against the global-median
null and global-mean references. No new descriptor search; no multi-feature factory.

## Result (frozen holdout, eV/atom)

| baseline | grouping granularity | holdout MAE |
|---|---|---|
| global-median null | none | 0.506092 |
| global mean | none | 0.525992 |
| **cation-group mean** | coarse (element family) | **0.525992** |
| **cation-pair mean** (RESULT-0021) | exact pair | **0.200606** |

The cation-group (coarse) baseline lands at 0.525992 — **identical to the global mean**
and slightly worse than the global-median null. Only the exact-cation-pair granularity
(0.200606) captures the formation-energy signal.

## Interpretation

The RESULT-0021 cation-pair advantage is a **descriptor-granularity effect localized at
the exact cation pair**: a coarse element-family grouping adds no lift over the global
baseline. Combined with the TASK-0789 preflight (the cation-pair baseline does not
transfer to unseen pairs), the consistent picture is that the baseline captures
exact-pair-local structure (memorization of seen pairs), not a coarse, transferable
composition trend. This is exactly the kind of control memory that should precede any
descriptor-modeling task.

## Limitations / no-claim

Computed-DFT MD-0002 stable ternary-oxide slice; frozen split only. This is a bounded
control ablation, not a material recommendation, synthesis guidance, experimental
validation, materials-discovery, or new-law statement, and it does not describe any
result as material-design knowledge. RESULT-0021 is unchanged; no new RESULT is created.

## Reproduce

```
python3 -c "from physics_lab.engines.materials_md0002_baseline import run_materials_md0002_formation_energy_benchmark as r, DEFAULT_CONFIG as c; m=r(c); b=m['baseline_summaries']; print({k: b[k]['metrics']['holdout']['mae'] for k in ('global_mean','global_median','cation_group_mean','cation_pair_mean')})"
```
