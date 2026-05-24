# Nuclear Pairing And Odd-Even Variant Scout

**Agent run:** AGENT-RUN-0014  
**Task:** TASK-0280  
**Evidence class:** bounded sandbox residual scout  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_pairing_odd_even_variant_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0014/metrics.json`

## Summary

This scout generated nine bounded pairing, odd-even, parity, or
local-staggering candidate ideas. Six were evaluated and three were rejected
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
| `PARTIALLY_VALID` | 1 |
| `INCONCLUSIVE` | 4 |
| `OVERFITTED` | 1 |

## Candidate Outcomes

| Candidate | Feature family | Primary delta MAE MeV | Even-even delta MAE MeV | Odd-odd delta MAE MeV | Odd-A delta MAE MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `PAIR-SCOUT-001` | pairing inverse-A | +0.006678 | +0.013737 | +0.014590 | +0.000000 | `INCONCLUSIVE` |
| `PAIR-SCOUT-002` | baseline-shape pairing | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |
| `PAIR-SCOUT-003` | pairing cube-root | -0.008470 | -0.014776 | -0.021041 | +0.000000 | `PARTIALLY_VALID` |
| `PAIR-SCOUT-004` | odd-A offset | +0.079643 | +0.000000 | +0.000000 | +0.150607 | `INCONCLUSIVE` |
| `PAIR-SCOUT-005` | per-parity-class offsets | +0.167279 | +0.032583 | +0.332913 | +0.150607 | `OVERFITTED` |
| `PAIR-SCOUT-006` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Negative deltas mean the candidate reduced MAE relative to the frozen baseline
on that retrospective subset. Positive deltas mean regression.

## Rejected Before Execution

- `PAIR-SCOUT-007`, free-power pairing exponent: rejected because fitting the exponent adds a nonlinear overfit knob.
- `PAIR-SCOUT-008`, N=82 gated pairing override: rejected because the gate would mix pairing with retrospective shell-cluster targeting.
- `PAIR-SCOUT-009`, per-nuclide parity memorization stack: rejected because row-level parity indicators would memorize residuals.

## Interpretation

`PAIR-SCOUT-003` is the only small, subset-scoped sandbox improvement. The
baseline-shape pairing refinement is effectively dormant, which is expected
because the frozen baseline already contains an explicit pairing term.

`PAIR-SCOUT-005` is the most useful negative result: adding free class offsets
regresses primary, odd-odd, and odd-A subsets. This suggests the current
pairing/odd-even lane is more likely to provide controls and falsification
than immediate registry candidates.

## Promotion Boundary

- No prediction registry files were edited.
- No canonical result files were edited.
- No claims or knowledge files were edited.
- No claim promotion is allowed by this task.

Any future registry or reveal work must be a separate maintainer-reviewed task.
