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
  `MD-0001` benchmark clarifies value.
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
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | It is blocked on source-grade direct rows; the current best paths are Norris-Bawendi source-copy handoff and Kang-Wise fallback source packaging. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy rows pinned, row roles assigned, a real-row loader, synthetic cross-source dry-run plumbing, Nemitz and Pizzocaro source artifacts, and a covariance policy; Pizzocaro row admissibility is next. |
| work on reusable benchmark datasets | [Materials Property Residuals](./materials-property-residuals.md) | It has the first pinned reusable-dataset candidate (`MD-0001`), holdout manifest, citation metadata, and first conservative baseline evidence. |
| work on the default science-output sprint | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It has a pinned snapshot, benchmark diagnostics, target-freeze protocol, reviewer capsule, null-baseline control panel, and second pinned snapshot; the next useful artifacts are coverage and delta decisions. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Baseline benchmark, sandbox pilots, deterministic factory, frozen prospective registry, no-leakage policy, shell-axis diagnostic-only decision, local-curvature no-leakage falsification, `NMD-0003` factory sprint with zero shortlist, and a frozen stratified NMD-0003 readiness gate. | `TASK-0583`, `TASK-0584`, `TASK-0553`, and `TASK-0585`: replay the frozen gate, run one bounded residual-feature sprint, score F2 under controls, and scout reveal-source manifests without values. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshot, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, null-baseline control panel, target-freeze protocol, reviewer capsule, and a second pinned PSCompPars snapshot (`EXO-0002`). | `TASK-0580`, `TASK-0581`, and `TASK-0582`: coverage gate, snapshot delta audit, then bounded baseline replay preflight only if the gate clears. |
| [Quantum Size Effects](./quantum-size-effects.md) | Scaffold, calibration-derived seeds, direct-source triage, source-artifact intake path, synthetic digitization fixture, calibration-consistency scorecard, and Norris-Bawendi blocker package exist; measurement-grade baseline remains blocked. | `TASK-0589` and `TASK-0588`: source-copy handoff for Norris-Bawendi and fallback Kang-Wise source artifact package. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy 2021 pinned direct rows, manifest-backed row roles, deterministic real-row loader, source-derived covariance approximation, synthetic cross-source dry-run, Nemitz source artifact, Pizzocaro source artifacts, and first-benchmark covariance policy. | `TASK-0567`: decide whether Pizzocaro can become an admissible second Yb/Sr row or remains blocker memory. |
| [Materials Property Residuals](./materials-property-residuals.md) | `MD-0001`, a pinned Materials Project stable-binary-oxides dataset with 169 rows, and first conservative baseline evidence: formation energy benefits more clearly from composition-aware baselines than band gap. | `TASK-0566`, `TASK-0578`, and `TASK-0579`: promotion preflight, independent replay, and band-gap null-control audit. |

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
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed, Stefan-Boltzmann/Wien exact-reference fixtures exist, exact-reference result preflight is done, and Stellar M-L source/baseline planning exists. | `TASK-0586` and `TASK-0587`: scoped exact-reference result packaging or blocker, plus Stellar M-L row-readiness gate. |
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
