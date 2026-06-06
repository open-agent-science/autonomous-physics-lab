# Materials MD-0001 Split-Sensitivity Audit

**Task:** `TASK-0601`
**Campaign:** Materials Property Residuals
**Status:** diagnostic-only
**Verdict:** `INCONCLUSIVE`
**Run:** `agent_runs/AGENT-RUN-0066/metrics.json`

## Scope

MD-0001 has only 169 included rows per axis and a single committed 33-row holdout
(`material_id_mod10_70_10_20`). Before MD-0001 is used as the basis for wider
Materials tasks, this audit measures whether the committed formation-energy and
band-gap baseline conclusions from TASK-0550 / TASK-0578 (`AGENT-RUN-0057`) are
stable under predeclared alternative splits, or whether they depend on that
particular small holdout.

It reuses the committed TASK-0550 baseline primitives (row inclusion, the three
declared baselines `global_mean` / `global_median` / `cation_group_mean`, and the
residual metrics) so the comparison is faithful. It uses committed rows only,
keeps formation energy and band gap as separate axes, fetches no data, tunes no
split after seeing scores, and promotes no claim or materials guidance.

## Method

Predeclared alternative splits:

- `seeded_random_70_30` — five fixed-seed shuffles (`0..4`) of the included rows,
  each split 70/30 into train/holdout. This is the apples-to-apples test of
  whether the committed-split baseline ordering survives random resampling of the
  small holdout.
- `leave_one_cation_group_out` — each cation group held out once while baselines
  fit on the remaining groups (extrapolation stress test).
- `leave_one_formula_family_out` — each oxide stoichiometry (monoxide,
  sesquioxide, dioxide, ...) held out once. All MD-0001 rows are oxides, so the
  anion family is degenerate; this oxide-stoichiometry diagnostic replaces it.

Predeclared robustness rule: the committed-holdout winning baseline is
`split_robust` for an axis only if it is also the seeded mean-MAE winner with at
least `4` of `5` seed wins **and** its seeded-mean margin over the runner-up
baseline exceeds the larger of the two baselines' across-seed standard deviations
(effect larger than split noise).

## Result

### Formation energy: `split_robust`

| baseline | committed holdout MAE | seeded mean MAE | seeded std | seed wins |
| --- | ---: | ---: | ---: | ---: |
| `cation_group_mean` | `0.646030` | `0.636112` | `0.043917` | `5 / 5` |
| `global_median` | `0.967090` | `0.978580` | `0.039967` | `0 / 5` |
| `global_mean` | `1.020563` | `0.988409` | `0.036406` | `0 / 5` |

`cation_group_mean` wins every seeded holdout, and its margin over the runner-up
(`0.342468`) dwarfs the across-seed noise (`0.043917`). The conclusion does not
depend on the committed holdout. Under `leave_one_cation_group_out` the advantage
disappears (`cation_group_mean` degenerates to the global mean, macro MAE
`1.164998`), so the signal is interpolative within known cation families, not
extrapolative to unseen ones. Under `leave_one_formula_family_out` it persists
(macro MAE `0.663378`), because held-out stoichiometries still share cations with
the train set.

### Band gap: `split_sensitive`

| baseline | committed holdout MAE | seeded mean MAE | seeded std | seed wins |
| --- | ---: | ---: | ---: | ---: |
| `cation_group_mean` | `1.247901` | `1.207487` | `0.062044` | `3 / 5` |
| `global_median` | `1.349133` | `1.266347` | `0.064471` | `2 / 5` |
| `global_mean` | `1.371747` | `1.321399` | `0.071735` | `0 / 5` |

`cation_group_mean` wins the committed holdout but is the *worst* baseline on the
committed validation split. Across seeds it wins only a bare majority (`3 / 5`),
and its margin over the runner-up (`0.058860`) is smaller than the across-seed
noise (`0.064471`). The band-gap baseline ordering is not stable to the choice of
holdout, reinforcing the committed `INCONCLUSIVE` / null-grade band-gap reading.

## Conclusion

- Formation energy is a split-robust single-axis benchmark signal and is suitable
  to carry into a wider MD-0002 replication slice.
- The band-gap baseline ordering is split-fragile and should not be treated as a
  settled conclusion; its committed-split holdout "win" does not survive
  resampling.

This is a methodological robustness note about MD-0001 split stability. It does
not promote a claim, propose materials, or issue materials guidance, and it leaves
the committed split, datasets, and result artifact unchanged.

## Limitations

- Computed DFT Materials Project stable-binary-oxide rows only; with 169 rows per
  axis even the alternative splits resample the same small dataset.
- Baselines are the committed null / composition-aware controls, not tuned ML
  models; the audit tests split stability, not model quality.
- Leave-one-group-out diagnostics are extrapolation stress tests; by design
  `cation_group_mean` degenerates to the global mean when its group is fully held
  out.
- Sandbox audit evidence only. No PRED, CLAIM, KNOW, or RESULT artifact is
  created.

## Output Routing Summary

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: `agent_runs/AGENT-RUN-0066/metrics.json`,
  `agent_runs/AGENT-RUN-0066/report.md`, this review.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
