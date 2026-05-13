# Autonomous Nuclear Pairing Sandbox Batch 01

**Task:** `TASK-0201`
**Agent run:** `AGENT-RUN-0011`
**Status:** sandbox-only review; no claim or canonical result promotion
**Claim boundary:** advisory; this review does not authorize a third
sandbox batch in the pairing lane and does not promote either executed
candidate.

## Scope

Second nuclear sandbox batch restricted to the pairing and odd-even
residual lane. Five hypothesis proposals were generated; two were
executed and three were rejected before execution. The two executed
families test:

1. whether the parity-dependent residual after the frozen baseline
   pairing term shows a steeper A-decay than the baseline `1/sqrt(A)`
   scaling (`HYP-PROPOSAL-0038` pairing A-inverse refinement);
2. whether the structured-holdout protocol still flags a
   trivially-flexible parity-class feature stack as `OVERFITTED`
   (`HYP-PROPOSAL-0041` per-parity-class free offsets, the **in-batch
   negative control**).

The lane does not target individual shell closures or isotopic chains
identified retrospectively on the post-AME2020 holdout, and does not
allow nonlinear knobs. Such targeted features were rejected explicitly
under [../nuclear-mass-robustness-gate.md](../nuclear-mass-robustness-gate.md)
leakage and complexity rules.

## Proposals

| Proposal | Family | Status | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0038` | pairing A-inverse refinement | Executed | Bounded fixed-exponent test of pairing A-dependence. |
| `HYP-PROPOSAL-0041` | per-parity-class free offsets | Executed | In-batch negative control on a trivially-flexible feature stack. |
| `HYP-PROPOSAL-0039` | free-power asymmetry `1 / A^p` with p fitted | Rejected | Nonlinear knob on an 11-row training surface. |
| `HYP-PROPOSAL-0040` | N=82 pairing override | Rejected | Post-hoc leakage from AGENT-RUN-0008 worst-residual cluster. |
| `HYP-PROPOSAL-0042` | per-nuclide pairing override | Rejected | Row memorization; most extreme form of HYP-0031 / 0035 / 0037 leakage family. |

## Method

Deterministic batch driven by `scripts/run_nuclear_pairing_batch.py` and
recomputed by `tests/test_nuclear_pairing_batch.py`.

For each executed family:

1. NMD-0002 four-holdout cross-validation: fit linear coefficients on
   the holdout complement, evaluate on the holdout, report MAE and RMSE
   deltas vs the frozen `RESULT-0015` baseline residuals.
2. Post-AME2020 evaluation: fit linear coefficients once on the full
   NMD-0002 residual surface, then apply to the 295-row primary
   holdout. Report feature-activation counts and per-subset MAE deltas,
   adding `even_even` and `odd_odd` subsets relative to the
   neutron-rich and shell-aware lanes so per-class behavior is
   auditable.

## Structured Holdout Results

Both candidates land in `OVERFITTED` on the structured protocol.

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) |
| --- | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0038` | 1 | 3 | +0.7183 | 2.9951 |
| `HYP-PROPOSAL-0041` | 1 | 3 | +0.0992 | 0.6482 |

## Post-AME2020 Primary Results (n=295)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE | Magic-any | Near-magic | NR (>=20) | Proton-rich | Heavy | Odd-A | EE | OO |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0038` | +0.0067 | +0.0019 | +0.0129 | +0.0034 | +0.0340 | +0.0016 | +0.0000 | +0.0137 | +0.0146 |
| `HYP-PROPOSAL-0041` | +0.1673 | +0.5557 | +0.0860 | -0.0688 | +0.4683 | +0.2361 | +0.1506 | +0.0326 | +0.3329 |

Two distinct readings:

- **`HYP-PROPOSAL-0038`** (pairing A-inverse) is numerically near-null
  on the time-split surface. The fitted coefficient on full NMD-0002 is
  `c = +4.696 MeV`; per-subset deltas are all `< +0.04 MeV`; the odd-A
  subset delta rounds to `+0.0000 MeV` by construction (the feature is
  zero on odd-A rows). The lane confirms that the baseline `1/sqrt(A)`
  pairing scaling is approximately correct on the slice; an `A^-1`
  refinement adds nothing to the time-split surface.
- **`HYP-PROPOSAL-0041`** (in-batch negative control) regresses primary
  MAE by `+0.167 MeV` and regresses every subset except
  `neutron_rich_delta_ge_20` (which improves by `-0.07 MeV`, well
  inside the `AGENT-RUN-0006` 48-split envelope). The `c_oo = +4.172
  MeV` coefficient memorizes the single NMD-0002 odd-odd row (`N-14`)
  and applies it uniformly to the 71 odd-odd rows in the post-AME2020
  primary holdout, producing the `odd_odd` subset regression
  `+0.333 MeV`. This is exactly the failure mode the in-batch negative
  control is designed to expose.

## Feature Activation

| Candidate | Feature | Activation (n=295) |
| --- | --- | ---: |
| `HYP-PROPOSAL-0038` | `pairing_a_inverse` | 139 |
| `HYP-PROPOSAL-0041` | `ee_indicator` | 68 |
| `HYP-PROPOSAL-0041` | `oo_indicator` | 71 |
| `HYP-PROPOSAL-0041` | `odd_a_indicator` | 156 |

`HYP-PROPOSAL-0041`'s three counts sum to 295 by construction (each row
activates exactly one parity-class indicator). `HYP-PROPOSAL-0038` fires
on the 68 even-even plus 71 odd-odd rows (139 = 68 + 71); it is zero on
the 156 odd-A rows. Neither candidate exhibits the dormant-feature
failure mode of `AGENT-RUN-0008`.

## In-Batch Negative Control Reading

`HYP-PROPOSAL-0041` is the explicit in-batch overfit reference. Its
`OVERFITTED` structured verdict and `+0.167 MeV` primary regression
confirm:

- the protocol's overfit detection still fires in this lane;
- the failure mode is explicit and reproducible (one-row anchoring of
  `c_oo` to N-14);
- on the post-AME2020 primary holdout, the overfit shows up most
  cleanly in the `odd_odd` subset (`+0.333 MeV`), where the memorized
  `c_oo` is uniformly subtracted from 71 rows whose mean residual is
  far from `+4.17 MeV`.

## External Negative-Control Reference (HYP-PROPOSAL-0022)

From `AGENT-RUN-0008`:

- `HYP-PROPOSAL-0022` primary delta MAE: `-0.3886 MeV`
- `HYP-PROPOSAL-0038` primary delta MAE: `+0.0067 MeV` (this run)
- `HYP-PROPOSAL-0041` primary delta MAE: `+0.1673 MeV` (this run)

The pairing-lane A-inverse refinement is at machine precision and does
not approach the HYP-0022 magnitude in either direction. Combined with
the HYP-0033 quartic-asymmetry reversal from `AGENT-RUN-0010`, this
strengthens the reading that the prior HYP-0022 aggregate improvement
was a quadratic-asymmetry-shape artifact on the small training surface,
not a generic small-parameter residual improvement that any compact
correction can replicate.

## Worst-Case Residuals After Correction

The In/Sb N=82 cluster persists:

- `HYP-PROPOSAL-0038`: `Ga-84` `37.69 MeV` (baseline `37.64`),
  `In-132` `17.91 MeV`, `In-131` `17.52 MeV`. The feature is essentially
  identity on these rows (`pairing_a_inverse <= |1/A|` is tiny at heavy
  A; zero on odd-A rows).
- `HYP-PROPOSAL-0041`: `Ga-84` `33.47 MeV` (apparently improved from
  `37.64` because Ga-84 is odd-odd and `c_oo = +4.17` happens to point
  the right way), `In-131` `18.98 MeV`, `In-133` `18.04 MeV`. The
  improvement on Ga-84 is coincidental sign alignment and does not
  generalize to other In/Sb rows because most are odd-A.

## Comparison Context

- `AGENT-RUN-0006` 48-split same-shape spread: mean delta MAE
  `-0.058 MeV`, worst `+0.948 MeV`. Both pairing-lane candidates land
  well inside this envelope.
- `AGENT-RUN-0008` reference: HYP-0021 `+0.080`, HYP-0022 `-0.389`.
  Neither pairing-lane candidate approaches either magnitude.
- `AGENT-RUN-0009` shell-aware lane (HYP-0029): primary delta MAE
  `-0.062 MeV` with proton-rich regression `+0.217 MeV`. HYP-0038 is
  much smaller and lacks the one-way subset trade.
- `AGENT-RUN-0010` neutron-rich lane (HYP-0033 quartic): primary delta
  MAE `+0.563 MeV` with quartic overshoot. HYP-0038's near-null
  behavior is qualitatively similar to HYP-0034's near-orthogonal
  behavior but for a structurally different reason
  (sign-colinearity with the baseline pairing term, not
  near-orthogonality with the training residuals).

## Robustness Gate

```text
Robustness gate:
- outcome: ALLOW_ONLY_AS_NEGATIVE_CONTROL (both executed candidates)
- baseline: RESULT-0015 :: model_fitted_semi_empirical (frozen)
- active holdouts: random_stratified, oxygen_chain, magic_heavy_region,
  neutron_rich_edge (NMD-0002 structured); post-AME2020 primary (295 rows).
- split-sensitivity summary: AGENT-RUN-0006 reference; same-shape spread
  mean -0.058 MeV, worst +0.948 MeV. HYP-0038 primary delta MAE +0.007
  MeV is at machine precision; HYP-0041 primary delta MAE +0.167 MeV is
  within the regression half of the spread.
- leakage review: HYP-PROPOSAL-0040 (N=82 pairing override) and
  HYP-PROPOSAL-0042 (per-nuclide row memorization) explicitly rejected;
  HYP-PROPOSAL-0039 rejected on complexity (free-power nonlinear knob).
  Executed features are a single linear A-inverse term and three
  orthogonal one-hot parity-class indicators; neither targets a
  specific shell, chain, or nuclide.
- complexity note: HYP-PROPOSAL-0038 has 1 linear parameter;
  HYP-PROPOSAL-0041 has 3 linear parameters (parity-class indicators).
  No nonlinear knobs, no discontinuities, no magic-number switches, no
  per-row indicators.
- negative control: HYP-PROPOSAL-0041 is the in-batch negative control.
  Observed structured verdict OVERFITTED; primary regression confirms
  protocol overfit-detection symmetry. External reference comparison
  against HYP-PROPOSAL-0022 (AGENT-RUN-0008) also provided.
- post-AME2020 status: ACTIVE_RETROSPECTIVE_TIME_SPLIT. HYP-0038 is
  numerically null; HYP-0041 regresses primary by +0.167 MeV.
- limitations: sandbox-only; NMD-0002 has 11 nuclides with only one
  odd-odd row (N-14); structured holdouts OVERFITTED on both;
  retrospective time-split only; HYP-0038 is sign-colinear with the
  baseline pairing term.
```

## Decision

- `HYP-PROPOSAL-0038`: `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Useful
  diagnostic that the baseline `1/sqrt(A)` pairing scaling is
  approximately correct on the slice; an `A^-1` refinement does not
  help on the time-split surface.
- `HYP-PROPOSAL-0041`: `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. Confirms
  overfit-detection symmetry; its `c_oo = +4.17` one-row anchoring is
  the textbook in-batch overfit example for this lane.

No third pairing sandbox batch is recommended from this run alone.
Promotion is blocked.

## Limitations

- Sandbox-only. No canonical artifact is updated.
- 11-row NMD-0002 training surface with one odd-odd row dominates
  structured-holdout instability and the one-row anchoring of
  HYP-PROPOSAL-0041's `c_oo`.
- Post-AME2020 evaluation is retrospective time-split, not blind
  prediction.
- HYP-PROPOSAL-0038's sign-colinearity with the baseline pairing term
  means this lane cannot distinguish a true pairing refinement from a
  noise fit even when the post-AME2020 effect is small.
- The HYP-PROPOSAL-0041 in-batch negative control's behavior is a
  diagnostic on the protocol, not a scientific finding about pairing
  physics.
