# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** Gate B replay for ThermoML
  `RESULT-0026`, no-peek uncertainty calibration for Nuclear `RESULT-0025`,
  maintainer/public wording for AGENT_VALIDATED FIRAS/Wien `RESULT-0023`,
  metadata-caveat repair for `RESULT-0024`, and source/readiness decisions for
  Materials / Atomic / Exoplanet / Quantum / Particle.
- **Fresh-data buildout:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows and a source-limited Yb/Sr consistency
  memory card plus a Pizzocaro aggregation contract that still blocks row
  admission; Quantum has six direct Almeida InP rows, a source-scoped sandbox
  baseline, a narrow ZnSe factual-extract route, and failed effective-mass
  transfer memory already routed as sandbox-only negative/control evidence).
- **Reusable-dataset buildout:** Materials Property Residuals now has `MD-0001`,
  `MD-0002`, AGENT_VALIDATED `RESULT-0021`, and internal release metadata; an
  external archive/DOI decision remains maintainer-gated and should be preceded
  by a deterministic archive-package dry run.
- **New thermophysical benchmark lane:** Thermophysical Property Residuals starts
  with ThermoML normal-boiling-temperature `RESULT-0026`, a bounded
  AGENT_PUBLISHED Joback transfer result that needs Gate B replay and
  local-only expansion feasibility checks before stronger wording.
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
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 produced six direct InP rows and a source-scoped sandbox baseline; the current blocker is a frozen ZnSe row-transfer readiness gate, not another correction-search pilot. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy and Nemitz Yb/Sr rows plus a first exploratory cross-source diagnostic; Pizzocaro remains diagnostic-only, so the next useful route is McGrew/NIST primary-ratio and independence adjudication, not another metric rerun. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, and scope-control memory; the current blocker is a deterministic external archive-package dry run and maintainer DOI decision, not benchmark replay. |
| work on source-pinned thermophysical data | [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | It has AGENT_PUBLISHED ThermoML `Tb` / Joback `RESULT-0026` on a bounded 40-row fixture; the current blocker is Gate B replay plus local-only identity/count feasibility, not broader chemistry claims. |
| monitor the exoplanet benchmark surface | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has pinned snapshots, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, and a Gate-A-blocked negative-result packaging path; new scoring waits for a source-version trigger. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, AGENT_VALIDATED `RESULT-0018`, exact-replayed `RESULT-0025` point-estimator evidence, a no-peek uncertainty-route preflight, and metadata-only DZ10 parity readiness awaiting closeout. | `TASK-0899` uncertainty-calibration audit; no broad F2, shell, local-curvature, Wigner, prediction-freeze, reveal-scoring, or duplicate DZ10 restart. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, closed `EXO-0002` reopen gate, and a Gate-A-blocked negative-result route. | `TASK-0904` canonical identity decision or `TASK-0905` metadata-only monitor check; no residual scoring unless a NOTIFY class appears. |
| [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 direct InP rows, source-scoped sandbox baseline, controls/holdout summary, narrow factual ZnSe route, and failed effective-mass transfer check routed as sandbox negative memory. | `TASK-0903`: prepare the ZnSe frozen-row transfer-readiness gate; no correction-search unblock. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy and Nemitz Yb/Sr rows, real-row loader, covariance policy, Pizzocaro diagnostic blocker/contract, source-limited consistency memory, and plausible McGrew/NIST route. | `TASK-0901`: adjudicate McGrew/NIST primary-ratio semantics and independence; no constants-drift or metric rerun. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, family-holdout scope boundary, descriptor-ablation control memory, transfer-negative replay, and repository-local release metadata. | `TASK-0900`: deterministic archive-package dry run before external dataset claims or DOI/upload decisions. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | AGENT_VALIDATED exact-reference `RESULT-0019`, AGENT_VALIDATED Stellar M-L `RESULT-0022`, AGENT_VALIDATED FIRAS/Wien `RESULT-0023`, and high-mass transfer `RESULT-0024` replay memory with a metadata caveat. | `TASK-0897` or `TASK-0898`: prepare RESULT-0023 public wording or repair/preserve RESULT-0024 metadata caveat; no universal formula claim. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | AGENT_PUBLISHED ThermoML `Tb` `RESULT-0026` on a 40-row family-stratified fixture, with a frozen Joback baseline, rights boundary, and esters/lactones negative memory. | `TASK-0894` or `TASK-0906`: replay RESULT-0026 or preflight local-only 80-row identity/count feasibility; no chemical-design or broad property-estimation claim. |

These are the main public-facing surfaces today. They should be presented as
disciplined research infrastructure, not as finished discoveries.

## Mature Quality-Floor Tracks

| Campaign | What it teaches APL |
| --- | --- |
| [Pendulum Formula Falsification](./pendulum-formula-falsification.md) | Exact-reference replay, approximation failure modes, AGENT_VALIDATED negative/overfit memory, leaderboard discipline, and honest range limits. |
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
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed, exact-reference fixtures exist, Stefan-Boltzmann and Stellar M-L are agent-validated, FIRAS/Wien RESULT-0023 is agent-validated calibration memory, and RESULT-0024 has a replay metadata caveat. | RESULT-0023 maintainer/public wording and RESULT-0024 metadata-caveat adjudication; no model-derived Gaia mass truth rows or universal formula claims. |
| Materials widenings | `MD-0002` stable ternary oxides are frozen and have AGENT_VALIDATED RESULT-0021 plus scope-control and transfer-negative memory. | External dataset-release decision before DOI/archive wording; no materials claims. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | Newly active source-pinned benchmark lane with ThermoML Tb RESULT-0026 and preserved esters/lactones failed-family memory. | Gate B replay and local-only identity/count feasibility before expansion; no raw archive vendoring or multi-property broadening. |

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
