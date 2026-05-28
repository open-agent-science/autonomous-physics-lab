# Exoplanet compact/sub-Neptune matched-control audit

- Agent run: `AGENT-RUN-0042`
- Task: `TASK-0427`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **SANDBOX_PASS**
- Pilot reproduction status: `match`

## Scope

This review tests whether the compact and sub-Neptune residual stress patterns identified in the TASK-0390 pilot (AGENT-RUN-0036) survive matched controls and deterministic negative controls. It uses only the committed PSCompPars snapshot and frozen CK17 residuals.

No live fetch, baseline refit, atmospheric inference, composition inference, inflation-physics claim, habitability wording, target-priority output, new mass-radius law, prediction entry, canonical result, claim update, or knowledge edit is authorized.

## Pilot reproduction

Pilot eligible baseline (TASK-0390, AGENT-RUN-0036): count=1207, log10 RMSE=0.158170. Current re-derived eligible baseline: count=1207, log10 RMSE=0.158170. Reproduces within 1e-09: `yes`.

## Per-slice outcome

| slice | label | count | RMSE | reproduces pilot | outcome | adverse control |
| --- | --- | ---: | ---: | :-: | --- | --- |
| CSN-001 | compact_radius_lt1p5Re | 92 | 0.263350 | yes | residual_stress_above_eligible_and_controls | per_class_median |
| CSN-002 | sub_neptune_radius_1p5_4Re | 340 | 0.204175 | yes | control_sensitive_residual_stress | nearest_radius_outside_slice |
| CSN-003 | compact_or_sub_neptune_radius_lt4Re | 432 | 0.218126 | yes | control_sensitive_residual_stress | per_class_median |

## Control families

- Matched cohorts (independent row slices outside target):
  - `nearest_radius_outside_slice` - radius proximity matching
  - `host_temperature_outside_slice` - host Teff matching (excludes targets without Teff)
  - `detection_method_outside_slice` - shared detection method, nearest log mass
  - `uncertainty_band_outside_slice` - shared combined uncertainty band, nearest log mass
  - `sample_size_random_outside` - deterministic seeded random outside-slice draw
- Residual-shift control:
  - `per_class_median` - target-row residual shifted by eligible per-class median
- Deterministic negative controls:
  - `shuffled_radius_label` - radius assignment shuffled within eligible pool
  - `uncertainty_equalized_subset` - target rows restricted to combined relative uncertainty <= 15%
  - `adverse_nearest_radius_outside_slice` - radius-matched cohort strictly outside slice; should rise toward target RMSE if signal is radius-position driven

## Output Routing

- Task verdict: `SANDBOX_PASS`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0042/` and this review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: sandbox-only validation task.
