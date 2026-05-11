# AGENT-RUN-0007 Preflight

**Task:** `TASK-0188`
**Boundary:** activation-guard dry run

## Checks

| Check | Status | Notes |
| --- | --- | --- |
| Source manifest available | `PASS` | `POST-AME2020-SOURCES-0001` exists and records reviewed source provenance. |
| Row-level holdout dataset | `REVIEW_NEEDED` | `data/nuclear_masses/post_ame2020_holdout.yaml` is not committed. |
| Candidate freeze | `PASS` | `HYP-PROPOSAL-0021` remains frozen as `r_corr = c1*m2 + c2*mh + c3*oa`. |
| Claim boundary | `PASS` | No canonical result, claim, knowledge, or dataset is promoted. |

## Preflight Verdict

The benchmark helper is ready for a future reviewed row-level holdout dataset,
but active post-AME2020 metrics remain disabled.
