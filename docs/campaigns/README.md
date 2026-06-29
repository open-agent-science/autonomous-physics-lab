# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** external-release decision for
  Materials `RESULT-0021`, Gate B replay for FIRAS/Wien `RESULT-0023`,
  maintainer-review packets for `RESULT-0024` / `RESULT-0025`, and public-safe
  negative/source-blocker memory for Nuclear / Atomic / Exoplanet / Pendulum.
- **Fresh-data buildout:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows and a source-limited Yb/Sr consistency
  memory card plus a Pizzocaro aggregation contract that still blocks row
  admission; Quantum has six direct Almeida InP rows, a source-scoped sandbox
  baseline, a license-limited ZnSe route, and failed effective-mass transfer
  memory already routed as sandbox-only negative/control evidence).
- **Reusable-dataset buildout:** Materials Property Residuals now has `MD-0001`,
  `MD-0002`, AGENT_VALIDATED `RESULT-0021`, and internal release metadata; an
  external archive/DOI decision remains maintainer-gated.
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
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 produced six direct InP rows and a source-scoped sandbox baseline; the current blocker is ZnSe/Toufanian license verification and baseline-readiness/transfer-source decision, not another correction-search pilot. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy and Nemitz Yb/Sr rows plus a first exploratory cross-source diagnostic; Pizzocaro remains diagnostic-only, so the next useful route is a new independent absolute Yb/Sr source scout or maintainer aggregation decision, not another metric rerun. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, and scope-control memory; the current blocker is an external archive/DOI release decision, not benchmark replay. |
| monitor the exoplanet benchmark surface | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has pinned snapshots, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, and a closed `EXO-0002` reopen gate; new scoring waits for a source-version trigger. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, AGENT_VALIDATED `RESULT-0018`, rejected Wigner-cusp sandbox memory, AGENT_PUBLISHED/Gate-B-replayed `RESULT-0025` point-estimator evidence, and a value-blind reveal-source preflight that found no admissible source manifest. | `TASK-0865`, `TASK-0878`, or `TASK-0890`: uncertainty-route preflight, DZ10 parity reference, or safe RESULT-0025 review packet; no broad F2, shell, local-curvature, Wigner, or prediction-freeze restart. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, closed `EXO-0002` reopen gate, and repeated no-notify source-version monitors. | Continue metadata-only monitoring; no residual scoring unless a NOTIFY class appears. |
| [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 direct InP rows, source-scoped sandbox baseline, controls/holdout summary, license-limited ZnSe route, and failed effective-mass transfer check routed as sandbox negative memory. | `TASK-0870`: verify the ZnSe source/license route; no correction-search unblock. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy and Nemitz Yb/Sr rows, real-row loader, covariance policy, Pizzocaro diagnostic blocker/contract, and a source-limited consistency memory card. | `TASK-0889`: scout one independent absolute Yb/Sr source route, or wait for maintainer aggregation decision; no constants-drift or metric rerun. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, family-holdout scope boundary, descriptor-ablation control memory, transfer-negative replay, and repository-local release metadata. | `TASK-0887`: prepare the external archive/DOI decision packet before external dataset claims. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | AGENT_VALIDATED exact-reference `RESULT-0019`, AGENT_VALIDATED Stellar M-L `RESULT-0022`, AGENT_PUBLISHED FIRAS/Wien `RESULT-0023`, and high-mass transfer `RESULT-0024` replay memory. | `TASK-0885` or `TASK-0886`: replay RESULT-0023 or prepare safe RESULT-0024 review wording; no universal formula claim. |

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
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed, exact-reference fixtures exist, Stefan-Boltzmann has an agent-validated software/convention result, Stellar M-L has AGENT_VALIDATED RESULT-0022, and FIRAS/Wien RESULT-0023 is workflow-packaged for replay. | RESULT-0023 Gate B replay and RESULT-0024 maintainer wording packets; no model-derived Gaia mass truth rows or universal formula claims. |
| Materials widenings | `MD-0002` stable ternary oxides are frozen and have AGENT_VALIDATED RESULT-0021 plus scope-control and transfer-negative memory. | External dataset-release decision before DOI/archive wording; no materials claims. |

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
