# Gate A Report — RESULT-0022 (Stellar M-L DEBCat controlled benchmark)

- **Artifact:** `results/EXP-0015/RUN-0001/result.yaml`
- **Task:** TASK-0764 · **Experiment:** EXP-0015 · **Hypothesis:** HYP-0015
- **Checker:** `python3 scripts/apl_check_result_publication.py results/EXP-0015/RUN-0001/result.yaml`
- **Result:** `PASS` · **Proposed tier:** AGENT_PUBLISHED · **Verdict:** VALID_IN_RANGE (frozen scope)

## Gate A self-check (9/9 True)

| gate | status | evidence |
|---|---|---|
| deterministic_run | ✅ | `replay_stellar_ml_result.py --check` → GATE_A_REPLAY PASS (tol 1e-6) |
| verification_block_populated | ✅ | 8 PASS checks with metrics |
| input_hashes_recorded | ✅ | config / experiment / hypothesis / task sha256 pinned |
| limitations_listed | ✅ | 5 scope + provenance limitations |
| engine_version_and_commit_pinned | ✅ | engine `0.1.0`, git_commit `0e23e2b6e5740f189e9957789ba1408a4b3da596` |
| schema_validation_passes | ✅ | validates against `result.schema.json`; repo `validate-repo --strict` PASS |
| no_protected_artifact_rewrite | ✅ | no CLAIM/KNOW promotion; no-op claim/knowledge stubs |
| no_forbidden_overclaim_wording | ✅ | controlled-benchmark framing; α=3.5 not falsified; no universal-law wording |
| dataset_provenance_valid | ✅ | DEBCat CC BY 4.0 (Southworth grant, TASK-0763), DATA_LICENSES-declared, raw not committed, no live fetch |

## Validation commands run

- `python3 -m ruff check .` → All checks passed
- `python3 -m pytest tests/test_docs_links.py tests/test_result_publication_gate.py` → passed
- `python3 scripts/apl_check_result_publication.py results/EXP-0015/RUN-0001/result.yaml` → PASS
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings` → PASS (0 ERROR, 0 WARNING)

## Headline numbers (frozen main-sequence holdout, dex)

- train-fitted α̂=4.526 → **0.119925**; piecewise α=4.0 → 0.137608; single α=3.5 → 0.184954; null → 0.331817
- single-3.5 → fitted gap 0.065029 dex and → piecewise gap 0.047346 dex both exceed the 0.04 dex split-noise reference
- split-sensitivity positive 5/5 seeds; real shuffle margin exceeds all shuffled

## Routing

- **Canonical destination:** `results/EXP-0015/RUN-0001/` (new identity; `agent_runs/AGENT-RUN-0073,0074/` untouched)
- **Gate A:** PASS → eligible for AGENT_PUBLISHED
- **Gate B (independent validation / maintainer review):** deferred to maintainer
- **Claim impact:** none (no CLAIM promotion proposed)
- **Knowledge impact:** none (no KNOW promotion proposed)
- **Publication blockers:** none for AGENT_PUBLISHED. Noted follow-up: reconcile the superseded seed-stage scope flags in the committed DEBCat dataset header (separate task).
