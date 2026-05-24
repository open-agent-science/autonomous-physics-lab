# Preflight

**Lane:** nuclear uncertainty-weighted residual hypothesis lane

- `task_scope`: `PASS` - TASK-0342 requests a sandbox uncertainty-weighted residual lane, not reveal scoring.
- `data_boundary`: `PASS` - Only committed NMD-0002 and post-AME2020 rows are used; no live external fetch is performed.
- `uncertainty_boundary`: `PASS` - Uncertainty fields are recorded as review-only diagnostics, not fit-grade likelihood weights.
- `promotion_boundary`: `PASS` - No prediction registry, canonical result, claim, or knowledge file is written.
