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

### TASK-0007 — Add `--fail-on-warnings` support for strict repository validation

Type: `repository_validation`  
Priority: `high`  
Suggested size: `small`

Expected output:

- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`
- tests
- docs update

### TASK-0008 — Add machine-readable review metadata for patch-style artifacts

Type: `knowledge_update`  
Priority: `medium`  
Suggested size: `medium`

Expected output:

- patch artifact metadata format
- tests
- docs update

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

None.

## BLOCKED

None.

## DONE RECENTLY

- `TASK-0003`
- `TASK-0004`
- `TASK-0005`
- `TASK-0006`
