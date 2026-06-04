# AGENT-RUN-0057 - Materials MD-0001 Baseline Residual Benchmark

**Task:** `TASK-0550`
**Benchmark:** `materials-md0001-baseline-residual-benchmark`
**Verdict:** `INCONCLUSIVE`

## Scope

This run benchmarks conservative null/composition-aware baselines over the
committed `MD-0001` Materials Project stable-binary-oxides pilot. It uses only
committed rows and the committed holdout/no-peek manifest. No live external
fetch, material candidate proposal, complex ML model, prediction entry, claim,
or knowledge artifact is produced.

Formation energy and band gap are evaluated as separate axes and are never
pooled.

## Method

Input references:

- `data/materials/md-0001-materials-project-formation-energy.yaml`
- `data/materials/md-0001-materials-project-band-gap.yaml`
- `data/materials/materials_snapshot_manifest.yaml`
- `data/materials/holdout_manifest.yaml`
- `examples/benchmarks/materials_md0001_baseline.yaml`

Split policy:

- sort rows by `material_id`;
- train: `sorted_index % 10 in {0, 1, 2, 3, 4, 5, 6}`;
- validation: `sorted_index % 10 == 7`;
- holdout: `sorted_index % 10 in {8, 9}`.

Baselines:

- `global_mean`;
- `global_median`;
- `cation_group_mean` with global-mean fallback.

## Metrics

Each axis has `169` rows: `119` train, `17` validation, and `33` holdout.

### Formation Energy Per Atom

| Baseline | Validation MAE | Holdout MAE |
| --- | ---: | ---: |
| `global_mean` | 1.061136 | 1.020563 |
| `global_median` | 1.008480 | 0.967090 |
| `cation_group_mean` | 0.664637 | 0.646030 |

Best validation and holdout baseline: `cation_group_mean`.

### Band Gap

| Baseline | Validation MAE | Holdout MAE |
| --- | ---: | ---: |
| `global_mean` | 1.242556 | 1.371747 |
| `global_median` | 1.214165 | 1.349133 |
| `cation_group_mean` | 1.442530 | 1.247901 |

Best validation baseline: `global_median`.
Best holdout baseline: `cation_group_mean`.

## Interpretation

The benchmark is useful but conservative. Cation grouping is clearly useful for
formation energy on both validation and holdout. Band gap is less stable:
validation prefers the global median while holdout prefers cation grouping.
This mixed behavior should be preserved as baseline evidence, not promoted as a
materials-property law or design rule.

## Limitations

- Computed DFT rows only; no experimental measurements.
- Stable binary oxides only.
- Simple null/composition baselines only; no tuned ML model.
- No synthesis, device, biomedical, or material-design guidance.
- No `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact is promoted.

## Output Routing

- Task verdict: `INCONCLUSIVE`
- Canonical destination: `agent_runs/AGENT-RUN-0057/` plus
  `docs/reviews/materials-md0001-baseline-residual-benchmark.md`
- Review tier: `none`
- Gate A status: not attempted
- Gate B status: not applicable
- Claim impact: none
- Knowledge impact: none
