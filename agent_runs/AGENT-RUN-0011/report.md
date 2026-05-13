# Agent Run AGENT-RUN-0011 - Pairing And Odd-Even Nuclear Sandbox Batch

**Task:** `TASK-0201`
**Lane:** pairing and odd-even residual corrections (second nuclear sandbox batch)
**Status:** SANDBOX_COMPLETE
**Claim boundary:** sandbox-only; no canonical result, claim, or knowledge artifact is updated.

## Scope

This batch generates five pairing-lane residual hypothesis proposals
(`HYP-PROPOSAL-0038` through `HYP-PROPOSAL-0042`), rejects three before
execution, and executes two:

- `HYP-PROPOSAL-0038` — pairing A-inverse residual refinement
  (`r_corr = c * pairing_sign(Z, N) / A`). Tests whether the parity-dependent
  residual after the frozen baseline shows a steeper A-decay than the
  baseline `1/sqrt(A)` pairing term.
- `HYP-PROPOSAL-0041` — per-parity-class free offsets
  (`r_corr = c_ee * I[ee] + c_oo * I[oo] + c_oA * I[odd-A]`). Included
  explicitly as the **in-batch negative control**: three free per-class
  offsets fitted on 8-9 training rows (with exactly one odd-odd row in
  NMD-0002, N-14) is a trivially-flexible feature stack whose expected
  `OVERFITTED` verdict confirms the protocol's overfit detection is still
  active in this lane.

The lane does not target individual shell closures or isotopic chains
identified retrospectively on the post-AME2020 holdout, and does not allow
nonlinear knobs. Such proposals were rejected explicitly under
[../../docs/nuclear-mass-robustness-gate.md](../../docs/nuclear-mass-robustness-gate.md)
leakage and complexity rules.

## Inputs

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml` (frozen RESULT-0015 baseline)
- `agent_runs/AGENT-RUN-0006/metrics.json` (split-sensitivity context)
- `agent_runs/AGENT-RUN-0008/metrics.json` (post-AME2020 time-split context, including the external HYP-PROPOSAL-0022 negative-control reference)

## Method

Deterministic. For each executed family:

1. NMD-0002 four-holdout cross-validation
   (`random_stratified`, `oxygen_chain`, `magic_heavy_region`,
   `neutron_rich_edge`): fit linear coefficients on the holdout complement,
   evaluate on the holdout, report per-holdout MAE and RMSE deltas vs the
   frozen baseline residuals.
2. Post-AME2020 evaluation: fit linear coefficients once on the full
   NMD-0002 residual surface, then apply to the 295-row post-AME2020
   primary holdout. Report feature-activation counts, per-subset MAE
   (`primary`, `magic_any`, `near_magic`, `neutron_rich_delta_ge_20`,
   `proton_rich_n_lt_z`, `heavy_a_ge_100`, `odd_a`, `even_even`,
   `odd_odd`), and the top 10 absolute residuals.

All numbers are reproducible from `scripts/run_nuclear_pairing_batch.py`
and the recomputation test `tests/test_nuclear_pairing_batch.py`.

## Structured Holdout Result

| Candidate | Improved | Regressed | Mean delta MAE (MeV) | Worst regression (MeV) | Structured verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `HYP-PROPOSAL-0038` | 1 | 3 | +0.7183 | 2.9951 | `OVERFITTED` |
| `HYP-PROPOSAL-0041` | 1 | 3 | +0.0992 | 0.6482 | `OVERFITTED` |

Both candidates fail the structured protocol. For `HYP-PROPOSAL-0038`, the
`random_stratified` per-complement fit produces `c = -35.26` while the
other three holdouts yield coefficients in the `+4.2` to `+4.6` range —
an extreme swing driven by removing He-4 plus two other rows from an
11-row training surface. For `HYP-PROPOSAL-0041`, the three per-class
fits oscillate in the `c_ee` and `c_oA` coefficients across holdouts
because the single odd-odd row (`N-14`) anchors `c_oo` at `+4.172` MeV
regardless of which holdout is active.

## Post-AME2020 Primary Result (n=295)

Baseline primary MAE: `4.5526 MeV`.

| Candidate | Primary delta MAE | Magic-any | Near-magic | NR (>=20) | Proton-rich | Heavy | Odd-A | Even-even | Odd-odd |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HYP-PROPOSAL-0038` | +0.0067 | +0.0019 | +0.0129 | +0.0034 | +0.0340 | +0.0016 | +0.0000 | +0.0137 | +0.0146 |
| `HYP-PROPOSAL-0041` | +0.1673 | +0.5557 | +0.0860 | -0.0688 | +0.4683 | +0.2361 | +0.1506 | +0.0326 | +0.3329 |

Two distinct readings:

- **`HYP-PROPOSAL-0038`** (pairing A-inverse) is **numerically near-null**
  on the time-split surface. The fitted coefficient on full NMD-0002 is
  `c = +4.696 MeV`, but the feature value `pairing_sign(Z, N) / A` is
  small at heavy A and zero on the 156 odd-A rows in the primary
  holdout. Per-subset deltas are all in the `< +0.04 MeV` range, and the
  odd-A subset delta rounds to `+0.0000 MeV` by construction. This is
  the expected outcome when the baseline `1/sqrt(A)` pairing term
  already captures the parity-dependent structure on the slice; the
  A-inverse refinement adds essentially nothing.
- **`HYP-PROPOSAL-0041`** (in-batch negative control) regresses primary
  MAE by `+0.167 MeV` and regresses every subset except
  `neutron_rich_delta_ge_20` (which improves by `-0.07 MeV` — a small
  consolation that is itself well within the same-shape split-sensitivity
  envelope from `AGENT-RUN-0006`). The odd-odd coefficient (`c_oo =
  +4.172 MeV`) memorizes the single `N-14` row in NMD-0002 and applies
  it uniformly to the 71 odd-odd rows in the post-AME2020 primary
  holdout (`odd_odd` subset delta `+0.333 MeV`), exactly the failure
  mode the in-batch negative control is designed to expose.

## Feature Activation

| Candidate | Feature | Activation count on primary (n=295) |
| --- | --- | ---: |
| `HYP-PROPOSAL-0038` | `pairing_a_inverse` | 139 |
| `HYP-PROPOSAL-0041` | `ee_indicator` | 68 |
| `HYP-PROPOSAL-0041` | `oo_indicator` | 71 |
| `HYP-PROPOSAL-0041` | `odd_a_indicator` | 156 |

For `HYP-PROPOSAL-0038`, the 139 activations correspond to the 68
even-even plus 71 odd-odd rows in the primary holdout; the feature is
zero on the 156 odd-A rows by construction (`pairing_sign = 0`). For
`HYP-PROPOSAL-0041`, each primary row activates exactly one indicator;
the three activation counts sum to 295 as required by construction.
Neither candidate exhibits the dormant-feature failure mode of
`AGENT-RUN-0008`.

## In-Batch Negative Control Reading

`HYP-PROPOSAL-0041` is the explicit in-batch negative control. Its
`OVERFITTED` structured verdict and `+0.167 MeV` primary regression
confirm:

- the protocol's overfit detection fires on a trivially-flexible feature
  stack in this lane;
- the failure mode is explicit and reproducible (one-row anchoring of
  `c_oo`);
- on the post-AME2020 primary holdout, the overfit is not catastrophic
  in aggregate (`+0.17 MeV` vs the baseline `4.55 MeV` aggregate MAE) but
  is clearly visible in the per-subset breakdown (most subsets regress).

The diagnostic value of the lane comes from `HYP-PROPOSAL-0041`, not
from `HYP-PROPOSAL-0038`. `HYP-PROPOSAL-0038`'s near-null behavior is
itself a finding: the lane confirms that the frozen baseline
`1/sqrt(A)` pairing scaling is approximately correct on the available
training surface, with no parity-dependent residual structure large
enough to drive an `A^-1` refinement away from zero on the time-split
surface.

## External Negative-Control Reference (HYP-PROPOSAL-0022)

From `AGENT-RUN-0008` on the same post-AME2020 primary surface:

- `HYP-PROPOSAL-0022` (`r_corr = a * I + b * I^2`) primary delta MAE:
  `-0.3886 MeV`
- `HYP-PROPOSAL-0038` (this run) primary delta MAE: `+0.0067 MeV`
- `HYP-PROPOSAL-0041` (this run) primary delta MAE: `+0.1673 MeV`

Reading: the pairing-lane A-inverse refinement does not approach the
prior `HYP-PROPOSAL-0022` aggregate magnitude in either direction; this
strengthens the reading from `AGENT-RUN-0010` (`HYP-PROPOSAL-0033`
quartic-asymmetry reversal) that the `HYP-PROPOSAL-0022` win was a
quadratic-asymmetry-shape artifact, not a generic small-parameter
residual improvement that any compact correction can replicate.

## Worst-Case Residuals After Correction

The In/Sb N=82 cluster persists. Top three absolute residuals:

- `HYP-PROPOSAL-0038`: `Ga-84` (`37.69 MeV` vs baseline `37.64`),
  `In-132` (`17.91 MeV`), `In-131` (`17.52 MeV`).
- `HYP-PROPOSAL-0041`: `Ga-84` (`33.47 MeV`; reduced from baseline
  `37.64` only because the odd-odd `c_oo = +4.17` correction subtracts
  by chance from the Ga-84 residual which is also odd-odd), `In-131`
  (`18.98 MeV`), `In-133` (`18.04 MeV`).

For `HYP-PROPOSAL-0038`, the candidate is essentially identity on the
worst-case rows: `Ga-84` has `pairing_a_inverse = -1/84 = -0.0119` and
`In-131` has `pairing_a_inverse = 0` (odd-A), so the candidate cannot
touch these rows materially. For `HYP-PROPOSAL-0041`, the apparent
`Ga-84` improvement (`-4.23 MeV`) is a coincidental sign alignment
between the fitted `c_oo` and the Ga-84 odd-odd residual; it does **not**
generalize to the other In/Sb rows because most of them are odd-A.

## Comparison With Prior Evidence

- `AGENT-RUN-0006` 48-split same-shape spread (HYP-PROPOSAL-0021): mean
  delta MAE `-0.058 MeV`, worst `+0.948 MeV`. Both pairing-lane
  candidates land well inside this envelope; HYP-PROPOSAL-0038
  (`+0.007`) is at machine precision and HYP-PROPOSAL-0041 (`+0.167`) is
  within the regression half of the spread.
- `AGENT-RUN-0008` reference: HYP-PROPOSAL-0021 `+0.080`,
  HYP-PROPOSAL-0022 `-0.389`. Pairing-lane candidates do not approach
  either magnitude.
- `AGENT-RUN-0009` shell-aware lane: HYP-PROPOSAL-0029 (continuous
  shell-proximity, N-only) primary delta MAE `-0.062 MeV` with
  `+0.217 MeV` proton-rich regression. HYP-PROPOSAL-0038 is smaller in
  magnitude and lacks the one-way subset trade.
- `AGENT-RUN-0010` neutron-rich lane: HYP-PROPOSAL-0033 (quartic
  asymmetry) primary delta MAE `+0.563 MeV`; HYP-PROPOSAL-0034
  (asymmetric neutron-excess) `~0 MeV` at floating-point noise. The
  pairing-lane HYP-PROPOSAL-0038's near-null result is qualitatively
  similar to HYP-PROPOSAL-0034 but for a structurally different reason
  (sign-colinearity with the baseline pairing term, not
  near-orthogonality with the training residuals).

## Verdict

`SANDBOX_PASS` for the run (sandbox protocol satisfied, no canonical
artifact changed). Scientific reading per candidate:

- `HYP-PROPOSAL-0038`: structured `OVERFITTED`; post-AME2020 primary
  effect is numerically near-null (`+0.007 MeV`). Gate outcome
  `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. The lane delivers a useful
  diagnostic: the baseline `1/sqrt(A)` pairing scaling is approximately
  correct on the available training surface; an A-inverse refinement
  cannot improve the time-split surface.
- `HYP-PROPOSAL-0041`: structured `OVERFITTED`; post-AME2020 primary
  regression `+0.167 MeV` with per-class memorization of the single
  N-14 odd-odd row. Gate outcome `ALLOW_ONLY_AS_NEGATIVE_CONTROL`. The
  candidate's diagnostic value is the demonstration that the
  structured-holdout protocol still flags trivially-flexible feature
  stacks in this lane.

No follow-up batch is recommended from this run. The pairing lane has
delivered the expected diagnostic value: the baseline pairing term is
approximately correct on the slice, and the in-batch negative control
confirms protocol symmetry.
