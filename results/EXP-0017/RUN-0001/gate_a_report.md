# Gate A Report - RESULT-0024 (Stellar M-L high-mass transfer)

- **Artifact:** `results/EXP-0017/RUN-0001/result.yaml`
- **Task:** TASK-0849 - **Experiment:** EXP-0017 - **Hypothesis:** HYP-0017
- **Proposed tier:** AGENT_PUBLISHED
- **Result:** PASS pending repository validation.

## Gate A self-check

| gate | status | evidence |
|---|---|---|
| deterministic_run | PASS | Pinned script regenerates sandbox metrics and result package from committed rows. |
| verification_block_populated | PASS | Five PASS checks with numeric metrics in result.yaml. |
| input_hashes_recorded | PASS | config / experiment / hypothesis / task / fixture sha256 pinned. |
| limitations_listed | PASS | Same-source, small-holdout, stage/provenance, no-claim boundaries listed. |
| engine_version_and_commit_pinned | PASS | engine_version and git_commit recorded. |
| schema_validation_passes | PASS | To be checked by validate-repo before PR. |
| no_protected_artifact_rewrite | PASS | RESULT-0022, CLAIM, PRED, KNOW, and source dataset untouched. |
| no_forbidden_overclaim_wording | PASS | Transfer-under-controls framing only. |
| dataset_provenance_valid | PASS | DEBCat normalized rows and TASK-0763 Route-2 boundary inherited. |

## Headline Numbers

- Primary holdout MAE: `0.334564` dex.
- Best control: `mass_matched_massband_mean` at `0.483879` dex.
- Transfer margin: `0.149315` dex.

## Routing

- Canonical destination: `results/EXP-0017/RUN-0001/`.
- Gate A: PASS for AGENT_PUBLISHED if repository validation passes.
- Gate B: deferred independent replay.
- Claim impact: none. Knowledge impact: none.
