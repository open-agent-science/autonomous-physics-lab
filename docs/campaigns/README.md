# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** Materials MD-0002 and the
  source-gated Atomic / Stellar / Quantum data-to-benchmark wave.
- **Fresh-data buildout:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows, Quantum still needs direct rows).
- **Reusable-dataset buildout:** Materials Property Residuals now has the first
  pinned reusable-dataset candidate (`MD-0001`) and first conservative
  baseline evidence.
- **Public verifier lane:** Textbook Formula Audit.
- **Monitor-only lane:** Exoplanet Mass-Radius, until a new pinned archive
  snapshot or source-version trigger reopens residual scoring.
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
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 is the selected, checksum-pinned source path; the current blocker is deterministic size-axis digitization and row-readiness, not another source scout. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy and Nemitz Yb/Sr rows plus a first exploratory cross-source diagnostic; the next question is result-path routing or a Pizzocaro third-source admissibility ledger. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has `MD-0001`, replayed baseline evidence, null/split controls, a frozen `MD-0002` widening, and sandbox-pass formation-energy evidence awaiting a publication-route decision. |
| monitor the exoplanet benchmark surface | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has pinned snapshots, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, and a closed `EXO-0002` reopen gate; new scoring waits for a source-version trigger. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, uncertainty-weighted diagnostic, replayable F2 signal, component-ablation evidence that keeps F2 diagnostic-only, and AGENT_VALIDATED diagnostic memory. | `TASK-0714` / `TASK-0746`: repair reveal-checklist links and select one non-F2 no-leakage lane; keep scoring blocked until a source-grade no-peek release exists. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, closed `EXO-0002` reopen gate, and a no-notify source-version monitor. | `TASK-0745`: decide whether `EXO-0003` remains monitor-only or needs a metadata-only scout / coverage-gate amendment. |
| [Quantum Size Effects](./quantum-size-effects.md) | Scaffold, calibration-derived seeds kept out of benchmark metrics, source-artifact intake path, synthetic/non-spherical digitization fixtures, and Almeida 2023 source bytes checksum-pinned under CC BY 4.0. | `TASK-0755`: digitize Almeida size axis and rerun row-readiness before any baseline. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy and Nemitz Yb/Sr rows, real-row loader, covariance policy, first exploratory cross-source diagnostic, Pizzocaro diagnostics, and preserved aggregation/source-limit blockers. | `TASK-0756` and `TASK-0742`: route the completed Yb/Sr diagnostic or run Pizzocaro third-source row-admissibility first. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001` pinned Materials Project binary-oxide dataset, replayed baseline, formation-energy control survival, split-robust formation-energy signal, split-fragile band gap, validated/frozen `MD-0002` snapshot, and TASK-0703 sandbox-pass formation-energy evidence. | Decide whether the TASK-0703 sandbox evidence warrants an explicit result-publication task, or remains sandbox memory; do not promote materials claims. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Verifier-first scaffold, exact-reference fixtures, Gate-B-validated Stefan-Boltzmann software/convention result, DEBCat source choice, and a Stellar M-L Route 2 sandbox-pass that is not Gate-A-ready. | `TASK-0759`: run stage-control, null/shuffle, split-sensitivity, and baseline-adequacy audit before any empirical result package. |

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
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed, exact-reference fixtures exist, Stefan-Boltzmann has an agent-validated software/convention result, and Stellar M-L has a local Route 2 sandbox-pass that is not Gate-A-ready. | Stage-control, null/shuffle controls, split sensitivity, and baseline adequacy before empirical result promotion; no model-derived Gaia mass truth rows. |
| Materials widenings | `MD-0002` stable ternary oxides are frozen and have a sandbox-pass formation-energy benchmark. | Route the TASK-0703 evidence before any canonical result package or public result promotion. |

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
