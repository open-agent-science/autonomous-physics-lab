# Autonomous Physics Lab

<p align="center">
  <img src="docs/figures/autonomous-physics-lab-workflow-concept.png" alt="Autonomous Physics Lab verification-first workflow for AI agents" width="100%">
</p>

Generate. Simulate. Falsify. Reuse.

Autonomous Physics Lab (APL) is an open-source infrastructure for generating,
testing, simulating, falsifying, and reusing physics hypotheses.

APL is not a chatbot. It is a verification-first engine for testing physics
ideas.

## Start With Your AI Agent

APL is now **Agent First**: the default path for Codex, Claude Code, or another
coding agent is a research mission, not a random support task.

Run:

```bash
python3 scripts/apl_mission.py
```

This starts Research Mode and recommends the highest-value reviewable
scientific action. For machine-readable agent context:

```bash
python3 scripts/apl_mission.py --json
python3 scripts/apl_mission.py --agent-prompt
```

Copy-paste prompt for a new agent:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode. Read AGENTS.md and docs/agent-task-protocol.md,
then run `python3 scripts/apl_mission.py --json`. Choose the recommended
research mission unless the maintainer gave a stricter task. Create a canonical
task branch before editing files. Execute the full loop autonomously: inspect
evidence, test or audit the hypothesis, preserve negative results, update
sandbox/review artifacts, run validation, generate a review bundle, and prepare
a PR. Keep outputs sandbox-only unless a canonical task explicitly allows
promotion. Do not promote claims, rewrite canonical results, or use
discovery/proved/solved wording.
```

Support and maintainer work remain explicit modes:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

See [docs/current-missions.md](docs/current-missions.md) for the human-readable
mission board and [missions/current.yaml](missions/current.yaml) for the
machine-readable source.

## How APL Works

```mermaid
flowchart TD
    classDef hyp fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,font-weight:bold
    classDef exp fill:#fef3c7,stroke:#f59e0b,color:#78350f,font-weight:bold
    classDef res fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold
    classDef bad fill:#fee2e2,stroke:#dc2626,color:#7f1d1d,font-weight:bold
    classDef mem fill:#f3e8ff,stroke:#a855f7,color:#581c87,font-weight:bold

    H["💡 Hypothesis"]:::hyp --> E["🔬 Experiment & Simulate"]:::exp --> R["📊 Result"]:::res
    R -->|"supported"| C["✅ Claim"]:::res
    R -->|"falsified"| F["❌ Falsification"]:::bad
    C & F --> M["🧠 Memory"]:::mem
    M -.->|"next cycle"| H
```

Every claim is backed by a reproducible experiment. Every falsification is
stored, not discarded. The memory grows with each run.

## Positioning

The long-term goal is not to claim a "theory of everything" from day one.
The goal is to build infrastructure for systematic theory search in physics.

The project combines three cores:

1. A hypothesis engine for proposing and testing candidate formulas or models.
2. A version-controlled scientific memory for storing hypotheses, claims,
   experiments, and results.
3. An open agent task network so humans and external agents can contribute reproducible work.

## Original MVP

The original MVP was `Pendulum Formula Discovery`.

It should:

1. Generate exact pendulum period ratio data.
2. Fit simple approximation families.
3. Compare candidate models.
4. Score accuracy and complexity.
5. Produce a reproducible Markdown report.

## Current Benchmarks

Eleven canonical experiments are currently stored in the repository.
The main public-facing benchmark surface should remain conservative: completed
benchmarks, falsifications, and sandbox pilots are reviewable evidence, not
automatic discovery claims. `EXP-0010` remains a guarded formula-search stress
test rather than a flagship success result.

1. `EXP-0001` — Pendulum Formula Discovery
2. `EXP-0002` — Damped Oscillator Regime Verification
3. `EXP-0004` — Charged-Lepton Koide Reproduction
4. `EXP-0005` — Historical Tau Holdout Prediction
5. `EXP-0006` — Dimensional Analysis Validator MVP
6. `EXP-0007` — Neutrino Koide Falsification
7. `EXP-0008` — Quark Koide Cascade Falsification
8. `EXP-0009` — Particle-Mass Relation Falsifier MVP
9. `EXP-0010` — Muon g-2 Formula-Search Stress Test (`INCONCLUSIVE`, not a
   public success story)
10. `EXP-0011` — Anharmonic Oscillator Period Benchmark
11. `EXP-0012` — Nuclear Mass Baseline Residual Benchmark

All results are stored as versioned run artifacts under `results/<experiment>/<run>/`.

## Key Results at a Glance

| Experiment | Verdict | Key metric |
|------------|---------|-----------|
| Pendulum gauntlet (EXP-0001) | VALID | 44/100 candidates pass in range |
| Koide charged leptons (EXP-0004) | VALID | Q = 0.6667 (gap < 0.5σ) |
| Tau holdout (EXP-0005) | VALID | Δm = 0.039 MeV, z = 0.43σ |
| Dimensional validator (EXP-0006) | VALID | 49/50 items correct (98%) |
| Neutrino Koide (EXP-0007) | INVALID | NH: 70.7σ below 2/3 |
| Quark Koide (EXP-0008) | INVALID | Down: 8.8σ, Up: 159σ above 2/3 |
| Particle-mass falsifier (EXP-0009) | INVALID | 2 of 3 charged-fermion families fail the standard Koide target |
| Nuclear mass baseline (EXP-0012) | PARTIAL | NMD-0002 residual surface established for sandbox-only follow-up |

→ **[Full visual result summary](docs/results/visual-summary.md)**
→ **[Koide campaign summary](docs/results/koide-campaign-summary.md)**
→ **[Negative results registry](docs/negative-results-registry.md)**
→ **[Reproducibility capsules](docs/reproducibility-capsules.md)**
→ **[External reviewer replication guide](docs/external-reviewer-replication-guide.md)**

### Selected Figures

**Koide Q across all SM fermion families:**

![Koide Q deviation](docs/figures/koide-q-deviation.png)

**Pendulum gauntlet top-10 leaderboard:**

![Pendulum leaderboard](docs/figures/pendulum-gauntlet-leaderboard.png)

These are scoped benchmark results with explicit limits, not discovery-level
physical conclusions, complete particle-mass explanations, or exact symbolic
proof. See `docs/results/visual-summary.md` for all figures with full captions.

## Start Here

If you are new to the repository, use this order:

1. Run `python3 scripts/apl_mission.py` for the current research-first mission.
2. [docs/current-missions.md](docs/current-missions.md)
3. [docs/mission-control.md](docs/mission-control.md)
4. [docs/campaigns/README.md](docs/campaigns/README.md)
5. [docs/status.md](docs/status.md)
6. [tasks/ACTIVE.md](tasks/ACTIVE.md)
7. [docs/agent-task-protocol.md](docs/agent-task-protocol.md)

This gives you the shortest path from "what is APL?" to "which campaign
already has evidence?" to "which task can I pick up safely?"

### Using a chat-based LLM instead of an agent?

Download [CONTEXT.md](CONTEXT.md) — a single-file bundle of the core
instructions, strategy, and current task board. Upload it to your chat session
to get full project context without reading multiple files.

To regenerate it locally after pulling updates:

```bash
python3 scripts/generate_context_bundle.py          # core (44 KB)
python3 scripts/generate_context_bundle.py --full   # + extended docs (~60 KB)
```

To replay the bounded current major result surface into a temporary output tree:

```bash
python3 scripts/reproduce_core_results.py
```

The replay leaves canonical `results/` artifacts untouched, writes regenerated
artifacts into per-slice `/tmp/apl-core-reproduction/*/` folders, and writes a
compact summary to `/tmp/apl-core-reproduction/CORE_REPRODUCTION_SUMMARY.md`. See
[docs/reproducibility-capsules.md](docs/reproducibility-capsules.md) for scope,
expected metrics, and skipped stress-test notes.

If you are reviewing APL from the outside rather than contributing code, start
with [docs/external-reviewer-replication-guide.md](docs/external-reviewer-replication-guide.md).

## Active Scientific Campaigns

```mermaid
flowchart LR
    classDef pend fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,font-weight:bold
    classDef part fill:#f3e8ff,stroke:#a855f7,color:#581c87,font-weight:bold
    classDef da   fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold

    P["🔭 Pendulum Track\nEXP-0001  Formula Discovery ✅\nEXP-0002  Damped Oscillator ✅\nRUN-0004  c=1/π fixed ✅"]:::pend
    K["⚛️ Particle Physics\nEXP-0004  Koide Q=2/3 ✅\nEXP-0005  Tau Holdout ✅\nEXP-0007  Neutrino ❌  70σ gap\nEXP-0008  Quark ❌  8.8σ / 159σ\nEXP-0009  Falsifier MVP ❌"]:::part
    D["📐 Dimensional Analysis\nMVP implemented ✅\n50-item frozen benchmark\n70-item curation surface"]:::da

    P ~~~ K ~~~ D
```

Full campaign details:

1. [Pendulum Formula Falsification](docs/campaigns/pendulum-formula-falsification.md)
2. [Particle Mass Relations](docs/campaigns/particle-mass-relations.md)
3. [Dimensional Analysis Validator](docs/campaigns/dimensional-analysis-validator.md)
4. [Thought-Experiment Consistency](docs/campaigns/thought-experiment-consistency.md)

The pendulum and particle-mass tracks already have scoped canonical results.
The dimensional-analysis track now has a canonical MVP benchmark result. The
thought-experiment track remains planning-first and should not be described as
a finished benchmark implementation.
`EXP-0010` exists as a guarded empirical formula-search stress test and should
not be presented as part of the public-facing success surface.

## Contribute With An AI Coding Agent

```mermaid
flowchart LR
    classDef quick  fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,font-weight:bold
    classDef task   fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold
    classDef sci    fill:#f3e8ff,stroke:#a855f7,color:#581c87,font-weight:bold
    classDef prop   fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef finish fill:#f1f5f9,stroke:#64748b,color:#1e293b,font-weight:bold

    Start(["▶ Enter repo"]) --> Mission["🚀 apl_mission.py\nResearch Mode"]
    Mission --> Read["📋 AGENTS.md\n+ mission context"]

    Read -->|"default"| Sci["🔬 Research mission\nhypothesis · replay · audit"]:::sci
    Read -->|"support mode"| MT["⚡ Microtask"]:::quick
    Read -->|"task mode"| RT["🎯 READY task"]:::task
    Read -->|"new idea"| Prop["💡 Task proposal\ntasks/proposals/"]:::prop

    MT  --> PR["📬 branch → PR\n→ maintainer review"]:::finish
    RT  --> PR
    Sci --> PR
    Prop --> PropPR["📋 TASK-PROPOSAL PR\nwait for TASK-XXXX"]:::prop
```

Every path ends with a PR — agents never merge their own work.

Invited contributors can use Codex, Claude Code, or other coding agents.
Start with [docs/private-contributor-pilot.md](docs/private-contributor-pilot.md)
for the private-alpha workflow and [AGENTS.md](AGENTS.md) for the canonical rules.

Not sure where to start? Run `python3 scripts/apl_mission.py`. Use the
**[Agent Work Menu](docs/agent-work-menu.md)** only when you intentionally want
support or short-session work sized for your session budget (30 min / 1 h / 2 h).

## Quickstart

```bash
git clone https://github.com/gladunrv/autonomous-physics-lab.git
cd autonomous-physics-lab

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"

python -m ruff check .
python -m pytest

python -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped

python -m physics_lab.cli validate-repo .
python -m physics_lab.cli status .
```

## Repository Shape

```text
autonomous-physics-lab/
  AGENTS.md
  CODEX_TASK.md
  README.md

  physics_lab/
    engines/
    registry/
    schemas/
    workflows/

  hypotheses/
  claims/
  experiments/
  results/
  knowledge/
  tasks/
  agents/
  docs/
  tests/
```

## Status

The repository is currently in:

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

See [docs/status.md](docs/status.md),
[docs/roadmap.md](docs/roadmap.md), and
[docs/implementation-plan.md](docs/implementation-plan.md).

## Planning Docs

Use these files to continue the project without guessing:

- [docs/mission-control.md](docs/mission-control.md) for the fastest project-level orientation
- [docs/campaigns/README.md](docs/campaigns/README.md) for the scientific campaign map
- [docs/strategy.md](docs/strategy.md) for the current strategic compass
- [tasks/ACTIVE.md](tasks/ACTIVE.md) for the shared live task board
- [docs/agent-operating-model.md](docs/agent-operating-model.md) for multi-agent handoff and task execution
- [docs/implementation-plan.md](docs/implementation-plan.md) for phased strategy
- [docs/next-steps.md](docs/next-steps.md) for the immediate working queue
- [docs/backlog.md](docs/backlog.md) for medium-term and deferred tasks
- [docs/status.md](docs/status.md) for the current project readiness snapshot
- [docs/architecture-index.md](docs/architecture-index.md) for the fastest codebase and artifact map
- [docs/private-contributor-pilot.md](docs/private-contributor-pilot.md) for invited private contributors using coding agents
- [docs/public-release-gates.md](docs/public-release-gates.md) for the gates that must be satisfied before the repository becomes public
- [docs/github-branch-protection-plan.md](docs/github-branch-protection-plan.md) for staged PR and branch-protection setup
- [docs/release-checklist.md](docs/release-checklist.md) for public-alpha tag and release prep
- [docs/releases/v0.1-public-alpha.md](docs/releases/v0.1-public-alpha.md) for prepared release notes
- [CONTRIBUTING.md](CONTRIBUTING.md) for contributor expectations
- [docs/contributing-workflow.md](docs/contributing-workflow.md) for the repository contribution flow
- [docs/claim-promotion-policy.md](docs/claim-promotion-policy.md) for claim-status review rules
