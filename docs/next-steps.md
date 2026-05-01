# Next Steps

## Purpose

This file is the short operational handoff for the next contributor.

Use it for:

- the immediate next implementation targets;
- the current recommended order of work;
- quick reality checks before starting new changes.

Use [implementation-plan.md](./implementation-plan.md)
for the broader phased strategy.

Use [../tasks/ACTIVE.md](../tasks/ACTIVE.md)
for the live task board and actual claimable work.

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
- theory-aware pendulum extension with committed `RESULT-0003` under `results/EXP-0001/RUN-0002/`;
- immutable run-input snapshots for canonical result artifacts to keep historical runs validation-stable.
- section-aware knowledge update artifacts for both benchmark slices, so proposed changes map more directly onto `knowledge/*.md`.
- strict repository validation with severity-based integrity checks for canonical run artifacts and orphan detection.
- patch-style claim and knowledge update artifacts plus maintainer-facing review summaries for canonical runs.
- shared agent task board and operating model for seamless Codex / Claude / human handoff.
- machine-readable `review_metadata.yaml` companion files for patch-style artifacts with a JSON Schema contract.
- pendulum hypothesis gauntlet: 100 deterministic candidates evaluated in `RUN-0003` / `RESULT-0004`; best model `model_t4_x1` (`1 + a·θ⁴ + b·sin²(θ/2)`) achieves VALID_IN_RANGE with test mean error 3.1×10⁻⁴.

Current validation commands:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

## Recommended Next Work

### 1. Use the Shared Task Board for Ready Work

The repository now has a dedicated live task board and agent operating model.

Best next operating rule:

- choose one `READY` task from [../tasks/ACTIVE.md](../tasks/ACTIVE.md);
- keep local work sequential by default unless tasks are clearly independent;
- update task state before and after meaningful work.

### 2. Plan the Third Benchmark (EXP-0003)

The pendulum gauntlet milestone is complete. The next recommended step is planning EXP-0003 as a
diffusion scaling benchmark (TASK-0009, READY).

Best next steps:

- choose one `READY` task from `tasks/ACTIVE.md` (currently TASK-0009);
- produce a benchmark candidate comparison and task spec — no implementation yet;
- keep damped-oscillator checks extensible for future driven or nonlinear variants;
- keep the two workflow modules stable and avoid pushing benchmark-specific logic back into `runner.py`.

Definition of done:

- the verification summary contains more than one structural physics check beyond fit quality and simple monotonic behavior.

### 3. Tighten Claim/Knowledge Evidence Semantics

The project now has generated status suggestions and a maintainer-facing claim
promotion policy, but evidence handling can still be stronger.

Best next improvements:

- optionally track which result artifact informed a proposed update in more than one knowledge note;
- make patch artifacts easier to consume automatically if future tooling wants machine-readable review hints.

### 4. Improve Maintainer Review Discipline

The public collaboration layer now exists and claim-promotion rules are
documented.

Best next docs/tools:

- keep the release checklist and prepared release notes in sync with the actual pre-public validation state;
- keep claim-promotion language consistent across claims, result artifacts, and review templates;
- keep `tasks/ACTIVE.md` and `docs/strategy.md` aligned so agents do not drift into stale priorities.

### 5. Keep Multi-Benchmark CI Non-Dirty

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
