# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** Exoplanet Mass-Radius.
- **Fresh-data buildout:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows, Quantum still needs direct rows).
- **Reusable-dataset buildout:** Materials Property Residuals now has the first
  pinned reusable-dataset candidate (`MD-0001`) and first conservative
  baseline evidence.
- **Public verifier lane:** Textbook Formula Audit.
- **Candidate new lanes:** future Materials widenings, only after the first
  `MD-0001` benchmark and MD-0002 source gates justify widening.
- **Quality floor:** Pendulum, Dimensional Analysis, and Particle Mass
  Relations.
- **Planning/watchlist:** Fresh Physics Data Axes, Anomaly Registry, and
  Thought-Experiment Consistency.

For a compact machine-readable portfolio map, see
[`campaign_profiles/_catalog.yaml`](../../campaign_profiles/_catalog.yaml) and
[`docs/campaign-registry.md`](../campaign-registry.md). The catalog summarizes
status, stage, agent capacity, gates, allowed work, forbidden work, and result
pointers for parallel agent planning; it does not replace this human-readable
campaign map or `missions/current.yaml`.

## Start By Intent

| If you want to... | Start here | Why |
| --- | --- | --- |
| see what can be shared publicly today | [Public Science Dashboard](./public-science-dashboard.md) | It has linkable result cards, safe wording, current questions, and expected next results per active campaign. |
| review the flagship validation challenge | [Nuclear Mass Surface](./nuclear-mass-surface.md) | It has a frozen baseline, sandbox scout evidence, prediction registry entries, source gates, explicit negative controls, and several useful negative/control results. |
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | It is blocked on source-grade direct rows; Norris-Bawendi now has a source-copy handoff, Kang-Wise is currently inadmissible, and the next safe path is a maintainer source copy or a new open direct-table scout. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy rows pinned, row roles assigned, a real-row loader, synthetic cross-source dry-run plumbing, Nemitz and Pizzocaro source artifacts, and a covariance policy; Pizzocaro row admissibility is next. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has the first pinned reusable-dataset candidate (`MD-0001`), holdout manifest, citation metadata, and first conservative baseline evidence. |
| work on the default science-output sprint | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has a pinned snapshot, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, and second pinned snapshot; the second snapshot did not reopen residual scoring. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, uncertainty-weighted diagnostic, replayable F2 signal, and component-ablation evidence that keeps F2 diagnostic-only. | `TASK-0641`: build the reveal-readiness matrix; keep reveal scoring blocked until a source-grade no-peek release exists. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, and closed `EXO-0002` reopen gate. | `TASK-0649` or `TASK-0650`: preserve negative/control memory and define source-version trigger discipline; no residual scoring on the current snapshot. |
| [Quantum Size Effects](./quantum-size-effects.md) | Scaffold, calibration-derived seeds, direct-source triage, source-artifact intake path, synthetic/non-spherical digitization fixtures, and Almeida 2023 source feasibility. | `TASK-0668` or `TASK-0656`: package Almeida source artifacts or scout a second open direct-table source before row curation. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy pinned rows, real-row loader, covariance policy, Nemitz/Pizzocaro/Lange source surfaces, Pizzocaro diagnostics, and a feasible PSD covariance-approximation path. | `TASK-0666` or `TASK-0669`: build the Pizzocaro covariance approximation or decide the Lange/PTB source-artifact route. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001` pinned Materials Project binary-oxide dataset, replayed baseline, formation-energy control survival, split-robust formation-energy signal, split-fragile band gap, and negative factory memory. | `TASK-0631`, `TASK-0645`, or `TASK-0646`: plan MD-0002 source gates or package band-gap negative memory before widening. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Verifier-first scaffold, exact-reference fixtures, Gate-B-validated Stefan-Boltzmann software/convention result, and DEBCat selected as the first independent Stellar M-L mass-source path. | `TASK-0658` after its blocker clears: run DEBCat row-readiness before empirical Stellar M-L metrics. |

These are the main public-facing surfaces today. They should be presented as
disciplined research infrastructure, not as finished discoveries.

## Mature Quality-Floor Tracks

| Campaign | What it teaches APL |
| --- | --- |
| [Pendulum Formula Falsification](./pendulum-formula-falsification.md) | Exact-reference replay, approximation failure modes, leaderboard discipline, and honest range limits. |
| [Particle Mass Relations](./particle-mass-relations.md) | Falsification-first handling of tempting numerical relations and uncertainty-sensitive wording. |
| [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | Fast formula sanity checks and benchmark hygiene for future generated hypotheses. |

These tracks are not the loudest public hook anymore, but they are the reason
the newer campaigns can be stricter.

## Planning And Watchlist Surfaces

| Campaign | Status | Safe contribution shape |
| --- | --- | --- |
| [Fresh Physics Data Axes](./fresh-physics-data-axes.md) | Planning and source-policy layer. | Source-policy review or manifest-only triage for less-saturated data axes. |
| [Anomaly Registry](./anomaly-registry.md) | Schema/admissibility scaffold, not a joint-fit campaign. | Schema validation, admissibility examples, or synthetic-only likelihood contracts. |
| [Thought-Experiment Consistency](./thought-experiment-consistency.md) | Planning active, no canonical benchmark run yet. | Scoped scenario planning and deterministic validator design. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed, exact-reference fixtures exist, Stefan-Boltzmann has an agent-validated software/convention result, and Stellar M-L source/baseline planning exists. | DEBCat row-readiness after holdout/leakage protocol; no empirical metrics before row provenance passes. |
| Materials widenings | First seed dataset exists; broader Materials slices are deferred. | Only widen via a pre-fetch-amended source acquisition task after `MD-0001` baseline evidence shows the next slice is worth curating. |

Do not turn planning surfaces into broad formula searches. A planning campaign
is useful when it prevents chaotic future work.

## Repository-Wide Orientation

Pair these campaign pages with:

- [Mission Control](../mission-control.md)
- [Current Missions](../current-missions.md)
- [Project Status](../status.md)
- [Open Agent Network](../open-agent-network.md)
- [Architecture Layers](../architecture-layers.md)
- [Campaign Registry](../campaign-registry.md)
- [Task views (current work)](../task-views/research.md)
