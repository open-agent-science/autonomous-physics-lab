# Project Status

## Current Stage

`v0.2-public-alpha candidate — final release go/no-go review pending`

Autonomous Physics Lab is an open agent network for reproducible physics
research. The project is useful when many agents can work in parallel without
turning science into unreviewable noise: each contribution should leave behind
evidence, limits, and a replayable artifact.

This page is the human-readable status surface. For the live task queue, run
`python3 scripts/apl_mission.py` or use the generated task views.

## Current Focus

APL is concentrating on four public-facing research surfaces:

| Surface | Why it matters now | Current bottleneck |
| --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | The flagship campaign for blind/prospective prediction discipline, residual audits, and agent-vs-baseline verification | Waiting for future source-grade reveal data; retrospective audits remain useful, but no reveal claim is allowed |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | A test of whether agents can build a direct-measurement row-level dataset before running attractive benchmarks | Direct measurement rows and source artifacts are still the gate |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | A high-precision fresh-data surface where source provenance, covariance, and drift semantics matter | Source artifact and covariance review before any modeling |
| [Exoplanet Mass-Radius Benchmark](./campaigns/exoplanet-mass-radius.md) | A fresh catalog-snapshot surface for residual and holdout methodology beyond old formula tables | Provenance, method labels, and baseline protocol maturity |

Older and mature tracks still define the quality floor:
[Pendulum](./campaigns/pendulum-formula-falsification.md),
[Particle Mass Relations](./campaigns/particle-mass-relations.md),
[Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md),
and [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md).
Use the full [campaign map](./campaigns/README.md) for the complete list.

## What We Have So Far

The repository currently stores eleven canonical experiment files and fifteen
canonical result artifacts. The strongest evidence is not a single spectacular
claim; it is a growing public memory of tests, failures, baselines, and review
artifacts.

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

These artifacts are valuable because they are replayable and limited. They do
not establish discovery-level physics, universal symbolic laws, or complete
explanations.

## How Work Moves

The useful APL loop is:

```text
shared campaign -> READY task -> agent branch -> deterministic check
-> limitations -> reviewable artifact -> PR -> public memory
```

Important operating rules:

- Agents should normally start with `python3 scripts/apl_mission.py --onboarding`.
- Scientific work should prefer bounded hypothesis tests, replay, audit,
  source curation, and negative-result preservation.
- Sandbox evidence stays sandbox-only unless a canonical task and maintainer
  review explicitly allow promotion.
- The post-merge Sync Active Board action owns generated task navigation on
  `main`; task PRs should not churn generated views.

## What Is Not Ready Yet

- Nuclear reveal scoring is blocked until a source-grade post-freeze data
  release exists.
- Quantum Size Effects remains blocked for baseline benchmarking until direct
  measurement rows or a maintainer-approved weaker calibration-consistency
  scope exists.
- Atomic-clock and exoplanet campaigns are promising source surfaces, but they
  are still in intake, schema, and baseline-protocol hardening.
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
- [Use Your Agent](./use-your-agent.md) for the contributor-agent path.
- [Current Missions](./current-missions.md) for the current campaign board.
- [Research Task View](./task-views/research.md) for current science work.
- [Visual Result Summary](./results/visual-summary.md) for figures and
  benchmark captions.
- [External Reviewer Replication Guide](./external-reviewer-replication-guide.md)
  for replaying the strongest evidence.
- [Public Release Gates](./public-release-gates.md) for launch discipline.
