# Active Task Board

## CURRENT STRATEGY

APL is verification-first scientific infrastructure.

Current phase: `v0.1-private-alpha`

Current goal:

- private contributor pilot
- measurable scientific result
- public release only after explicit gates are satisfied

The repository remains private until
[../docs/public-release-gates.md](../docs/public-release-gates.md) are
satisfied.

Use [../docs/strategy.md](../docs/strategy.md) as the strategic compass and
[../docs/agent-task-protocol.md](../docs/agent-task-protocol.md) as the
canonical execution protocol. Use
[../docs/agent-operating-model.md](../docs/agent-operating-model.md) for
supporting workflow context and handoff norms.

## READY

### TASK-0012 — Run a private multi-agent contributor dry run

Type: `agent_workflow`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- `docs/multi-agent-dry-run.md`
- pilot summary
- linked PR list
- workflow lessons learned

### TASK-0013 — Plan a particle mass relation falsifier inspired by Koide-style formulas

Type: `benchmark_planning`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- task spec
- benchmark plan
- evaluation design
- scientific constraint summary

### TASK-0015 — Plan the diffusion scaling benchmark

Type: `benchmark_planning`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- task spec
- benchmark plan
- future `EXP-0003` output outline
- limitation summary


## PROPOSED

### TASK-0016 — Plan an electromagnetic invariance mini-benchmark

Type: `benchmark_planning`  
Priority: `medium`  
Suggested size: `medium`

Expected output:

- task spec
- mini-benchmark plan
- scope constraints
- candidate check inventory

## IN_PROGRESS

None.

## REVIEW_READY

### TASK-0022 — Add PR review bundle snapshot script

Type: `agent_workflow`  
Priority: `medium`  
Branch: `agent/claude/task-0022-review-bundle-script`

Completed outputs:

- `scripts/apl_review_bundle.sh` — produces full diff + commit list vs main
- `docs/agent-task-protocol.md` — review bundle referenced under Required Validation

### TASK-0011 — Audit numerical precision versus model residual for the pendulum gauntlet run

Type: `numerical_audit`  
Priority: `high`  
Branch: `agent/codex/task-0011-numerical-audit`

Completed outputs:

- `docs/numerical-accuracy-policy.md`
- `results/EXP-0001/RUN-0003/precision_audit.yaml`
- `results/EXP-0001/RUN-0003/precision_audit.md`
- tests
- updated `results/EXP-0001/RUN-0003/report.md` wording

### TASK-0019 — Standardize agent branch, commit, and pull request protocol

Type: `agent_workflow`  
Priority: `high`  
Suggested size: `medium`

Completed outputs:

- `docs/agent-task-protocol.md`
- `CLAUDE.md`
- updated agent and contributor entrypoints
- updated PR template
- aligned task-board guidance

### TASK-0018 — Support planning-only and workflow tasks without fake hypothesis references

Type: `repository_validation`  
Priority: `high`  
Suggested size: `medium`

Completed outputs:

- multi-mode task input schema for science, planning-only, and workflow tasks
- repository validation that keeps science-task references strict without forcing fake benchmark links for planning/workflow tasks
- updated planning and workflow task specs without fake pendulum references
- updated `tasks/TASK-TEMPLATE.yaml`
- updated contributor and operating-model docs
- tests covering the new task input modes

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

## DONE RECENTLY

- `TASK-0021` — AI agent attribution policy (merged)
- `TASK-0020` — pytest-timeout and quick validation script (merged)
- `TASK-0017` — dimensional analysis challenge set (merged)
- `TASK-0014` — thought-experiment consistency-suite planning (merged)
- `TASK-0003`
- `TASK-0004`
- `TASK-0005`
- `TASK-0006`
- `TASK-0007`
- `TASK-0010` — pendulum gauntlet (100 candidates) → `RESULT-0004` / `RUN-0003`

## DO NOT START YET

- dashboard
- web API
- arXiv or OpenAlex ingestion
- multi-agent runtime
- database backend
- public launch
- claims of "new physics"

## PROPOSED NOTE

`PROPOSED` items are backlog ideas, not active execution tasks. Agents should
start from `READY` tasks unless a maintainer explicitly redirects them.
