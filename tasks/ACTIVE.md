# Active Task Board

## Strategy Reminder

APL is verification-first scientific infrastructure.

Do not add speculative claims.
Do not add dashboard, web API, literature ingestion, or multi-agent runtime
before current verification goals are met.
Prefer atomic tasks with reproducible outputs and small commits.

Use [../docs/strategy.md](../docs/strategy.md) as the strategic compass and
[../docs/agent-operating-model.md](../docs/agent-operating-model.md) as the
shared execution protocol.

## READY

### TASK-0011 — Audit numerical vs model error for pendulum benchmark results

Type: `verification_extension`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- high-precision reference audit for pendulum benchmark reporting
- tolerance-aware wording update for pendulum result artifacts or notes
- deterministic tests distinguishing approximation residual from reference uncertainty

### TASK-0009 — Plan `EXP-0003` as a diffusion scaling benchmark

Type: `benchmark_planning`  
Priority: `high`  
Suggested size: `small`

Expected output:

- task spec only
- benchmark candidate comparison
- no implementation yet

## CLAIMED

None.

## IN_PROGRESS

None.

## REVIEW_READY

### TASK-0008 — Add machine-readable review metadata for patch-style artifacts

Type: `knowledge_update`  
Priority: `medium`  
Suggested size: `medium`

Completed outputs:

- `review_metadata.yaml` generated per-run alongside existing patch artifacts
- `physics_lab/schemas/review_metadata.schema.json` — JSON Schema 2020-12
- `render_review_metadata()` in `artifacts.py`
- `review_metadata` added to result schema artifacts, repository strict validation, CLI output
- `knowledge_update` added to `STRICT_DONE_TASK_TYPES_WITHOUT_RESULTS`
- tests updated in `test_pendulum.py` and `test_damped_oscillator.py`
- `docs/notes/review-metadata-contract.md`

## BLOCKED

None.

## DONE RECENTLY

- `TASK-0003`
- `TASK-0004`
- `TASK-0005`
- `TASK-0006`
- `TASK-0007`
- `TASK-0010` — pendulum gauntlet (100 candidates) → `RESULT-0004` / `RUN-0003`
