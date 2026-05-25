# Fresh-Data Readiness Matrix Review

Task: `TASK-0378`

## Scope

This review records the method and limitations for
[Fresh-Data Readiness Matrix](../fresh-data-readiness-matrix.md) and
[Campaign Maturity States](../campaign-maturity-states.md).

The work is documentation-only apart from moving its own task to
`REVIEW_READY`. It does not change other task statuses, ingest source
artifacts, curate rows, run benchmarks, score nuclear prediction reveals, open
prediction-registry entries, or promote claims.

## Inputs Reviewed

- [Nuclear Mass Surface](../campaigns/nuclear-mass-surface.md)
- [Quantum Size Effects](../campaigns/quantum-size-effects.md)
- [Atomic-Clock Residuals](../campaigns/atomic-clock-residuals.md)
- [Exoplanet Mass-Radius](../campaigns/exoplanet-mass-radius.md)
- [Campaign Curator Brief - 2026-05-24](campaign-curator-brief-2026-05-24.md)
- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)
- [Fresh-Data Stop Conditions](../fresh-data-stop-conditions.md)
- [Source Manifest Minimum Schema](../source-manifest-minimum-schema.md)
- [Nuclear Prediction Registry Reveal-Readiness Report](nuclear-prediction-registry-reveal-readiness-report.md)
- [Exoplanet Mass-Radius Residual Failure Map](exoplanet-mass-radius-residual-failure-map.md)
- [Exoplanet True-Mass Residual Slice Audit](exoplanet-true-mass-residual-slice-audit.md)

## Method

Each campaign was assigned one current maturity state and one next allowed
maturity state from the new maturity vocabulary. Readiness cells were then
filled using only committed docs, task files, source manifests, row schemas,
and review artifacts.

Cell status rules:

- `READY` means the next task can cite the artifact without redoing the gate.
- `PARTIAL` means a scaffold or policy exists but a concrete source, row,
  checksum, covariance, or reveal condition remains unresolved.
- `BLOCKED` means downstream work must not proceed before the named unblock
  task or maintainer decision.
- `NOT_APPLICABLE` means the gate is outside current campaign scope.

Every `PARTIAL` or `BLOCKED` cell names a next unblock path in the matrix. The
names are task references or future task shapes where no canonical task is
currently open.

## Campaign Read

| Campaign | Current state | Main blocker | Next safe work |
| --- | --- | --- | --- |
| Nuclear | `PREDICTION_FREEZE_READY` | Real reveal source, no-peek audit, and maintainer approval are absent. | `TASK-0367` for diagnostics; future source-manifest task before `TASK-0305`. |
| Quantum | `SOURCE_SURFACE` | Direct measurement rows or admissible direct-table artifacts are absent. | `TASK-0364`; then `TASK-0293` if rows land. |
| Atomic | `SOURCE_SURFACE` | Beloy 2021 artifact, covariance, checksum, and version-drift gates must pass before rows. | `TASK-0371`. |
| Exoplanet | `FAILURE_MAP_READY` | No source blocker for the current snapshot; next risk is over-broad formula search. | Narrow hypothesis-pilot scoping from completed failure-map artifacts. |

## Negative And Inconclusive Results Preserved

- Nuclear reveal readiness remains blocked even though the prediction registry
  is machine-readable and contains frozen entries.
- Quantum calibration-derived rows remain visible but do not unblock the
  direct measurement-versus-model benchmark.
- Atomic synthetic loader and source-class reviews are useful scaffolds, not
  real-row evidence.
- Exoplanet baseline and residual maps remain `INCONCLUSIVE` benchmark
  evidence, not planet-law claims.

## Limitations

The matrix is a snapshot of committed repository state at this task's branch.
It does not query live source availability, inspect paywalled artifacts, fetch
catalog updates, recompute benchmark metrics, or validate row schemas beyond
the repository validation commands.

The maturity states are intentionally compact. Campaign maintainers may add
stricter campaign-specific gates later, especially for covariance semantics,
source redistribution, partial reveal handling, and claim-promotion review.

## Verdict

`REVIEW_READY`

The repository now has a compact cross-campaign readiness surface that tells
agents which campaigns can proceed to source intake, row curation, baseline
work, hypothesis pilots, prediction freeze, or reveal checks without promoting
claims or skipping blockers.
