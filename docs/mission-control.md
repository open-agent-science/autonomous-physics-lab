# Mission Control

## What APL Is Trying To Do

Autonomous Physics Lab (APL) is verification-first scientific infrastructure.
Its job is to make physics hypotheses testable, falsifiable, reproducible, and
reviewable through deterministic code and version-controlled evidence.

APL is currently in:

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

The repository stays private while current campaigns, contributor workflow, and
public-release gates are still being validated.

## What APL Is Not Trying To Do

- It is not a chatbot for speculative physics claims.
- It is not treating numerically interesting fits as discovery-level evidence.
- It is not presenting benchmark fits as complete explanations of particle masses.
- It is not presenting range-limited benchmarks as globally valid theories.
- It is not public-launch ready yet.

## Active Campaigns

APL currently organizes work around four contributor-facing campaign surfaces:

| Campaign | Status | Why it exists | Best starting point |
| --- | --- | --- | --- |
| [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md) | Active with canonical results | Stress-test approximation discovery against an exact reference with explicit failure modes | [pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md) |
| [Particle Mass Relations](./campaigns/particle-mass-relations.md) | Active with scoped reproductions and falsifications | Test whether impressive mass relations survive disciplined, falsification-first handling | [koide-neutrino-falsification.md](./results/koide-neutrino-falsification.md) |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | Active with canonical MVP result | Build a quality floor for future formula and benchmark work | [RUN-0006 report](../results/EXP-0006/RUN-0006/report.md) |
| [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md) | Planning active, no canonical run yet | Extend APL into consistency checks that do not depend on curve fitting alone | [thought-experiment-consistency-suite.md](./notes/thought-experiment-consistency-suite.md) |

## Current Results

The clearest current repository-level results are:

1. [Pendulum Gauntlet 100](./results/pendulum-gauntlet-100-summary.md) —
   100 deterministic pendulum candidate formulas evaluated with stored
   leaderboard, diagnostics, and precision audit.
2. [Dimensional Analysis Validator MVP](../results/EXP-0006/RUN-0006/report.md)
   — a canonical 50-item validator benchmark with 49/50 agreement under
   explicit MVP limits.
3. [Koide charged-lepton reproduction](./results/koide-charged-lepton-reproduction.md)
   — a narrow dataset-based reproduction benchmark with uncertainty-aware
   comparison.
4. [Koide tau holdout](./results/koide-tau-holdout.md) — a historical
   holdout-style benchmark associated with `RESULT-0006`, kept narrow and
   explicitly non-explanatory.
5. [Koide neutrino falsification](./results/koide-neutrino-falsification.md)
   and [Negative Results Registry](./negative-results-registry.md) — clean
   falsification surfaces for the original neutrino extension and related
   particle-mass follow-ups.
6. [`RESULT-0010` quark cascade falsification](./notes/koide-quark-cascade.md)
   — the current quark-sector falsification result under stored dataset and
   scale assumptions.

These results matter because they are reproducible and reviewable. They do not
authorize exact symbolic proof, universal scope, or deeper physical
explanation by themselves.

## Current Packaging Focus

The near-term documentation goal is a cautious `v0.2` packaging pass:

- top-level docs should reflect the actual benchmark and falsification surface;
- Koide work should read as one falsification-first campaign, not a handful of
  disconnected notes;
- negative results should stay as visible as successful reproductions;
- public-opening decisions should remain gated behind wording discipline and
  release checks.

## How Contributors Can Plug In

The current contributor workflow is branch-based and task-driven.

Operational entry points:

- [docs/agent-work-menu.md](./agent-work-menu.md) for a fast time-budgeted
  menu of safe, reviewable work (30 min / 1 h / 2 h);
- [tasks/ACTIVE.md](../tasks/ACTIVE.md) for the live board of canonical tasks;
- [tasks/microtasks/README.md](../tasks/microtasks/README.md) for campaign-specific scientific microtask queues;
- [docs/negative-results-registry.md](./negative-results-registry.md) for the
  current falsification index;
- [docs/agent-task-protocol.md](./agent-task-protocol.md) for branch, task,
  PR, validation, and task-state rules;
- [docs/agent-scientific-work-mode.md](./agent-scientific-work-mode.md) for
  spare-budget scientific work mode;
- [docs/scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md)
  for queue and batching rules;
- [tasks/proposals/README.md](../tasks/proposals/README.md) for the
  proposal-first workflow when no canonical task fits;
- [docs/private-contributor-pilot.md](./private-contributor-pilot.md) for the
  invited private contributor flow;
- `python3 -m physics_lab.cli sync-active-board .` for keeping the active board
  aligned with task YAML files;
- maintainer review and closeout tooling for review bundles and handoff.

Low-risk contribution patterns right now:

- improve status, roadmap, onboarding, or campaign documentation;
- tighten wording, diagnostics, or visual summaries around existing results;
- complete one small batch from a single scientific microtask queue;
- work on planning or validation tasks that do not churn canonical result
  artifacts.

## What Not To Claim

- Do not describe APL as having resolved physics.
- Do not describe the repository as having made a discovery-level physical breakthrough.
- Do not call pendulum approximations exact or globally valid.
- Do not treat charged-lepton or tau-holdout benchmarks as explanations of
  particle masses.
- Do not turn neutrino or quark falsifications into a blanket claim about all
  possible Koide variants.
- Do not describe planning-only campaigns as implemented benchmark systems.
- Do not present the repository as public before the release gates are met.

## Read Order For New Contributors

1. [README.md](../README.md)
2. [docs/mission-control.md](./mission-control.md)
3. [docs/campaigns/README.md](./campaigns/README.md)
4. [docs/status.md](./status.md)
5. [tasks/ACTIVE.md](../tasks/ACTIVE.md)
6. [docs/agent-task-protocol.md](./agent-task-protocol.md)
