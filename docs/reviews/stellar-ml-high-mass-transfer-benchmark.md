# Stellar M-L High-Mass DEBCat Transfer Benchmark

Task: `TASK-0837`
Sandbox run: `agent_runs/AGENT-RUN-0085/`
Related result: `RESULT-0022` (`AGENT_VALIDATED`)
Verdict: **TRANSFER_NOT_SUPPORTED_BEST_CONTROL**

## Scope

This benchmark tests whether the frozen `RESULT-0022` best relation transfers
from its validated 0.5-2.0 M_sun main-sequence-compatible slice onto the disjoint
high-mass DEBCat Route 2 regime (`mass_solar > 2.0`). It uses only committed
DEBCat rows, performs no live source fetch, and does not edit `RESULT-0022`.

The transfer slice intentionally keeps all high-mass stage flags in the primary
benchmark and reports stage/provenance strata separately. This follows the scout
warning that the high-mass route is useful but stage-confounded.

## Result

- Frozen relation: `log10(L/L_sun) = 4.526004 * log10(M/M_sun)`.
- High-mass holdout: `56`
  rows across `32`
  systems.
- Frozen relation holdout MAE: `0.409289` dex.
- Best control: `mass_matched_high_mass_train_nearest` at
  `0.306352` dex.
- Survival margin: `-0.102937` dex
  (best control minus relation), threshold
  `0.02` dex.
- Decision: `TRANSFER_NOT_SUPPORTED_BEST_CONTROL`.

The frozen relation beats the null and shuffled controls, but it does **not**
beat the nearest-mass high-mass train-lane control. Therefore this run records an
honest high-mass transfer boundary rather than promoting a new canonical result.

## Controls

- `null_high_mass_train_massband_median`: mass-band median luminosity from the
  high-mass train lane.
- `shuffled_relation_predictions`: frozen RESULT-0022 predictions shuffled across
  high-mass holdout rows, preserving prediction distribution but breaking row
  pairing.
- `mass_matched_high_mass_train_nearest`: nearest high-mass train row by
  `log_mass_solar`; predicts that row's observed luminosity.

## Gate-B Replayability

- Command: `python3 scripts/run_stellar_ml_high_mass_transfer.py --output-dir agent_runs/AGENT-RUN-0085 --review-note docs/reviews/stellar-ml-high-mass-transfer-benchmark.md`
- Code reference: `scripts/run_stellar_ml_high_mass_transfer.py`
- Inputs: committed DEBCat rows, `RESULT-0022`, the transfer scout note, and the
  Gate-B replay note; hashes are recorded in
  `agent_runs/AGENT-RUN-0085/metrics.json`.
- Engine version: `0.1.0`.

## Output Routing Summary

- Canonical destination: sandbox `AGENT-RUN-0085` plus this review note.
- Gate A: not attempted; relation failed the best-control survival margin.
- Gate B: replay metadata recorded.
- RESULT impact: no `RESULT-*` artifact created.
- Claim impact: none.
- Knowledge impact: none.
- Limitation: same committed DEBCat source posture; this is a disjoint-regime
  transfer test, not an external-catalog validation or a universal-law claim.
