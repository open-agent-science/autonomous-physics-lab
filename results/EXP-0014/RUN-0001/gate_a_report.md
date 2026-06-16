# Gate A Report — RESULT-0021 (Materials MD-0002 formation-energy benchmark)

- **Artifact:** `results/EXP-0014/RUN-0001/result.yaml`
- **Task:** TASK-0765 · **Experiment:** EXP-0014 · **Hypothesis:** HYP-0014
- **Checker:** `python3 scripts/apl_check_result_publication.py results/EXP-0014/RUN-0001/result.yaml`
- **Result:** `PASS` · **Proposed tier:** AGENT_PUBLISHED · **Verdict:** VALID_IN_RANGE (frozen scope)

## Gate A self-check (9/9 True)

| gate | status | evidence |
|---|---|---|
| deterministic_run | ✅ | `replay_materials_md0002_result.py --check` → GATE_A_REPLAY PASS (tol 1e-6); row-order invariant |
| verification_block_populated | ✅ | 6 PASS checks with metrics |
| input_hashes_recorded | ✅ | config / experiment / hypothesis / task sha256 pinned |
| limitations_listed | ✅ | 5 scope + provenance limitations |
| engine_version_and_commit_pinned | ✅ | engine `0.1.0`, git_commit `0e23e2b6e5740f189e9957789ba1408a4b3da596` |
| schema_validation_passes | ✅ | validates against `result.schema.json`; repo `validate-repo --strict` PASS |
| no_protected_artifact_rewrite | ✅ | no CLAIM/KNOW promotion; no-op claim/knowledge stubs |
| no_forbidden_overclaim_wording | ✅ | benchmark framing only; no discovery/synthesis/universal-law wording |
| dataset_provenance_valid | ✅ | MD-0002 Materials Project CC BY 4.0, DATA_LICENSES-declared, computed DFT, no live fetch |

## Validation commands run

- `python3 -m ruff check .` → All checks passed
- `python3 -m pytest tests/test_docs_links.py tests/test_result_publication_gate.py` → 13 passed
- `python3 scripts/apl_check_result_publication.py results/EXP-0014/RUN-0001/result.yaml` → PASS
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings` → PASS (0 ERROR, 0 WARNING)

## Headline numbers (frozen holdout)

- cation-pair baseline MAE **0.200606 eV/atom** vs global-median null **0.506092** (60.4% lower)
- 5/5 seeded splits won; beats label-shuffle and cation-label-shuffle nulls in every seed

## Routing

- **Canonical destination:** `results/EXP-0014/RUN-0001/` (new identity; `agent_runs/AGENT-RUN-0072/` untouched)
- **Gate A:** PASS → eligible for AGENT_PUBLISHED
- **Gate B (independent validation / maintainer review):** not performed here; deferred to maintainer
- **Claim impact:** none (no CLAIM promotion proposed)
- **Knowledge impact:** none (no KNOW promotion proposed)
- **Publication blockers:** none for AGENT_PUBLISHED; higher tiers require maintainer review
