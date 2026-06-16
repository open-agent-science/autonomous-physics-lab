# MD-0002 Formation-Energy Benchmark — Result Routing Summary (TASK-0765)

Routing record for packaging the MD-0002 formation-energy widening retest
(`agent_runs/AGENT-RUN-0072/`) as a maintainer-gated RESULT candidate.

## Canonical destination

- Hypothesis: `hypotheses/HYP-0014-materials-md0002-formation-energy-benchmark.yaml`
- Experiment: `experiments/EXP-0014-materials-md0002-formation-energy-benchmark.yaml`
- Result: `results/EXP-0014/RUN-0001/result.yaml` (**RESULT-0021**)
- Gate A report: `results/EXP-0014/RUN-0001/gate_a_report.md`
- Source-discovery evidence (unchanged): `agent_runs/AGENT-RUN-0072/`

## Status

| dimension | state |
|---|---|
| Gate A (agent-published readiness) | **PASS** — `apl_check_result_publication.py` PASS, 9/9 gates True |
| Proposed review tier | **AGENT_PUBLISHED** (not independently validated or maintainer-reviewed) |
| Proposed verdict | **VALID_IN_RANGE** — bounded to the frozen 362-row MD-0002 slice |
| Gate B (independent validation / maintainer review) | **not performed** — deferred to maintainer |
| Claim impact | **none** — no CLAIM created or updated |
| Knowledge impact | **none** — no KNOW note created or updated |
| Publication blockers | **none** for AGENT_PUBLISHED; higher tiers need maintainer review |

## Scientific content (frozen holdout)

- Exact cation-pair mean baseline: holdout MAE **0.200606 eV/atom**.
- Global-median null: holdout MAE **0.506092 eV/atom** → **60.4%** improvement.
- Robustness: 5/5 seeded re-splits won; beats label-shuffle (min control 0.530919)
  and cation-label-shuffle (min control 0.474316) nulls in every seed; row-order
  invariant; deterministic replay reproduces the metrics within tol 1e-6.

## Framing guard-rails (held)

Computed-DFT, slice-limited reusable-dataset + conservative-baseline evidence. **Not**
a material recommendation, synthesis guide, device or biomedical claim, experimental
measurement, or new materials law. Band gap remains diagnostic-only and is excluded
from the promoted metrics.

## Reproduce

```
python3 scripts/replay_materials_md0002_result.py --check
python3 scripts/apl_check_result_publication.py results/EXP-0014/RUN-0001/result.yaml
```
