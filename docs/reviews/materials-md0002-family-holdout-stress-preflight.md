# Materials MD-0002 Family-Holdout Stress Preflight (TASK-0789)

**Verdict:** `STRESS_SPLIT_READY` — a disjoint cation-pair family-holdout is feasible
on the committed MD-0002 formation-energy slice, and the preflight already shows the
RESULT-0021 cation-pair baseline does **not** transfer across unseen cation-pair
families (it collapses to the global-mean baseline). This is a control/preflight
diagnostic only; no RESULT, claim, or materials-design statement is made.

## Scope and inputs

- Data: committed `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`,
  formation-energy rows only (`property_kind: formation_energy_per_atom`,
  `inclusion_status: included`). No live fetch; no row or holdout mutation.
- Metadata used: `cations` (the unordered non-oxygen cation pair). Single axis only.

## Family-holdout axis (predeclared, one axis)

**Cation-pair family** — hold out *entire* unordered non-oxygen cation pairs so the
train and holdout lanes share **no** cation pair. This directly stresses whether any
baseline transfers to compositions whose cation pair was never seen in training,
rather than memorizing per-pair means.

- Distinct cation pairs: **89** across **362** rows (16 singleton pairs with 1 row; 60 pairs with ≥3 rows).
- Deterministic split (`random.Random(0)`, 30% of pairs held out): **27 / 89** pairs → **train 243 / holdout 119** rows.
- Leakage: **none by construction** — train/holdout cation pairs are disjoint.

## Declared row-count floor (before any future metric run)

- Floor: holdout ≥ 40 rows AND ≥ 10 held-out pairs.
- Observed: holdout 119 rows / 27 pairs → **floor met**.

## Baselines on the disjoint-pair holdout (preflight)

| baseline | holdout MAE (eV/atom) | note |
|---|---|---|
| global-median null | 0.653596 | reference |
| cation-pair mean (RESULT-0021 model) | 0.636977 | **every holdout pair is unseen → falls back to the global train mean for all rows** |

For comparison, on the standard frozen split the same cation-pair baseline reaches
0.200606 (RESULT-0021). The gap is the point: the cation-pair baseline's standard-split
advantage is **memorization of seen pairs**, not generalization — under a disjoint-pair
family-holdout it provides essentially no lift over the null (0.637 vs 0.654).

## Recommendation

- The split is ready, so a later metric task *could* run it — but the preflight is
  already conclusive for the existing baseline: a pair-mean (lookup) model cannot
  transfer to unseen cation pairs. A future family-holdout metric task is only worth
  opening for a **genuinely transfer-capable descriptor** (e.g. element-property
  features), not for the pair-mean baseline, and would need its own task authorization.
- No descriptor search, RESULT, or claim is opened here.

## Limitations / no-claim

Computed-DFT MD-0002 stable ternary-oxide slice only. This is a split-feasibility and
control preflight, not a material recommendation, synthesis guidance, experimental
validation, materials-discovery, or universal-law statement. RESULT-0021 is unchanged.

## Reproduce

Deterministic; uses only committed rows (group by sorted non-O `cations`, 30%-of-pairs
holdout under `random.Random(0)`, global-median null and global-train-mean fallback).
