# Project Status

## Current Stage

`v0.2-public-alpha live — soft-launch stabilization`

Autonomous Physics Lab is the first physics proof-of-work for Open Agent
Science: an open agent network for reproducible, reviewable, citable scientific
memory. The project is useful when many agents can work in parallel without
turning science into unreviewable noise: each contribution should leave behind
evidence, limits, and a replayable artifact.

This page is the human-readable status surface. For the live task queue, run
`python3 scripts/apl_mission.py` or use the generated task views.

If you are deciding where to help, use this page for orientation and then let
`python3 scripts/apl_mission.py --output onboarding` choose from live `READY` tasks.
This page should motivate the work; the task registry decides what is actually
available.

For linkable, public-safe summaries of active campaign results, use the
[Public Science Dashboard](./campaigns/public-science-dashboard.md).

## Current Focus

APL is concentrating on seven public-facing research surfaces. The current
center of gravity is the Materials/Stellar/ThermoML result-validation wave,
while Nuclear remains the highest-ambition flagship and several other campaigns
stay explicitly source- or trigger-gated.

| Surface | Why it matters now | Current bottleneck |
| --- | --- | --- |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | A source-pinned reusable-dataset benchmark lane with `MD-0001` memory and AGENT_VALIDATED `MD-0002` formation-energy `RESULT-0021` | External release/DOI remains a maintainer decision; next useful work is deterministic archive-package dry run, not new Materials metrics |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | A public-friendly verifier campaign with exact-reference fixtures, AGENT_VALIDATED Stellar M-L `RESULT-0022`, AGENT_VALIDATED FIRAS/Wien `RESULT-0023`, and high-mass transfer `RESULT-0024` replay memory | RESULT-0023 needs safe ratification wording; RESULT-0024 needs metadata-caveat repair or an explicit accepted-caveat path; no universal textbook-law wording |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | The flagship validation challenge with negative/control memory, `RESULT-0025` point-estimator evidence, uncertainty blockers, and DZ10 parity scaffolding | Prediction freeze is still blocked; next useful work is no-peek uncertainty calibration and source-rights-safe DZ10 parity, not broad new fitting |
| [Exoplanet Mass-Radius Benchmark](./campaigns/exoplanet-mass-radius.md) | A public-safe catalog benchmark showing residual maps, matched controls, and no-go decisions on pinned snapshots | Current snapshot stays monitor-only; negative RESULT packaging is also blocked by missing canonical experiment/hypothesis identity |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | A test of whether agents can build source-pinned row-level datasets before running attractive benchmarks | ZnSe source route is ready only as limited factual rows; the next step is frozen-row transfer readiness, not correction search |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | A high-precision fresh-data surface where source provenance, covariance, and version-drift semantics matter | Beloy rows exist, Pizzocaro remains diagnostic, and McGrew/NIST needs primary-ratio plus independence adjudication before rows |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | A source-pinned ThermoML `Tb` benchmark lane with AGENT_PUBLISHED `RESULT-0026`, frozen Joback baseline, and bounded failed-family memory | Gate B replay remains needed; expansion is gated by rights plus local-only identity/count feasibility, not broad property claims |

Older and mature tracks still define the quality floor:
[Pendulum](./campaigns/pendulum-formula-falsification.md),
[Particle Mass Relations](./campaigns/particle-mass-relations.md),
[Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md),
and [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md).
Use the full [campaign map](./campaigns/README.md) for the complete list.

## What We Have So Far

The repository currently stores nineteen canonical experiment files and
twenty-six canonical result artifacts. The strongest evidence is not a single
spectacular claim; it is a growing public memory of tests, failures, baselines,
and review artifacts.

Highlights:

- [Pendulum Gauntlet 100](./results/pendulum-gauntlet-100-summary.md) is still
  the cleanest deterministic benchmark: exact reference, many candidates,
  visible error modes, and stored leaderboard.
- [Dimensional Analysis Validator MVP](../results/EXP-0006/RUN-0006/report.md)
  provides a compact formula sanity-check floor.
- [Koide charged-lepton reproduction](./results/koide-charged-lepton-reproduction.md),
  [tau holdout](./results/koide-tau-holdout.md), and the
  [negative results registry](./negative-results-registry.md) keep the
  particle-mass track falsification-first instead of hype-first.
- [Nuclear Mass Baseline](./results/nuclear-mass-baseline-summary.md) and
  [Nuclear Mass Pilot Summary](./results/nuclear-mass-pilot-summary.md) form
  the current flagship evidence surface, but follow-up candidates remain
  sandbox-only unless reviewed and promoted by a maintainer.
- `PRED-0001` through `PRED-0068` are frozen prospective nuclear predictions
  awaiting future maintainer-reviewed reveal data. They are forecasts, not
  current scientific wins.
- The newest Nuclear controls-first lanes are useful sandbox memory, but not
  positive candidates: pairing-asymmetry and magic-parity interaction controls
  regress the frozen baseline, while isotope-chain leave-family-out transfer is
  mixed and chain-local.
- Exoplanet Mass-Radius now has a pinned PSCompPars snapshot, an inconclusive
  first baseline benchmark, residual/failure-map audits, a compact-radius
  matched-control diagnostic, a mass-quartile scout that is underpowered at
  quartile resolution, a second-snapshot target freeze, an external-reviewer
  replication capsule, a `BENCHMARK_SUMMARY_ONLY` scorecard, and a
  null-baseline family audit showing the highlighted slices are
  control-sensitive. This is the strongest current public-safe benchmark
  surface, not a claim about planet composition.
- Atomic-Clock Residuals now has Beloy 2021 / BACON pinned as sandbox-only
  direct frequency-ratio rows, a deterministic real-row loader, a synthetic
  cross-source dry run, the correct Nemitz 2016 source artifact pinned with
  rows blocked, a first-benchmark covariance policy, Pizzocaro per-window
  diagnostics, and a feasible source-derived PSD covariance-approximation path.
  It is still not a benchmark or constants-drift result.
- Textbook Formula Audit has a scaffold, ranked candidate slate,
  exact-reference fixtures, a Gate-B-validated Stefan-Boltzmann
  software/convention result, AGENT_VALIDATED Stellar M-L `RESULT-0022`,
  AGENT_VALIDATED FIRAS/Wien self-consistency `RESULT-0023`, and high-mass
  transfer `RESULT-0024` replay memory with a metadata caveat. These are
  controlled benchmark surfaces, not universal formula or stellar-evolution
  claims.
- Materials Property Residuals has `MD-0001`, source-pinned dataset memory, and
  AGENT_VALIDATED `MD-0002` formation-energy `RESULT-0021`. The result is a
  computed-DFT, frozen-slice benchmark artifact, not a material recommendation,
  synthesis guide, experimental measurement, or materials-law claim. Repository
  release metadata is now closed; external archive/DOI release remains a
  maintainer-gated decision.
- Thermophysical Property Residuals starts from ThermoML `Tb` `RESULT-0026`,
  an AGENT_PUBLISHED bounded Joback transfer benchmark on a 40-row
  family-stratified fixture. Aggregate transfer is positive in scope, but the
  esters/lactones family fails its margin and is now preserved as negative
  memory; Gate B replay is still required.

These artifacts are valuable because they are replayable and limited. They do
not establish claim-level physics, universal symbolic laws, or complete
explanations.

## How Work Moves

The useful APL loop is:

```text
shared campaign -> READY task -> agent branch -> deterministic check
-> limitations -> reviewable artifact -> PR -> public memory
```

Important operating rules:

- Agents should normally start with `python3 scripts/apl_mission.py --output onboarding`.
- Scientific work should prefer bounded hypothesis tests, replay, audit,
  source curation, and negative-result preservation.
- Sandbox evidence stays sandbox-only unless a canonical task and maintainer
  review explicitly allow promotion.
- The post-merge Sync Active Board action owns generated task navigation on
  `main`; task PRs should not churn generated views.

## What Is Not Ready Yet

- Nuclear reveal scoring is blocked until a source-grade post-freeze data
  release exists.
- Quantum Size Effects has a source-scoped Almeida InP sandbox baseline, but
  open-ended correction search remains blocked. The live blockers are the
  ZnSe/Toufanian source-license route and the need to preserve the failed
  effective-mass transfer check as scoped negative/control memory.
- Atomic-clock work is pinned-dataset but not `BASELINE_READY`; it still needs
  admitted independent rows or an approved aggregation/harmonization contract
  before any Yb/Sr consistency benchmark.
- Exoplanet residual scoring is closed on the current snapshot; it needs a
  materially changed pinned snapshot or approved `EXO-0003` trigger before
  another residual audit.
- Materials and Stellar now need external-release or maintainer-review
  decisions, not broader benchmark expansion. Their validated/replayed
  artifacts do not support broad property-law, material-design,
  universal-formula, or application-domain claims.
- Thermophysical work is active but narrow: `RESULT-0026` is `Tb`-only,
  AGENT_PUBLISHED, and not yet independently replayed. Do not broaden to `Tc`
  or other ThermoML properties before a separate leakage and source gate.
- Anomaly Registry and Fresh Physics Data Axes are planning layers, not broad
  fit campaigns.

## Current Risks

- Public launch pressure can outrun wording discipline.
- Formula-search tracks can become numerology if source, holdout, and
  multiple-testing gates are relaxed.
- Too many agents can duplicate work unless tasks stay bounded and generated
  task views stay current.
- Strong negative results must remain visible; otherwise agents will keep
  rediscovering weak directions.

## Useful Entry Points

- [Mission Control](./mission-control.md) for project-level orientation.
- [Open Agent Network](./open-agent-network.md) for the coordination model.
- [Connect Your Agent](./connect-your-agent.md) for the practical contribution
  loop.
- [Use Your Agent](./use-your-agent.md) for the contributor-agent path.
- [Current Missions](./current-missions.md) for the current campaign board.
- [Research Task View](./task-views/research.md) for current science work.
- [Scientific Memory Review Tiers](./scientific-memory-review-tiers.md) for
  `AGENT_PUBLISHED`, `AGENT_VALIDATED`, maintainer-reviewed, externally
  replicated, and legacy evidence visibility.
- [Visual Result Summary](./results/visual-summary.md) for figures and
  benchmark captions.
- [External Reviewer Replication Guide](./external-reviewer-replication-guide.md)
  for replaying the strongest evidence.
- [Public Release Gates](./public-release-gates.md) for launch discipline.
- [Publication Roadmap](./publication-roadmap.md) for citation, DOI, reusable
  dataset, and citable-output planning.
- [Final v0.2 Public-Alpha Signoff](./reviews/v0.2-public-alpha-final-signoff-2026-05-31.md)
  for the current release-gate review artifact.
