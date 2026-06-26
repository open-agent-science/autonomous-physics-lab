# AGENT-RUN-0082 - Stellar M-L High-Mass DEBCat Transfer Benchmark

**Task:** `TASK-0837`
**Benchmark:** `stellar-ml-high-mass-debcat-transfer`
**Verdict:** `TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS`

## Scope

Transfer benchmark of the **frozen** RESULT-0022 stellar mass-luminosity
relation `log L = alpha * log M (fixed intercept log L0 = 0)` with the main-sequence train-fitted exponent
`alpha = 4.526004`. The relation is evaluated BY TRANSFER on the
disjoint high-mass DEBCat regime (`mass_solar > 2.0`) chosen by the TASK-0819
transfer scout. The exponent is **not** refit on the high-mass holdout, and
neither RESULT-0022 nor the committed DEBCat main-sequence slice is edited.
The frozen alpha re-derives exactly from the committed main-sequence train lane
(`4.526004`), pinning the predictor to its source.

The judge is **experimental**: DEBCat masses are direct dynamical measurements
(`mass_provenance_class: direct_observation`). The high-mass regime spans
`2.0049`-`27.2709` M_sun across `121` systems
(`217` admitted components). It is stage-confounded
(components by stage: evolved 73, main_sequence_compatible 92, subgiant 11, unknown 41) and luminosity-provenance-mixed
(by luminosity source: debcat_catalogue_reported_logL 187, stefan_boltzmann_from_debcat_logR_logT 30), so the PRIMARY lane is the stage-matched
high-mass main-sequence-compatible holdout (apples-to-apples with the RESULT-0022
fit slice); the all-stage high-mass holdout is a documented secondary diagnostic.

## Predeclared contract (frozen before reading holdout error)

- Transfer regime: `mass_solar > 2.0`, split by `system_id` (no binary-component leakage).
- Target: `log_luminosity_solar`; primary stage lane: `main_sequence_compatible`.
- Survival margin: **0.04 dex** (RESULT-0022 across-seed split-noise reference (0.04 dex)).
- Controls: per-mass-band median **null**, deterministic luminosity **shuffle** (seeds [11, 23, 37, 53, 71]), and a **mass-matched** per-mass-band-mean constant.
- Survival rule: the frozen relation must beat the BEST (lowest-MAE) control by the margin AND beat every shuffle seed.

## Primary high-mass main-sequence holdout

Holdout: `24` components / `15` systems (train `43`).

| Predictor / control | Holdout MAE (dex) |
| --- | ---: |
| **Frozen RESULT-0022 relation (alpha=4.526004)** | **0.334564** |
| null (mass-band median) | 0.522176 |
| mass-matched (mass-band mean) | 0.483879 |
| shuffled target (best of 5 seeds) | 1.294700 |

- Best control: `mass_matched_massband_mean` at `0.483879` dex.
- Frozen relation minus best control: **0.149315 dex** vs predeclared margin `0.04` -> clears: **True**.
- Beats every shuffle seed: **True**.

## Secondary all-stage high-mass holdout (diagnostic)

Holdout: `56` components / `32` systems.
Frozen relation MAE `0.409289` dex vs best control `mass_matched_massband_mean` `0.449571` dex; margin `0.040282` dex; clears: `True`. The all-stage margin is materially tighter than the primary lane, which is the expected
 signature of the high-mass stage confound and motivates the stage-matched primary choice.

## Sensitivity (scout-required)

Luminosity provenance on the primary holdout:
- `debcat_catalogue_reported_logL`: `21` rows, MAE `0.267489` dex.
- `stefan_boltzmann_from_debcat_logR_logT`: `3` rows, MAE `0.804088` dex.

By evolutionary stage on the high-mass holdout (frozen relation MAE, dex):

| stage | holdout MAE (dex) |
| --- | ---: |
| main_sequence_compatible | 0.334564 |
| subgiant | 0.643122 |
| evolved | 0.395773 |
| unknown | 0.519425 |

## Interpretation

On the stage-matched high-mass main-sequence holdout, the frozen RESULT-0022 relation (MAE `0.334564` dex) clears the predeclared survival margin over the best control and beats every shuffle seed, so it **transfers to the high-mass regime under controls**.

The transfer error is markedly larger than the in-domain main-sequence holdout MAE
RESULT-0022 reported for the same model (`0.119925` dex), so the relation **degrades**
on transfer to higher masses while still carrying predictive signal beyond the controls.
This is a scope-extension boundary measurement, not a universal mass-luminosity law,
a stellar-evolution claim, or a discovery.

## Output-routing summary

- Task verdict: `TRANSFERS_TO_HIGH_MASS_UNDER_CONTROLS` (transfers to high mass: `True`).
- Canonical destination: SANDBOX - `agent_runs/AGENT-RUN-0082/metrics.json`, this report, and `docs/reviews/stellar-ml-high-mass-debcat-transfer-benchmark.md`.
- Review tier: `none`. Gate A: not attempted (sandbox; a published RESULT needs hypothesis/experiment evidence links outside this task's scope). Gate B: not applicable (no RESULT replay target created); the run is itself deterministically replayable via the pinned command + input hashes + engine version + git commit.
- Transfer MAE (primary high-mass holdout): `0.334564` dex vs best control `mass_matched_massband_mean` `0.483879` dex (margin `0.149315` dex; predeclared `0.04`; clears: `True`).
- Claim impact: `none`. Knowledge impact: `none`.
- Limitations: single relation; disjoint-regime (same-source) holdout, not an independent external catalogue; stage-confounded and luminosity-provenance-mixed high-mass regime; small primary holdout (`24` components); not a new law.
