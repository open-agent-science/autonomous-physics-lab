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

<!-- BEGIN AUTO TASK STATUS BOARD -->

> This task-status snapshot is generated from canonical task YAML files.
> Edit `tasks/TASK-*.yaml` for routine status transitions, then run
> `python3 -m physics_lab.cli sync-active-board .` on the maintainer branch.

## READY

- `TASK-0012` — Run a private multi-agent contributor dry run (`agent_workflow`, priority `high`, difficulty `medium`)
- `TASK-0024` — Create task index table (`documentation`, priority `medium`, difficulty `low`)
- `TASK-0025` — Create result artifacts index (`documentation`, priority `medium`, difficulty `low`)
- `TASK-0026` — Add 10 more dimensional-analysis challenge items (`physics_dataset_extension`, priority `high`, difficulty `low`)
- `TASK-0027` — Create units and physical constants reference (`physics_reference`, priority `medium`, difficulty `low`)
- `TASK-0028` — Plan light-clock thought experiment consistency check (`thought_experiment_planning`, priority `high`, difficulty `low`)
- `TASK-0029` — Audit project language for overclaim risk (`scientific_safety_review`, priority `high`, difficulty `low`)
- `TASK-0030` — Record first friend contributor dry run (`contributor_pilot`, priority `medium`, difficulty `low`)
- `TASK-0037` — Reproduce Koide charged-lepton relation (`relation_reproduction`, priority `high`, difficulty `medium`)
- `TASK-0038` — Reproduce historical tau-mass holdout prediction (`historical_prediction_benchmark`, priority `high`, difficulty `medium`)
- `TASK-0047` — Reduce closeout PR conflicts around active board sync (`maintainer_workflow`, priority `high`, difficulty `medium`)

## IN_PROGRESS

None.

## REVIEW_READY

- `TASK-0015` — Plan the diffusion scaling benchmark (`benchmark_planning`, priority `high`, difficulty `medium`)
- `TASK-0017` — Create a dimensional analysis challenge set (`benchmark_planning`, priority `high`, difficulty `medium`)
- `TASK-0020` — Add pytest-timeout and validation safeguards against hanging tests (`repository_validation`, priority `medium`, difficulty `low`)
- `TASK-0021` — Add AI agent attribution policy (`agent_workflow`, priority `medium`, difficulty `low`)
- `TASK-0035` — Refactor maintainer review checks into smaller modules (`code_quality_refactor`, priority `medium`, difficulty `medium`)
- `TASK-0036` — Create particle mass dataset scaffold (`scientific_dataset`, priority `high`, difficulty `medium`)
- `TASK-0039` — Design Koide-like triplet search with baselines (`benchmark_planning`, priority `high`, difficulty `medium`)
- `TASK-0041` — Design complexity penalty for mass-relation formulas (`scoring_design`, priority `medium`, difficulty `medium`)
- `TASK-0048` — Add schema support for dataset-based particle-mass reproduction benchmarks (`schema_extension`, priority `high`, difficulty `high`)

## DONE RECENTLY

- `TASK-0044` — Sync active task board from task files to reduce merge conflicts (merged)
- `TASK-0043` — Add task proposal protocol and id allocation rules (merged)
- `TASK-0042` — Add numerology guardrails for particle mass relation work (merged)
- `TASK-0034` — Add maintainer review agent mode (merged)
- `TASK-0033` — Standardize contributor-agent identity format (merged)
- `TASK-0032` — Build public scientific result package for Pendulum Gauntlet 100 (merged)
- `TASK-0031` — Add beginner-friendly contributor task set (merged)
- `TASK-0023` — Create first contributor runbook (merged)
- `TASK-0022` — Add PR review bundle snapshot script (merged)
- `TASK-0019` — Standardize agent branch, commit, and pull request protocol (merged)
- `TASK-0018` — Support planning-only and workflow tasks without fake hypothesis references (merged)
- `TASK-0014` — Plan a thought-experiment consistency suite (merged)
- `TASK-0013` — Plan a particle mass relation falsifier inspired by Koide-style formulas (merged)
- `TASK-0011` — Audit numerical precision versus model residual for the pendulum gauntlet run (merged)
- `TASK-0010` — Run pendulum hypothesis gauntlet with 100 candidate formulas (merged)
- `TASK-0008` — Add machine-readable review metadata for patch-style evidence artifacts (merged)
- `TASK-0007` — Add fail-on-warnings support for strict repository validation (merged)
- `TASK-0006` — Establish shared agent task board and operating model (merged)
- `TASK-0005` — Add artifact hash drift validation (merged)
- `TASK-0004` — Strengthen claim promotion policy (merged)
- `TASK-0003` — Add theory-aware pendulum approximation near the separatrix (merged)
- `TASK-0002` — Verify damped oscillator regimes against exact solutions (merged)
- `TASK-0001` — Find better pendulum correction formula (merged)

## PROPOSED

- `TASK-0016` — Plan an electromagnetic invariance mini-benchmark (`benchmark_planning`, priority `medium`, difficulty `medium`)
- `TASK-0040` — Build particle mass relation falsifier MVP (`scientific_falsification`, priority `high`, difficulty `high`)

## BLOCKED

None.

## REJECTED

- `TASK-0009` — Plan EXP-0003 as a diffusion scaling benchmark (`benchmark_planning`, priority `high`, difficulty `medium`)

<!-- END AUTO TASK STATUS BOARD -->

## Recommended first tasks for new contributors

Prefer independent `READY` tasks with:

- documentation-only scope;
- no canonical result-artifact churn;
- no shared branch or board-maintenance coupling;
- validation that does not require regenerating benchmark outputs.

If multiple `READY` tasks fit, pick the smallest one that does not touch the
same artifact surface as another open PR.

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
