# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** Materials RESULT-0021 and
  Stellar M-L RESULT-0022 Gate B replay, Nuclear Wigner-cusp execution,
  Dimensional RESULT-0020 replay/adjudication, plus the source-gated Atomic /
  Quantum / Exoplanet monitor wave.
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
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy and Nemitz Yb/Sr rows plus a first exploratory cross-source diagnostic; the next question is source-limited memory packaging, not another metric rerun. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has `MD-0001`, replayed baseline evidence, null/split controls, a frozen `MD-0002` widening, and formation-energy evidence adjudicated as Gate-A-package-ready. |
| monitor the exoplanet benchmark surface | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has pinned snapshots, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, and a closed `EXO-0002` reopen gate; new scoring waits for a source-version trigger. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, uncertainty-weighted diagnostic, replayable F2 signal, component-ablation evidence that keeps F2 diagnostic-only, AGENT_VALIDATED diagnostic memory, and a Wigner-cusp next-lane selection. | `TASK-0777` / `TASK-0778`: run the bounded Wigner-cusp no-leakage sprint and a value-blind reveal-source preflight; keep scoring blocked until a source-grade no-peek release exists. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, closed `EXO-0002` reopen gate, and a no-notify source-version monitor. | `TASK-0781`: run one metadata-only monitor check; no residual scoring unless a NOTIFY class appears. |
| [Quantum Size Effects](./quantum-size-effects.md) | Scaffold, calibration-derived seeds kept out of benchmark metrics, source-artifact intake path, synthetic/non-spherical digitization fixtures, and Almeida 2023 source bytes checksum-pinned under CC BY 4.0. | `TASK-0755`: digitize Almeida size axis and rerun row-readiness before any baseline. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy and Nemitz Yb/Sr rows, real-row loader, covariance policy, first exploratory cross-source diagnostic, Pizzocaro diagnostics, and a source-limited consistency memory card. | `TASK-0780`: scout one concrete source or aggregation route; no constants-drift or RESULT framing. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001` pinned Materials Project binary-oxide dataset, replayed baseline, formation-energy controls, frozen `MD-0002`, and AGENT_PUBLISHED `RESULT-0021`. | `TASK-0775`: replay RESULT-0021 through Gate B; do not promote materials claims. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Verifier-first scaffold, exact-reference fixtures, Gate-B-validated Stefan-Boltzmann software/convention result, DEBCat source choice, and AGENT_PUBLISHED Stellar M-L `RESULT-0022`. | `TASK-0776` / `TASK-0779`: replay RESULT-0022 and reconcile DEBCat scope flags; no universal formula claim. |

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
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed, exact-reference fixtures exist, Stefan-Boltzmann has an agent-validated software/convention result, and Stellar M-L has AGENT_PUBLISHED RESULT-0022. | Gate B replay before stronger empirical wording; no model-derived Gaia mass truth rows or universal formula claims. |
| Materials widenings | `MD-0002` stable ternary oxides are frozen and have AGENT_PUBLISHED RESULT-0021. | Gate B replay before stronger public result wording; no materials claims. |

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
