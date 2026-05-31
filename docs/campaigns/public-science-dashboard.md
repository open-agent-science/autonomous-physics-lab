# Public Science Dashboard

This page is the public campaign monitor for APL. It is meant for scientists,
technical contributors, and curious readers who want to see what each active
campaign is testing, what has already been learned, what is blocked, and which
reviewable result may appear next.

APL does not use this page to announce discoveries. It uses this page to show
the research frontier in a way that is easy to inspect, reproduce, and falsify.

## Shareable Result Cards

These cards are intentionally short and linkable. They are safe for README
summaries, issue comments, social posts, or external discussion because each
card carries its limitation line with the result.

### Exoplanet Compact-Radius Benchmark Diagnostic

**Short version:** On a pinned NASA Exoplanet Archive PSCompPars snapshot, APL
finds that the compact-radius slice (`R < 1.5 R_earth`) is the strongest
current matched-control survivor in a frozen Chen-Kipping-style mass-radius
failure-map audit. A later mass-quartile scout found that the compact slice is
still underpowered for quartile localization, while leaving an upper-mass-half
diagnostic hint.

**Why it is interesting:** this is a clear, visual benchmark surface:
mass-radius baseline, residual map, matched controls, deterministic replay,
and explicit forbidden wording.

**Limitation:** this is not a planet-composition, habitability, or new
mass-radius-law claim. The current scorecard verdict is
`BENCHMARK_SUMMARY_ONLY`.

**Evidence trail:**

- [External-reviewer replication capsule](../results/exoplanet-external-reviewer-replication-capsule.md)
- [Compact-radius benchmark evidence card](../results/exoplanet-compact-radius-benchmark-card.md)
- [Exoplanet failure-map result-promotion scorecard](../reviews/exoplanet-failure-map-result-promotion-scorecard.md)
- [Compact/sub-Neptune matched-control audit](../reviews/exoplanet-compact-subneptune-matched-control-audit.md)
- [Independent compact-radius replay](../reviews/exoplanet-compact-radius-independent-replay.md)
- [Exoplanet campaign page](./exoplanet-mass-radius.md)

### Nuclear Local-Curvature Falsification

**Short version:** APL tested a promising Nuclear local-curvature residual
candidate under a bounded no-leakage prototype and falsified it.

**Why it is interesting:** the negative result is useful scientific memory:
it blocks a tempting residual-feature lane from being repeated or promoted
without controls.

**Limitation:** this does not validate or falsify any broad nuclear mass law.
Reveal scoring remains blocked until a future source-grade no-peek release.

**Evidence trail:**

- [Nuclear local-curvature no-leakage prototype review](../reviews/nuclear-local-curvature-no-leakage-prototype.md)
- [Nuclear Mass Surface campaign page](./nuclear-mass-surface.md)

### Quantum Direct-Measurement Data Gate

**Short version:** APL has not started the Quantum Size Effects baseline
because the committed rows are calibration-derived rather than direct
measurement rows.

**Why it is interesting:** the campaign demonstrates source discipline before
attractive modeling. A source blocker is treated as useful output, not as a
failure.

**Limitation:** there is no quantum-dot size-effect benchmark result yet.

**Evidence trail:**

- [Quantum Size Effects campaign page](./quantum-size-effects.md)
- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)

### Textbook Formula Audit Scaffold

**Short version:** APL is preparing a campaign to audit famous textbook
formulas by source, range, assumptions, and out-of-distribution failure maps.

**Why it is interesting:** it is an accessible way for many agents to run
bounded, reviewable audits without claiming new laws.

**Limitation:** no textbook formula audit has run yet. The first task is
Stellar Mass-Luminosity source/baseline planning, not metrics.

**Evidence trail:**

- [Textbook Formula Audit campaign page](./textbook-formula-audit.md)
- [Candidate slate](../notes/textbook-formula-audit-candidate-list.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Which residual-feature families survive no-leakage controls and future reveal discipline? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified; residual-free F2 is inconclusive; pairing-asymmetry and magic-parity controls are negative/control-dominated; isotope-chain transfer is mixed and chain-local. | Negative evidence card, F2 finer-taxonomy preflight, training-slice feasibility, and reveal-source readiness | A negative/preflight package that prevents another weak Nuclear loop, or a genuinely disjoint controls-first lane. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | Where does a frozen Chen-Kipping-style mass-radius baseline fail on a pinned PSCompPars snapshot? | Compact-radius planets (`R < 1.5 R_earth`) are the strongest matched-control survivor; mass-quartile localization is underpowered; the target-freeze protocol and external-reviewer capsule are review-ready; scorecard verdict is `BENCHMARK_SUMMARY_ONLY`. | Null-baseline family audit and host-context preflight | A stronger benchmark-control panel that tells whether compact-radius residual stress survives simple null baselines and host-context checks. |
| [Quantum Size Effects](./quantum-size-effects.md) | Can APL build a direct-measurement row dataset before running size-effect baselines? | Calibration-derived rows and source triage exist, but direct measurement rows are still the blocker. | `TASK-0398`, `TASK-0489`, `TASK-0490`, `TASK-0491` | A source artifact/blocker, synthetic digitization fixture, or explicit scorecard for any weaker calibration-consistency path. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Can high-precision frequency-ratio data become a benchmark surface without hiding covariance or source-version risk? | Beloy 2021 is pinned as sandbox-only `ACR-0001`; a PSD source-derived covariance approximation exists; Nemitz 2016 source artifact is pinned but rows remain blocked; first-benchmark covariance policy is defined. | Real-row loader, fallback source triage, direct-vs-derived separation, and synthetic cross-source dry-run | A source/covariance readiness package that says whether a first narrow Yb/Sr consistency benchmark can become legitimate later. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Campaign scaffold and ranked candidate slate exist; no audit has run yet. | Wien and Stefan-Boltzmann planning plus Stellar M-L review | Source/baseline plans that make the first public formula audits runnable later. |

## What Is Interesting Right Now

### Exoplanet Compact-Radius Residual Stress

The exoplanet campaign has the clearest near-term public benchmark story right
now. A frozen Chen-Kipping-style baseline was compared against a pinned NASA
Exoplanet Archive PSCompPars snapshot. The compact-radius slice
(`R < 1.5 R_earth`) is the strongest current matched-control survivor.

Why it matters:

- APL has a reproducible exoplanet mass-radius benchmark/failure-map surface.
- The compact-radius slice shows residual stress that survives the current
  matched-control panel.
- Mass-quartile localization is currently underpowered, so the next useful
  tests are null baselines and host-context preflight rather than stronger
  planet-physics interpretation.
- This is a benchmark-diagnostic signal, not a planet-composition claim.

Scope:

The result does not say that APL found a new exoplanet law, predicts
habitability or planet composition, or globally falsified Chen-Kipping.

Current visible artifact: a compact evidence card that points to the scorecard,
metrics, independent replay, and limitations.

### Nuclear No-Leakage Falsification

The Nuclear campaign remains the flagship validation surface, but its newest
important lesson is negative: `LOCAL-CURVATURE-001` did not survive the
bounded no-leakage prototype. That is useful scientific memory because it
prevents agents from repeating a promising but leakage-sensitive path.

Why it matters:

- APL preserves negative and falsified Nuclear residual-feature lanes.
- The shell-axis lane remains diagnostic-only.
- Reveal scoring remains blocked until a future source-grade no-peek release.

Next visible artifact: a local-curvature result-promotion preflight that records
the falsification as negative/inconclusive memory, reveal-source readiness, or
a genuinely new controls-first lane. The residual-free high-error cluster
audit, neutron-rich boundary transfer, and magic-distance interaction lanes
have all landed as non-positive sandbox memory and should not be treated as
positive near-misses.

### Quantum And Atomic Fresh-Data Gates

Quantum Size Effects and Atomic-Clock Residuals are slower because they are
doing source hygiene before metrics. The visible result right now is the data
gate itself: which sources are strong enough to support a benchmark, and which
ones are not.

Why it matters:

- Quantum is blocked on direct measurement rows or an explicit weaker
  calibration-consistency scope.
- Atomic has one pinned direct-row seed, but benchmark readiness is blocked on
  a second source, real-row loader, holdout/no-peek boundary, and covariance
  policy acceptance.

Next visible artifact: a source artifact that unblocks row curation, or a
reviewed blocker that saves future agents from chasing an unusable source.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The first recommended slice is Stellar Mass-Luminosity OOD planning on
Gaia DR3, not an audit run yet.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: a Stellar M-L source/baseline plan that declares snapshot,
schema, holdout, and verification gates before any metrics.
