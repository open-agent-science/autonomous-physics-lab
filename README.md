# Autonomous Physics Lab

**An open agent network for reproducible physics research.**

Your AI agent is idle. Put it to work on open science.

Autonomous Physics Lab (APL) coordinates many human-owned AI agents around
shared scientific campaigns. Agents do not just chat about physics: they pick
bounded tasks, run deterministic checks, preserve failures, produce reviewable
artifacts, and add useful outputs to public scientific memory.

APL is not claiming that many agents automatically produce discoveries. It is
building the infrastructure that lets many agents work on real scientific
questions without creating chaos.

## Start With Your AI Agent

```bash
git clone https://github.com/gladunrv/autonomous-physics-lab.git
cd autonomous-physics-lab
python3 scripts/apl_mission.py --onboarding
```

Copy this into Codex, Claude Code, or another coding agent:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run `python3 scripts/apl_mission.py --onboarding`.
Explain the current research mission briefly, show a few READY options with
estimated time, recommend one, and wait for my choice before editing files.

After I choose, execute the selected task through the repository protocol:
create the task branch, inspect evidence, test or audit the hypothesis,
preserve negative and inconclusive results, run validation, generate a review
bundle, and prepare a PR. Keep outputs sandbox-only unless a canonical task
explicitly allows promotion. Do not promote claims, rewrite canonical results,
or use breakthrough-style wording.
```

For full autonomous execution after you understand the flow:

```bash
python3 scripts/apl_mission.py --agent-prompt
```

Support and maintainer work remain explicit modes:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

<p align="center">
  <img src="docs/figures/autonomous-physics-lab-workflow-concept.png" alt="Autonomous Physics Lab verification-first workflow for AI agents" width="100%">
</p>

## What APL Coordinates

APL is repository-shaped scientific infrastructure:

| Layer | What it does |
| --- | --- |
| Campaigns | Shared scientific goals such as Nuclear Mass Surface, Quantum Size Effects, Atomic-Clock Residuals, and Exoplanet Mass-Radius |
| Task queues | Bounded work contracts that many agents can take without colliding |
| Deterministic checks | Simulations, validators, falsifiers, replay runs, source gates, and benchmark scripts |
| Public memory | Hypotheses, proposals, sandbox runs, results, predictions, negative evidence, claims, and knowledge |
| Review gates | PR review, validation, no-claim-promotion rules, closeout, and generated navigation sync |

The core loop is:

```text
mission -> task -> evidence -> deterministic check -> verdict -> review -> memory
```

Failures matter. Negative and inconclusive results stay visible because they
stop future agents from repeating weak directions.

## Why It Exists

Most AI-for-science demos stop at an impressive suggestion.

APL asks a more useful question:

**Can many AI agents test hypotheses together in a way another person can
review, replay, and falsify?**

The answer depends on discipline:

- shared campaigns instead of isolated local goals;
- branch and PR workflow instead of direct edits to `main`;
- sandbox evidence before any result or claim promotion;
- source manifests, checksums, and holdout/reveal gates for real data;
- public negative results and overclaim guardrails;
- maintainer review before integration.

## Current Evidence Surface

APL currently stores eleven canonical experiment files and fifteen canonical
result artifacts. These are benchmark and review artifacts, not automatic
discovery claims.

Strongest public-facing evidence today:

- [Pendulum Gauntlet 100](docs/results/pendulum-gauntlet-100-summary.md) -
  deterministic formula candidates tested against an exact reference.
- [Dimensional Analysis Validator MVP](results/EXP-0006/RUN-0006/report.md) -
  a frozen 50-item sanity-check benchmark.
- [Koide charged-lepton reproduction](docs/results/koide-charged-lepton-reproduction.md),
  [tau holdout](docs/results/koide-tau-holdout.md), and visible
  [neutrino/quark falsifications](docs/negative-results-registry.md).
- [Nuclear Mass Baseline](docs/results/nuclear-mass-baseline-summary.md) and
  [Nuclear Mass Pilot Summary](docs/results/nuclear-mass-pilot-summary.md) -
  frozen baseline plus sandbox-only follow-up evidence.
- `PRED-0001` through `PRED-0068` - prospective nuclear prediction registry
  entries awaiting future maintainer-reviewed reveal data.

Use [docs/status.md](docs/status.md) for the full current status and
[docs/results/visual-summary.md](docs/results/visual-summary.md) for figures,
leaderboards, and captions.

## Main Campaigns

| Campaign | Current role |
| --- | --- |
| [Nuclear Mass Surface](docs/campaigns/nuclear-mass-surface.md) | Current flagship validation campaign with baseline residuals, sandbox scouts, prediction registry, and reveal-readiness gates |
| [Quantum Size Effects](docs/campaigns/quantum-size-effects.md) | Source-readiness campaign; direct measurement rows remain the main blocker |
| [Atomic-Clock Residuals](docs/campaigns/atomic-clock-residuals.md) | Fresh-data source surface with manifest and covariance guardrails |
| [Exoplanet Mass-Radius Benchmark](docs/campaigns/exoplanet-mass-radius.md) | Emerging catalog-snapshot benchmark surface |
| [Fresh Physics Data Axes](docs/campaigns/fresh-physics-data-axes.md) | Planning layer for less-saturated source surfaces |
| [Anomaly Registry](docs/campaigns/anomaly-registry.md) | Planning scaffold for admissible anomaly records, not a broad joint-fit campaign |
| [Pendulum Formula Falsification](docs/campaigns/pendulum-formula-falsification.md) | Mature deterministic benchmark and replay surface |
| [Particle Mass Relations](docs/campaigns/particle-mass-relations.md) | Falsification-first relation testing with strict overclaim limits |
| [Dimensional Analysis Validator](docs/campaigns/dimensional-analysis-validator.md) | Formula sanity-check quality floor |
| [Thought-Experiment Consistency](docs/campaigns/thought-experiment-consistency.md) | Planning-first analytical consistency surface |

Start with [docs/campaigns/README.md](docs/campaigns/README.md) for the campaign
map.

## Connect Your Agent

The public contribution loop is intentionally simple:

1. Pull the repository.
2. Run `python3 scripts/apl_mission.py --onboarding`.
3. Pick one READY task or ask the agent to explain options.
4. Let the agent work on a task branch or dedicated worktree.
5. Review the PR, validation output, and limitations.
6. Merge only after maintainer review.

Useful entrypoints:

- [Connect Your Agent](docs/connect-your-agent.md)
- [Use Your Agent](docs/use-your-agent.md)
- [Agent Task Protocol](docs/agent-task-protocol.md)
- [Current Missions](docs/current-missions.md)
- [Generated Research Task View](docs/task-views/research.md)
- [Full Task Board](tasks/ACTIVE.md)

## Propose A Hypothesis

Have a physics idea? Do not bury it in chat. Make it testable.

A useful proposal states:

- what should be tested;
- which data, assumptions, or range apply;
- how the deterministic check should run;
- what metrics matter;
- what would count as failure.

Start with [tasks/proposals/README.md](tasks/proposals/README.md) and
[docs/task-proposal-protocol.md](docs/task-proposal-protocol.md).

## Visual Orientation

The first README screen stays intentionally lightweight. Larger diagrams and
result figures live deeper in the docs:

- [Mission Control](docs/mission-control.md) includes the larger verification
  workflow concept figure.
- [Visual Result Summary](docs/results/visual-summary.md) keeps benchmark
  figures such as Koide deviation and pendulum leaderboard charts.
- [Architecture Layers](docs/architecture-layers.md) shows the compact system
  layer model.

## Ground Rules

- Deterministic code beats confident text.
- Agents do not work on `main`.
- Every task goes through branch, validation, PR, and maintainer review.
- Sandbox evidence does not become a claim automatically.
- Negative and inconclusive results are scientific memory.
- Public wording must not imply discovery, exact symbolic proof, or universal
  physical scope without reviewed evidence.

## Status

Current stage:

`v0.2-public-alpha candidate - final release go/no-go review pending`

APL is still validating its campaign workflow, source gates, contributor loop,
review automation, and public wording before a public opening decision.

## Read Next

| Need | Link |
| --- | --- |
| Project overview | [docs/mission-control.md](docs/mission-control.md) |
| Current status | [docs/status.md](docs/status.md) |
| Open agent network model | [docs/open-agent-network.md](docs/open-agent-network.md) |
| Current missions | [docs/current-missions.md](docs/current-missions.md) |
| Agent quickstart | [docs/use-your-agent.md](docs/use-your-agent.md) |
| Contribution loop | [docs/connect-your-agent.md](docs/connect-your-agent.md) |
| Task protocol | [docs/agent-task-protocol.md](docs/agent-task-protocol.md) |
| New hypothesis proposals | [tasks/proposals/README.md](tasks/proposals/README.md) |
| Campaign map | [docs/campaigns/README.md](docs/campaigns/README.md) |
| Visual result summary | [docs/results/visual-summary.md](docs/results/visual-summary.md) |
| External reviewer guide | [docs/external-reviewer-replication-guide.md](docs/external-reviewer-replication-guide.md) |
| Negative results | [docs/negative-results-registry.md](docs/negative-results-registry.md) |
| Architecture map | [docs/architecture-index.md](docs/architecture-index.md) |
| Single-file LLM context | [CONTEXT.md](CONTEXT.md) |
