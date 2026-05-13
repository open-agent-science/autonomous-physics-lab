# Agent Run AGENT-RUN-0011 - Pairing And Odd-Even Nuclear Sandbox Batch

**Task:** `TASK-0201`
**Lane:** pairing and odd-even residual corrections
**Status:** SANDBOX_COMPLETE
**Claim boundary:** sandbox-only; no canonical result, claim, or knowledge artifact is updated.

## Scope

This batch generates five pairing or odd-even residual hypothesis proposals
(`HYP-PROPOSAL-0038` through `HYP-PROPOSAL-0042`), rejects three before
execution, and executes two:

- `HYP-PROPOSAL-0038` - odd-A residual offset
  (`r_corr = a * 1[A is odd]`).
- `HYP-PROPOSAL-0039` - even-even and odd-odd pairing-class offsets
  (`r_corr = a * 1[even-even] + b * 1[odd-odd]`).

The rejected proposals preserve the negative side of the search: a free
odd-even exponent, per-chain odd-even corrections, and pairing-by-shell
interactions were rejected before execution because they add nonlinear knobs,
leakage-sensitive chain targeting, or duplicate the shell-aware lane.

## Inputs

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml` (frozen RESULT-0015 baseline)
- `agent_runs/AGENT-RUN-0006/metrics.json` (split-sensitivity context)
- `agent_runs/AGENT-RUN-0008/metrics.json` (post-AME2020 time-split context)
- `docs/nuclear-mass-holdout-protocol.md`
- `docs/nuclear-mass-robustness-gate.md`

## Method

Deterministic. For each executed family:

1. NMD-0002 four-holdout cross-validation
   (`random_stratified`, `oxygen_chain`, `magic_heavy_region`,
   `neutron_rich_edge`): fit linear coefficients on the holdout complement,
   evaluate on the holdout, and report MAE/RMSE deltas vs the frozen baseline
   residuals.
2. Post-AME2020 evaluation: fit coefficients once on the full NMD-0002
   residual surface, then apply them to the 295-row post-AME2020 primary
   holdout. Report feature activation counts, per-subset MAE, and worst
   residual rows.

All numbers are reproducible from `scripts/run_nuclear_pairing_batch.py` and
`tests/test_nuclear_pairing_batch.py`.

## Structured Holdout Result

| Candidate | Improved | Regressed | Tied | Mean delta MAE (MeV) | Worst regression (MeV) | Structured verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `HYP-PROPOSAL-0038` | 2 | 0 | 2 | -0.2150 | 0.0000 | `PARTIALLY_VALID` |
| `HYP-PROPOSAL-0039` | 1 | 3 | 0 | +0.3142 | 1.0693 | `OVERFITTED` |

The odd-A offset passes the internal structured-holdout threshold used by the
runner, but the gate does not stop at internal splits. The post-AME2020 surface
is required before any stronger reading.

## Post-AME2020 Primary Result (295 rows)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE | Odd-A delta | Neutron-rich delta >=20 | Proton-rich delta | Heavy A>=100 delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0038` | +0.0796 | +0.1506 | +0.3887 | -0.0894 | -0.0148 |
| `HYP-PROPOSAL-0039` | +0.0876 | +0.0000 | -0.4575 | +0.5577 | +0.2508 |

Both executed candidates regress the post-AME2020 primary surface. The
pairing-class offset improves the neutron-rich subset, but this is paired with
primary, proton-rich, and heavy subset regressions. The odd-A offset improves
some internal holdouts but regresses the primary, odd-A, and neutron-rich
post-AME2020 slices.

## Feature Activation

| Candidate | Feature | Activation count on primary (n=295) |
| --- | --- | ---: |
| `HYP-PROPOSAL-0038` | `odd_a_indicator` | 156 |
| `HYP-PROPOSAL-0039` | `even_even_indicator` | 68 |
| `HYP-PROPOSAL-0039` | `odd_odd_indicator` | 71 |

The features are active on substantial portions of the primary holdout, so the
result is not a dormant-feature artifact. The failure mode is subset tradeoff
and training-slice instability.

## Robustness Gate

- outcome: `BLOCK_PROMOTION`
- baseline: frozen `RESULT-0015`, `model_fitted_semi_empirical`
- active holdouts: NMD-0002 four-holdout protocol and post-AME2020 primary holdout
- split-sensitivity summary: internal structured evidence is insufficient;
  `HYP-PROPOSAL-0038` improves internal holdouts but regresses post-AME2020
  primary
- leakage review: chain-specific and shell-interaction proposals were rejected
  before execution
- complexity note: executed candidates use one and two fitted parameters
- negative control: `HYP-PROPOSAL-0039` is an overfit control; rejected
  proposals are preserved
- post-AME2020 status: both executed candidates regress primary MAE
- limitations: sandbox-only; retrospective time-split, not blind prediction

## Verdict

`SANDBOX_PASS` for the run because the batch met the sandbox protocol and
preserved negative results. Scientific reading per candidate:

- `HYP-PROPOSAL-0038`: internally `PARTIALLY_VALID`, but blocked from follow-up
  because post-AME2020 primary and odd-A subsets regress. Gate outcome
  `BLOCK_PROMOTION`.
- `HYP-PROPOSAL-0039`: structured `OVERFITTED`; neutron-rich subset improvement
  is offset by primary, proton-rich, and heavy subset regressions. Gate outcome
  `ALLOW_ONLY_AS_NEGATIVE_CONTROL`.

No follow-up batch is recommended from this lane without a broader pinned
training surface and maintainer review.
