# AGENT-RUN-0011 Preflight

**Task:** `TASK-0201`
**Lane:** pairing and odd-even residual corrections
**Status:** PASS

## Checks

| Check | Status | Notes |
|-------|--------|-------|
| Campaign scope | PASS | `nuclear-mass-surface` WHITELISTED_LIMITED; frozen-baseline sandbox work is in scope |
| Proposal schema | PASS | 5 proposals (HYP-PROPOSAL-0038..0042); 3 rejected, 2 executed |
| Triage boundary | PASS | Rejected proposals documented with specific rationale before execution |
| Leakage review | PASS | No executed feature targets a chain or shell closure identified post-hoc from AGENT-RUN-0008 |
| Promotion boundary | PASS | No canonical result, claim, knowledge, or dataset is changed |

## Proposal Triage Summary

| Proposal | Decision | Rationale |
|----------|----------|-----------|
| HYP-PROPOSAL-0038 | Execute | Differential even-even / odd-odd pairing; expected to overfit on 1 odd-odd row |
| HYP-PROPOSAL-0039 | Execute | Wigner N=Z energy; minimal post-AME2020 activation expected |
| HYP-PROPOSAL-0040 | Reject | Data-sparsity overfit: 0 odd-Z/even-N rows in NMD-0002 |
| HYP-PROPOSAL-0041 | Reject | Near-collinear with baseline pairing term on 11-row slice |
| HYP-PROPOSAL-0042 | Reject | Feature redundant with HYP-PROPOSAL-0038 η_ee indicator |

## Input Artifacts

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml` — frozen training slice (11 rows)
- `data/nuclear_masses/post_ame2020_holdout.yaml` — reviewed row-level holdout (295 primary rows)
- `results/EXP-0012/RUN-0001/result.yaml` — RESULT-0015 frozen baseline coefficients
- `agent_runs/AGENT-RUN-0006/metrics.json` — split-sensitivity context
- `agent_runs/AGENT-RUN-0008/metrics.json` — post-AME2020 time-split context
