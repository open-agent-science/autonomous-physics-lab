# Exoplanet neptunian residual matched-control audit

- Agent run: `AGENT-RUN-0037`
- Task: `TASK-0391`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**

## Scope

This review tests whether the neptunian true-mass/transit-radius residual stress remains visible after matched controls. It uses only the committed PSCompPars snapshot and frozen CK17 residuals.

No live fetch, baseline refit, atmospheric-composition inference, inflation-physics claim, habitability wording, target-priority output, new mass-radius law, prediction entry, canonical result, claim update, or knowledge edit is authorized.

## Result

- Outcome: `control_sensitive_residual_stress`
- Adverse control: `per_class_median`
- neptunian log10 RMSE = 0.18279037426371253; eligible log10 RMSE = 0.1581701926744863; adverse control = per_class_median (log10 RMSE = 0.1712143142505201); margin = 0.022.

## Control Table

| control | status | count | RMSE | interpretation |
| --- | --- | ---: | ---: | --- |
| per_class_median | usable_control | 588 | 0.171214 | Per-class median residual shift on the target rows; this controls for neptunian class bias but is not an independent row slice. |
| nearest_radius_non_neptunian | usable_control | 588 | 0.127901 | nearest_radius_non_neptunian meets the minimum count gate. |
| host_temperature_non_neptunian | usable_control | 560 | 0.131558 | host_temperature_non_neptunian meets the minimum count gate. |
| uncertainty_band_non_neptunian | partial_control | 474 | 0.126122 | uncertainty_band_non_neptunian has fewer rows than the neptunian target (474 vs 588); interpret as partial control. |

## Output Routing

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0037/` and this review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: sandbox-only validation task.
