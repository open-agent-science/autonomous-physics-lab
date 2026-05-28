# AGENT-RUN-0037 - Exoplanet neptunian residual matched-control audit

- Task: TASK-0391
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**

## Boundary

Sandbox-only matched-control audit on committed snapshot rows. The primary axis is true-mass/transit-radius rows; minimum-mass rows are diagnostic-only. The frozen CK17 baseline is not refit.

## Primary Slice

- Eligible true-mass/transit-radius rows: 1207
- Neptunian true-mass/transit-radius rows: 588
- Diagnostic minimum-mass/transit-radius rows: 2
- Eligible RMSE: 0.158170; neptunian RMSE: 0.182790; delta: 0.024620

## Matched Controls

| control | status | count | log10 RMSE | delta neptunian-control | notes |
| --- | --- | ---: | ---: | ---: | --- |
| per_class_median | usable_control | 588 | 0.171214 | 0.011576 | Per-class median residual shift on the target rows; this controls for neptunian class bias but is not an independent row slice. |
| nearest_radius_non_neptunian | usable_control | 588 | 0.127901 | 0.054889 | nearest_radius_non_neptunian meets the minimum count gate. |
| host_temperature_non_neptunian | usable_control | 560 | 0.131558 | 0.051233 | host_temperature_non_neptunian meets the minimum count gate. |
| uncertainty_band_non_neptunian | partial_control | 474 | 0.126122 | 0.056668 | uncertainty_band_non_neptunian has fewer rows than the neptunian target (474 vs 588); interpret as partial control. |

## Classification

- Outcome: `control_sensitive_residual_stress`
- Adverse control: `per_class_median`
- neptunian log10 RMSE = 0.18279037426371253; eligible log10 RMSE = 0.1581701926744863; adverse control = per_class_median (log10 RMSE = 0.1712143142505201); margin = 0.022.

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0037/` and review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: task scope authorizes sandbox evidence only.
