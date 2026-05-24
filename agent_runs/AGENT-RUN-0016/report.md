# Nuclear Shell-Axis Adversarial Stress Scout

**Agent run:** AGENT-RUN-0016  
**Task:** TASK-0288  
**Evidence class:** bounded sandbox residual scout  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_shell_axis_stress_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0016/metrics.json`

## Summary

This stress scout generated 9 adversarial shell-axis candidate ideas. 6 were evaluated and 3 were rejected before execution due to overfit, degree-of-freedom inflation, or duplicate-search risk.

| Item | Count |
| --- | ---: |
| Generated candidates | 9 |
| Executed candidates | 6 |
| Rejected before execution | 3 |
| Near-null control preserved | yes |

Verdict counts:

| Verdict | Count |
| --- | ---: |
| `INCONCLUSIVE` | 2 |
| `PARTIALLY_VALID` | 4 |

## Candidate Outcomes

| Candidate | Feature family | Primary ΔMAE MeV | Magic Z ΔMAE MeV | Magic N ΔMAE MeV | Heavy A>=100 ΔMAE MeV | Chain-neighbor ΔMAE MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `STRESS-SHELL-001` | Proton-axis Gaussian shell proximity (re-eval of SHELL-SCOUT-003) | -0.091504 | -0.387579 | -0.291542 | -0.087801 | -0.824735 | `PARTIALLY_VALID` |
| `STRESS-SHELL-002` | Proton x neutron product shell proximity (re-eval of SHELL-SCOUT-005) | -0.071641 | -0.015759 | -0.411085 | -0.089679 | -0.382745 | `PARTIALLY_VALID` |
| `STRESS-SHELL-003` | Neutron-axis Gaussian shell proximity overlap diagnostic (re-eval of SHELL-SCOUT-002) | -0.061969 | -0.014413 | -0.591750 | +0.019771 | -0.611142 | `PARTIALLY_VALID` |
| `STRESS-SHELL-004` | Sign-inverted proton-axis Gaussian adversarial control | +0.127005 | +0.670711 | +0.352300 | +0.108097 | +0.824735 | `INCONCLUSIVE` |
| `STRESS-SHELL-005` | Shuffled proton-axis Gaussian control (cyclic-shift-5) | -0.000060 | -0.000247 | -0.000216 | -0.000050 | -0.000603 | `PARTIALLY_VALID` |
| `STRESS-SHELL-006` | Near-null shell-axis sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Frontier and additional subset deltas:

| Candidate | Mid-mass ΔMAE MeV | Light A<50 ΔMAE MeV | Heavy A>=100 ΔMAE MeV | Frontier contrast MeV | Neutron-rich (N-Z)/A>=0.25 ΔMAE MeV |
| --- | ---: | ---: | ---: | ---: | ---: |
| `STRESS-SHELL-001` | -0.178553 | +0.181030 | -0.087801 | -0.225167 | -0.357017 |
| `STRESS-SHELL-002` | -0.124308 | +0.172426 | -0.089679 | -0.165681 | -0.229458 |
| `STRESS-SHELL-003` | -0.217785 | +0.347373 | +0.019771 | -0.401357 | -0.276888 |
| `STRESS-SHELL-004` | +0.224739 | -0.099556 | +0.108097 | +0.220468 | +0.357017 |
| `STRESS-SHELL-005` | -0.000160 | +0.000356 | -0.000050 | -0.000313 | -0.000326 |
| `STRESS-SHELL-006` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |

Negative deltas mean lower retrospective MAE than the frozen baseline on that subset. Positive deltas mean regression.

## Repeated-Target Pressure

Overrepresented registry targets and whether they appear in the holdout:

| Target | Z | A | Registry entry count | In holdout |
| --- | ---: | ---: | ---: | --- |
| `Ni-76` | 28 | 76 | 18 | no |
| `Ca-55` | 20 | 55 | 14 | no |
| `Ga-85` | 31 | 85 | 14 | no |
| `Zn-80` | 30 | 80 | 14 | no |

Chain-neighbor holdout rows (same Z, |A - registry_A| <= 2):

| Nuclide | Z | N | A | Registry target |
| --- | ---: | ---: | ---: | --- |
| `Ca-54` | 20 | 34 | 54 | `Ca-55` |
| `Ga-83` | 31 | 52 | 83 | `Ga-85` |
| `Ga-84` | 31 | 53 | 84 | `Ga-85` |
| `Ni-74` | 28 | 46 | 74 | `Ni-76` |
| `Ni-75` | 28 | 47 | 75 | `Ni-76` |
| `Zn-79` | 30 | 49 | 79 | `Zn-80` |

## Rejected Before Execution

- `STRESS-SHELL-007` (Free-sigma proton Gaussian): Rejected before execution because tuning sigma on an 11-row NMD-0002 residual slice adds a nonlinear free knob with high overfit risk and duplicates the fixed-sigma proton-axis probe STRESS-SHELL-001.
- `STRESS-SHELL-008` (Per-magic-number offsets): Rejected before execution because one coefficient per element of {2,8,20,28,50,82,126} introduces 7 free coefficients on an 11-row residual training slice, which inflates degrees of freedom and memorizes training shell-cluster rows.
- `STRESS-SHELL-009` (SHELL-SCOUT-001 additive form re-test): Rejected before execution because SHELL-SCOUT-001 (beta_z*s_z2 + beta_n*s_n2) is already documented as OVERFITTED in docs/reviews/nuclear-scout-lane-synthesis-after-pred-0062.md, so re-running it would be duplicate-search rather than adversarial stress.

## Interpretation

Sandbox signals are sub-MeV and fitted on an 11-row residual slice. They are scout-triage evidence only and are not promoted as discoveries.

`PARTIALLY_VALID` candidates: `STRESS-SHELL-001`, `STRESS-SHELL-002`, `STRESS-SHELL-003`, `STRESS-SHELL-005`.

`INCONCLUSIVE` candidates: `STRESS-SHELL-004`, `STRESS-SHELL-006`.

## Promotion Boundary

- No prediction registry files were edited.
- No canonical result files were edited.
- No claims or knowledge files were edited.
- No claim promotion is allowed by this task.

Any future registry or reveal work must be a separate maintainer-reviewed task.
