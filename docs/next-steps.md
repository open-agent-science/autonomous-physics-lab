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

### 1. Strengthen Nuclear Validation Before More Batches

The nuclear-mass surface campaign has now landed its first complete wave:
campaign scaffold, dataset layer, baseline residual benchmark, structured
holdout protocol, and one sandbox-only autonomous residual pilot.

The next scientific goal is not to multiply residual formulas. It is to harden
the evidence boundary around the current nuclear surface:

- package the current pilot evidence without claim promotion;
- finish independent audit and split-sensitivity interpretation;
- turn the post-AME2020 source manifest into reviewed row-level holdout data;
- evaluate the frozen baseline and sandbox candidates on that row-level
  time-split surface;
- define a robustness gate before allowing another autonomous nuclear batch;
- add a prediction registry only for future before-measurement predictions.

Recommended nuclear validation queue:

- `TASK-0174` nuclear pilot evidence card and visual funnel, now merged
- `TASK-0188` post-AME2020 time-split guard, complete in conservative
  source-manifest-only mode with no active benchmark metrics
- `TASK-0196` reviewed row-level post-AME2020 nuclear mass holdout dataset,
  now merged
- `TASK-0197` real post-AME2020 nuclear time-split benchmark, now
  review-ready as `AGENT-RUN-0008`
- `TASK-0189` nuclear prediction registry policy
- `TASK-0178` second nuclear sandbox batch, blocked until the robustness gate,
  row-level holdout dataset, and real time-split benchmark all pass review

Current nuclear-mass baseline state:

- `EXP-0012` / `RESULT-0015` now exist as the first reviewable baseline
  residual surface;
- the best current model is the slice-fitted semi-empirical baseline with
  `2.825 MeV` overall MAE and `2.449 MeV` magic-subset MAE on `NMD-0002`;
- `TASK-0169` now defines the required structured holdout contract for random,
  isotope-chain, magic-region, and neutron-rich evaluation;
- the campaign now has one sandbox-only autonomy package under
  `AGENT-RUN-0005`;
- `TASK-0170` is complete, so any nuclear-mass continuation should be a new
  maintainer-reviewed comparison, dataset-expansion, or curation task rather
  than automatic result promotion.
- post-AME2020 measured masses are now treated as retrospective time-split
  evidence through `AGENT-RUN-0008`, not as strict blind prediction;
- `AGENT-RUN-0007` is useful guard evidence, but it is not an active
  post-AME2020 benchmark result;
- `AGENT-RUN-0008` is useful active retrospective time-split evidence, but it
  is inconclusive and does not promote `HYP-PROPOSAL-0021` or any negative
  control;
- prospective prediction requires a registry entry created before later
  measurements are compared.

The nuclear queue should stay conservative:

- no universal mass-formula claims;
- no discovery framing;
- explicit baseline comparison, holdout discipline, and negative-result preservation.
- no second nuclear sandbox batch until `TASK-0173`, `TASK-0190`, `TASK-0196`,
  and `TASK-0197` are done and maintainer review allows follow-up.

### 2. Validate Private Contributors And Agents

The workflow-validation goal remains important, but it should now run alongside
the harder nuclear evidence queue rather than replacing it.

This phase should test whether contributors can understand APL from repository
instructions, follow task and branch protocol, produce reviewable artifacts,
pass CI, survive maintainer review, and complete closeout without automatic
claim promotion.

Recommended private-validation queue:

- `TASK-0172` private contributor and agent validation plan
- `TASK-0173` independent replay and audit of `HYP-PROPOSAL-0021`
- `TASK-0175` public-facing docs sync after the nuclear wave
- `TASK-0177` private agent challenge pack

Target evidence before broader opening:

- 3 to 5 contributors using agents;
- 10 or more task-based PRs;
- 3 or more scientific sandbox PRs;
- 2 or more technical, docs, or test PRs;
- 2 or more independent replay or audit PRs;
- zero direct pushes to `main`;
- zero automatic claim promotions;
- zero dirty active-board sync after merge;
- zero public-facing local path leaks;
- green GitHub CI on the release-candidate branch.

Also clear the remaining open workflow-maintenance PRs and keep the active
board synchronized:

- `TASK-0115` docs-link integrity check
- `TASK-0116` microtask queue summary generator
- `TASK-0117` maintainer review and closeout flow diagram
- `TASK-0136` validation and scientific-memory integrity split

### 3. Keep Anharmonic and Pendulum Work as Methodological Proof

Pendulum and anharmonic work remain useful as proof that the autonomy loop,
benchmark framing, and maintainer review workflow can function end to end.

The next step is not "more approximation for its own sake." It is to keep the
same protocol visible across every follow-up campaign:

- hypothesis proposals
- preflight gate
- sandbox runs
- holdout evaluation
- negative controls
- reviewable PRs

### 4. Preserve Replay and Validation Quality

The scientific credibility layer now includes the merged holdout protocol and
result-quality rubric. The next hardening work should keep repository
validation and replay surfaces easy to trust:

- `TASK-0136` split repository validation and scientific-memory integrity checks
- `TASK-0137` split maintainer review helper into clearer policy layers
- `TASK-0138` add canonical replay and golden-result hardening layer

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
