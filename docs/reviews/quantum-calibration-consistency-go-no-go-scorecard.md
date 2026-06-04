# Quantum calibration-consistency go/no-go scorecard

- Task: `TASK-0491`
- Campaign: `quantum_size_effects`
- Decision: `NEEDS_MAINTAINER_DECISION`
- Task verdict: `not_applicable` (quality-gate planning artifact)
- Benchmark label if approved: `quantum_calibration_curve_consistency`
- Evidence class if approved: `calibration_curve_consistency_only`

## Scope

This scorecard decides whether a future, separate calibration-curve
consistency benchmark is sufficiently bounded to be proposed for maintainer
approval. It does not authorize that benchmark, run metrics, fit a model,
add rows, promote a result, unblock the direct-row benchmark, or change any
claim or knowledge artifact.

Inputs reviewed:

- `docs/reviews/quantum-calibration-consistency-waiver-decision.md`
- `docs/reviews/quantum-calibration-curve-consistency-benchmark-scope.md`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
- `data/quantum_dots/qd-0002-moreels-2009-pbs-absorption.yaml`
- `TASK-0225`

## Current evidence state

The current committed Quantum row surface is useful for a deliberately weak
consistency check, but not for direct measurement-versus-model validation.

| Dataset | Materials | Rows | Property axis | Provenance class |
| --- | --- | ---: | --- | --- |
| `qd-0001-yu-2003-absorption` | CdTe, CdSe, CdS | 12 | `absorption_peak_eV` | `calibration_derived` |
| `qd-0002-moreels-2009-pbs-absorption` | PbS | 9 | `absorption_peak_eV` | `calibration_derived` |

All 21 rows are source-pinned and schema-valid. They are evaluations or
inversions of published sizing curves, not direct table values, reviewed
figure-digitization points, or independently curated TEM plus spectroscopy
measurements. A future score against these rows would compare a baseline family
to published calibration surfaces. It would not estimate measurement error.

## Decision vocabulary

| Route | Meaning |
| --- | --- |
| `GO` | A maintainer has explicitly approved a new, separate sandbox-only implementation task that satisfies every scorecard rule below. |
| `NO_GO` | The proposed task blurs calibration-derived rows with direct measurements, omits required labels or controls, weakens the direct-row blocker, or proposes unsupported public interpretation. |
| `NEEDS_MAINTAINER_DECISION` | The protocol is bounded enough for a maintainer decision, but no explicit approval exists yet. Do not run metrics. |

## Current decision

`NEEDS_MAINTAINER_DECISION`

`TASK-0326` recommended a separate weaker benchmark, and `TASK-0335` defined a
safe planning contract. That is enough to ask a maintainer whether a sandbox
implementation task is worthwhile. It is not enough for an agent to start the
run autonomously.

The original `TASK-0225` direct measurement-versus-model benchmark remains
`BLOCKED`. This scorecard does not change `TASK-0293` direct-row readiness
requirements either.

## Required identity and labels

Any future maintainer-approved implementation must use all of these labels:

| Field | Required value |
| --- | --- |
| Benchmark label | `quantum_calibration_curve_consistency` |
| Evidence class | `calibration_curve_consistency_only` |
| Included-row provenance | `calibration_derived` |
| Result title wording | `Quantum-dot calibration-curve consistency benchmark` |
| Review-note wording | `weaker benchmark; not direct measurement evidence` |
| Initial output tier | sandbox-only |

The future task must use a new task id and separate output namespace, for
example:

`agent_runs/<run-id>/quantum_calibration_curve_consistency/`

It must not reuse `TASK-0225` paths, titles, result identifiers, or
measurement-versus-model wording.

## Allowed row use

A future implementation may use only committed rows that satisfy all of these
conditions:

- the dataset file is under `data/quantum_dots/qd-*.yaml`;
- its source is accepted in `data/quantum_dots/source_manifest.yaml`;
- its property axis is `absorption_peak_eV`;
- every included row is labeled `calibration_derived`;
- output metadata preserves `calibration_curve_consistency_only`;
- source, material, and size-bin summaries remain separate.

The initial eligible surface is limited to `qd-0001` and `qd-0002`. Direct
measurement rows, future digitized points, emission values, and bandgap values
must not be silently mixed into this calibration-only surface.

## Allowed diagnostic metrics

A future approved task may compute only consistency diagnostics:

- MAE and RMSE in eV against calibration-derived `absorption_peak_eV`;
- source-by-source residual summaries for Yu 2003 and Moreels 2009;
- material-level residual summaries for CdTe, CdSe, CdS, and PbS;
- fixed size-bin summaries with boundaries frozen before scoring;
- held-out-material diagnostics labeled as calibration-surface transfer, not
  measurement generalization.

No metric may be described as direct-measurement error or physical-model
validation.

## Required negative controls

The future task must freeze and report at least these controls before scoring:

1. A per-material bulk-bandgap constant predictor.
2. A wrong-material or shuffled-material-label control that exposes whether a
   reported improvement depends on the declared material mapping.
3. A simple sizing-curve baseline appropriate to the included property axis,
   with its provenance and parameter source recorded.

The implementation must stop rather than reinterpret the benchmark if a
negative control matches or beats the proposed baseline on the headline
diagnostic.

## Required limitations

Every report, plot caption, and summary must make these limitations explicit:

- the rows are calibration-derived;
- the benchmark tests consistency with published sizing curves;
- it is not a direct measurement benchmark;
- it is not a claim about material design or device behavior;
- it does not validate a universal quantum-dot size-effect law;
- source families and materials remain sparse;
- direct-row readiness remains blocked until measurement-grade rows land.

## Automatic stop conditions

Route the proposed implementation to `NO_GO` or stop the run if it would:

- run without explicit maintainer approval for the separate scoped task;
- call calibration-derived values direct measurements or measurement errors;
- omit the benchmark label, evidence class, or row-level provenance;
- merge absorption, emission, and bandgap values on one residual axis;
- pool material or source subsets into a headline number without breakdowns;
- choose size-bin boundaries after inspecting residuals;
- treat held-out-material behavior as measurement generalization;
- omit the required negative controls;
- unblock `TASK-0225` or `TASK-0293`;
- create `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifacts from this
  planning task;
- imply synthesis, fabrication, biomedical, device-performance, or
  material-selection guidance.

## Required maintainer decision

The next action is a maintainer decision, not an implementation run. A future
task may proceed only after the maintainer records approval equivalent to:

> I approve a separate sandbox-only implementation of
> `quantum_calibration_curve_consistency` as a calibration-derived benchmark.
> It must not unblock `TASK-0225` or `TASK-0293`, must not claim direct
> measurement validation, must freeze the declared controls before scoring,
> and must label all outputs `calibration_curve_consistency_only` and
> `calibration_derived`.

If the maintainer does not approve that weaker lane, the correct route is
`NO_GO`: continue direct-source artifact and row-curation work instead.

## Public wording boundary

Safe wording if a later sandbox run is approved:

> APL may run a sandbox diagnostic that compares simple baselines with
> calibration-derived quantum-dot absorption sizing curves. This tests
> consistency with published sizing curves, not agreement with direct
> measurement rows. The direct-row benchmark remains blocked until
> measurement-grade rows land.

Do not infer material design, device behavior, synthesis guidance, biomedical
use, physical-model validation, or a new quantum-dot law.

## Output routing

- Task verdict: `not_applicable` (quality-gate planning artifact).
- Canonical destination:
  `docs/reviews/quantum-calibration-consistency-go-no-go-scorecard.md`.
- Review tier: `none`.
- Gate A: not attempted; no canonical result or prediction artifact.
- Gate B: not attempted; no canonical artifact replay upgrade.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: explicit maintainer approval is required before any
  separate sandbox calibration-consistency implementation task; direct
  measurement rows remain absent.
