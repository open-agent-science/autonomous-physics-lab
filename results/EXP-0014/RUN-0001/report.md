# RESULT-0021 — Materials MD-0002 Formation-Energy Cation-Pair Baseline Benchmark

- **Experiment:** EXP-0014 · **Run:** RUN-0001 · **Hypothesis:** HYP-0014 · **Task:** TASK-0765
- **Review tier:** AGENT_PUBLISHED (agent-published; not independently validated or maintainer-reviewed)
- **Verdict:** VALID_IN_RANGE — scope-limited to the frozen MD-0002 stable ternary-oxide slice

## Scope and framing

This is a **benchmark / dataset evaluation**, not a materials-discovery, design, or
universal-law claim. It characterizes how much a simple composition-aware baseline
reduces formation-energy residuals on the checksum-pinned, holdout-frozen MD-0002
stable ternary-oxide slice (alkali / alkaline-earth + first-row transition), and how
robust that reduction is to predeclared controls.

## Data

- Dataset: `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`
  (sha256 `516ed06f…81b1d1`; Materials Project snapshot `2026.04.13`,
  checksum `5bfb3e7f…349567`).
- Source / license: The Materials Project, **CC BY 4.0**, declared in
  `data/DATA_LICENSES.yaml`; provenance class **computed DFT** (not experimental).
- 724 rows total; 362 included formation-energy rows; frozen 70/15/15 split by
  `material_id` ordering → train 253 / validation 55 / holdout 54. No live fetch.
- Band gap is **diagnostic-only** and excluded from the promoted metrics.

## Models

| model | description | complexity |
|---|---|---|
| `model_cation_pair_mean` | train-mean formation energy per unordered non-O cation pair (global train-mean fallback) | 2 |
| `model_global_median_null` | train-lane global median formation energy | 1 |

## Frozen-holdout result

| metric | cation-pair | null (global median) |
|---|---|---|
| holdout MAE (eV/atom) | **0.200606** | 0.506092 |
| holdout RMSE (eV/atom) | 0.297225 | 0.583126 |

Absolute improvement **0.305485 eV/atom** (**60.4%** lower MAE than the null).

## Controls (predeclared)

- **Deterministic replay** — `python3 scripts/replay_materials_md0002_result.py --check`
  recomputes both baselines from committed data and matches the committed metrics
  within tol `1e-6` → `GATE_A_REPLAY: PASS`. Canonical and reversed-input runs are
  identical (row-order invariant).
- **Split sensitivity** — across 5 seeded 70/30 re-splits the cation-pair baseline is
  the lowest-MAE baseline in **5/5** seeds (holdout MAE 0.172–0.216), while null
  baselines stay near 0.51–0.56.
- **Shuffle controls** — the real cation-pair holdout MAE (0.200606) beats **every**
  seed of both the label-shuffle null (min control 0.530919) and the
  cation-label-shuffle null (min control 0.474316).

## Interpretation

Within the frozen MD-0002 slice, composition identity (the cation pair) carries most
of the explainable formation-energy signal a memorization-class baseline can capture,
and the advantage is not an artifact of split luck or label structure. The cation-pair
baseline is a **reference baseline**, not a predictive materials model: it has no
per-structure features and does not extrapolate beyond seen cation pairs. No
materials-discovery or universal-law statement is made.

## Reproduce

```
python3 scripts/replay_materials_md0002_result.py --check
```

Source-discovery evidence (controls, split sensitivity, shuffle nulls):
`agent_runs/AGENT-RUN-0072/`.
