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
- private-alpha contributor workflow docs, release-gating docs, and branch-protection planning for invited contributors.

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

### 1. Generalize the Autonomous Loop Beyond Pendulum

The first pendulum autonomous pilot and the PR-packaging layer are now merged.
The next proof point is breadth: show that the same repository contract works
for a second campaign without promoting claims automatically.

Highest-value next execution task:

- `TASK-0155` second dimensional-validator autonomous pilot

Success looks like:

- generated challenge hypotheses enter through the proposal lane;
- weak items fail deterministic checks before sandbox output is treated as evidence;
- sandbox evidence remains outside canonical `results/`;
- maintainers can review a second autonomous PR without reading raw scratch artifacts.

### 2. Build the Stronger Benchmark Path

The next scientific-value jump should come from a richer nonlinear mechanics
benchmark, not another speculative numerology surface.

Current strongest benchmark path:

- `TASK-0159` anharmonic oscillator period benchmark is now implemented and in review-ready state.
- `TASK-0160` autonomous anharmonic research pilot is the next high-value execution step.

This path should remain downstream of the autonomy contract, but it is now the
best candidate for a higher-value benchmark with lower overclaim risk.

### 3. Preserve Replay and Validation Quality

The scientific credibility layer now includes the merged holdout protocol and
result-quality rubric. The next hardening work should keep repository
validation and replay surfaces easy to trust:

- `TASK-0136` split repository validation and scientific-memory integrity checks
- `TASK-0137` split maintainer review helper into clearer policy layers
- `TASK-0138` add canonical replay and golden-result hardening layer

### 4. Keep Docs and Gates Aligned

Always keep these files aligned when priorities change:

- [status.md](./status.md)
- [strategy.md](./strategy.md)
- [../tasks/ACTIVE.md](../tasks/ACTIVE.md)
- [public-release-gates.md](./public-release-gates.md)
- [private-contributor-pilot.md](./private-contributor-pilot.md)

### 5. Public Release Remains Gated

Do not prepare the repository as public-ready until all gates are satisfied.

Public release is explicitly downstream of:

- technical stability
- autonomous pilot evidence
- holdout or stronger validation evidence
- at least one reviewable result-draft PR from the autonomous loop
- cautious public narrative and README summary

## Do Not Prioritize Yet

- dashboards;
- web APIs;
- multi-agent orchestration runtime;
- literature ingestion;
- public article or launch work before the autonomy and credibility gates are satisfied;
- new speculative particle-physics formula-search tracks;
- Hubble-tension or broad constants-derivation work;
- heavy storage backends;
- speculative theory-graph features before verification quality improves.

## Handoff Notes

If you are a future LLM or another contributor:

1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/implementation-plan.md`.
4. Run the validation commands above.
5. Prefer the smallest reproducible next step over larger refactors.
