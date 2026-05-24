# Nuclear Neutron-Rich Variant Scout

**Agent run:** AGENT-RUN-0013  
**Task:** TASK-0279  
**Evidence class:** bounded sandbox residual scout  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_neutron_rich_variant_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0013/metrics.json`

## Summary

This scout generated nine bounded neutron-rich, neutron-excess, asymmetry, or
frontier-residual candidate ideas. Six were evaluated and three were rejected
before execution due to leakage, duplicate-search, or overfit risk.

| Item | Count |
| --- | ---: |
| Generated candidates | 9 |
| Executed candidates | 6 |
| Rejected before execution | 3 |
| Near-null control preserved | yes |

Verdict counts:

| Verdict | Count |
| --- | ---: |
| `PARTIALLY_VALID` | 2 |
| `INCONCLUSIVE` | 3 |
| `OVERFITTED` | 1 |

## Candidate Outcomes

| Candidate | Feature family | Primary delta MAE MeV | N-Z >= 20 delta MAE MeV | High-asymmetry delta MAE MeV | Verdict |
| --- | --- | ---: | ---: | ---: | --- |
| `NR-SCOUT-001` | quadratic neutron-excess ramp | -0.000000 | -0.000000 | -0.000000 | `INCONCLUSIVE` |
| `NR-SCOUT-002` | cubic neutron-excess ramp | +0.025327 | +0.048296 | +0.138252 | `INCONCLUSIVE` |
| `NR-SCOUT-003` | positive asymmetry fraction | -0.024320 | -0.052276 | -0.126016 | `PARTIALLY_VALID` |
| `NR-SCOUT-004` | frontier excess after N-Z = 20 | -0.018140 | -0.046132 | -0.143094 | `PARTIALLY_VALID` |
| `NR-SCOUT-005` | matched quadratic+cubic pair | +1.368811 | +1.970989 | +4.812167 | `OVERFITTED` |
| `NR-SCOUT-006` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Negative deltas mean the candidate reduced MAE relative to the frozen baseline
on that retrospective subset. Positive deltas mean regression.

## Rejected Before Execution

- `NR-SCOUT-007`, free-power neutron-excess exponent: rejected because fitting a free exponent on the 11-row residual slice adds an unbounded nonlinear overfit knob.
- `NR-SCOUT-008`, In/Sb frontier-cluster indicator: rejected because element-cluster targeting would be retrospective leakage against known post-AME2020 residual clusters.
- `NR-SCOUT-009`, per-threshold neutron-rich sweep: rejected because threshold sweeps duplicate the bounded frontier ramp while adding arbitrary selection degrees of freedom.

## Interpretation

The two material sandbox improvements are small and subset-scoped. They are
useful as reviewable follow-up signals, not as claims. The matched
quadratic+cubic pair is the most informative negative result: it improves no
promotion boundary and strongly worsens the high-asymmetry subset.

The near-null and near-zero outcomes are kept in the record so later agents do
not rediscover them as apparent candidate families.

## Promotion Boundary

- No prediction registry files were edited.
- No canonical result files were edited.
- No claims or knowledge files were edited.
- No claim promotion is allowed by this task.

Any future registry or reveal work must be a separate maintainer-reviewed task.
