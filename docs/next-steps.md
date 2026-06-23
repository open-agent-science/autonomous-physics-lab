# Next Steps

## Purpose

This file is the short operational handoff for the next contributor.

Use it for:

- the immediate next implementation targets;
- the current recommended order of work;
- quick reality checks before starting new changes.

Use [implementation-plan.md](./implementation-plan.md)
for the broader phased strategy.

Use [the task views](task-views/research.md)
for the live task board and actual claimable work.

Use [backlog.md](./backlog.md)
for lower-priority or later work.

Use [future-research-portfolio.md](./future-research-portfolio.md)
to decide whether a scientific direction belongs in `NOW`, `NEXT`, or
`WATCHLIST` before starting a new task branch.

## Current Operational Handoff (2026-06-23)

Use `python3 scripts/apl_mission.py --output onboarding` and
`docs/current-missions.md` for live routing. The current next wave is not a
repeat of the older Nuclear/Quantum/Exoplanet expansion queues; it is a
post-validation gate wave:

- source readiness: close concrete dataset, source, checksum, citation,
  permission, uncertainty, or metric-contract blockers;
- transfer: scout one independent source, material, regime, or dataset route
  before broader generalization;
- ratification: prepare narrowly scoped maintainer decision packets without
  changing claim status;
- external reveal: preserve value-blind/no-peek discipline until a source-grade
  reveal route exists.

The immediate high-signal READY tasks are surfaced by the mission script. As of
this handoff, the core next-wave anchors are Materials `TASK-0809`, Textbook
Wien/FIRAS `TASK-0815`, Quantum `TASK-0810` / `TASK-0816`, Nuclear `TASK-0821`,
Atomic `TASK-0804`, Anharmonic `TASK-0818`, Dimensional `TASK-0807`,
Pendulum `TASK-0814`, Particle Mass `TASK-0820`, and Stellar transfer
`TASK-0819`.

The detailed sections below are historical planning context and quality-floor
memory. They are useful for understanding why the repository arrived here, but
they are not a replacement for the live mission script, canonical task YAML, or
generated task views.

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

## Historical Detail And Background

### 1. Advance Nuclear Through Feature-Term Slates And Reveal Discipline

The nuclear-mass surface campaign has now landed its first complete benchmark
and prediction-registration wave: campaign scaffold, dataset layer, baseline
residual benchmark, structured holdout protocol, sandbox pilots, a deterministic
prediction factory, reusable target batches, and selected prospective registry
entries through `PRED-0068`.

The next scientific goal is not to multiply frozen registry entries casually.
It is to finish reveal-readiness, adversarially stress the strongest scout
families, preserve negative evidence, and let Quantum Size Effects advance only
through measurement-grade row-level data:

- use the completed registry coverage audit, synthetic reveal dry-run, and
  scout synthesis as the map for the next wave;
- use concrete real-source, checksum, no-peek, and partial-reveal criteria
  before any future reveal comparison;
- run bounded adversarial stress lanes for shell-axis and asymmetry-frontier
  candidates without editing the frozen registry;
- package the latest scout evidence so positive and negative outcomes are easy
  to review;
- preserve the no-peek boundary while waiting for future reviewed
  measurements;
- avoid adding more frozen prediction-registry entries until coverage and
  reveal-readiness are reviewed again after the shell-axis mini-wave.

Recent nuclear validation sequence:

- `TASK-0288` shell-axis adversarial stress scout: strongest sandbox signal
  follow-up, focused on `SHELL-SCOUT-003` / `SHELL-SCOUT-005` with sign and
  null controls.
- `TASK-0289` asymmetry-frontier stress scout: secondary Nuclear lane using
  `NR-SCOUT-005` as the required overfit negative control.
- `TASK-0290` nuclear scout evidence card: compact maintainer-facing package
  for the shell-axis signal and mid-mass/isotope-chain negative result.
- `TASK-0295` agent-vs-factory comparison: answer whether agent-designed
  Nuclear scouts add value beyond deterministic factory/grid generation.
- `TASK-0296` shell-axis target-batch design: completed conservative target
  design for `shell-axis-balanced-001`.
- `TASK-0297` shell-axis prospective mini-wave: registers `PRED-0063` through
  `PRED-0068` as frozen prospective records only.
- Future reveal or reveal-scoring tasks must follow the `TASK-0266` protocol
  and the source-readiness checklist instead of ad hoc source comparison
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
  `PRED-0051` through `PRED-0062`, plus the shell-axis mini-wave
  `PRED-0063` through `PRED-0068`.

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
- after the shell-axis mini-wave, do not score or reveal `PRED-0063` through
  `PRED-0068` until a separate source-manifest/no-peek reveal task is approved.
- do not register more scout-derived `PRED-*` entries until the shell-axis
  mini-wave coverage and future reveal-readiness implications are reviewed.
- `TASK-0307` completed as a negative-but-useful source-manifest review: no
  acceptable post-registration source was pinned, so `TASK-0305` remains
  blocked behind a future reviewed source manifest and explicit maintainer
  approval.
- `TASK-0310` completed the first full-known shell-axis retrospective audit as
  sandbox evidence. The next Nuclear wave should not add more `PRED-*`
  entries; it should test the validity domain, coefficient stability, and
  specificity of that signal.
- `TASK-0333` fixed the shell-axis lane as `DIAGNOSTIC_ONLY`: useful sandbox
  evidence, but not a discovery candidate, not a reveal-scoring
  justification, and not a reason to keep slicing the same lane.

Portfolio status: APL should keep at least four active scientific surfaces in
the READY pool when parallel agents are available. Nuclear Mass Surface remains
the flagship validation track, while Quantum Size Effects, Atomic Clock
Residuals, Exoplanet Mass-Radius, Textbook Formula Audit, and future Materials
lanes should carry source, baseline, holdout, and blocker-review work at
different maturity levels.

The next parallel research wave should maintain at least eight independent
scientific `READY` tasks, prefer 15 during larger agent waves, span at least
four surfaces, and avoid letting one campaign hold more than about 40% of the
READY science pool. The current task-queue wave opens fresh lanes instead of
extending the shell-axis audit loop:

- `TASK-0338` for Nuclear deformation-proxy hypothesis testing;
- `TASK-0339` for Nuclear local residual curvature and kink testing;
- `TASK-0340` for Nuclear odd-even by shell-proximity interactions;
- `TASK-0341` for Nuclear measured/extrapolated boundary diagnostics;
- `TASK-0342` for Nuclear uncertainty-weighted residual stability;
- `TASK-0343` for Nuclear high-error cluster hypotheses;
- `TASK-0344` for Atomic Clock covariance and uncertainty semantics;
- `TASK-0345` for Exoplanet PSCompPars snapshot ingestion planning;
- `TASK-0346` for Exoplanet baseline and holdout protocol;
- `TASK-0347` for Quantum alternative direct table source triage;
- `TASK-0351` for Nuclear local-curvature adversarial controls after the
  first strong-but-inconclusive signal;
- `TASK-0352` for a no-leakage local-curvature freeze protocol before any
  predictive use of neighbor-residual features;
- `TASK-0353` is review-ready with the first pinned Exoplanet PSCompPars
  mass-radius snapshot; do not run metrics until it is reviewed and a
  separate baseline task is opened;
- `TASK-0354` for an Exoplanet loader dry run that can proceed in parallel
  with snapshot ingestion;
- `TASK-0355` for one concrete Atomic Clock direct-ratio source-artifact
  review;
- `TASK-0356` for a Quantum direct source-artifact intake path so
  maintainer-provided SI/table files can unblock row curation quickly;
- `TASK-0361` for the first Exoplanet Mass-Radius baseline benchmark on the
  pinned PSCompPars snapshot;
- `TASK-0362` as a blocked follow-up to package the Exoplanet residual
  failure map after baseline metrics exist;
- `TASK-0363` for the Atomic Clock Beloy 2021 source-artifact and covariance
  preflight before direct ratio rows;
- `TASK-0364` for a concrete Quantum PMC/arXiv direct-table source attempt;
- `TASK-0365` as a blocked Nuclear synthesis after uncertainty/high-error/
  local-curvature adversarial lanes finish;
- `TASK-0330` remains the current Atomic Clock direct frequency-ratio source
  review;
- `TASK-0332` remains the current Atomic Clock real-row readiness gate.

For Nuclear, agents should now run many bounded hypothesis lanes in parallel.
Each lane should complete a mini-loop: hypothesis, deterministic feature or
runner, baseline comparison, matched controls, holdout/subset report,
negative-result preservation, and conservative verdict. Do not add `PRED-*`
entries or claim promotion from this wave.

The next prepared campaign is Quantum Size Effects, but it should start from
campaign and data foundations rather than formula search:

- `TASK-0222` has created the Quantum Size Effects campaign scaffold;
- `TASK-0223` and `TASK-0224` have delivered the dataset/source-manifest and
  holdout-protocol foundation;
- `TASK-0275` has delivered the first source-manifest seed;
- `TASK-0281` and `TASK-0282` delivered calibration-derived row-level
  absorption seeds;
- `TASK-0283` reviewed the row-level data surface and kept the first baseline
  blocked because current rows are not direct measurements;
- `TASK-0291` is blocked until direct absorption rows have a reviewed
  table-value or digitisation path; do not use LLM-estimated figure
  coordinates or published sizing-polynomial values;
- `TASK-0292` has a review-only band-edge blocker record: Jasieniak 2011
  appears to contain a suitable Supporting Information table, but a curator
  still needs access to the table values or a deterministic digitisation
  artifact before committing a `qd-*.yaml` band-edge seed;
- `TASK-0325` has preserved the Jasieniak 2011 path as a blocker package,
  because the repository still has no committed SI/table extraction or
  deterministic digitisation artifact for `>=6` direct rows;
- `TASK-0306` has defined the digitisation protocol and artifact requirements
  needed before figure-derived absorption rows can unblock `TASK-0291`; the
  remaining gate is a committed artifact, primary table values,
  maintainer-provided rows, or an explicit waiver;
- `TASK-0293` should re-run the readiness gate after a direct-measurement seed
  lands, or after an explicit maintainer waiver;
- `TASK-0298` triaged direct-measurement source candidates, but later
  absorption work should treat Yu 2003 as requiring digitisation or primary
  tables rather than immediate table-row curation;
- `TASK-0334` has packaged the Jasieniak 2011 source locator and deterministic
  acquisition plan as metadata-only evidence; preserve the blocker until the
  actual SI/table extraction or digitisation artifact is reviewed;
- `TASK-0347` should look for open alternative direct-table or deterministic
  digitisation sources in parallel with any maintainer-provided Jasieniak SI
  path;
- `TASK-0356` defines the local intake path for maintainer-provided or open
  direct source artifacts;
- `TASK-0364` should attempt a single PMC/arXiv direct-table source from the
  TASK-0347 ranking and either curate a small direct seed or preserve a
  blocker without relaxing provenance rules;
- `TASK-0335` should define, not run, the weaker
  `calibration_curve_consistency` benchmark scope;
- `TASK-0336` should stay blocked until `TASK-0334` or an equivalent
  maintainer-provided artifact makes direct band-edge rows reproducible;
- `TASK-0225` is intentionally blocked until reviewed row-level
  `data/quantum_dots/qd-*.yaml` measurement rows exist, or a maintainer waiver
  scopes the first benchmark as calibration-curve consistency;
- `TASK-0276` and `TASK-0277` are queued after `TASK-0225` for visualization
  and readiness review before the autonomous pilot;
- `TASK-0226` remains blocked until the baseline is reviewed;
- `TASK-0227` has landed as a small lepton g-2 cross-observable falsifier and
  remains a guardrail result, not a flagship campaign.

The fourth campaign is now Exoplanet Mass-Radius:

- use `TASK-0337` to create the value-free source manifest template, row
  schema, holdout protocol, and source-surface review;
- `TASK-0353` pinned the first NASA Exoplanet Archive PSCompPars snapshot and
  committed both raw and normalized artifacts;
- do not fetch live NASA Exoplanet Archive data again for downstream
  benchmarks; use the committed snapshot;
- expected later results are baseline reproduction, uncertainty-aware
  residual maps, failure maps by planet class and detection method, and
  negative controls for simple mass-radius formulas.
- use `TASK-0345` to prepare the first PSCompPars pinned-snapshot ingestion
  plan without fetching rows;
- use `TASK-0346` to define the baseline protocol before any agent sees or
  scores row-level catalog values.
- use `TASK-0361` next for the first baseline benchmark, then `TASK-0362` for
  residual/failure-map packaging if the baseline artifact lands cleanly.

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
- [task views](task-views/research.md)
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
