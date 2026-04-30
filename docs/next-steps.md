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
- damped-oscillator benchmark scaffold:
  - `HYP-0002`
  - `EXP-0002`
  - `TASK-0002`
  - `CLAIM-0002`
  - `KNOW-0002`
  - exact-solution engine helpers
- runnable damped-oscillator verification workflow with committed `RESULT-0002`;
- second benchmark example config: `examples/damped_oscillator.yaml`;
- deterministic damped-oscillator checks for:
  - regime classification
  - initial-condition recovery
  - underdamped energy decay
  - oscillatory vs non-oscillatory behavior
  - dimensional consistency
  - `c -> 0` undamped-limit behavior
  - underdamped envelope decay-rate behavior
  - critical damping boundary behavior
  - overdamped asymptotic tail behavior

Current validation commands:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-results
python3 -m physics_lab.cli validate-repo .
```

## Recommended Next Work

### 1. Deepen the Physics Verification Stack

The first two verification benchmarks are real now, but the verification stack is still intentionally narrow.

Best next checks:

- symbolic consistency hooks;
- theory-aware candidate families that behave better near the separatrix.
- stronger asymptotic checks for more candidate families.
- better non-polynomial or theory-aware checks for behavior closer to the separatrix as `theta` approaches `pi`.
- stronger damped-oscillator checks such as envelope fitting, decay-rate checks, and `c -> 0` limit behavior.
- keep the two workflow modules stable and avoid pushing benchmark-specific logic back into `runner.py`.
- deepen evidence semantics now that both benchmarks have stronger verification gates.

Definition of done:

- the verification summary contains more than one structural physics check beyond fit quality and simple monotonic behavior.

### 2. Tighten Claim/Knowledge Evidence Semantics

The project now generates update suggestions, but evidence handling can still be stronger.

Best next improvements:

- derive claim status suggestions from validated results and verification gate outcomes;
- make knowledge updates more structured and section-aware;
- optionally track which result artifact informed a proposed update in more than one knowledge note.

### 3. Deepen Public Contribution Policy

The first public collaboration layer now exists, but the review policy can still
be stronger.

Best next docs/tools:

- define when a claim file may move from `DRAFT` to `PARTIALLY_SUPPORTED` or `SUPPORTED`;
- document who is expected to make that promotion decision;
- add a short architecture index or contributor map for faster handoff.

### 4. Keep Multi-Benchmark CI Non-Dirty

The repository now has two canonical benchmark slices, so CI and smoke tests
must keep using temp outputs.

Best next checks:

- preserve `--output-dir` coverage for both workflows;
- keep `git diff --exit-code` in CI after example runs;
- avoid tests that rewrite committed `results/` artifacts as part of normal validation.

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
