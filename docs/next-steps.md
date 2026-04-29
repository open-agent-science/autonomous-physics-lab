# Next Steps

## Purpose

This file is the short operational handoff for the next contributor.

Use it for:

- the immediate next implementation targets;
- the current recommended order of work;
- quick reality checks before starting new changes.

Use [implementation-plan.md](/Users/roman/Documents/Autonomous%20Physics%20Lab/docs/implementation-plan.md)
for the broader phased strategy.

Use [backlog.md](/Users/roman/Documents/Autonomous%20Physics%20Lab/docs/backlog.md)
for lower-priority or later work.

## Current State

Completed:

- repository architecture and positioning docs;
- public-memory layout (`hypotheses/`, `claims/`, `experiments/`, `results/`, `tasks/`, `agents/`);
- pendulum formula discovery MVP;
- deterministic simulator, fitting, scoring, critic, runner, and CLI;
- Markdown report and machine-readable result artifact generation;
- JSON schema validation for hypothesis, experiment, task, agent, claim, and result;
- `physics-lab validate` and `physics-lab validate-repo`;
- referential integrity checks across core registry objects.
- richer result metadata:
  - `task_id`
  - `code_reference`
  - `limitations`
  - `engine_version`
  - `generated_at`

Current validation commands:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml
python3 -m physics_lab.cli validate-repo .
```

## Recommended Next Work

### 1. Add Knowledge and Example Schemas

The public-memory layer is still missing formal contracts for:

- `knowledge/`;
- example config files such as `examples/pendulum.yaml`.

Definition of done:

- JSON schema(s) added;
- loader/validator helpers added if needed;
- `validate-repo` or a related command checks them.

### 2. Add Claim/Knowledge Update Workflow

Right now claims and knowledge notes are manually curated.

Next improvement:

- add a helper that updates or proposes updates after a validated run;
- keep wording cautious and range-aware.

Definition of done:

- workflow can emit structured summary text;
- claim and knowledge update path is documented and testable.

### 3. Expand the Physics Verification Stack

The next scientific layer should go beyond numeric fit quality.

Best next checks:

- known-limit checks;
- symbolic consistency hooks;
- dimensional analysis hooks.

Definition of done:

- at least one extra verification signal beyond curve fit metrics is active.

## Do Not Prioritize Yet

- dashboards;
- web APIs;
- multi-agent orchestration runtime;
- literature ingestion;
- heavy storage backends;
- speculative theory-graph features before verification quality improves.

## Handoff Notes

If you are a future LLM or another contributor:

1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/implementation-plan.md`.
4. Run the validation commands above.
5. Prefer the smallest reproducible next step over larger refactors.
