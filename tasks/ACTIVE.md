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

### TASK-0024 — Create task index table

Type: `documentation`  
Priority: `medium`  
Suggested size: `small`

Expected output:

- `docs/task-index.md`
- task inventory table
- first-contributor suitability column

### TASK-0025 — Create result artifacts index

Type: `documentation`  
Priority: `medium`  
Suggested size: `small`

Expected output:

- `docs/result-artifacts-index.md`
- run-by-run result summary
- artifact navigation guide

### TASK-0026 — Add 10 more dimensional-analysis challenge items

Type: `physics_dataset_extension`  
Priority: `high`  
Suggested size: `small`

Expected output:

- extended `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`
- 10 new challenge items
- domain coverage note

### TASK-0027 — Create units and physical constants reference

Type: `physics_reference`  
Priority: `medium`  
Suggested size: `small`

Expected output:

- `knowledge/reference/units-and-dimensions.md`
- `knowledge/reference/physical-constants.yaml`
- reference-data warning note

### TASK-0028 — Plan light-clock thought experiment consistency check

Type: `thought_experiment_planning`  
Priority: `high`  
Suggested size: `small`

Expected output:

- `docs/notes/light-clock-consistency-check.md`
- light-clock planning note
- future benchmark outline

### TASK-0029 — Audit project language for overclaim risk

Type: `scientific_safety_review`  
Priority: `high`  
Suggested size: `small`

Expected output:

- `docs/notes/overclaim-language-audit.md`
- risky-language inventory
- safer replacement guidance

### TASK-0030 — Record first friend contributor dry run

Type: `contributor_pilot`  
Priority: `medium`  
Suggested size: `small`

Expected output:

- updated `docs/multi-agent-dry-run.md`
- friend-contributor dry-run entry
- workflow friction summary

### Developer-friendly tasks

### TASK-0036 — Create agent contributor quickstart

Type: `contributor_experience`  
Priority: `high`  
Suggested size: `small`

Expected output:

- `docs/agent-contributor-quickstart.md`
- updated contributor workflow docs
- concise branch/validation onboarding

### TASK-0038 — Create static benchmark index

Type: `documentation`  
Priority: `medium`  
Suggested size: `small`

Expected output:

- `docs/benchmark-index.md`
- benchmark navigation table
- implemented vs planned benchmark summary

### TASK-0039 — Add maintainer review agent smoke tests

Type: `repository_validation`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- expanded maintainer review smoke tests
- CLI helper coverage
- review-safety regression checks

### Scientist-friendly tasks

### TASK-0041 — Build dimensional analysis engine MVP

Type: `engine_implementation`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- dimensional analysis engine module
- deterministic challenge evaluation
- tests and smoke validation path

### TASK-0042 — Formalize light-clock thought experiment benchmark

Type: `thought_experiment_formalization`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- `docs/notes/light-clock-formalization.md`
- formal benchmark assumptions
- implementation-ready check inventory

### TASK-0045 — Define negative-result registry format

Type: `knowledge_update`  
Priority: `high`  
Suggested size: `small`

Expected output:

- `docs/negative-result-registry-format.md`
- negative-result entry template
- linkage guidance for tasks, hypotheses, and results

## Recommended first tasks for new contributors

These tasks are independent and safe for first-time contributors.

- `TASK-0023` — create first contributor runbook
- `TASK-0024` — create task index table
- `TASK-0025` — create result artifacts index
- `TASK-0026` — add 10 more dimensional-analysis challenge items
- `TASK-0027` — create units and physical constants reference
- `TASK-0028` — plan light-clock thought experiment consistency check
- `TASK-0029` — audit project language for overclaim risk
- `TASK-0030` — record first friend contributor dry run

`TASK-0030` should be started after a real first-contributor PR exists, since it
records an actual dry-run event rather than planning one in the abstract.

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

### High-impact but needs careful review

### TASK-0037 — Design agent performance metrics for private alpha

Type: `benchmark_planning`  
Priority: `medium`  
Suggested size: `medium`

Expected output:

- metric design note
- maintainer burden metrics
- measurement caveats summary

### TASK-0040 — Plan Pendulum Gauntlet v2 with separatrix-aware candidates

Type: `benchmark_planning`  
Priority: `high`  
Suggested size: `large`

Expected output:

- `docs/notes/pendulum-gauntlet-v2-plan.md`
- candidate-family inventory
- evaluation-range policy note

### TASK-0043 — Re-scope particle mass relation falsifier planning

Type: `benchmark_planning`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- particle-mass falsifier rescope note
- baseline/null-model checklist
- scientific risk summary

### TASK-0044 — Re-scope diffusion scaling benchmark planning

Type: `benchmark_planning`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- diffusion scaling rescope note
- metric and compute budget outline
- deferral decision guidance

## IN_PROGRESS

None.

## REVIEW_READY

### TASK-0046 — Add developer and scientist task batch for private alpha

Type: `agent_workflow`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- `tasks/TASK-0036-*.yaml` through `tasks/TASK-0045-*.yaml`
- updated `tasks/ACTIVE.md`
- grouped developer/scientist/review task sections

### TASK-0034 — Add maintainer review agent mode

Type: `maintainer_workflow`  
Priority: `high`  
Suggested size: `medium`

Expected output:

- `docs/maintainer-review-agent.md`
- `docs/review-checklists/maintainer-pr-review-checklist.md`
- `docs/review-checklists/task-closeout-checklist.md`
- `scripts/apl_task_closeout_check.py`
- maintainer closeout guidance

## DONE RECENTLY

- `TASK-0032` — public scientific result package for Pendulum Gauntlet 100 (merged)
- `TASK-0031` — beginner-friendly contributor task set (merged)
- `TASK-0023` — first contributor runbook (merged)
- `TASK-0022` — PR review bundle snapshot script (merged)
- `TASK-0019` — standardize agent branch, commit, and PR protocol (merged)
- `TASK-0018` — planning-only and workflow task input modes (merged)
- `TASK-0011` — numerical precision audit for pendulum gauntlet (merged)
- `TASK-0008` — machine-readable review metadata artifacts (merged)
- `TASK-0033` — contributor-agent identity format and agent commit rules (merged)
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
