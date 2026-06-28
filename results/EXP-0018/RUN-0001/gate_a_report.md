# Gate A Report - RESULT-0025 (NMD-0003 GP extrapolation replay)

- **Artifact:** `results/EXP-0018/RUN-0001/result.yaml`
- **Task:** TASK-0843 - **Experiment:** EXP-0018 - **Hypothesis:** HYP-0018
- **Proposed tier:** AGENT_PUBLISHED
- **Result:** PASS pending repository validation.

## Gate A self-check

| gate | status | evidence |
|---|---|---|
| deterministic_run | PASS | Pinned script regenerates metrics and result package from committed inputs. |
| verification_block_populated | PASS | Five PASS checks with numeric metrics in result.yaml. |
| input_hashes_recorded | PASS | config / experiment / hypothesis / task / fixture sha256 pinned. |
| limitations_listed | PASS | Retrospective, single-model, miscalibration, and no-claim boundaries listed. |
| engine_version_and_commit_pinned | PASS | engine_version and git_commit recorded. |
| schema_validation_passes | PASS | To be checked by validate-repo before PR. |
| no_protected_artifact_rewrite | PASS | No golden result, CLAIM, KNOW, PRED, or TASK-0824 artifact rewritten. |
| no_forbidden_overclaim_wording | PASS | Control-surviving retrospective result wording only. |
| dataset_provenance_valid | PASS | Committed NMD-0003/post-AME2020 inputs; no live fetch. |

## Headline Numbers

- GP minus best-control margin: `1.869312` MeV.
- Predeclared margin: `0.25` MeV.
- Calibration verdict: `HEAVY_TAILED_MISCALIBRATED`.

## Routing

- Canonical destination: `results/EXP-0018/RUN-0001/`.
- Gate A: PASS for AGENT_PUBLISHED if repository validation passes.
- Gate B: not attempted.
- Claim impact: none. Knowledge impact: none. Prediction impact: none.
