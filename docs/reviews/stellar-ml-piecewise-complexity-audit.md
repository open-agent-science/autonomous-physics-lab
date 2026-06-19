# Stellar M-L Piecewise-vs-Single-Alpha Complexity Audit (TASK-0792)

**Verdict:** `PIECEWISE_NOT_JUSTIFIED` — under a predeclared physical breakpoint and a
fixed complexity penalty, a two-segment piecewise exponent improves the frozen-holdout
MAE by only 0.004 dex over the single train-fitted exponent, far below the 0.04 dex
penalty threshold. The single fitted-α (≈4.53) remains the parsimonious model; the extra
segment is not warranted. The audit is admissible (breakpoint chosen on physical grounds,
not from holdout performance). Sandbox control memory only; no RESULT change, claim, or
stellar-evolution statement.

## Scope and inputs

- Data: committed DEBCat Route 2 rows
  (`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`), admitted
  main-sequence-compatible components in 0.5–2.0 Msun, **frozen** lane (train 102 /
  holdout 65). No live fetch; same scope flags and metric (holdout MAE, dex) as RESULT-0022.

## Predeclared design (chosen before computing metrics)

- **Piecewise split axis (one):** a single mass breakpoint at **M = 1 Msun**
  (log₁₀M = 0) — a physical regime boundary, **not** selected from holdout performance.
  Two segments (M < 1, M ≥ 1), each a fixed-intercept train-fitted exponent.
- **Complexity penalty / selection rule (one):** the piecewise model (2 fitted exponents)
  is preferred over the single fitted exponent (1 exponent) **only if** it lowers the
  frozen-holdout MAE by more than the **0.04 dex** split-noise reference. Otherwise the
  single fitted exponent wins by parsimony.

Admissibility: the breakpoint is fixed a priori (no holdout tuning) and there is no broad
hyperparameter search, so the audit is admissible (not `PIECEWISE_AUDIT_NOT_ADMISSIBLE`).

## Result (frozen holdout, dex)

| model | parameters | holdout MAE |
|---|---|---|
| single textbook α=3.5 | 0 fit | 0.184954 |
| **single fitted α = 4.526** | 1 | **0.119925** |
| **piecewise (α_low=4.83, α_high=4.43 @ M=1)** | 2 | **0.115737** |
| per-mass-band null | — | 0.331817 |

- Piecewise gain over the single fitted exponent: **0.004188 dex** — well under the
  0.04 dex penalty threshold.
- Train split at the breakpoint: 26 components (M<1) / 76 (M≥1).

## Interpretation

A single fitted exponent already captures the main-sequence M–L trend on this slice; the
two-segment refinement buys a noise-level 0.004 dex and does not survive a modest
complexity penalty. This reinforces RESULT-0022's reading — textbook α=3.5 is inadequate
and a single fitted α≈4.5 is the right *simple* model — and shows that adding piecewise
structure is **not** justified here. No new model family or broad search is opened.

## Limitations / no-claim

CC-BY-4.0 DEBCat direct-dynamical main-sequence slice only. A piecewise fit here is a
descriptive baseline, **not** stellar-evolution theory; α=3.5 is not asserted as falsified
and no universal mass-luminosity law is claimed. RESULT-0022 is unchanged; no claim is
promoted.

## Reproduce

Deterministic; committed rows only; fixed breakpoint log₁₀M = 0; fixed-intercept
least-squares α per segment; frozen train/holdout lane.
