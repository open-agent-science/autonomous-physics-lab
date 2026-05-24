# Nuclear Asymmetry-Frontier Adversarial Stress Scout

**Agent run:** AGENT-RUN-0017  
**Task:** TASK-0289  
**Evidence class:** bounded sandbox residual scout  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_asymmetry_frontier_stress_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0017/metrics.json`

## Summary

This scout generated 9 bounded asymmetry-frontier stress candidate ideas. 6 were evaluated and 3 were rejected before execution due to overfit, row-memorization, or duplicate-search risk.

| Item | Count |
| --- | ---: |
| Generated candidates | 9 |
| Executed candidates | 6 |
| Rejected before execution | 3 |
| Near-null control preserved | yes |

Verdict counts:

| Verdict | Count |
| --- | ---: |
| `INCONCLUSIVE` | 3 |
| `OVERFITTED` | 1 |
| `PARTIALLY_VALID` | 2 |

## Candidate Outcomes

| Candidate | Feature family | Primary ΔMAE MeV | asymmetry>=0.25 ΔMAE MeV | n_z_ge_20 ΔMAE MeV | heavy_a_ge_100 ΔMAE MeV | mid_mass ΔMAE MeV | Frontier contrast MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ASYM-STRESS-001` | Positive asymmetry fraction (re-eval of NR-SCOUT-003) | -0.024320 | -0.126016 | -0.052276 | -0.010178 | -0.049755 | -0.099820 | `PARTIALLY_VALID` |
| `ASYM-STRESS-002` | Frontier excess beyond N-Z = 20 (re-eval of NR-SCOUT-004) | -0.018140 | -0.143094 | -0.046132 | -0.029664 | -0.044866 | -0.120661 | `PARTIALLY_VALID` |
| `ASYM-STRESS-003` | Quadratic+cubic neutron-excess matched pair (overfit neighbor of NR-SCOUT-005) | +1.368811 | +4.812167 | +1.970989 | +2.037928 | +1.354381 | +4.087158 | `OVERFITTED` |
| `ASYM-STRESS-004` | Sign-inverted positive asymmetry fraction (adversarial control) | +0.025314 | +0.126016 | +0.053928 | +0.011431 | +0.051258 | +0.099068 | `INCONCLUSIVE` |
| `ASYM-STRESS-005` | Clipped asymmetry above 0.25 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |
| `ASYM-STRESS-006` | Near-null asymmetry sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Negative ΔMAE means lower retrospective MAE than the frozen baseline on that subset. Positive ΔMAE means regression.

## Adversarial Controls

- `ASYM-STRESS-003` (matched quadratic+cubic): primary ΔMAE = +1.368811 MeV. Reproduces the NR-SCOUT-005 catastrophic overfit and is preserved as an OVERFITTED negative control neighbor.
- `ASYM-STRESS-004` (sign-inverted): applied coefficient on `positive_asymmetry_fraction` = -0.486943 MeV, which is the negation of ASYM-STRESS-001's fitted coefficient +0.486943 MeV.
- `ASYM-STRESS-006` (near-null control): all subset deltas are 0.0; verdict `INCONCLUSIVE`.

## Lane Recommendation

**Value:** `keep_as_review_surface`

At least one of the asymmetry-frontier candidates concentrates improvement on the high-asymmetry subset with a flat primary surface and a small worst-subset regression; the lane should remain available as a future maintainer-reviewed surface.

Evidence:

- ASYM-STRESS-001: asymmetry_ge_0_25 delta -0.126016 MeV, primary delta -0.024320 MeV, worst regression +0.000000 MeV
- ASYM-STRESS-002: asymmetry_ge_0_25 delta -0.143094 MeV, primary delta -0.018140 MeV, worst regression +0.000000 MeV

## Rejected Before Execution

- `ASYM-STRESS-007` (Free-power asymmetry exponent): Rejected before execution because a free exponent on ((N-Z)/A)^p is a nonlinear knob fitted on the 11-row NMD-0002 residual training slice with high overfit risk; mirrors the NR-SCOUT-007 rejection from the original neutron-rich lane.
- `ASYM-STRESS-008` (Per-Z asymmetry slopes): Rejected before execution because per-Z separate coefficients on an 11-row training slice memorize individual training rows and inflate degrees of freedom beyond what the bounded linear scout contract allows.
- `ASYM-STRESS-009` (Asymmetry-threshold sweep grid): Rejected before execution because sweeping separate indicators for thresholds in {0.10, 0.15, 0.20, 0.25, 0.30} adds arbitrary cutoffs and duplicates the continuous positive_asymmetry_fraction probe; mirrors the NR-SCOUT-009 rejection.

## Interpretation

Sandbox signals are sub-MeV and fitted on an 11-row residual slice. They are scout triage evidence only and are not promoted as discoveries.

`PARTIALLY_VALID` candidates: `ASYM-STRESS-001`, `ASYM-STRESS-002`. Frontier-contrast values are reported so any high-asymmetry-only gain that masks mid-mass or light regression is flagged as fragile.

`OVERFITTED` candidates: `ASYM-STRESS-003`.

## Promotion Boundary

- No prediction registry files were edited.
- No canonical result files were edited.
- No claims or knowledge files were edited.
- No claim promotion is allowed by this task.

Any future registry or reveal work must be a separate maintainer-reviewed task.
