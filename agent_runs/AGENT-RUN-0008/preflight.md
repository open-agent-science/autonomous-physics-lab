# Preflight - AGENT-RUN-0008

| Check | Status | Notes |
| --- | --- | --- |
| row_level_holdout_dataset | PASS | TASK-0196 committed a schema-validated row-level holdout with 296 rows and 295 primary rows. |
| source_activation | PASS | TASK-0197 explicitly activates retrospective metrics from committed rows only. |
| frozen_baseline | PASS | Uses RESULT-0015 fitted SEMF coefficients without rewriting RESULT artifacts. |
| candidate_freeze | PASS | Formula families for HYP-0020/0021/0022 are unchanged. |
| no_live_fetch | PASS | All inputs are committed repository files. |
| claim_boundary | PASS | No claim, canonical result, or knowledge promotion is allowed. |
