# Next Steps

## Purpose

This file is the short operational handoff for the next contributor.

Use it for:

- the immediate next implementation targets;
- the current recommended order of work;
- quick reality checks before starting new changes.

Use [implementation-plan.md](./implementation-plan.md)
for the broader phased strategy.

Use [backlog.md](./backlog.md)
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
- schema coverage for:
  - `knowledge/`
  - example configs such as `examples/pendulum.yaml`
- claim and knowledge update helper artifacts generated from validated runs
- run-based artifact layout under `results/<experiment>/<run>/`
- pendulum verification checks for:
  - small-angle limit
  - small-angle exact-window agreement
  - small-angle curvature agreement
  - upper-range exact-window agreement
  - near-separatrix extrapolation diagnostic
  - separatrix asymptotic-alignment diagnostic
  - evenness
  - monotonicity
  - known small-angle coefficient comparisons
  - structure-aware dimensional consistency checks
- CI coverage for:
  - `ruff`
  - `pytest`
  - example workflow execution
  - `validate-repo`

Current validation commands:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml
python3 -m physics_lab.cli validate-repo .
```

## Recommended Next Work

### 1. Deepen the Physics Verification Stack

The first verification gate is real now, but it is still intentionally narrow.

Best next checks:

- symbolic consistency hooks;
- theory-aware candidate families that behave better near the separatrix.
- stronger asymptotic checks for more candidate families.
- better non-polynomial or theory-aware checks for behavior closer to the separatrix as `theta` approaches `pi`.

Definition of done:

- the verification summary contains more than one structural physics check beyond fit quality and simple monotonic behavior.

### 2. Add Repo Status and Contributor Docs

The project now has enough moving parts that handoff quality matters more.

Best next docs/tools:

- a contributor guide for humans and LLM agents;
- a repo-level status command;
- a short architecture index or map.

### 3. Tighten Claim/Knowledge Evidence Semantics

The project now generates update suggestions, but evidence handling can still be stronger.

Best next improvements:

- derive claim status suggestions from validated results and verification gate outcomes;
- make knowledge updates more structured and section-aware;
- optionally track which result artifact informed a proposed update in more than one knowledge note.

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
