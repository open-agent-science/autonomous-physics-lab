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

### 1. Finish the Autonomous Research Foundation First

The next major proof point is not a public article or a broader roadmap. It
is one real autonomous loop that produces reviewable sandbox research PR
artifacts without promoting claims automatically.

Current highest-value foundation tasks:

- `TASK-0151` autonomous research loop contract and campaign profiles
- `TASK-0152` proposal preflight gate and sandbox agent-run layout
- `TASK-0154` agent-run PR packaging and maintainer review checklist

Success looks like:

- agents can generate hypothesis and experiment proposals under repository rules;
- weak proposals fail deterministically before sandbox execution;
- sandbox evidence stays outside canonical `results/` until review;
- maintainers can review one agent-run PR without re-reading raw sandbox files manually.

### 2. Raise Scientific Credibility Before Any Public Story

The strongest near-term credibility gains are:

- `TASK-0149` blind holdout benchmark protocol
- `TASK-0148` scientific result quality rubric
- `TASK-0146` one-command core result reproduction script

These tasks improve the repository more than another speculative benchmark
would. They make future autonomous work easier to trust and easier to replay.

### 3. Run the First Autonomous Pilots Only After Foundation Work

After `TASK-0151` and `TASK-0152` are complete, the next pilots should be:

- `TASK-0153` first pendulum autonomous research pilot
- `TASK-0155` second dimensional-validator autonomous pilot

The pendulum pilot should be the first real autonomy demo because it has exact
references, low numerology risk, and clear failure modes.

### 4. Add a Stronger Non-Numerological Benchmark Path

To raise scientific value without drifting into muon g-2, Hubble, or broad
particle numerology, prefer nonlinear mechanics:

- `TASK-0159` anharmonic oscillator period benchmark
- `TASK-0160` autonomous anharmonic research pilot

This path should stay behind the autonomy foundation and holdout protocol, but
it is the best current candidate for a richer benchmark with lower overclaim
risk.

### 5. Keep Docs and Gates Aligned

Always keep these files aligned when priorities change:

- [status.md](./status.md)
- [strategy.md](./strategy.md)
- [../tasks/ACTIVE.md](../tasks/ACTIVE.md)
- [public-release-gates.md](./public-release-gates.md)
- [private-contributor-pilot.md](./private-contributor-pilot.md)

### 6. Public Release Remains Gated

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
