# Stellar M-L Alternate-Split Stability Audit (TASK-0791)

**Verdict:** `CONCLUSION_STABLE` (modest margin) — across three predeclared alternate
value-blind splits, the RESULT-0022 conclusion holds in every split: textbook α=3.5
beats the per-mass-band null but is inadequate as the sole baseline, and a train-fitted
single exponent (α≈4.5–4.6) is materially better. The fitted-vs-3.5 gap hovers just above
the 0.04 dex split-noise reference, so the inadequacy is consistent but modest. Sandbox
control audit only; no RESULT change, claim, or universal-law statement.

## Scope and inputs

- Data: committed DEBCat Route 2 rows
  (`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`), admitted
  main-sequence-compatible components in 0.5–2.0 Msun (223 components, 134 systems).
  No live fetch.
- Metric: holdout MAE in dex. Baselines compared: textbook α=3.5, train-fitted single
  α (fixed intercept), and the per-mass-band train-median null (the RESULT-0022 control).
  No new model family.

## Predeclared alternate splits (chosen before computing metrics)

Three value-blind **system-level** 70/30 splits under seeds **101, 202, 303** — distinct
from the RESULT-0022 split seeds (11, 23, 37, 53, 71). System-level keeps both components
of a binary in the same lane (no within-system leakage). Decision rule per split:
(a) does α=3.5 beat the null? (b) does the fitted single-α beat α=3.5 by more than the
0.04 dex split-noise reference?

## Result (holdout MAE, dex)

| seed | train/holdout | α=3.5 | fitted α | fitted MAE | null | α=3.5 < null | fitted < α=3.5 by > 0.04 |
|---|---|---|---|---|---|---|---|
| 101 | 159/64 | 0.1684 | 4.584 | 0.1186 | 0.3022 | yes | yes (gap 0.0498) |
| 202 | 159/64 | 0.1393 | 4.636 | 0.0974 | 0.3128 | yes | yes (gap 0.0419) |
| 303 | 160/63 | 0.1446 | 4.545 | 0.0875 | 0.2966 | yes | yes (gap 0.0571) |

## Interpretation

- **Stable direction:** in all three alternate splits α=3.5 beats the null and the fitted
  single-α beats α=3.5 by more than the split-noise reference — the same qualitative
  conclusion as RESULT-0022 (which used different seeds).
- **Stable fitted exponent:** the fitted α stays ≈4.5–4.6 across splits, consistent with
  the RESULT-0022 headline α̂≈4.53.
- **Modest margin:** the fitted-vs-3.5 gap (0.042–0.057 dex) sits just above the 0.04 dex
  reference; seed 202 is the closest (0.0419). The inadequacy of α=3.5 is consistent but
  not large, and this is preserved here rather than overstated.

## Limitations / no-claim

CC-BY-4.0 DEBCat direct-dynamical main-sequence slice only. This is a split-stability
control audit, not a universal mass-luminosity law, stellar-evolution, or
application-domain claim, and α=3.5 is **not** asserted as falsified. RESULT-0022 metrics
are unchanged; no claim is promoted.

## Reproduce

Deterministic; committed rows only; system-level 70/30 splits under seeds 101/202/303;
fixed-intercept train-fitted α; per-mass-band train-median null (global-median fallback).
