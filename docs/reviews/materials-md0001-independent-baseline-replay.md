# Materials MD-0001 Independent Baseline Replay

**Task:** `TASK-0578` (independent validation of `TASK-0550`)
**Benchmark:** `materials-md0001-baseline-residual-benchmark`
**Decision:** `REPRODUCED` — committed metrics reproduced exactly

## Method

Re-ran the deterministic benchmark engine from committed inputs only (no live
fetch) and compared its full output structurally against the committed
`TASK-0550` artifact:

- Engine: `physics_lab/engines/materials_md0001_baseline.py`
- Config: `examples/benchmarks/materials_md0001_baseline.yaml`
- Committed result: `agent_runs/AGENT-RUN-0057/metrics.json`
- Comparison: JSON round-trip deep-equality of the entire metrics object.

No baselines were added, no parameters tuned, no dataset widened, and no
holdout membership changed.

## Result

The fresh run equals the committed artifact **exactly** (full-object equality).
Headline figures (best holdout baseline per axis):

| Axis | Best holdout baseline | MAE | RMSE |
| --- | --- | --- | --- |
| `formation_energy_per_atom` (eV/atom) | `cation_group_mean` | 0.64603 | 0.842409 |
| `band_gap` (eV) | `cation_group_mean` | 1.247901 | 1.62569 |

Overall benchmark verdict (unchanged): `INCONCLUSIVE`. Formation energy and band
gap remain separate axes and are not pooled.

## Reproducibility guard added

`tests/test_materials_md0001_replay.py` asserts the engine output equals
`agent_runs/AGENT-RUN-0057/metrics.json`, so any future drift in the engine,
dataset, or holdout manifest fails CI rather than silently changing a published
result.

## Output Routing Summary

- Task verdict: `REPRODUCED` (validation; no new scientific claim).
- Canonical destination: this review + `tests/test_materials_md0001_replay.py`.
- Review tier: `none` (reproduces an existing benchmark; no new RESULT/PRED).
- Gate A/B: not applicable (no new metric promoted).
- Claim impact: none. Knowledge impact: none.
- Limitations / blockers: replays the existing conservative baseline only;
  computed-DFT stable binary oxides; no material-property or design claim.

## Limitations

- This confirms reproducibility, not correctness of the underlying DFT values.
- The benchmark stays `INCONCLUSIVE`; null/composition baselines are not tuned
  models and no promotion is implied.
