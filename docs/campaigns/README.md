# Campaign Map

This directory is the campaign-level map for APL. Use it when you want to
understand where the repository is doing science, where it is only preparing a
data surface, and where agents can help without overclaiming.

The short version:

- **Flagship validation challenge:** Nuclear Mass Surface.
- **Default near-term science-output sprint:** Exoplanet Mass-Radius.
- **Fresh-data buildout:** Atomic-Clock Residuals and Quantum Size Effects
  (source-gated; Atomic has pinned rows, Quantum still needs direct rows).
- **Public verifier lane:** Textbook Formula Audit.
- **Candidate new lanes:** Materials Property Residuals, pending
  source/baseline scaffolds.
- **Quality floor:** Pendulum, Dimensional Analysis, and Particle Mass
  Relations.
- **Planning/watchlist:** Fresh Physics Data Axes, Anomaly Registry, and
  Thought-Experiment Consistency.

For a compact machine-readable portfolio map, see
[`campaigns/catalog.yaml`](../../campaigns/catalog.yaml) and
[`docs/campaign-registry.md`](../campaign-registry.md). The catalog summarizes
status, stage, agent capacity, gates, allowed work, forbidden work, and result
pointers for parallel agent planning; it does not replace this human-readable
campaign map or `missions/current.yaml`.

## Start By Intent

| If you want to... | Start here | Why |
| --- | --- | --- |
| see what can be shared publicly today | [Public Science Dashboard](./public-science-dashboard.md) | It has linkable result cards, safe wording, current questions, and expected next results per active campaign. |
| review the flagship validation challenge | [Nuclear Mass Surface](./nuclear-mass-surface.md) | It has a frozen baseline, sandbox scout evidence, prediction registry entries, source gates, explicit negative controls, and several useful negative/control results. |
| help build the next direct-measurement dataset | [Quantum Size Effects](./quantum-size-effects.md) | It is blocked on source-grade direct rows before benchmark work can honestly begin. |
| work on high-precision fresh data | [Atomic-Clock Residuals](./atomic-clock-residuals.md) | It has Beloy rows pinned, a real-row loader, synthetic cross-source dry-run plumbing, Nemitz source artifact pinned with rows blocked, and a covariance policy; fallback, direct-vs-derived, and readiness gates are next. |
| work on the default science-output sprint | [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | It now has a pinned snapshot, benchmark diagnostics, target-freeze protocol, reviewer capsule, and null-baseline control panel; host-context preflight is the next useful artifact. |
| replay mature evidence | [Pendulum Formula Falsification](./pendulum-formula-falsification.md) or [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | These are safer quality-floor tracks with deterministic replay value. |
| propose a longer-horizon direction | [Fresh Physics Data Axes](./fresh-physics-data-axes.md) or [Anomaly Registry](./anomaly-registry.md) | These are planning surfaces; keep them schema- and guardrail-first. |

## Current Public-Facing Surfaces

| Campaign | Current maturity | Best next contribution |
| --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Baseline benchmark, sandbox pilots, deterministic factory, frozen prospective registry, no-leakage policy, shell-axis diagnostic-only decision, local-curvature no-leakage falsification, and several negative/control/local residual lanes. | `TASK-0477`, `TASK-0478`, and `TASK-0479`: negative evidence card, F2 taxonomy preflight, and training-slice feasibility review before another fitting wave. |
| [Exoplanet Mass-Radius Benchmark](./exoplanet-mass-radius.md) | Pinned catalog snapshot, CK17-style baseline, residual/failure map, compact-radius matched-control diagnostic, underpowered mass-quartile scout, target-freeze protocol, reviewer capsule, `BENCHMARK_SUMMARY_ONLY` promotion scorecard, and `TASK-0483` null-baseline control panel showing the highlighted slices are control-sensitive. | `TASK-0481`: host-context preflight before any further residual pilot. |
| [Quantum Size Effects](./quantum-size-effects.md) | Scaffold, calibration-derived seeds, direct-source triage, source-artifact intake path, and synthetic digitization fixture exist; measurement-grade baseline remains blocked. | `TASK-0398`, `TASK-0489`, and `TASK-0491`: source artifact review and go/no-go criteria for any weaker calibration-consistency benchmark. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Beloy 2021 pinned direct rows, deterministic real-row loader, source-derived covariance approximation, synthetic cross-source dry-run, Nemitz 2016 source artifact pinned with rows blocked, and first-benchmark covariance policy. | `TASK-0485`, `TASK-0487`, and then `TASK-0455`: fallback source triage, direct-vs-derived separation, and baseline-readiness gate. |

These four are the main public-facing surfaces today. They should be presented
as disciplined research infrastructure, not as finished discoveries.

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
| [Textbook Formula Audit](./textbook-formula-audit.md) | Scaffold landed (TASK-0438), Stellar M-L planning exists, and first public-verifier follow-ups are queued. | `TASK-0492` and `TASK-0493` plan Wien displacement and Stefan-Boltzmann audits; keep them source/baseline/holdout-first before any metrics. |
| Materials Property Residuals | Candidate scaffold task pending. | Source-manifest, schema, pinned snapshot, and baseline planning before any property-residual modeling. |

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
