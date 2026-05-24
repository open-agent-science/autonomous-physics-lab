# Quantum Calibration-Curve Consistency Benchmark Scope

**Task:** `TASK-0335`
**Type:** benchmark protocol
**Status:** scope package only; no benchmark run
**Benchmark label:** `quantum_calibration_curve_consistency`
**Evidence class:** `calibration_curve_consistency_only`

## Scope

This note defines the permitted scope for a future quantum-dot
calibration-curve consistency benchmark. It does not run the benchmark,
compute residual metrics, add data rows, promote a result, or unblock
`TASK-0225`.

The future benchmark, if explicitly approved by the maintainer, may compare
conservative size-scaling baseline families against published
calibration-derived absorption sizing curves. It must be framed as a
diagnostic consistency check against source calibration surfaces, not as a
measurement-versus-model validation.

Inputs reviewed:

- `docs/reviews/quantum-calibration-consistency-waiver-decision.md`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `docs/campaigns/quantum-size-effects.md`
- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/README.md`
- `tasks/TASK-0326-decide-quantum-calibration-consistency-waiver.yaml`

No new numerical rows were added. No baseline model was fit. No result,
claim, or knowledge artifact was promoted.

## Benchmark Identity

Use the following names if a future implementation task is approved:

| Field | Required value |
| --- | --- |
| Benchmark label | `quantum_calibration_curve_consistency` |
| Evidence class | `calibration_curve_consistency_only` |
| Required row provenance | `calibration_derived` |
| Result title wording | `Quantum-dot calibration-curve consistency benchmark` |
| Review note wording | `weaker benchmark; not direct measurement evidence` |

Output directory naming for a future run must keep this benchmark separate
from measurement-versus-model work:

- sandbox-only agent runs: `agent_runs/<run-id>/quantum_calibration_curve_consistency/`;
- maintainer-assigned canonical results, if ever approved:
  `results/<assigned-result-id>/quantum_calibration_curve_consistency/`;
- file prefixes: `quantum_calibration_curve_consistency_*`.

A future implementation must not reuse `TASK-0225` titles, paths, result
identifiers, or direct-measurement benchmark wording.

## Dataset Inclusion Rules

A future implementation may include only rows that satisfy all of these
conditions:

- the dataset file is committed under `data/quantum_dots/qd-*.yaml`;
- the dataset source is registered in `data/quantum_dots/source_manifest.yaml`
  with `inclusion_decision: accepted`;
- `property_kind_covered` is `absorption_peak_eV`;
- every included row is explicitly calibration-derived from a published
  sizing curve or calibration surface;
- row notes or future structured fields preserve the provenance label
  `calibration_derived`;
- the output metadata records `calibration_curve_consistency_only`.

The initial eligible surface is limited to the current calibration-derived
absorption rows:

| Dataset | Source | Materials | Rows | Allowed role |
| --- | --- | --- | ---: | --- |
| `qd-0001-yu-2003-absorption` | Yu 2003 | CdTe, CdSe, CdS | 12 | calibration-derived absorption sizing surface |
| `qd-0002-moreels-2009-pbs-absorption` | Moreels 2009 | PbS | 9 | calibration-derived PbS absorption sizing surface |

Do not include:

- direct-measurement rows in this benchmark unless a separate task explicitly
  defines how they are withheld from calibration-only scoring;
- emission, bandgap, electrical, synthesis, device, biomedical, or
  concentration-calibration fields;
- theoretical-model references as observations;
- live-fetched, unpinned, or unreviewed data;
- relaxed figure reads or digitized points unless a separate deterministic
  artifact task has already made their provenance acceptable.

## Allowed Metrics

A future implementation may define and compute metrics only as consistency
checks against calibration-derived absorption rows. Allowed metric families
are:

- MAE and RMSE in eV against `absorption_peak_eV`;
- source-by-source residual summaries for Yu 2003 and Moreels 2009;
- material-level residual summaries for CdTe, CdSe, CdS, and PbS;
- fixed size-bin residual summaries, for example `d <= 3 nm`,
  `3 < d < 6 nm`, and `d >= 6 nm`;
- curve-family sanity checks that test whether simple baseline families track
  or diverge from published sizing curves in a documented way;
- held-out material diagnostics only when labeled as calibration-surface
  transfer, not measurement generalization;
- negative controls such as per-material bulk-bandgap constant predictors.

Metric tables and plots must carry the benchmark label and evidence class in
their metadata or caption-equivalent text.

## Forbidden Metrics And Claims

A future implementation must fail review if it:

- describes residuals as measurement error;
- calls the benchmark a direct-measurement benchmark;
- reports agreement with direct experimental rows;
- presents calibration-curve consistency as validation of a physical model;
- merges absorption, emission, and bandgap values on one residual axis;
- promotes a claim, canonical result, or knowledge entry from this evidence;
- implies material-design, device-behavior, synthesis, or biomedical meaning;
- unblocks `TASK-0225` or `TASK-0293` without separate maintainer approval.

Required public wording for any future review bundle:

- "calibration-derived rows";
- "consistency with published sizing curves";
- "not a direct measurement benchmark";
- "not a claim about material design or device behavior";
- "direct-row benchmark remains blocked until measurement-grade rows land".

## Difference From TASK-0225

`TASK-0225` remains the measurement-versus-model residual benchmark. It needs
measurement-grade row-level data or an explicit maintainer rewrite of its
scope. The current calibration-derived rows do not satisfy that requirement.

This benchmark scope is weaker. It can only ask whether baseline families are
consistent with published calibration curves. That is useful for planning,
negative controls, and residual-shape diagnostics, but it does not measure
model error against independent experimental observations.

Therefore, completing this scope package does not unblock `TASK-0225`. A
future implementation of this protocol also must not unblock `TASK-0225`
unless the maintainer separately changes the TASK-0225 acceptance criteria.

## Required Maintainer Approval Text

A future implementation task may run this benchmark only after the maintainer
records approval equivalent to the following text:

> I approve a separate implementation of
> `quantum_calibration_curve_consistency` as a calibration-derived benchmark.
> It must not unblock `TASK-0225`, must not claim direct measurement
> validation, and must label all outputs
> `calibration_curve_consistency_only` and `calibration_derived`.

Without that approval, this protocol remains planning-only.

## Follow-Up Task Recommendation

If the maintainer approves the text above, create a separate implementation
task with these bounds:

- run only `quantum_calibration_curve_consistency`;
- use only eligible calibration-derived `absorption_peak_eV` rows;
- produce sandbox review artifacts first;
- include negative controls and source/material/size breakdowns;
- preserve all overclaim blockers from this scope package;
- leave direct-row readiness and `TASK-0225` blocked unless separately
  authorized.

## Verdict

`TASK-0335` defines a safe benchmark contract for a possible weaker
calibration-curve consistency benchmark. It does not authorize a benchmark
run, produce residual metrics, add rows, promote claims, or change the blocked
state of the direct measurement-versus-model benchmark.
