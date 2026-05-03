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

For new task ideas without a maintainer-assigned canonical `TASK-XXXX` id, use
the proposal-first flow in [../docs/task-proposal-protocol.md](../docs/task-proposal-protocol.md).

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

### TASK-0030 — Record first friend contributor dry run

Type: `contributor_pilot`  
Priority: `medium`  
Suggested size: `small`

Expected output:

- updated `docs/multi-agent-dry-run.md`
- friend-contributor dry-run entry
- workflow friction summary

### TASK-0035 — Refactor maintainer review checks into smaller modules

Type: `code_quality_refactor`  
Priority: `medium`  
Suggested size: `medium`

Expected output:

- smaller maintainer review modules under `physics_lab/registry/`
- stable `apl_review_pr.py` and `apl_closeout_task.py` behavior
- updated maintainer review tests

### Particle mass relation / Koide track

This track was decomposed by `TASK-0013`. Because `TASK-0035` is already in
use, the new particle-mass tasks start at `TASK-0036`.

#### READY

- `TASK-0036` — create particle mass dataset scaffold
- `TASK-0037` — reproduce Koide charged-lepton relation
- `TASK-0038` — reproduce historical tau-mass holdout prediction
- `TASK-0039` — design Koide-like triplet search with baselines
- `TASK-0041` — design complexity penalty for mass-relation formulas
- `TASK-0042` — add numerology guardrails for particle mass relation work

#### PROPOSED

- `TASK-0040` — build particle mass relation falsifier MVP

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

### TASK-0040 — Build particle mass relation falsifier MVP

Type: `scientific_falsification`  
Priority: `high`  
Suggested size: `large`

Expected output:

- falsifier workflow
- scoring and baseline integration
- reproducible benchmark result artifacts
- limitation summary

## IN_PROGRESS

None.

## REVIEW_READY

### TASK-0029 — Audit project language for overclaim risk

Type: `scientific_safety_review`  
Priority: `high`  
Branch: `agent/roman/codex/task-0029-overclaim-language-audit`

Completed outputs:

- `docs/notes/overclaim-language-audit.md`
- safer wording updates in `README.md`
- future-release wording updates in public-alpha draft docs

### TASK-0035 — Refactor maintainer review checks into smaller modules

Type: `code_quality_refactor`  
Priority: `medium`  
Branch: `agent/roman/claude/task-0035-maintainer-review-refactor`

Completed outputs:

- fixed multi-proposal PR blocker in `physics_lab/registry/maintainer_review.py`
- new test in `tests/test_maintainer_review.py`
- updated `tasks/ACTIVE.md`

### TASK-0015 — Plan the diffusion scaling benchmark

Type: `benchmark_planning`  
Priority: `high`  
Branch: `agent/roman/claude/task-0015-diffusion-scaling-benchmark`

Completed outputs:

- `docs/notes/diffusion-scaling-benchmark.md`
- benchmark plan with scoring criteria and EXP-0003 output outline
- limitation summary

## DONE RECENTLY

- `TASK-0043` — task proposal protocol and id allocation rules (merged)
- `TASK-0013` — particle mass relation falsifier planning / Koide track (merged)
- `TASK-0034` — Add maintainer review agent mode (merged)
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
