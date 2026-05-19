# Mission Control

## What APL Is Trying To Do

Autonomous Physics Lab (APL) is verification-first scientific infrastructure.
Its job is to make physics hypotheses testable, falsifiable, reproducible, and
reviewable through deterministic code and version-controlled evidence.

APL is also an open agent network for science: many contributors can connect
their AI agents to shared scientific campaigns, and accepted outputs become
public scientific memory rather than isolated local chat artifacts.

APL is currently in:

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

The repository stays private while current campaigns, contributor workflow, and
public-release gates are still being validated.

## Agent First Entry Point

New contributors and coding agents should start from the mission script:

```bash
python3 scripts/apl_mission.py
```

Default mode is `research`. It recommends a current scientific mission,
guardrails, and PR-ready outputs before showing support work.

Explicit non-default lanes:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

This keeps maintainer review and closeout automation intact while making the
normal contributor path research-first.

## What APL Is Not Trying To Do

- It is not a chatbot for speculative physics claims.
- It is not treating numerically interesting fits as discovery-level evidence.
- It is not presenting benchmark fits as complete explanations of particle masses.
- It is not presenting range-limited benchmarks as globally valid theories.
- It is not public-launch ready yet.

## Active Campaigns

APL currently organizes work around five contributor-facing campaign surfaces:

| Campaign | Status | Why it exists | Best starting point |
| --- | --- | --- | --- |
| [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md) | Active with canonical results | Stress-test approximation discovery against an exact reference with explicit failure modes | [pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md) |
| [Particle Mass Relations](./campaigns/particle-mass-relations.md) | Active with scoped reproductions and falsifications | Test whether impressive mass relations survive disciplined, falsification-first handling | [koide-neutrino-falsification.md](./results/koide-neutrino-falsification.md) |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | Active with canonical MVP result | Build a quality floor for future formula and benchmark work | [RUN-0006 report](../results/EXP-0006/RUN-0006/report.md) |
| [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md) | Planning active, no canonical run yet | Extend APL into consistency checks that do not depend on curve fitting alone | [thought-experiment-consistency-suite.md](./notes/thought-experiment-consistency-suite.md) |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation campaign, sandbox-only candidates | Test nuclear residual candidates with frozen baselines, robustness gates, and post-AME2020 time-split discipline | [nuclear-mass-pilot-summary.md](./results/nuclear-mass-pilot-summary.md) |

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
7. [`RESULT-0011` particle-mass relation falsifier MVP](../results/EXP-0009/RUN-0001/report.md)
   — fixed-target Koide family-survival falsification with uncertainty,
   baseline, and complexity-penalty reporting.
8. [Anharmonic Oscillator Period Benchmark](./results/anharmonic-oscillator-summary.md)
   — `EXP-0011` nonlinear mechanics benchmark with perturbative and empirical
   baselines, kept range-limited.
9. [Nuclear Mass Baseline](./results/nuclear-mass-baseline-summary.md) and
   [Nuclear Mass Pilot Summary](./results/nuclear-mass-pilot-summary.md) —
   `EXP-0012` baseline evidence plus sandbox-only autonomous pilot and
   retrospective post-AME2020 checks. `AGENT-RUN-0007` is only an
   `INCONCLUSIVE` source-manifest guard, while `AGENT-RUN-0008` remains
   sandbox-only retrospective time-split evidence.

The nuclear prediction registry is a prospective forecast surface, not a
result surface: `PRED-0001` through `PRED-0020` are frozen entries awaiting
future maintainer-reviewed reveal data, and `TASK-0228` through `TASK-0237`
split follow-up variants into bounded parallel lanes.

These results matter because they are reproducible and reviewable. They do not
authorize exact symbolic proof, universal scope, or deeper physical
explanation by themselves.

## Current Packaging Focus

The near-term documentation goal is a cautious `v0.2` packaging pass:

- top-level docs should reflect the actual benchmark and falsification surface;
- Koide work should read as one falsification-first campaign, not a handful of
  disconnected notes;
- negative results should stay as visible as successful reproductions;
- `EXP-0010` should remain a guarded stress-test surface rather than a flagship
  public result;
- Nuclear Mass Surface should be described as benchmark and sandbox
  validation evidence: `AGENT-RUN-0007` is not an active benchmark result,
  and post-AME2020 scoring is retrospective rather than strict blind
  prediction;
- prediction-registry entries should read as frozen prospective forecasts
  awaiting future comparison, not as evidence of predictive success;
- public-opening decisions should remain gated behind wording discipline and
  release checks.

## How Contributors Can Plug In

The current contributor workflow is branch-based and task-driven.

Operational entry points:

- [docs/open-agent-network.md](./open-agent-network.md) for the coordination
  model behind shared campaign work;
- [docs/current-missions.md](./current-missions.md) and
  `python3 scripts/apl_mission.py` for the Agent First mission menu;
- [docs/external-reviewer-replication-guide.md](./external-reviewer-replication-guide.md)
  for outside reviewers who want to replay or sanity-check the strongest
  evidence before learning the contributor workflow;
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
- Do not turn the particle-mass falsifier MVP into a blanket claim about all
  possible mass-relation formulas.
- Do not present `EXP-0010` muon g-2 output as a discovery-level, explanatory,
  or flagship public result.
- Do not describe planning-only campaigns as implemented benchmark systems.
- Do not present the repository as public before the release gates are met.

## Read Order For New Contributors

1. Run `python3 scripts/apl_mission.py` for the current research-first mission.
2. [README.md](../README.md)
3. [docs/current-missions.md](./current-missions.md)
4. [docs/mission-control.md](./mission-control.md)
5. [docs/campaigns/README.md](./campaigns/README.md)
6. [docs/status.md](./status.md)
7. [tasks/ACTIVE.md](../tasks/ACTIVE.md)
8. [docs/agent-task-protocol.md](./agent-task-protocol.md)
