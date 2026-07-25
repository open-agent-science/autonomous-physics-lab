# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** complete the `f_K/f_pi`
  value-admissibility gate after two partial-hold dependency audits, run
  identity-independent CHARA replay, independently replay bounded OQMD
  negative/control memory, and execute the source-ready ThermoML fixture
  extraction. FRB, Exoplanet, Nuclear, Atomic, and Quantum remain reveal- or
  source-trigger-gated.
- **Fresh-data monitoring:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows and a source-limited `171Yb/87Sr`
  consistency memory card plus source-blocked McGrew and `171Yb/88Sr` routes;
  Quantum has six direct Almeida InP rows, a source-scoped sandbox baseline,
  and `RESULT-0029`, an AGENT_VALIDATED ZnSe/InP no-refit transfer result that
  failed to clear its predeclared margin; the Kim-2020 route is underpowered
  and has no qualifying independent source).
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
| inspect a stopped direct-measurement route | [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 produced six direct InP rows and `RESULT-0029`; Kim-2020 produced separate four-row absorption and emission surfaces, but both are underpowered and no independent source cleared the gates. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy and Nemitz `171Yb/87Sr` rows plus a first exploratory cross-source diagnostic; Pizzocaro and McGrew are blocked, and the multi-species path is `KEEP_MONITOR_ONLY`, so the live work is trigger/blocker memory. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, a citable MD-0002 release, and AGENT_PUBLISHED `RESULT-0032`, a bounded within-OQMD negative/control result awaiting independent replay. |
| inspect source-pinned thermophysical evidence | [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | It has AGENT_VALIDATED ThermoML `Tb` / Joback `RESULT-0026` and failed-family `RESULT-0028`; exact-80 is stopped and the frozen at-most-74-row fixture is ready for value-blind extraction from the private-source archive. |
| monitor the exoplanet benchmark surface | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has pinned snapshots, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, `NO_NOTIFY` monitor check 3, and AGENT_VALIDATED `RESULT-0027`; new scoring waits for a source-version trigger. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| test a new source-gated campaign | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) | The Lattice-QCD incubator selected `f_K/f_pi` for one bounded primary-source/dependency pilot; no central values or full campaign are authorized. |
| propose a longer-horizon direction | [Anomaly Registry](./anomaly-registry.md) | This remains a planning surface; keep it schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | `NMD-0003` frozen stratified gate, negative factory memory, AGENT_VALIDATED `RESULT-0018`, exact-replayed `RESULT-0025` point-estimator evidence, failed no-peek uncertainty calibration, DZ10 parity readiness, and frozen point-only prospective PRED entries. | Approved reveal-source/watch discipline and the `TASK-0305` scoring lane; no interval claim, broad F2, shell, local-curvature, Wigner, or ad hoc reveal scoring. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshots, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, reviewer capsule, closed `EXO-0002` reopen gate, `NO_NOTIFY` monitor check 3, and AGENT_VALIDATED `RESULT-0027`. | Monitor-only until a NOTIFY class appears; no residual scoring on the unchanged snapshot. |
| [Quantum Size Effects](./quantum-size-effects.md) | Almeida 2023 direct InP rows, AGENT_VALIDATED `RESULT-0029`, Kim-2020 `UNCERTAINTY_BLOCKED` digitization memory, and separate four-row absorption/emission surfaces. | Monitor for a genuinely new source trigger; the current route is underpowered and has no qualifying independent source. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy and Nemitz `171Yb/87Sr` rows, real-row loader, covariance policy, Pizzocaro diagnostic blocker/contract, source-limited consistency memory, blocked McGrew/NIST route, `171Yb/88Sr` isotope-mismatch blocker, and `KEEP_MONITOR_ONLY` multi-species verdict. | Durable reopen-trigger ledger; no constants-drift or metric rerun. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001`, `MD-0002`, AGENT_VALIDATED `RESULT-0021`, a citable Zenodo DOI, and AGENT_PUBLISHED `RESULT-0032` negative/control memory on a source-replayed 172-row OQMD surface. | Independently replay the unchanged failed exact-pair gate; do not refit or pool databases. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Four narrow results are AGENT_VALIDATED; CHARA `RESULT-0031` is AGENT_PUBLISHED INCONCLUSIVE with repaired publisher provenance, while Gaia DR4 remains held on luminosity semantics. | Perform identity-independent replay without rescuing the margin. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | AGENT_VALIDATED ThermoML `Tb` `RESULT-0026` and failed-family `RESULT-0028`; exact-80 failed, and a value-blind at-most-74-row contract is frozen. | Extract through the private-source boundary and enforce article-cap/information-floor gates; no score yet. |

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
| [Fresh Physics Data Axes](./fresh-physics-data-axes.md) | Atomic and FRB have graduated; the Lattice-QCD incubator selected `f_K/f_pi` and now preserves two partial-hold dependency audits. | Complete the no-value admissibility policy; numeric activation adjudication remains blocked. |
| [Anomaly Registry](./anomaly-registry.md) | Schema/admissibility scaffold, not a joint-fit campaign. | Schema validation, admissibility examples, or synthetic-only likelihood contracts. |
| [Thought-Experiment Consistency](./thought-experiment-consistency.md) | Planning active, no canonical benchmark run yet. | Scoped scenario planning and deterministic validator design. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Stefan-Boltzmann, Stellar M-L, FIRAS/Wien, and high-mass transfer are agent-validated; CHARA has a bounded AGENT_PUBLISHED INCONCLUSIVE result with repaired publisher provenance. | Replay only with an identity-independent executor; no model-derived Gaia truth rows or universal formula claims. |
| Materials widenings | `MD-0002` stable ternary oxides are frozen and have AGENT_VALIDATED RESULT-0021 plus scope-control, transfer-negative memory, and Zenodo DOI record-back. | Future rebuild requires a versioned release reason; otherwise use the citable v0.1.0 archive as fixed memory. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | Source-pinned benchmark with AGENT_VALIDATED RESULT-0026/0028 and a revised at-most-74-row no-score contract. | Archive-gated extraction only; no raw archive vendoring, partial fixture, threshold shopping, or multi-property broadening. |

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
