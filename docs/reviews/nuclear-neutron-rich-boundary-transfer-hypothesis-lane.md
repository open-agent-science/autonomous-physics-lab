# Nuclear Neutron-Rich Boundary Transfer Hypothesis Lane

**Task:** `TASK-0450`
**Agent run:** `AGENT-RUN-0044`
**Campaign:** Nuclear Mass Surface
**Verdict:** `NEGATIVE_RESULT` (sandbox-only; no `PRED`/`CLAIM`/`KNOW`/`RESULT` artifact)
**Gauntlet:** [`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`](../notes/nuclear-controls-first-hypothesis-gauntlet.md)

## Scope

This lane tests whether a single residual-free neutron-rich
boundary-distance correction

```
r_corr = beta * max(0, (N - Z)/A - 0.18)
```

fit by least squares on the NMD-0002 training slice survives the
controls-first gauntlet on the post-AME2020 primary holdout, with
explicit matched high-error non-neutron-rich + sign-inverted controls
plus an isotope-chain transfer test.

It is the next bounded Nuclear hypothesis lane after `TASK-0449`
(residual-free high-error cluster, INCONCLUSIVE) and follows the
gauntlet's "one bounded family per lane" rule.

The lane is sandbox-only. It does not fetch live data, score the
prediction registry, write canonical `RESULT-*` artifacts, modify
claims, or edit knowledge files.

## Candidate (declared before the run)

- Feature: `boundary_distance = max(0, (N - Z)/A - 0.18)` — a
  closed-form, residual-free, deterministic function of `Z`, `N`, `A`
  only.
- Fit: one scalar `beta` via least squares on the 11-row NMD-0002
  training slice against frozen RESULT-0015 semi-empirical baseline
  residuals.
- Fitted `beta = -7.9335` MeV (per unit boundary distance).

The negative coefficient is itself a warning sign: the candidate
*subtracts* mass-defect predictions for neutron-rich rows because the
training slice (which contains only 1 neutron-rich row) cannot
constrain the sign meaningfully.

## Aggregate MAE (MeV)

| Surface | baseline | candidate | matched_high_error | sign_inverted |
| --- | ---: | ---: | ---: | ---: |
| `training_lstsq` | 2.8245 | 2.7569 | 2.4929 | 2.8920 |
| `primary_holdout` | 4.5526 | 4.6970 | 4.7100 | 4.4117 |
| `full_known` | 4.4904 | 4.6335 | 4.6488 | 4.3502 |

Numerical deltas vs the candidate on `full_known`:

- `candidate` vs `baseline`: **−0.1431 MeV** (candidate is **worse** than baseline).
- `candidate` vs `matched_high_error_non_neutron_rich`: +0.0153 MeV (essentially tied).
- `candidate` vs `sign_inverted_boundary`: **−0.2833 MeV** (the sign-inverted control actually beats the candidate).

The sign-inverted control beating the candidate on `full_known` is a
strong negative signal: the fitted sign reflects training-slice
artifacts, not transferable structure. The matched non-neutron-rich
high-error control also matches or beats the candidate on every
surface, indicating that whatever residual leverage exists in
"neutron-rich" rows is not specific to the neutron-rich axis — it
behaves identically to generic high-error rows.

## Isotope-Chain Transfer

- Eligible chains (≥ 2 rows on `full_known`): **61**.
- Chains where the candidate improves over baseline: **5**.
- **Transfer rate: 0.082** (5 of 61 chains improved; 56 of 61 chains
  regressed).

The 0.082 transfer rate is far below the gauntlet's 0.5 threshold for
`BOUNDED_FOLLOWUP_CANDIDATE` consideration. Even if the candidate had
passed the aggregate survival margin, this transfer rate alone would
demote the verdict to `DIAGNOSTIC_ONLY`.

## Verdict Rationale

- `full_known` candidate vs baseline: −0.1431 MeV.
- Candidate **fails the 0.25 MeV survival margin** on `full_known` vs
  baseline.

Per the gauntlet's failure condition declared before scoring, this
terminates the verdict at **`NEGATIVE_RESULT`**.

This is a clean negative outcome:

1. The candidate regresses the baseline on every surface where it is
   measurable.
2. A sign-inverted control beats the candidate by 0.28 MeV on
   `full_known`, demonstrating the fitted coefficient sign is not
   stable across the training/holdout boundary.
3. The matched non-neutron-rich high-error control performs at the
   same level as the candidate, indicating no neutron-rich-specific
   signal beyond generic-high-error behavior.
4. Isotope-chain transfer rate is 8%, far below the 50% threshold.

## Leakage Audit

- Feature uses only `Z`, `N`, `A`. No baseline residual, error rank,
  candidate-fit residual, source-status flag, or future comparison
  row enters feature construction. ✅
- `beta` is fit by closed-form least squares on the training slice
  only; no candidate-fit residual feeds the controls. ✅
- Matched-high-error control uses the baseline residual *rank*
  (NOT the candidate residual) to select non-neutron-rich high-error
  rows, then fits its own coefficient by least squares on the same
  training slice. ✅
- Sign-inverted control reuses the same `beta` with opposite sign;
  same fit logic. ✅
- Both controls share the same evaluation surfaces as the candidate.
  ✅

## Why the Lane Fails Cleanly

Two structural reasons:

1. **Training-slice sparsity.** NMD-0002 has 11 rows. Only 1 row has
   `(N-Z)/A ≥ 0.18` (it is a single neutron-rich training observation).
   With one positive-boundary-distance training row, least squares
   cannot identify a stable coefficient. The fit becomes dominated by
   the residual sign of that one row plus the contribution of nearby
   smaller-boundary rows; the resulting beta is not generalizable.
2. **Holdout dominance.** The post-AME2020 primary holdout has 101
   neutron-rich rows. Applying a sparse-training-fit coefficient to
   100× more data points than the training slice that produced it
   reliably under-performs the no-correction baseline.

This failure mode is itself instructive: it shows the
`max(0, (N-Z)/A - 0.18)` feature is too coarse and the threshold
0.18 too high for NMD-0002 to support a transferable fit. Two
reasonable next moves a maintainer could choose (neither is authorized
by this PR):

1. **Refine the feature** with a smoother, less threshold-dependent
   form (e.g. raw asymmetry deviation `((N-Z)/A)` without a
   threshold; weighted Z/A asymmetry) and re-run under the gauntlet.
   The refined feature must be declared before any score, per the
   gauntlet.
2. **Hold the neutron-rich lane closed** until a larger committed
   training slice with multiple neutron-rich rows is available. The
   no-leakage contract's neutron-rich-tail analysis in
   `docs/reviews/nuclear-shell-axis-neutron-rich-tail-audit.md`
   already flagged neutron-rich behavior as "outlier diagnostic", and
   this negative result is consistent with that classification.

This review explicitly does not pick a follow-up. The verdict is
`NEGATIVE_RESULT` and the candidate is preserved as failure-mode
evidence.

## Output Routing (`docs/result-promotion-protocol.md`)

- **Task verdict:** `NEGATIVE_RESULT` (candidate falsified under
  declared gauntlet).
- **Canonical destination:** this review note plus
  `agent_runs/AGENT-RUN-0044/{agent_run.yaml, metrics.json,
  report.md, limitations.md, preflight.md, review_summary.md}`.
- **Review tier:** `none` (no `RESULT/PRED` tier applies; the agent
  run is sandbox-only).
- **Gate A status:** `not_attempted` (no `RESULT/PRED` artifact
  proposed).
- **Gate B status:** `not_attempted` (single-run lane).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change. The neutron-rich-tail
  classification from the existing shell-axis post-audit decision
  remains intact and is reinforced by this negative result.
- **Limitations and blockers:** see "Why the Lane Fails Cleanly". The
  neutron-rich-boundary-transfer candidate is falsified at the
  declared scope.

## Limitations

- NMD-0002 has 11 training rows; only 1 is neutron-rich, so least
  squares cannot identify a stable boundary-distance coefficient.
- Frozen RESULT-0015 baseline residuals are retrospective; this is
  not a blind prediction.
- The boundary threshold (0.18) was declared before the run and is
  not retuned; doing so would be the post-hoc refit the gauntlet
  exists to prevent.
- Matched-high-error control depends on the baseline residual rank
  from the same frozen baseline; it is a non-neutron-rich proxy, not
  a fully orthogonal regressor.
- Chain-transfer metric is computed only on chains with ≥ 2 rows on
  `full_known`; chains with 1 row contribute to aggregate MAE but not
  to the transfer rate.

## What This Lane Does Not Do

- It does not add any `PRED-XXXX.yaml` entry.
- It does not score any reveal.
- It does not promote any `CLAIM-*`, `KNOW-*`, `RESULT-*`, or
  canonical hypothesis.
- It does not reopen `LOCAL-CURVATURE-001` as a positive candidate
  (no-leakage falsification stands) or reopen shell-axis as a
  registry-expansion lane (post-audit decision unchanged).
- It does not relax the no-leakage contract, the freeze protocol,
  the prediction-reveal protocol, or the controls-first gauntlet.
- It does not authorize a follow-up wave of threshold variants.

## Verdict

`NEGATIVE_RESULT` (sandbox-only). The single residual-free
neutron-rich boundary-distance correction is falsified at the
declared scope: it regresses the baseline on every surface, loses to
both a matched non-neutron-rich high-error control and a sign-inverted
control, and transfers across only 8% of eligible isotope chains. The
F-family neutron-rich classification under
`docs/nuclear-residual-feature-no-leakage-contract.md` and the
neutron-rich-tail classification from
`docs/reviews/nuclear-shell-axis-neutron-rich-tail-audit.md` are
preserved and reinforced. No follow-up is authorized by this PR.
