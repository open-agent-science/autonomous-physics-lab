# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** FRB reveal-source discipline
  after the registered and GitHub-anchored `PRED-0001`, Exoplanet
  `RESULT-0027` monitor-only trigger discipline after Gate-B-safe replay,
  Nuclear point-only reveal governance, and source/readiness decisions for Atomic, Quantum, Stellar,
  Particle, Materials, and ThermoML.
- **Fresh-data buildout:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows and a source-limited `171Yb/87Sr`
  consistency memory card plus source-blocked McGrew and `171Yb/88Sr` routes;
  Quantum has six direct Almeida InP rows, a source-scoped sandbox baseline,
  and `RESULT-0029`, an AGENT_VALIDATED ZnSe/InP no-refit transfer result that
  failed to clear its predeclared margin).
- **Reusable-dataset buildout:** Materials Property Residuals now has `MD-0001`,
  `MD-0002`, AGENT_VALIDATED `RESULT-0021`, and a citable MD-0002 Zenodo
  release with DOI `10.5281/zenodo.21207072`.
- **New thermophysical benchmark lane:** Thermophysical Property Residuals has
  ThermoML normal-boiling-temperature `RESULT-0026`, a bounded
  AGENT_VALIDATED Joback transfer result, plus `RESULT-0028`, an
  AGENT_VALIDATED esters/lactones failed-family negative/control result.
- **Public verifier lane:** Textbook Formula Audit.
- **Monitor-only lane:** Exoplanet Mass-Radius, until a new pinned archive
  snapshot or source-version trigger reopens residual scoring.
- **Quality floor:** Pendulum, Dimensional Analysis, and Particle Mass
  Relations.
- **Planning/source gate:** Lattice-QCD aggregated consistency inside Fresh
  Physics Data Axes.
- **Watchlist:** Anomaly Registry and Thought-Experiment Consistency.

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
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 produced six direct InP rows and a source-scoped sandbox baseline; `RESULT-0029` preserves the ZnSe no-refit miss, and Kim-2020 now has a frozen contract for exactly twelve CdSe observations before any metric. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy and Nemitz `171Yb/87Sr` rows plus a first exploratory cross-source diagnostic; Pizzocaro and McGrew are blocked, and the multi-species path is `KEEP_MONITOR_ONLY`, so the live work is trigger/blocker memory. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, and a citable MD-0002 release; bounded OQMD acquisition is under review, while only within-source controls may be planned value-blind. |
| inspect source-pinned thermophysical evidence | [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | It has AGENT_VALIDATED ThermoML `Tb` / Joback `RESULT-0026` and failed-family `RESULT-0028`; the exact 80-row route is stopped because acids and ketones are underpopulated under the frozen contract. |
| monitor the exoplanet benchmark surface | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has pinned snapshots, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, `NO_NOTIFY` monitor check 3, and AGENT_VALIDATED `RESULT-0027`; new scoring waits for a source-version trigger. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| test a new source-gated campaign | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) | The Lattice-QCD incubator selected `f_K/f_pi` for one bounded primary-source/dependency pilot; no central values or full campaign are authorized. |
| propose a longer-horizon direction | [Anomaly Registry](./anomaly-registry.md) | This remains a planning surface; keep it schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, AGENT_VALIDATED `RESULT-0018`, exact-replayed `RESULT-0025` point-estimator evidence, failed no-peek uncertainty calibration, DZ10 parity readiness, and frozen point-only prospective PRED entries. | Approved reveal-source/watch discipline and the `TASK-0305` scoring lane; no interval claim, broad F2, shell, local-curvature, Wigner, or ad hoc reveal scoring. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, closed `EXO-0002` reopen gate, `NO_NOTIFY` monitor check 3, and AGENT_VALIDATED `RESULT-0027`. | Monitor-only until a NOTIFY class appears; no residual scoring on the unchanged snapshot. |
| [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 direct InP rows, source-scoped sandbox baseline, frozen factual ZnSe rows, AGENT_VALIDATED `RESULT-0029`, and a pinned Kim-2020 CdSe source plus twelve-observation extraction contract. | Extract and independently reconcile only the predeclared CdSe rows; no metrics or repeat transfer yet. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy and Nemitz `171Yb/87Sr` rows, real-row loader, covariance policy, Pizzocaro diagnostic blocker/contract, source-limited consistency memory, blocked McGrew/NIST route, `171Yb/88Sr` isotope-mismatch blocker, and `KEEP_MONITOR_ONLY` multi-species verdict. | Durable reopen-trigger ledger; no constants-drift or metric rerun. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, scope-control memory, transfer-negative replay, and a citable Zenodo MD-0002 dataset DOI. | Finish bounded OQMD acquisition review; plan within-source controls value-blind, with split and metrics still gated. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Four narrow results are AGENT_VALIDATED; CHARA now has twelve component rows across six systems plus a frozen dependence policy, while Gaia DR4 remains value-blind and source-gated. | Independently replay CHARA provenance, then run a frozen-relation no-refit transfer; do not fill source-limited systems with inferred values. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | AGENT_VALIDATED ThermoML `Tb` `RESULT-0026` and failed-family `RESULT-0028`; the frozen exact-80 count gate failed at acids 6/10 and ketones 8/10. | Monitor only; reopen for a new source or independently motivated predeclared contract, not threshold lowering. |

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
| [Fresh Physics Data Axes](./fresh-physics-data-axes.md) | Atomic and FRB have graduated; the Lattice-QCD incubator selected `f_K/f_pi` for a bounded source/dependency pilot. | Audit primary-publication and shared-ensemble metadata; no central values or world average. |
| [Anomaly Registry](./anomaly-registry.md) | Schema/admissibility scaffold, not a joint-fit campaign. | Schema validation, admissibility examples, or synthetic-only likelihood contracts. |
| [Thought-Experiment Consistency](./thought-experiment-consistency.md) | Planning active, no canonical benchmark run yet. | Scoped scenario planning and deterministic validator design. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Stefan-Boltzmann, Stellar M-L, FIRAS/Wien, and Stellar high-mass transfer are agent-validated within narrow scopes; CHARA now has a bounded six-system component surface and dependence policy. | Replay the CHARA source surface and score the fixed relation without refit; no model-derived Gaia truth rows or universal formula claims. |
| Materials widenings | `MD-0002` stable ternary oxides are frozen and have AGENT_VALIDATED RESULT-0021 plus scope-control, transfer-negative memory, and Zenodo DOI record-back. | Future rebuild requires a versioned release reason; otherwise use the citable v0.1.0 archive as fixed memory. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | Monitor-only source-pinned benchmark with AGENT_VALIDATED RESULT-0026 and failed-family RESULT-0028. | Exact-80 is stopped by family underpopulation; no raw archive vendoring, threshold shopping, or multi-property broadening. |

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
