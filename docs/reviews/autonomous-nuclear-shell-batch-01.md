# Autonomous Nuclear Shell-Aware Sandbox Batch 01

**Task:** `TASK-0200`
**Agent run:** `AGENT-RUN-0009`
**Status:** sandbox-only review; no claim or canonical result promotion
**Claim boundary:** advisory; this review does not authorize a third
sandbox batch in the shell lane and does not promote either executed
candidate.

## Scope

This review summarizes the second nuclear sandbox batch, restricted to the
shell-aware residual lane. Five hypothesis proposals were generated; two
were executed and three were rejected before execution. The two executed
families test whether a continuous Gaussian shell-proximity feature can
overcome the dormant-feature failure mode of `HYP-PROPOSAL-0020` and
`HYP-PROPOSAL-0021` reported in
[post-ame2020-time-split-benchmark-result.md](./post-ame2020-time-split-benchmark-result.md)
and `AGENT-RUN-0008`.

The lane intentionally does not target individual shell closures or any
particular post-AME2020 worst-residual cluster. Such targeted features were
rejected explicitly under
[../nuclear-mass-robustness-gate.md](../nuclear-mass-robustness-gate.md)
leakage rules.

## Proposals

| Proposal | Family | Status | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0028` | continuous Gaussian shell-proximity (Z+N) | Executed | Two-parameter linear extension of the strict shell motivation; features fire on every row. |
| `HYP-PROPOSAL-0029` | continuous Gaussian shell-proximity (N only) | Executed | One-parameter minimal variant; tests whether the neutron axis carries the shell signal alone. |
| `HYP-PROPOSAL-0030` | near-magic binary indicator (both axes) | Rejected | Coarse step-function approximation of HYP-0028; adds no interpretive value. |
| `HYP-PROPOSAL-0031` | N=82 targeted switch | Rejected | Post-hoc leakage from the AGENT-RUN-0008 worst-residual cluster. |
| `HYP-PROPOSAL-0032` | multiplicative shell-proximity with free sigma | Rejected | Nonlinear knob on an 11-row training surface; high overfit risk and no separable Z vs N reading. |

## Method

Deterministic batch driven by `scripts/run_nuclear_shell_batch.py` and
recomputed by `tests/test_nuclear_shell_batch.py`. For each executed family:

1. NMD-0002 four-holdout cross-validation: fit coefficients on the holdout
   complement, evaluate on the holdout, report MAE and RMSE deltas vs the
   frozen `RESULT-0015` baseline residuals.
2. Post-AME2020 evaluation: fit coefficients once on the full NMD-0002
   residual surface, then apply to the 295-row primary holdout. Report
   feature-activation counts and per-subset MAE deltas.

The shell-proximity feature is
`s_x = exp(-d(x, MAGIC)^2 / (2 * sigma^2))` with `sigma = 2` and
`MAGIC = (2, 8, 20, 28, 50, 82, 126)`. `sigma` is frozen at design time.

## Structured Holdout Results

Both candidates land in `OVERFITTED` on the structured protocol because the
worst regression on any holdout exceeds `1.0 MeV`.

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) |
| --- | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0028` | 1 | 3 | +1.5701 | 2.9166 |
| `HYP-PROPOSAL-0029` | 3 | 1 | +0.2957 | 1.6508 |

This is expected on an 11-row training slice where each holdout
complement has 8-9 rows. The structured protocol is a useful upper bound on
overfit; both candidates fail it.

## Post-AME2020 Primary Results (n=295)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE | Magic-any | Near-magic | Neutron-rich | Proton-rich | Heavy A>=100 | Odd-A |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0028` | +0.0467 | -0.2590 | +0.1133 | -0.0847 | +0.2585 | +0.1921 | -0.0226 |
| `HYP-PROPOSAL-0029` | -0.0620 | -0.3993 | -0.1693 | -0.1702 | +0.2174 | +0.0198 | -0.1076 |

Two readings:

- The Z+N candidate regresses primary MAE because the Z-axis term pulls in
  the wrong direction on near-magic-Z light/medium rows (`proton_rich`
  regresses by `+0.26 MeV`, `near_magic` by `+0.11 MeV`).
- The N-only candidate improves primary MAE marginally by improving
  `magic_any` (`-0.40 MeV` on `n = 18`), `near_magic` (`-0.17 MeV`),
  `neutron_rich` (`-0.17 MeV`), and `odd_a` (`-0.11 MeV`), at the cost of
  `proton_rich` regression (`+0.22 MeV` on `n = 28`).

This is the same one-way subset trade pattern observed in
`HYP-PROPOSAL-0022`. The aggregate improvement is smaller and the
sandbox-only reading is identical: a residual family that absorbs
neutron-rich baseline-shape bias is not a discovered correction.

## Feature Activation

| Candidate | s_z_gauss | s_n_gauss |
| --- | ---: | ---: |
| `HYP-PROPOSAL-0028` | 295 | 295 |
| `HYP-PROPOSAL-0029` | n/a | 295 |

Both features fire on every primary post-AME2020 row. This addresses the
core failure mode documented in `AGENT-RUN-0008`: the strict
`magic_both` / `heavy_double_magic` features in HYP-0020 and HYP-0021 fire
0 times on this surface and therefore cannot test the shell hypothesis.
The shell-aware lane has fixed that specific problem; what remains is
structured-holdout instability and proton-rich subset regression.

## Comparison With Prior Evidence

- `AGENT-RUN-0006` 48-split same-shape spread for `HYP-PROPOSAL-0021`:
  mean delta MAE `-0.058 MeV`, worst `+0.948 MeV`. The N-only candidate's
  primary delta MAE (`-0.062 MeV`) is essentially at the centre of that
  spread and inside its envelope, so the time-split result is not
  out-of-spread evidence.
- `AGENT-RUN-0008` post-AME2020 reference:
  `HYP-PROPOSAL-0021` primary delta MAE `+0.080 MeV`,
  `HYP-PROPOSAL-0022` primary delta MAE `-0.389 MeV`. The N-only candidate
  improves primary by `1/6` of the negative-control improvement.

## Worst-Case Residuals After Correction

The In/Sb N=82 cluster persists. For `HYP-PROPOSAL-0029` the top three
absolute residuals on the primary holdout are `Ga-84` (`37.12 MeV`),
`In-134` (`16.64 MeV`), and `In-132` (`16.46 MeV`). The symmetric
shell-proximity feature gives `s_n = 0.32` for `Ga-84` and roughly
`0.32-0.88` for the indium chain near N=82, but the residuals do not
collapse because the candidate's coefficient is constrained by neutron-rich
training rows that pull in the wrong direction for these specific shell
closures.

## Robustness Gate

Following `docs/nuclear-mass-robustness-gate.md`:

```text
Robustness gate:
- outcome: ALLOW_ONLY_AS_NEGATIVE_CONTROL (both executed candidates)
- baseline: RESULT-0015 :: model_fitted_semi_empirical (frozen)
- active holdouts: random_stratified, oxygen_chain, magic_heavy_region,
  neutron_rich_edge (NMD-0002 structured); post-AME2020 primary (295 rows).
- split-sensitivity summary: AGENT-RUN-0006 reference; same-shape spread
  mean -0.058 MeV, worst +0.948 MeV. N-only candidate primary delta MAE
  -0.062 MeV is inside this envelope.
- leakage review: HYP-PROPOSAL-0031 explicitly rejected for targeting the
  AGENT-RUN-0008 N=82 worst-residual cluster. Executed candidates use
  symmetric magic-number proximity with sigma frozen at design time.
- complexity note: HYP-PROPOSAL-0028 has 2 linear parameters and
  HYP-PROPOSAL-0029 has 1 linear parameter; sigma is frozen. No
  discontinuities, magic-number switches, or piecewise behavior.
- negative control: comparison against HYP-PROPOSAL-0022 (prior overfit /
  negative control). The N-only candidate exhibits the same proton-rich
  regression direction but a much smaller aggregate improvement.
- post-AME2020 status: ACTIVE_RETROSPECTIVE_TIME_SPLIT. HYP-0028 regresses
  primary; HYP-0029 marginally improves primary with proton-rich subset
  regression.
- limitations: sandbox-only; NMD-0002 has 11 nuclides; structured holdouts
  are OVERFITTED on both candidates; retrospective time-split evaluation
  only.
```

## Decision

- `HYP-PROPOSAL-0028`: `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Failure on the
  structured holdouts plus post-AME2020 primary regression places it
  squarely as negative evidence. Keep for diagnostic comparison against
  future shell-aware proposals.
- `HYP-PROPOSAL-0029`: `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Marginal primary
  improvement does not satisfy the gate's stability requirements; one-way
  subset trade and structured-protocol failure remain visible.

No third shell-aware sandbox batch is recommended from this run alone.
Promotion is blocked.

## Limitations

- Sandbox-only. No canonical artifact is updated.
- 11-row NMD-0002 training surface is the dominant source of
  structured-holdout instability.
- Post-AME2020 evaluation is retrospective time-split, not blind
  prediction.
- The two executed candidates are linear in their features; the rejected
  proposals would have introduced nonlinear knobs (`HYP-PROPOSAL-0032`) or
  retrospective features (`HYP-PROPOSAL-0031`), which is why they were
  rejected before execution.
