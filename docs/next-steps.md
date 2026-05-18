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

Use [future-research-portfolio.md](./future-research-portfolio.md)
to decide whether a scientific direction belongs in `NOW`, `NEXT`, or
`WATCHLIST` before starting a new task branch.

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

### 1. Advance Nuclear Through Feature-Term Slates And Reveal Discipline

The nuclear-mass surface campaign has now landed its first complete benchmark
and prediction-registration wave: campaign scaffold, dataset layer, baseline
residual benchmark, structured holdout protocol, sandbox pilots, a deterministic
prediction factory, reusable target batches, and selected prospective registry
entries through `PRED-0062`.

The next scientific goal is not to multiply frozen registry entries casually.
It is to audit the registry, dry-run the reveal machinery on synthetic sources,
keep three disjoint Nuclear scout lanes available for parallel agents, and let
Quantum Size Effects become the next near-term benchmark-result surface:

- audit coverage across coefficient-only, manual, and feature-term prediction
  families;
- test reveal protocol mechanics on synthetic/fake data only;
- run bounded shell-neighborhood, neutron-rich, and pairing/odd-even scout
  lanes as sandbox work without editing the frozen registry;
- preserve the no-peek boundary while waiting for future reviewed
  measurements;
- avoid adding more frozen prediction-registry entries until coverage and
  reveal-readiness issues are understood.

Recommended nuclear validation queue for parallel agents:

- `TASK-0174` nuclear pilot evidence card and visual funnel, now merged
- `TASK-0188` post-AME2020 time-split guard, complete in conservative
  source-manifest-only mode with no active benchmark metrics
- `TASK-0196` reviewed row-level post-AME2020 nuclear mass holdout dataset,
  now merged
- `TASK-0197` real post-AME2020 nuclear time-split benchmark, now merged as
  inconclusive `AGENT-RUN-0008` evidence
- `TASK-0189` nuclear prediction registry policy, now merged
- `TASK-0200` bounded shell-aware nuclear sandbox batch
- `TASK-0201` bounded pairing / odd-even nuclear sandbox batch, now merged
- `TASK-0202` bounded neutron-rich nuclear sandbox batch
- `TASK-0204` adversarial review of the completed second-batch sandbox outputs,
  now merged
- `TASK-0205` first prospective nuclear-mass prediction registry entries, now
  merged as `PRED-0001` through `PRED-0020`
- `TASK-0228` through `TASK-0237` nuclear prediction variant expansion wave:
  ten parallel lanes where agents add and pre-reveal validate their own bounded
  `PRED-0021+` variants without live external fetch or claim promotion; the
  unfinished manual lanes are now fallback work behind the factory-first path
- `TASK-0249` nuclear prediction variant factory: automate the repetitive
  coefficient-grid / target-batch inner loop so agents curate and review a
  smaller selected slate instead of hand-generating every candidate
- `TASK-0250` first factory-generated slate: create and review 30-80 draft
  candidates without committing raw draft PRED YAML
- `TASK-0252` factory tooling expansion: add feature-term variants before
  scaling registry commits; `TASK-0253` ranking helper is already merged and
  should be used by `TASK-0250`
- `TASK-0254` target-batch library: now merged; future slates should reuse the
  reviewed target batches instead of copying ad hoc target lists
- `TASK-0251` selected factory registry wave: now merged as `PRED-0041`
  through `PRED-0050`, using reviewed coefficient-transform slate-001
- `TASK-0265` selected feature-term registry wave: merged in PR #367 as
  `PRED-0051` through `PRED-0062`; still needs routine task closeout if the
  generated board shows `REVIEW_READY`
- `TASK-0272` registry coverage audit: next primary Nuclear audit task before
  adding more variants
- `TASK-0273` synthetic reveal dry-run harness: test reveal protocol mechanics
  without real measurement data
- `TASK-0274` registry status/evidence summary: make the post-`PRED-0062`
  campaign state legible without validation claims
- `TASK-0278` shell-neighborhood variant scout: let an agent generate and test
  bounded shell/magic-number candidates in sandbox without adding PRED entries
- `TASK-0279` neutron-rich variant scout: let an agent test bounded
  neutron-excess/asymmetry candidates in sandbox without adding PRED entries
- `TASK-0280` pairing and odd-even variant scout: let an agent test bounded
  pairing/parity/staggering candidates in sandbox without adding PRED entries
- Future reveal or reveal-scoring tasks must follow the `TASK-0266` protocol
  checklist instead of ad hoc source comparison
- `TASK-0203` post-AME2020 time-split failure-mode analysis
- `TASK-0178` broad second nuclear sandbox batch remains blocked as an
  umbrella; keep broad sandbox expansion behind factory-slate and
  reveal protocol review

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
  measurements are compared;
- the current prospective registry includes `PRED-0001` through `PRED-0030`,
  `PRED-0037`, `PRED-0038`, selected coefficient-transform factory entries
  `PRED-0041` through `PRED-0050`, and selected feature-term entries
  `PRED-0051` through `PRED-0062`.

The nuclear queue should stay conservative:

- no universal mass-formula claims;
- no discovery framing;
- explicit baseline comparison, holdout discipline, and negative-result preservation.
- parallel science lanes are encouraged across different campaigns and within
  the same campaign, but each lane must use a separate branch/worktree,
  disjoint hypothesis family or artifact surface, and sandbox-only outputs;
- no broad second nuclear sandbox batch from `TASK-0178`; use the factory
  path for bounded expansion and keep future reveal comparison in a separate
  reviewed task.
- after the post-`PRED-0062` registry status summary, use `TASK-0285`,
  `TASK-0286`, and `TASK-0287` as the next Nuclear Mass Surface wave:
  synthesize scout evidence, probe mid-mass/isotope-chain gaps, and define
  source-readiness before any real reveal.
- do not register scout-derived `PRED-*` entries until the scout synthesis and
  reveal source-readiness work are reviewed.

Portfolio status: Nuclear Mass Surface is the only `NOW` scientific flagship.
Use the portfolio document before moving any other scientific direction into
active work.

The next prepared campaign is Quantum Size Effects, but it should start from
campaign and data foundations rather than formula search:

- `TASK-0222` has created the Quantum Size Effects campaign scaffold;
- `TASK-0223` and `TASK-0224` have delivered the dataset/source-manifest and
  holdout-protocol foundation;
- `TASK-0275` has delivered the first source-manifest seed;
- `TASK-0281` and `TASK-0282` should run next as parallel row-level
  absorption-data curation tasks;
- `TASK-0283` should review the row-level data surface and only then unblock
  the first baseline;
- `TASK-0225` is intentionally blocked until reviewed row-level
  `data/quantum_dots/qd-*.yaml` measurement rows exist; the source manifest
  alone is not benchmark data;
- `TASK-0276` and `TASK-0277` are queued after `TASK-0225` for visualization
  and readiness review before the autonomous pilot;
- `TASK-0226` remains blocked until the baseline is reviewed;
- `TASK-0227` has landed as a small lepton g-2 cross-observable falsifier and
  remains a guardrail result, not a flagship campaign.

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
- muon g-2 follow-up outside guarded review or stress-test framing;
- broad all-mass relation searches;
- heavy storage backends;
- speculative theory-graph features before verification quality improves.

## Handoff Notes

If you are a future LLM or another contributor:

1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/implementation-plan.md`.
4. Run the validation commands above.
5. Prefer the smallest reproducible next step over larger refactors.
