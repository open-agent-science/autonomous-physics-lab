# Review summary

- Verdict: **SANDBOX_PASS**
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Pilot reproduction status: `match`
- Target slices audited: 3
- CSN-001 (compact_radius_lt1p5Re): outcome=`residual_stress_above_eligible_and_controls`, target_count=92, target_rmse=0.263350
- CSN-002 (sub_neptune_radius_1p5_4Re): outcome=`control_sensitive_residual_stress`, target_count=340, target_rmse=0.204175
- CSN-003 (compact_or_sub_neptune_radius_lt4Re): outcome=`control_sensitive_residual_stress`, target_count=432, target_rmse=0.218126

The audit preserves control-sensitive and underpowered outcomes; it does not promote a result, prediction, claim, or knowledge artifact.
