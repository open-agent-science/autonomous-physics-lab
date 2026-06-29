# Gate A Report - RESULT-0026 (ThermoML Tb bounded Joback transfer)

- Artifact: `results/EXP-0020/RUN-0001/result.yaml`
- Task: `TASK-0869`
- Experiment: `EXP-0020`
- Hypothesis: `HYP-0020`
- Checker: `python scripts/apl_check_result_publication.py results/EXP-0020/RUN-0001/result.yaml`
- Result: `PASS`
- Proposed tier: `AGENT_PUBLISHED`
- Verdict: `VALID_IN_RANGE`

## Gate A Self-Check

| gate | status | evidence |
| --- | --- | --- |
| deterministic_run | PASS | `python scripts/run_thermoml_tb_family_transfer.py --write` recomputes the source metrics from committed fixture and engines. |
| verification_block_populated | PASS | Five PASS checks cover fidelity, rights, aggregate margin, family survival, and provenance. |
| input_hashes_recorded | PASS | Run snapshots for config, fixture, experiment, hypothesis, and task are hashed. |
| limitations_listed | PASS | Result limitations include trust tier, Tb-only scope, source rights, frozen estimator, failed family, and no-claim boundary. |
| engine_version_and_commit_pinned | PASS | engine `0.1.0`, git commit `fc863667a48a3a50f196ac3a479af699e1975932`. |
| schema_validation_passes | PASS | Checked by `scripts/apl_check_result_publication.py` and strict repository validation. |
| no_protected_artifact_rewrite | PASS | New result id and path; no golden-results pin or existing result rewrite. |
| no_forbidden_overclaim_wording | PASS | Bounded transfer wording only; no broad property-estimation, chemical-design, CLAIM, or KNOW promotion. |
| dataset_provenance_valid | PASS | NIST ThermoML DOI, published SHA-256, and redistribution boundary are recorded. |

## Headline Numbers

- Joback aggregate MAE: `14.925825 K`.
- Best non-oracle aggregate control: `molecular_weight_only` at `43.427943 K`.
- Aggregate margin: `28.502118 K` versus required `5.0 K`.
- Family survival: `7/8` families; failed family `esters/lactones`.

## Routing

- Canonical destination: `results/EXP-0020/RUN-0001/result.yaml`.
- Gate A: PASS, eligible for `AGENT_PUBLISHED`.
- Gate B: not attempted; future independent replay should compare aggregate and per-family metrics.
- Claim impact: none.
- Knowledge impact: none.
- Publication blockers: none for agent-published bounded result packaging.
