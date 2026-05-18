# Nuclear Mid-Mass And Isotope-Chain Gap Scout

**Agent run:** AGENT-RUN-0015  
**Task:** TASK-0286  
**Evidence class:** bounded sandbox residual scout  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_midmass_isotope_gap_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0015/metrics.json`

## Summary

This scout generated 8 bounded mid-mass and isotope-chain candidate ideas. 5 were evaluated and 3 were rejected before execution due to row-memorization, degree-of-freedom inflation, or duplicate-search risk.

| Item | Count |
| --- | ---: |
| Generated candidates | 8 |
| Executed candidates | 5 |
| Rejected before execution | 3 |
| Near-null control preserved | yes |

Verdict counts:

| Verdict | Count |
| --- | ---: |
| `INCONCLUSIVE` | 1 |
| `OVERFITTED` | 4 |

## Candidate Outcomes

| Candidate | Feature family | Primary delta MAE MeV | Mid-mass delta MAE MeV | Light delta MAE MeV | Heavy delta MAE MeV | Frontier contrast MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `MIDMASS-SCOUT-001` | Mid-mass Gaussian peak (sigma 20, center A=100) | +0.372488 | +0.569391 | -0.011737 | -0.011416 | +0.580967 | `OVERFITTED` |
| `MIDMASS-SCOUT-002` | Mid-mass indicator times asymmetry | +0.796498 | +1.204959 | +0.000000 | +0.000000 | +1.204959 | `OVERFITTED` |
| `MIDMASS-SCOUT-003` | Isotope-chain slope, N minus per-Z median N | +18.639764 | +13.203721 | +4.731626 | +34.619944 | -6.472064 | `OVERFITTED` |
| `MIDMASS-SCOUT-004` | Mid-mass shell-distance Gaussian fall-off | +0.256400 | +0.387888 | +0.000000 | +0.000000 | +0.387888 | `OVERFITTED` |
| `MIDMASS-SCOUT-005` | Near-null mid-mass sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Isotope-chain deltas (small subsets, fragile):

| Candidate | Z=20 delta MAE MeV | Z=28 delta MAE MeV | Z=50 delta MAE MeV |
| --- | ---: | ---: | ---: |
| `MIDMASS-SCOUT-001` | +0.066016 | +0.552516 | +2.007636 |
| `MIDMASS-SCOUT-002` | +1.301361 | +1.785661 | +0.292400 |
| `MIDMASS-SCOUT-003` | -1.873882 | +4.810704 | +6.791602 |
| `MIDMASS-SCOUT-004` | +0.000000 | +3.055241 | +5.241494 |
| `MIDMASS-SCOUT-005` | +0.000000 | +0.000000 | +0.000000 |

Negative deltas mean lower retrospective MAE than the frozen baseline on that subset. Positive deltas mean regression.

## Rejected Before Execution

- `MIDMASS-SCOUT-006` (Per-Z fitted intercepts): Rejected before execution because per-Z intercepts on an 11-row NMD-0002 training slice memorize individual rows rather than test a bounded mid-mass or isotope-chain residual feature.
- `MIDMASS-SCOUT-007` (A-binned 8-bin step function): Rejected before execution because an 8-bin A-step function inflates degrees of freedom relative to the 11-row residual training slice and would be a row-memorizing overfit risk.
- `MIDMASS-SCOUT-008` (Free sigma in mid-mass Gaussian): Rejected before execution because tuning sigma adds a nonlinear free knob on an 11-row residual slice and duplicates the fixed-sigma continuous probe MIDMASS-SCOUT-001.

## Interpretation

Sandbox signals are sub-MeV and fitted on an 11-row residual slice. They are scout triage evidence only and are not promoted as discoveries.

No candidate reached `PARTIALLY_VALID`. The lane preserves negative and null evidence rather than promoting a signal.

`OVERFITTED` candidates: `MIDMASS-SCOUT-001`, `MIDMASS-SCOUT-002`, `MIDMASS-SCOUT-003`, `MIDMASS-SCOUT-004`.

## Promotion Boundary

- No prediction registry files were edited.
- No canonical result files were edited.
- No claims or knowledge files were edited.
- No claim promotion is allowed by this task.

Any future registry or reveal work must be a separate maintainer-reviewed task.
