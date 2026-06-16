# RESULT-0022 — Stellar M-L DEBCat Controlled Baseline Benchmark

- **Experiment:** EXP-0015 · **Run:** RUN-0001 · **Hypothesis:** HYP-0015 · **Task:** TASK-0764
- **Review tier:** AGENT_PUBLISHED (agent-published; not independently validated or maintainer-reviewed)
- **Verdict:** VALID_IN_RANGE — scope-limited to the frozen DEBCat main-sequence slice

## Headline (the TASK-0762 lesson, preserved)

On the frozen DEBCat main-sequence slice (0.5–2.0 Msun), the textbook single
mass-luminosity exponent **α=3.5 beats the null but is _not_ the adequate sole
baseline**: a train-fitted exponent (α̂≈4.53) and the textbook piecewise mid-mass
exponent α=4.0 reduce holdout residuals materially further. **This does not falsify
α=3.5 as a textbook relation** — it shows α=3.5 alone is an inadequate frozen
baseline on this scoped slice. No universal mass-luminosity law or stellar-evolution
claim is made.

## Scope and framing

A **controlled benchmark / dataset evaluation**, not a discovery, universal law, or
application-domain claim. Stage restriction, null + shuffle controls, seeded
split-sensitivity, and baseline-adequacy are all predeclared.

## Data

- Rows: `data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`;
  holdout manifest: `…/debcat_holdout_manifest.yaml`.
- Source / license: DEBCat (Southworth 2015, ASP Conf. Ser. 496, 164), **CC BY 4.0**
  by explicit maintainer grant (TASK-0763); declared in `data/DATA_LICENSES.yaml`.
  Direct dynamical masses; raw `debs.dat` not committed (Route 2); no live fetch.
- Slice: admitted main-sequence-compatible components, 0.5–2.0 Msun → **223**
  components, frozen value-blind system-level split **train 102 / val 56 / holdout 65**.
- Evolved / subgiant / unknown stages are **diagnostics only**.

## Frozen-holdout result

| baseline | holdout MAE (dex) | vs single 3.5 |
|---|---|---|
| train-fitted α̂=4.526 | **0.119925** | −0.065029 |
| textbook piecewise α=4.0 | 0.137608 | −0.047346 |
| textbook single α=3.5 | 0.184954 | 0.0 |
| per-mass-band median null | 0.331817 | — |

The single-3.5 → fitted gap (0.065 dex) and single-3.5 → piecewise gap (0.047 dex)
both exceed the **0.04 dex** split-noise reference ⇒ single α=3.5 is **inadequate**
as the sole baseline.

## Controls (predeclared)

- **Deterministic replay** — `python3 scripts/replay_stellar_ml_result.py --check`
  recomputes all baselines, split-sensitivity, and shuffle margins from committed
  data and matches within tol `1e-6` → `GATE_A_REPLAY: PASS`.
- **Split sensitivity** — null-minus-formula holdout margin positive in **5/5**
  seeded system-level (no-leakage) re-splits (0.102–0.180 dex).
- **Shuffle control** — real margin 0.146863 dex exceeds **every** seed of the
  deterministic luminosity-shuffle null (all shuffled margins negative).
- **Stage confound (diagnostic)** — by-stage holdout formula MAE: main-sequence
  0.185, subgiant 0.308, evolved 1.709, unknown 0.238 dex; the evolved confound
  motivates the main-sequence restriction.

## Interpretation

Within this slice the M–L power-law _form_ is well supported (every power-law
baseline beats the null and survives the shuffle/split controls), but the textbook
_constant_ α=3.5 is not the best frozen exponent; α≈4.0–4.5 fits the
direct-dynamical main-sequence data better. The fitted/piecewise baselines remain
simple power laws with ~0.12 dex residual; they are reference baselines, not
predictive stellar models.

## Reproduce

```
python3 scripts/replay_stellar_ml_result.py --check
```

Source-discovery evidence (stage-control/split: `agent_runs/AGENT-RUN-0073/`;
baseline-adequacy: `agent_runs/AGENT-RUN-0074/`).
