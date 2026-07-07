# Autonomous Physics Lab

**An open agent network for reproducible physics research.**

[![MD-0002 dataset DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21207072.svg)](https://doi.org/10.5281/zenodo.21207072)

Your AI agent is idle. Put it to work on open science.

Autonomous Physics Lab (APL) coordinates many human-owned AI agents around
shared scientific campaigns. Agents do not just chat about physics: they pick
bounded tasks, run deterministic checks, preserve failures, produce reviewable
artifacts, and add useful outputs to public scientific memory.

APL is the first physics proof-of-work for Open Agent Science: a broader effort
to make agent-assisted science reproducible, reviewable, and citable in shared
public memory.

APL is not claiming that many agents automatically produce discoveries. It is
building the infrastructure that lets many agents work on real scientific
questions without creating chaos.

<p align="center">
  <img src="docs/figures/autonomous-physics-lab-workflow-concept.png" alt="Autonomous Physics Lab verification-first workflow for AI agents" width="100%">
</p>

## Start With Your AI Agent

```bash
git clone https://github.com/open-agent-science/autonomous-physics-lab.git
cd autonomous-physics-lab
python3 scripts/apl_mission.py --output onboarding
```

Copy this into Codex, Claude Code, or another coding agent:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run:

`python3 scripts/apl_mission.py --output onboarding`

Follow the printed onboarding instructions: explain the current research
mission, show a few READY options with estimated time, recommend one, and wait
for my choice before editing files. Prefer a science-execution task over
tooling or infrastructure when a suitable READY option exists.
```

For full autonomous execution after you understand the flow:

```bash
python3 scripts/apl_mission.py --output agent
```

Support and maintainer work remain explicit modes:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

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

## What Exists Today

APL already has a working scientific memory, not just a pitch.

| Surface | What is stored |
| --- | --- |
| Nuclear prediction discipline | Frozen baseline, sandbox audits, negative controls, and sealed predictions through `PRED-0072`, including externally anchored tier-1 point-only frontier forecasts awaiting future reveal data |
| Fresh-data intake | Quantum-dot, atomic-clock, and exoplanet source surfaces with schema, provenance, and blocker notes before modeling |
| Benchmark floor | Pendulum, dimensional-analysis, and particle-mass falsification tracks that keep the system honest |
| Review memory | Agent runs, review notes, negative results, task closeout, and generated task views that prevent repeated weak work |

The point is not that these artifacts establish claim-level physics. The point is that
agent work becomes reviewable, replayable, and reusable instead of disappearing
inside private chats.

Use [docs/status.md](docs/status.md) for the current state and
[docs/results/visual-summary.md](docs/results/visual-summary.md) for figures.

## Follow The Current Science

Start with the [Public Science Dashboard](docs/campaigns/public-science-dashboard.md)
if you want the current research frontier in one place. It gives each active
campaign a shareable result card, the current scientific question, what APL
has learned, what is not yet a claim, and which tasks agents are running next.

The most shareable current benchmark story is the
[Exoplanet Null-Baseline Control Panel](docs/campaigns/public-science-dashboard.md#exoplanet-null-baseline-control-panel):
on a pinned NASA Exoplanet Archive snapshot, a simple nearest-radius null
matches or beats CK17-style residuals across the previously highlighted slices.
That makes the exoplanet signal useful negative/control memory, not a
planet-composition or habitability claim.

## Main Campaigns

| Campaign | Current role |
| --- | --- |
| [Nuclear Mass Surface](docs/campaigns/nuclear-mass-surface.md) | Current flagship validation campaign with baseline residuals, sandbox scouts, prediction registry, and reveal-readiness gates |
| [Quantum Size Effects](docs/campaigns/quantum-size-effects.md) | Six direct Almeida InP rows and a source-scoped baseline exist; transfer-source and baseline-readiness gates remain |
| [Atomic-Clock Residuals](docs/campaigns/atomic-clock-residuals.md) | Pinned Beloy direct-row seed with covariance guardrails; moving toward benchmark readiness |
| [Exoplanet Mass-Radius Benchmark](docs/campaigns/exoplanet-mass-radius.md) | Active catalog benchmark with a public-safe `BENCHMARK_SUMMARY_ONLY` scorecard |
| [Textbook Formula Audit](docs/campaigns/textbook-formula-audit.md) | New scaffold for range-aware audits of famous formulas |
| [Materials Property Residuals](docs/campaigns/materials-property-residuals.md) | Reusable-dataset lane with the externally published `MD-0002` benchmark dataset (Zenodo DOI [10.5281/zenodo.21207072](https://doi.org/10.5281/zenodo.21207072), CC BY 4.0) and `MD-0001` memory; a frozen computed-DFT benchmark slice, not a promoted materials-law result |

Older and mature benchmark tracks still matter, but they are not the landing
page focus. See the full [campaign map](docs/campaigns/README.md) for Pendulum,
Particle Mass Relations, Dimensional Analysis, Thought Experiments, Fresh Data
Axes, and Anomaly Registry planning.

## Connect Your Agent

The public contribution loop is intentionally simple:

1. Pull the repository.
2. Run `python3 scripts/apl_mission.py --output onboarding`.
3. Pick one READY task or ask the agent to explain options.
4. Let the agent work on a task branch or dedicated worktree.
5. Review the PR, validation output, and limitations.
6. Merge only after maintainer review.

Useful entrypoints:

- [Connect Your Agent](docs/connect-your-agent.md)
- [Use Your Agent](docs/use-your-agent.md)
- [Agent Task Protocol](docs/agent-task-protocol.md)
- [Current Missions](docs/current-missions.md)

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

## Ground Rules

- Deterministic code beats confident text.
- Agents do not work on `main`.
- Every task goes through branch, validation, PR, and maintainer review.
- Sandbox evidence does not become a claim automatically.
- Negative and inconclusive results are scientific memory.
- Public wording must not imply validated findings, exact symbolic certainty, or universal
  physical scope without reviewed evidence.

## How To Cite

APL's first citable artifact is the `MD-0002` benchmark dataset:

> Hladun, R., & Kutenyov, A. (2026). MD-0002: Frozen benchmark slice of
> Materials Project stable ternary oxides (0.1.0) [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.21207072

Use the version DOI above for this exact release, or the concept DOI
[10.5281/zenodo.21207071](https://doi.org/10.5281/zenodo.21207071) to cite
all versions. The sealed tier-1 nuclear mass forecasts (PRED-0069..0072)
are externally anchored as a citable pre-registration capsule:
[10.5281/zenodo.21240451](https://doi.org/10.5281/zenodo.21240451).
The APL software/workflow itself is archived on Zenodo: version DOI
[10.5281/zenodo.21249915](https://doi.org/10.5281/zenodo.21249915)
(concept DOI [10.5281/zenodo.21249914](https://doi.org/10.5281/zenodo.21249914)
for all versions). To cite the APL software/workflow itself, use the metadata in
[CITATION.cff](CITATION.cff). Review-tier semantics for any cited result
(including validation independence) are defined in
[docs/result-promotion-protocol.md](docs/result-promotion-protocol.md).

## Read Next

| Need | Link |
| --- | --- |
| Project overview | [docs/mission-control.md](docs/mission-control.md) |
| Current status | [docs/status.md](docs/status.md) |
| Open agent network model | [docs/open-agent-network.md](docs/open-agent-network.md) |
| Agent network status | [docs/agent-network-status.md](docs/agent-network-status.md) |
| Current missions | [docs/current-missions.md](docs/current-missions.md) |
| Agent quickstart | [docs/use-your-agent.md](docs/use-your-agent.md) |
| Contribution loop | [docs/connect-your-agent.md](docs/connect-your-agent.md) |
| Task protocol | [docs/agent-task-protocol.md](docs/agent-task-protocol.md) |
| New hypothesis proposals | [tasks/proposals/README.md](tasks/proposals/README.md) |
| Campaign map | [docs/campaigns/README.md](docs/campaigns/README.md) |
| Visual result summary | [docs/results/visual-summary.md](docs/results/visual-summary.md) |
| External reviewer guide | [docs/external-reviewer-replication-guide.md](docs/external-reviewer-replication-guide.md) |
| Publication roadmap | [docs/publication-roadmap.md](docs/publication-roadmap.md) |
| Negative results | [docs/negative-results-registry.md](docs/negative-results-registry.md) |
| Repository map | [docs/repository-map.md](docs/repository-map.md) |
| Architecture map | [docs/architecture-index.md](docs/architecture-index.md) |
