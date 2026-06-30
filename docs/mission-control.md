# Mission Control

## What APL Is Trying To Do

Autonomous Physics Lab (APL) is verification-first scientific infrastructure.
Its job is to make physics hypotheses testable, falsifiable, reproducible, and
reviewable through deterministic code and version-controlled evidence.

APL is also an open agent network for science: many contributors can connect
their AI agents to shared scientific campaigns, and accepted outputs become
public scientific memory rather than isolated local chat artifacts.

<p align="center">
  <img src="figures/autonomous-physics-lab-workflow-concept.png" alt="Autonomous Physics Lab verification-first workflow for AI agents" width="100%">
</p>

## Agent First Entry Point

New contributors and coding agents should start from the mission script:

```bash
python3 scripts/apl_mission.py --output onboarding
```

Onboarding mode keeps the first run human-friendly: it explains the current
research mission, shows a few `READY` options, estimates effort, recommends
one path, and waits before editing files.

Explicit non-default lanes:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

This keeps maintainer review and closeout automation intact while making the
normal contributor path research-first.

For humans, the practical path is:

1. read the short project pitch in [README.md](../README.md);
2. run `python3 scripts/apl_mission.py --output onboarding`;
3. choose one `READY` task or ask the agent to explain the options;
4. review the PR evidence and limitations before merge.

Use [Connect Your Agent](./connect-your-agent.md) for the contribution loop and
[Use Your Agent](./use-your-agent.md) for agent prompt guidance.

## What APL Is Not Trying To Do

- It is not a chatbot for speculative physics claims.
- It is not treating numerically interesting fits as claim-level evidence.
- It is not presenting benchmark fits as complete explanations of particle masses.
- It is not presenting range-limited benchmarks as globally valid theories.

## Active Campaigns

APL currently organizes work around one flagship validation campaign, several
post-validation gate surfaces, fresh-data source surfaces, and older
benchmark/falsification surfaces that still define the project's quality floor:

If you are new, start with the first several rows. They are the current
public-facing research surfaces. The later rows are still important, but they
are either quality-floor benchmarks or planning/watchlist surfaces.

| Campaign | Status | Why it exists | Best starting point |
| --- | --- | --- | --- |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Post-validation dataset/transfer gate | Dry-run a deterministic `MD-0002` archive package before any external upload, DOI, or broader transfer wording | [materials-property-residuals.md](./campaigns/materials-property-residuals.md) |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier, replay, and source-contract gate | Keep famous-formula checks source-first; FIRAS/Wien is agent-validated calibration memory, while high-mass transfer needs metadata-caveat adjudication before stronger wording | [textbook-formula-audit.md](./campaigns/textbook-formula-audit.md) |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation campaign, negative/control memory, and uncertainty-gated prospective reveal | Test nuclear residual candidates with frozen baselines and future reveal discipline, while keeping `RESULT-0025` point-estimator gains separate from uncalibrated intervals | [nuclear-mass-pilot-summary.md](./results/nuclear-mass-pilot-summary.md) |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source/negative-memory gate after a source-scoped baseline | Prepare a frozen ZnSe row-transfer gate from existing narrow factual extracts without unblocking open-ended correction search | [quantum-size-effects.md](./campaigns/quantum-size-effects.md) |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | Fresh-data source surface and public-safe negative-memory lane | Adjudicate whether the McGrew/NIST Yb/Sr route provides a primary independent row before any metric rerun | [atomic-clock-source-candidates.md](./notes/atomic-clock-source-candidates.md) |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | Source-pinned thermophysical benchmark lane | Replay ThermoML `Tb` `RESULT-0026` and test local-only expansion feasibility without raw archive vendoring or broad property claims | [thermophysical-property-residuals.md](./campaigns/thermophysical-property-residuals.md) |
| [Exoplanet Mass-Radius Benchmark](./campaigns/exoplanet-mass-radius.md) | Monitor/trigger-gated catalog benchmark surface | Decide whether null-baseline memory should receive canonical identities, and reopen residual scoring only after source-version or coverage triggers | [exoplanet-mass-radius-baseline-protocol.md](./exoplanet-mass-radius-baseline-protocol.md) |
| [Fresh Physics Data Axes](./campaigns/fresh-physics-data-axes.md) | Planning and intake layer | Keep future campaigns focused on less-saturated source surfaces instead of formula mining old tables | [fresh-data-source-policy.md](./notes/fresh-data-source-policy.md) |
| [Anomaly Registry](./campaigns/anomaly-registry.md) | Planning scaffold, not a joint-fit campaign | Define admissible anomaly records and guardrails before any cross-anomaly modeling | [anomaly-registry-admissibility.md](./notes/anomaly-registry-admissibility.md) |
| [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md) | Active with canonical results | Stress-test approximation search against an exact reference with explicit failure modes | [pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md) |
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
10. Materials `RESULT-0021`, Textbook/Stellar `RESULT-0022`, AGENT_VALIDATED
    FIRAS/Wien `RESULT-0023`, caveated Stellar high-mass transfer
    `RESULT-0024`, Nuclear point-estimator `RESULT-0025`, and ThermoML `Tb`
    `RESULT-0026` are the current strongest post-validation, replay-ready, or
    source-pinned dataset-backed surfaces. They are useful as scoped,
    review-tiered memory and transfer/source-readiness prompts, not as
    material-discovery, stellar-law, nuclear-law, thermophysical-law, or
    universal-formula claims.

The nuclear prediction registry is a prospective forecast surface, not a
result surface: `PRED-0001` through `PRED-0068` are frozen entries awaiting
future maintainer-reviewed reveal data.

These results matter because they are reproducible and reviewable. They do not
authorize exact symbolic certainty, universal scope, or deeper physical
explanation by themselves.

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
- [docs/task-views/research.md](./task-views/research.md) for generated current-work navigation; use `git log` for task history;
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
- the `Sync Active Board` post-merge GitHub Action keeps the active board
  and `docs/task-views/*.md` aligned with task YAML files on `main`;
- `python3 -m physics_lab.cli sync-active-board .` remains available for
  maintainer dry-runs and explicit board-sync PRs;
- maintainer review and closeout tooling for review bundles and handoff.

Low-risk contribution patterns right now:

- improve status, roadmap, onboarding, or campaign documentation;
- tighten wording, diagnostics, or visual summaries around existing results;
- complete one small batch from a single scientific microtask queue;
- work on planning or validation tasks that do not churn canonical result
  artifacts.

## What Not To Claim

- Do not describe APL as having finalized physics.
- Do not describe AGENT_VALIDATED or Gate-B-replayed benchmark artifacts as
  maintainer-endorsed physical discoveries.
- Do not call pendulum approximations exact or globally valid.
- Do not treat charged-lepton or tau-holdout benchmarks as explanations of
  particle masses.
- Do not turn neutrino or quark falsifications into a blanket claim about all
  possible Koide variants.
- Do not turn the particle-mass falsifier MVP into a blanket claim about all
  possible mass-relation formulas.
- Do not present `EXP-0010` muon g-2 output as a validated, explanatory,
  or flagship public result.
- Do not describe planning-only campaigns as implemented benchmark systems.

## Read Order For New Contributors

1. Run `python3 scripts/apl_mission.py --output onboarding` for the current research-first mission.
2. [README.md](../README.md)
3. [docs/current-missions.md](./current-missions.md)
4. [docs/mission-control.md](./mission-control.md)
5. [docs/campaigns/README.md](./campaigns/README.md)
6. [docs/status.md](./status.md)
7. [docs/task-views/research.md](./task-views/research.md)
8. [docs/agent-task-protocol.md](./agent-task-protocol.md)
