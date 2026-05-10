# Autonomous Nuclear Mass Pilot 01

## Scope

`TASK-0170` runs the first sandbox-only autonomous residual pilot for the
nuclear-mass campaign after the repository gained:

- campaign scaffold and guardrails;
- pinned measured slice `NMD-0002`;
- first baseline benchmark `EXP-0012` / `RESULT-0015`;
- reviewed structured holdout protocol.

This review note covers:

- `hypothesis_proposals/nuclear-mass/`
- `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0005-nuclear-mass-sandbox-batch.yaml`
- `agent_runs/AGENT-RUN-0005/`
- `tests/test_nuclear_mass_autonomous_pilot.py`

## Proposal Triage Summary

| Proposal | Status | Decision | Reason |
| --- | --- | --- | --- |
| `HYP-PROPOSAL-0020` | `REVIEW_READY` | Executed | Compact shell-aware comparator with one small regression and three improvements. |
| `HYP-PROPOSAL-0021` | `REVIEW_READY` | Executed | Best bounded family in this batch; improves all active holdout slices on the frozen benchmark. |
| `HYP-PROPOSAL-0022` | `REVIEW_READY` | Executed | Explicit overfit negative control. |
| `HYP-PROPOSAL-0023` | `REJECTED` | Not executed | Chain-memorization risk. |
| `HYP-PROPOSAL-0024` | `REJECTED` | Not executed | Two-row heavy memorization patch. |
| `HYP-PROPOSAL-0025` | `REJECTED` | Not executed | Complexity and discontinuity budget too high. |
| `HYP-PROPOSAL-0026` | `REJECTED` | Not executed | Advanced-model comparison lane is still deferred. |
| `HYP-PROPOSAL-0027` | `REJECTED` | Not executed | Live time-split fetch is blocked until a pinned later-measurement dataset exists. |

## What We Learned

1. A shell-aware additive correction can survive all active holdout slices on
   the pinned benchmark without any canonical promotion.
2. A slightly simpler shell-only family is still useful because it shows where
   the extra odd-A term matters.
3. A visually plausible asymmetry refinement can fail exactly where this
   campaign needs skepticism most: heavy magic and neutron-rich slices.

## Maintainer Recommendation

- Keep `AGENT-RUN-0005` as sandbox evidence only.
- Do not promote any claim or canonical result.
- Treat `HYP-PROPOSAL-0021` as the only executed family that may deserve a
  later maintainer-reviewed canonical comparison task.
- Keep `HYP-PROPOSAL-0022` as explicit negative evidence that this benchmark
  can reject attractive but brittle residual families.
