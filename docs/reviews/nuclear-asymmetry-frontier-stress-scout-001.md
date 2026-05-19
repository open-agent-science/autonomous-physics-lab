# Nuclear Asymmetry-Frontier Adversarial Stress Scout 001

**Task:** TASK-0289  
**Agent run:** `agent_runs/AGENT-RUN-0017/`  
**Script:** `scripts/run_nuclear_asymmetry_frontier_stress_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0017/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`

## Scope

This review records a sandbox-only adversarial stress scout for the nuclear
asymmetry-frontier lane. It directly re-evaluates `NR-SCOUT-003` and
`NR-SCOUT-004` from AGENT-RUN-0013 (TASK-0279), preserves `NR-SCOUT-005` as
the required `OVERFITTED` negative-control neighbor, and adds three new
adversarial controls: a sign-inverted variant of the positive asymmetry
fraction, a clipped-above-0.25 asymmetry variant, and a near-null sanity
control. It uses only repository-pinned datasets and does not fetch live
measurements. It does not edit the nuclear prediction registry or promote
claims.

## Candidate Triage

Nine candidate ideas were generated:

- Six bounded candidates were executed (two re-evals plus four adversarial
  / control variants).
- Three candidates were rejected before execution for free-exponent
  nonlinear overfit, per-Z row-memorization, and threshold-sweep
  duplicate-search risk on the 11-row NMD-0002 training slice.
- The near-null control was preserved.

| Candidate | Decision | Reason |
| --- | --- | --- |
| `ASYM-STRESS-001` | executed | re-eval of `NR-SCOUT-003` positive asymmetry fraction; single bounded linear feature |
| `ASYM-STRESS-002` | executed | re-eval of `NR-SCOUT-004` frontier excess after N-Z = 20; single bounded linear feature |
| `ASYM-STRESS-003` | executed | matched quadratic+cubic neutron-excess pair re-used from NR-SCOUT-001/-002 scalings; required OVERFITTED negative-control neighbor of NR-SCOUT-005 |
| `ASYM-STRESS-004` | executed | sign-inverted application of the positive asymmetry fraction; adversarial sign-direction control |
| `ASYM-STRESS-005` | executed | clipped asymmetry above 0.25; tests whether the asymmetry signal lives above the 0.25 threshold |
| `ASYM-STRESS-006` | executed | near-null sanity control, `r_corr = 0.0` |
| `ASYM-STRESS-007` | rejected_before_execution | free-power asymmetry exponent is a nonlinear knob on an 11-row training slice; mirrors NR-SCOUT-007 rejection |
| `ASYM-STRESS-008` | rejected_before_execution | per-Z asymmetry slopes memorize individual training rows and inflate degrees of freedom |
| `ASYM-STRESS-009` | rejected_before_execution | asymmetry-threshold sweep grid duplicates the continuous positive-asymmetry probe; mirrors NR-SCOUT-009 rejection |

## Results

| Candidate | Description | Primary ΔMAE MeV | asymmetry>=0.25 ΔMAE MeV | n_z_ge_20 ΔMAE MeV | heavy_a_ge_100 ΔMAE MeV | mid_mass ΔMAE MeV | Frontier contrast MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ASYM-STRESS-001` | positive asymmetry fraction (re-eval) | -0.024320 | -0.126016 | -0.052276 | -0.010178 | -0.049755 | -0.099820 | `PARTIALLY_VALID` |
| `ASYM-STRESS-002` | frontier excess after N-Z = 20 (re-eval) | -0.018140 | -0.143094 | -0.046132 | -0.029664 | -0.044866 | -0.120661 | `PARTIALLY_VALID` |
| `ASYM-STRESS-003` | matched quadratic+cubic pair (overfit neighbor) | +1.368811 | +4.812167 | +1.970989 | +2.037928 | +1.354381 | +4.087158 | `OVERFITTED` |
| `ASYM-STRESS-004` | sign-inverted positive asymmetry fraction | +0.025314 | +0.126016 | +0.053928 | +0.011431 | +0.051258 | +0.099068 | `INCONCLUSIVE` |
| `ASYM-STRESS-005` | clipped asymmetry above 0.25 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |
| `ASYM-STRESS-006` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Negative ΔMAE means lower retrospective MAE than the frozen baseline on
that subset. Positive ΔMAE means regression.

The frontier-contrast metric is
`asymmetry_ge_0_25_delta − 0.5 · (mid_mass_delta + light_a_lt_50_delta)`.
Negative frontier-contrast means the asymmetry frontier improves more than
the mid-mass and light subsets, i.e. the signal is concentrated at the
frontier. Positive frontier-contrast means the frontier regresses
relative to other subsets.

## Adversarial Controls

- `ASYM-STRESS-003` (matched quadratic+cubic): primary ΔMAE = +1.368811
  MeV; asymmetry>=0.25 ΔMAE = +4.812167 MeV. This reproduces the
  NR-SCOUT-005 catastrophic +1.37 MeV primary blow-up by design and is
  preserved as the required `OVERFITTED` negative-control neighbor. The
  extra cubic degree of freedom inflates the high-asymmetry surface
  relative to the linear bounded probes.
- `ASYM-STRESS-004` (sign-inverted): the runner fits the coefficient on
  training as in `ASYM-STRESS-001` and then applies the negated
  coefficient on the holdout. The applied coefficient on
  `positive_asymmetry_fraction` is `-0.486943` MeV, exactly the negation
  of `ASYM-STRESS-001`'s fitted `+0.486943` MeV. As expected, the inverted
  correction regresses every subset that `ASYM-STRESS-001` improves; the
  sign-direction signal is therefore consistent and the inverted candidate
  does not slip into an improvement that would have indicated a sign-flip
  ambiguity.
- `ASYM-STRESS-005` (clipped above 0.25): no training row has `(N-Z)/A`
  above 0.25 in the NMD-0002 residual slice (the highest training
  asymmetry is `U-238` at 0.2269). The least-squares fit therefore lands
  on a dormant column and the candidate produces exactly zero deltas on
  every subset. The clipping does not concentrate the signal above the
  threshold within this training surface; the variant is preserved as
  documented evidence that the 11-row training slice cannot resolve a
  threshold above 0.25.
- `ASYM-STRESS-006` (near-null sanity control): all deltas are 0.0;
  verdict `INCONCLUSIVE`. The fitting machinery is not injecting spurious
  signal.

## Rejections Preserved

- `ASYM-STRESS-007`, free-power asymmetry exponent: rejected as a
  nonlinear overfit knob outside the bounded linear scout contract.
- `ASYM-STRESS-008`, per-Z asymmetry slopes: rejected because per-Z
  coefficients memorize individual training rows on an 11-row slice.
- `ASYM-STRESS-009`, asymmetry-threshold sweep grid: rejected because the
  five-threshold indicator grid duplicates the continuous
  `positive_asymmetry_fraction` probe and adds arbitrary cutoffs.

## Interpretation

The asymmetry-frontier lane survives this adversarial pass in a narrow
sense:

- `ASYM-STRESS-001` and `ASYM-STRESS-002` keep the same small,
  frontier-concentrated `PARTIALLY_VALID` outcome that they had as
  `NR-SCOUT-003` and `NR-SCOUT-004` (primary ΔMAE -0.024 and -0.018 MeV,
  asymmetry>=0.25 ΔMAE -0.126 and -0.143 MeV, all subsets non-regressing
  to within numerical tolerance).
- The OVERFITTED matched quadratic+cubic neighbor and the regressing
  sign-inverted control both behave as expected.
- The clipped-above-0.25 variant cannot be resolved on the current
  training slice and contributes a useful negative result.

This is consistent with the lane-synthesis ranking in
`docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md`: the
asymmetry-frontier lane is a smaller signal than the shell-axis lane, and
its high-asymmetry concentration is real but small.

## Lane Recommendation

`keep_as_review_surface`.

Both `ASYM-STRESS-001` and `ASYM-STRESS-002` show
`asymmetry_ge_0_25_delta < -0.02 MeV` with primary ΔMAE within ±0.05 MeV
and worst-subset regression at 0.0 MeV. The frontier-concentrated
improvement is small but consistent and adversarially robust within this
bounded sandbox. The lane should remain available as a future
maintainer-reviewed surface, scoped strictly to the high-asymmetry
frontier. It is not promoted into registry or reveal work by this scout.

## Limitations

- Retrospective committed post-AME2020 rows are used only as a stress surface.
- Coefficients are fitted on an 11-row residual slice, and no training row crosses `(N-Z)/A` = 0.25, so the clipped-above-0.25 variant fits a dormant column.
- `ASYM-STRESS-003` reproduces the NR-SCOUT-005 catastrophic blow-up by design and is preserved as an `OVERFITTED` negative control rather than a discovery candidate.
- The `asymmetry_ge_0_25` subset is small relative to the primary holdout, so concentrated deltas should be read as scout-grade triage signal rather than a precise effect size.
- No prediction registry entries are created or updated.
- No canonical results, claims, or knowledge entries are promoted.

## Verdict

`REVIEW_READY` as sandbox evidence. The asymmetry-frontier lane is
preserved as a future review surface (`keep_as_review_surface`) but is
explicitly not promoted as a discovery. Any future registry, reveal, or
RESULT-* work must come from a separate maintainer-reviewed task.
