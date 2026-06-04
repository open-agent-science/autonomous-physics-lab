# Quantum Calibration-Curve Consistency Waiver Decision

**Task:** `TASK-0326`
**Status:** review decision; no benchmark run
**Decision:** recommend a separate limited-scope calibration-curve consistency
benchmark, while keeping `TASK-0225` blocked for measurement-versus-model
benchmarking.

## Scope

This review decides whether the current calibration-derived quantum-dot rows
should remain a blocker for the first benchmark, or whether they can support a
deliberately weaker benchmark with explicit wording and artifact labels.

Inputs reviewed:

- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
- `data/quantum_dots/qd-0002-moreels-2009-pbs-absorption.yaml`
- `docs/reviews/quantum-size-direct-absorption-seed-review.md`
- `docs/reviews/quantum-size-direct-band-edge-seed-review.md`
- `TASK-0225`
- `TASK-0293`
- `docs/campaigns/quantum-size-effects.md`

No new numerical rows were added. No baseline model was fit. No claim,
canonical result, or knowledge artifact was promoted.

## Current Evidence State

The committed row-level quantum-dot data are useful, source-pinned, and schema
valid, but they are not measurement-grade rows:

| Dataset | Rows | Property | Provenance |
| --- | ---: | --- | --- |
| `qd-0001-yu-2003-absorption` | 12 | `absorption_peak_eV` | calibration-derived sizing-curve points |
| `qd-0002-moreels-2009-pbs-absorption` | 9 | `absorption_peak_eV` | calibration-derived sizing-curve points |

TASK-0283 correctly kept `TASK-0225` blocked because scoring a physical
baseline against those rows would compare one model family to published
calibration curves, not to direct measurements. TASK-0291 and TASK-0292 then
recorded blocker findings rather than adding direct rows: Yu 2003 exposes no
clean table values in the reviewed pass, and Jasieniak 2011 remains blocked on
Supporting Information access or a deterministic digitisation artifact.

## Option A: Keep TASK-0225 Blocked For Direct Rows

This option remains mandatory for the original first baseline scope.

`TASK-0225` should remain blocked as a measurement-versus-model residual
benchmark until one of these conditions is met:

- at least one direct-measurement `qd-*.yaml` seed lands with table values;
- a deterministic digitisation package lands with calibrated figure points;
- maintainer-provided rows satisfy the direct-measurement protocol;
- a later maintainer decision explicitly rewrites the TASK-0225 scope.

Benefits:

- preserves the clean measurement-versus-model meaning of residual metrics;
- avoids overstating agreement or disagreement against calibration curves;
- keeps `TASK-0293` as the correct readiness gate after direct rows land.

Risks:

- Quantum Size Effects can stall while source access or digitisation remains
  blocked;
- current curated rows remain useful but underused;
- contributors may keep rediscovering the same direct-row blockers.

## Option B: Authorize A Separate Calibration-Curve Consistency Benchmark

This option is scientifically useful if, and only if, it is separated from
`TASK-0225`.

Allowed meaning:

- compare conservative baseline families against published calibration-derived
  absorption sizing surfaces;
- detect whether simple baselines track or diverge from the calibration curves
  in a reproducible, source-pinned way;
- expose material and size-range residual structure as a planning diagnostic.

Forbidden meaning:

- not a measurement-versus-model benchmark;
- not evidence that a model matches direct experimental rows;
- not a basis for claim promotion;
- not a substitute for direct rows or `TASK-0293`;
- not a public-facing quantum-dot result without very explicit limitations.

Recommended labels and artifact names:

- benchmark label: `quantum_calibration_curve_consistency`;
- evidence class: `calibration_curve_consistency_only`;
- provenance label on every row: `calibration_derived`;
- result title wording: `Quantum-dot calibration-curve consistency benchmark`;
- review note wording: `weaker benchmark; not direct measurement evidence`;
- output location, if later authorized: a sandbox agent-run or a distinct
  maintainer-assigned result path that does not reuse the original
  `TASK-0225` measurement benchmark title.

Recommended metrics:

- MAE and RMSE in eV against calibration-derived `absorption_peak_eV` rows;
- per-material residuals for CdTe, CdSe, CdS, and PbS;
- size-bin residuals with fixed bins, such as `d <= 3 nm`, `3 < d < 6 nm`,
  and `d >= 6 nm`;
- held-out material diagnostics, if the split is documented as
  calibration-surface transfer rather than measurement generalization;
- negative controls such as bulk-bandgap constant predictors.

Required public wording:

- "calibration-derived rows";
- "consistency with published sizing curves";
- "not a direct measurement benchmark";
- "not a claim about material design or device behavior";
- "direct-row benchmark remains blocked until measurement-grade rows land".

## Decision

Recommend **Option B as a separate follow-up benchmark**, while preserving
**Option A for TASK-0225**.

In practical terms:

- `TASK-0225` stays `BLOCKED`;
- `TASK-0293` stays blocked until direct rows land or an explicit future waiver
  tells it to run a calibration-only gate;
- the current rows may support a future maintainer-approved
  calibration-curve consistency task;
- that future task should not reuse measurement-versus-model language or
  imply direct-row evidence.

This is a waiver recommendation, not the waiver itself. A maintainer still
needs to approve a concrete follow-up task or TASK-QUEUE item before any
calibration-consistency benchmark is run.

## Overclaim Blockers

Any future calibration-consistency benchmark should block or fail review if it:

- describes residuals as measurement error;
- merges absorption, emission, and bandgap values under one residual axis;
- omits per-row calibration-derived provenance;
- reports public-facing success language without the weaker-benchmark label;
- unblocks `TASK-0225` without direct measurement rows or explicit maintainer
  scope rewrite;
- promotes a claim, result, or knowledge entry from calibration-only evidence.

## Verdict

`PARTIALLY_VALID` as a campaign decision:

- valid to create a separate, weaker calibration-curve consistency benchmark
  after maintainer approval;
- invalid to treat the current rows as sufficient for the original
  measurement-versus-model `TASK-0225` benchmark;
- inconclusive for direct measurement readiness until TASK-0325 or another
  future data task lands compliant rows.
