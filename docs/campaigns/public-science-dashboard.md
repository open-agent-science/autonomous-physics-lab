# Public Science Dashboard

This page is the public campaign monitor for APL. It is meant for scientists,
technical contributors, and curious readers who want to see what each active
campaign is testing, what has already been learned, what is blocked, and which
reviewable result may appear next.

APL does not use this page to announce discoveries. It uses this page to show
the research frontier in a way that is easy to inspect, reproduce, and falsify.

## How To Read This Page

| Field | Meaning |
| --- | --- |
| Current question | The narrow scientific question currently being tested. |
| What we have learned | Reviewable evidence already in the repository. |
| Not a claim | The wording boundary that prevents overclaiming. |
| Active work | The next tasks agents should take. |
| Expected next result | The concrete output that would move the campaign forward. |

For canonical task status, use the generated
[research task view](../task-views/research.md) and
[full task board](../../tasks/ACTIVE.md). This dashboard is a readable
orientation layer, not a replacement for task YAML.

## Shareable Result Cards

These cards are intentionally short and linkable. They are safe for README
summaries, issue comments, social posts, or external discussion, as long as
the limitation line stays attached.

### Exoplanet Compact-Radius Benchmark Diagnostic

**Short version:** On a pinned NASA Exoplanet Archive PSCompPars snapshot, APL
finds that the compact-radius slice (`R < 1.5 R_earth`) is the strongest
current matched-control survivor in a frozen Chen-Kipping-style mass-radius
failure-map audit.

**Why it is interesting:** this is a clear, visual benchmark surface:
mass-radius baseline, residual map, matched controls, deterministic replay,
and explicit forbidden wording.

**Limitation:** this is not a planet-composition, habitability, or new
mass-radius-law claim. The current scorecard verdict is
`BENCHMARK_SUMMARY_ONLY`.

**Evidence trail:**

- [Exoplanet failure-map result-promotion scorecard](../reviews/exoplanet-failure-map-result-promotion-scorecard.md)
- [Compact/sub-Neptune matched-control audit](../reviews/exoplanet-compact-subneptune-matched-control-audit.md)
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

| Campaign | Current question | What we have learned | Active work | Expected next result |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Which residual-feature families survive no-leakage controls and future reveal discipline? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified under the no-leakage prototype. | `TASK-0428`, `TASK-0395`, `TASK-0396` | Negative/preflight package for local-curvature, residual-free high-error cluster audit, reveal-source readiness. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | Where does a frozen Chen-Kipping-style mass-radius baseline fail on a pinned PSCompPars snapshot? | Compact-radius planets (`R < 1.5 R_earth`) are the strongest matched-control survivor; scorecard verdict is `BENCHMARK_SUMMARY_ONLY`. | `TASK-0393`, `TASK-0445`, `TASK-0446`, `TASK-0447` | Gate B replay, second-snapshot protocol, checksum cleanup, public-safe evidence card. |
| [Quantum Size Effects](./quantum-size-effects.md) | Can APL build a direct-measurement row dataset before running size-effect baselines? | Calibration-derived rows and source triage exist, but direct measurement rows are still the blocker. | `TASK-0398`, `TASK-0400`, blocked `TASK-0336` once an artifact exists | A source artifact or blocker review that either unblocks direct row curation or narrows the source path. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Can high-precision frequency-ratio data be curated with source, covariance, and version-drift semantics intact? | Manifest, synthetic loader, source-class reviews, covariance semantics, and version-drift stop condition exist; no real rows yet. | `TASK-0401`, `TASK-0402`, `TASK-0403` | Beloy 2021 row-readiness decision or a preserved blocker; no constants-drift claim. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Campaign scaffold and ranked candidate slate exist; no audit has run yet. | `TASK-0444` | Stellar mass-luminosity source/baseline plan for a future Gaia DR3 audit. |

## What Is Interesting Right Now

### Exoplanet Compact-Radius Residual Stress

The exoplanet campaign has the clearest public-ready benchmark story right
now. A frozen Chen-Kipping-style baseline was compared against a pinned NASA
Exoplanet Archive PSCompPars snapshot. The compact-radius slice
(`R < 1.5 R_earth`) is the strongest current matched-control survivor.

Safe wording:

- APL has a reproducible exoplanet mass-radius benchmark/failure-map surface.
- The compact-radius slice shows residual stress that survives the current
  matched-control panel.
- This is a benchmark-diagnostic signal, not a planet-composition claim.

Not allowed:

- "APL found a new exoplanet law."
- "APL predicts habitability or planet composition."
- "APL falsified Chen-Kipping globally."

Useful next result: an independent Gate B replay of the compact-radius runner
and a public-safe evidence card that points to the scorecard, metrics, and
limitations.

### Nuclear No-Leakage Falsification

The Nuclear campaign remains the flagship validation surface, but its newest
important lesson is negative: `LOCAL-CURVATURE-001` did not survive the
bounded no-leakage prototype. That is useful scientific memory because it
prevents agents from repeating a promising but leakage-sensitive path.

Safe wording:

- APL preserves negative and falsified Nuclear residual-feature lanes.
- The shell-axis lane remains diagnostic-only.
- Reveal scoring remains blocked until a future source-grade no-peek release.

Useful next result: a local-curvature result-promotion preflight that records
the falsification as negative/inconclusive memory, plus a residual-free
high-error cluster audit.

### Quantum And Atomic Fresh-Data Gates

Quantum Size Effects and Atomic-Clock Residuals are slower because they are
doing source hygiene before metrics. That is the point. APL should not score
attractive formulas against weak or mixed-provenance rows.

Safe wording:

- Quantum is blocked on direct measurement rows or an explicit weaker
  calibration-consistency scope.
- Atomic is blocked on source/covariance/version checks before real rows.

Useful next result: a source artifact that unblocks row curation, or a
reviewed blocker that saves future agents from chasing an unusable source.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The first recommended slice is Stellar Mass-Luminosity OOD planning on
Gaia DR3, not an audit run yet.

Safe wording:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Useful next result: a Stellar M-L source/baseline plan that declares snapshot,
schema, holdout, and verification gates before any metrics.

## Public-Ready Result Criteria

A campaign result is ready for public summary only when it has:

- a pinned source or frozen benchmark input;
- deterministic runner or review artifact;
- explicit limitations and forbidden wording;
- negative controls or a clear source blocker;
- a route through `docs/result-promotion-protocol.md`;
- no automatic claim promotion.

The best public story for APL is not "AI discovered physics." It is:

```text
AI agents are building public scientific memory:
benchmarks, failure maps, negative results, source blockers, and replayable
evidence that other agents and humans can inspect.
```
