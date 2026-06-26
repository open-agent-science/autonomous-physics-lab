# Stellar M-L High-Mass DEBCat Transfer Benchmark (TASK-0837)

**Task:** `TASK-0837`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Agent run:** `agent_runs/AGENT-RUN-0082/` (sandbox)
**Verdict:** `TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS` — the frozen `RESULT-0022`
mass-luminosity relation clears the predeclared survival margin over its best
control on the disjoint high-mass main-sequence holdout, while degrading
materially versus its in-domain accuracy. Sandbox evidence only; no
universal-law claim, no `RESULT-*`, no claim/knowledge promotion.
**Scope note:** dated transfer benchmark, not a live board or RESULT promotion.

## What this is

A TRANSFER test of an already-validated stellar relation. `RESULT-0022`
(Gate-B replayed) fit `log L = alpha * log M` (fixed intercept `log L0 = 0`)
on the `0.5-2.0 M_sun` main-sequence DEBCat slice and reported the train-fitted
exponent `alpha = 4.526004` as its best model. The campaign's next validity
gate is TRANSFER. The TASK-0819 transfer scout selected exactly one route: the
disjoint high-mass DEBCat regime (`mass_solar > 2.0`) inside the already
committed Route-2 rows.

This benchmark **freezes** that relation (no refit on the holdout) and scores
its predictions on the high-mass regime under controls. It does **not** edit
`RESULT-0022` or the committed DEBCat main-sequence slice. The frozen `alpha`
re-derives exactly (`4.526004`) from the committed main-sequence train lane, so
the predictor is pinned to its source; a drift guard raises if that ever stops
holding.

## Method (predeclared, controls-first, no-peek)

`scripts/run_stellar_ml_high_mass_transfer.py` runs the deterministic engine
`physics_lab/engines/stellar_ml_high_mass_transfer.py`. The survival margin and
the three controls are frozen as module constants **before** any high-mass
holdout error is read:

- Transfer regime: admitted DEBCat rows with `mass_solar > 2.0`, split by
  `system_id` (binaries never split across lanes).
- Target: `log_luminosity_solar`.
- Primary lane: high-mass **main-sequence-compatible** holdout — the
  stage-matched, apples-to-apples comparison to the `RESULT-0022` fit slice. The
  all-stage high-mass holdout is a documented secondary diagnostic because the
  high-mass regime is stage-confounded.
- Controls: per-mass-band-median **null**, deterministic luminosity **shuffle**
  (seeds 11/23/37/53/71), and a **mass-matched** per-mass-band-mean constant.
- Survival rule: the frozen relation must beat the BEST (lowest-MAE) control by
  at least the predeclared margin **and** beat every shuffle seed.
- Survival margin: **0.04 dex**, the `RESULT-0022` across-seed split-noise
  reference — a pre-existing principled threshold, not chosen by inspecting
  high-mass error.

The judge is **experimental**: DEBCat masses are direct dynamical measurements
(`mass_provenance_class: direct_observation`). The committed normalized rows are
CC BY 4.0 (Southworth grant, TASK-0763); raw `debs.dat` is not committed
(Route 2); no live fetch. The high-mass regime spans `2.005`-`27.271 M_sun`
across 121 systems (217 admitted components).

## Result — primary high-mass main-sequence holdout (24 components, 15 systems)

| Predictor / control | Holdout MAE (dex) |
| --- | ---: |
| **Frozen `RESULT-0022` relation (alpha=4.526)** | **0.334564** |
| null (mass-band median) | 0.522176 |
| mass-matched (mass-band mean) | 0.483879 |
| shuffled target (best of 5 seeds) | 1.294700 |

- Best control: mass-matched mass-band-mean, `0.483879` dex.
- Frozen relation minus best control: **`0.149315` dex** ≥ predeclared
  `0.04` → **clears**. Beats every shuffle seed (`0.335` < `1.295`).
- Transfer verdict: **`TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS`**.

## Result — secondary all-stage high-mass holdout (56 components, diagnostic)

Frozen relation MAE `0.409289` dex vs best control (mass-matched) `0.449571`
dex; margin **`0.040282` dex** — barely at the `0.04` threshold. The all-stage
margin is far tighter than the stage-matched primary lane, which is the expected
signature of the high-mass stage confound and confirms that the stage-matched
primary lane is the cleaner transfer test.

## Sensitivity (scout-required)

By luminosity provenance on the primary holdout: catalogue-reported rows
(21 rows) `0.267489` dex versus Stefan-Boltzmann-derived rows (3 rows)
`0.804088` dex — the small derived subset is noticeably worse, consistent with
the scout's provenance-mixture caveat.

By evolutionary stage on the high-mass holdout (frozen-relation MAE, dex):
main-sequence `0.334564`, evolved `0.395773`, unknown `0.519425`,
subgiant `0.643122`.

## Interpretation

The frozen main-sequence-fit slope (`alpha ≈ 4.53`) still carries real
predictive signal on the disjoint high-mass regime: on the stage-matched
holdout it beats the null, the mass-matched constant, and every luminosity
shuffle by a clear margin, so the relation **transfers under controls**. But the
transfer error (`0.335` dex) is roughly 2.8x the in-domain main-sequence holdout
MAE the same model reported in `RESULT-0022` (`0.119925` dex): the relation
**degrades** when extrapolated to higher masses. This is consistent with
standard stellar astrophysics, where the high-mass branch is shallower than the
`0.43-2 M_sun` branch whose steeper slope this `alpha` encodes.

This is a scope-extension **boundary measurement**, not a universal
mass-luminosity law, a stellar-evolution claim, or a discovery. The relation is
not refit, widened, or given extra free parameters; the honest reading is "the
`RESULT-0022` relation extends to the high-mass main-sequence regime with
control-surviving but materially degraded accuracy."

## Output-routing summary

- Task verdict: `VALID_IN_RANGE` (transfer survives controls on the
  stage-matched high-mass holdout, with degraded accuracy);
  engine verdict `TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS`.
- Canonical destination: **sandbox** — `agent_runs/AGENT-RUN-0082/` (metrics.json
  + report.md) and this review note.
- Review tier: `none`. Gate A: **not attempted** — a published `RESULT-*` would
  require hypothesis/experiment evidence links outside this benchmark task's
  authorized change surface, so the run is deliberately sandbox-only. Gate B:
  not applicable (no `RESULT-*` replay target created); the run is itself
  deterministically replayable via the pinned command, input file hashes,
  engine version, and git commit (re-running yields identical numbers).
- Transfer margin vs baseline + best control: frozen relation `0.334564` dex
  vs best control (mass-matched) `0.483879` dex → margin `0.149315` dex vs
  predeclared `0.04` (clears).
- Claim impact: `none`. Knowledge impact: `none`. `RESULT-0022` and the frozen
  DEBCat main-sequence slice are unchanged.
- Limitations: single relation; disjoint-regime holdout inside the **same**
  committed DEBCat source (a scope-extension test, not an independent external
  catalogue); stage-confounded and luminosity-provenance-mixed high-mass regime;
  small primary holdout (24 components / 15 systems); a small Stefan-Boltzmann
  luminosity subset is materially worse; not a new law.
