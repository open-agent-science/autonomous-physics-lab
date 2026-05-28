# Exoplanet Host And Uncertainty Selection-Effects Audit

**Task:** `TASK-0392`
**Agent run:** `AGENT-RUN-0038`
**Snapshot:** `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
**Evidence class:** sandbox-only selection-effects audit
**Verdict:** `INCONCLUSIVE`

## Scope

This audit quantifies frozen CK17 residual summaries by host-star fields, detection method, measurement uncertainty, and missingness indicators. It uses committed snapshot rows only, keeps true-mass and minimum-mass axes separate, and compares each slice with deterministic sample-size matched controls from the same axis.

No live fetch, baseline refit, canonical result, prediction, claim, knowledge, composition, habitability, biosignature, or target-priority output is produced.

## Axis Summary

| axis | rows | log10 RMSE | control-erased slices | persistent slices | underpowered slices |
| --- | ---: | ---: | ---: | ---: | ---: |
| true_mass_with_transit_radius | 1207 | 0.158170 | 0 | 7 | 8 |
| minimum_mass_with_transit_radius | 2 | 0.207728 | 0 | 0 | 16 |

## True-Mass Count-Supported Slice Diagnostics

| dimension | slice | rows | slice RMSE | control RMSE | delta vs axis | delta vs control | classification |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| mass_uncertainty | missing_mass_uncertainty | 130 | 0.361898 | 0.116034 | 0.203728 | 0.245864 | selection_effect_persists_vs_control |
| missing_mass_uncertainty | mass_uncertainty_missing | 130 | 0.361898 | 0.116034 | 0.203728 | 0.245864 | selection_effect_persists_vs_control |
| stellar_mass | low_mass_lt0p7Msun | 208 | 0.219209 | 0.150751 | 0.061039 | 0.068458 | selection_effect_persists_vs_control |
| stellar_radius | small_radius_lt0p7Rsun | 229 | 0.213097 | 0.152269 | 0.054926 | 0.060828 | selection_effect_persists_vs_control |
| host_temperature | K_3900_5200K | 235 | 0.197335 | 0.166528 | 0.039164 | 0.030807 | selection_effect_persists_vs_control |
| host_temperature | M_lt3900K | 140 | 0.193176 | 0.154466 | 0.035006 | 0.038710 | selection_effect_persists_vs_control |
| radius_uncertainty | moderate_5_10pct | 335 | 0.182294 | 0.150945 | 0.024123 | 0.031349 | selection_effect_persists_vs_control |
| radius_uncertainty | loose_10_15pct | 81 | 0.179969 | 0.143868 | 0.021799 | 0.036101 | no_apparent_signal_above_axis |
| any_core_host_missing | any_core_host_missing | 41 | 0.174934 | 0.204195 | 0.016763 | -0.029261 | no_apparent_signal_above_axis |
| host_temperature | missing_teff | 41 | 0.174934 | 0.204195 | 0.016763 | -0.029261 | no_apparent_signal_above_axis |
| missing_host_temperature | host_temperature_missing | 41 | 0.174934 | 0.204195 | 0.016763 | -0.029261 | no_apparent_signal_above_axis |
| missing_stellar_mass | stellar_mass_present | 1203 | 0.158396 | 0.059226 | 0.000226 | 0.099170 | control_insufficient |

## Limitations Table

| axis | dimension | slice | rows | slice RMSE | control RMSE | limitation |
| --- | --- | --- | ---: | ---: | ---: | --- |
| minimum_mass_with_transit_radius | any_core_host_missing | core_host_present | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | detection_method | transit | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | host_temperature | G_5200_6000K | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | mass_uncertainty | loose_15_30pct | 1 | 0.010858 | 0.293571 | underpowered_slice |
| minimum_mass_with_transit_radius | mass_uncertainty | missing_mass_uncertainty | 1 | 0.293571 | 0.010858 | underpowered_slice |
| minimum_mass_with_transit_radius | missing_host_temperature | host_temperature_present | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | missing_mass_uncertainty | mass_uncertainty_missing | 1 | 0.293571 | 0.010858 | underpowered_slice |
| minimum_mass_with_transit_radius | missing_mass_uncertainty | mass_uncertainty_present | 1 | 0.010858 | 0.293571 | underpowered_slice |
| minimum_mass_with_transit_radius | missing_radius_uncertainty | radius_uncertainty_present | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | missing_stellar_mass | stellar_mass_present | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | missing_stellar_radius | stellar_radius_present | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | radius_uncertainty | tight_le5pct | 2 | 0.207728 | n/a | underpowered_slice |
| minimum_mass_with_transit_radius | stellar_mass | solar_high_1p0_1p3Msun | 1 | 0.293571 | 0.010858 | underpowered_slice |
| minimum_mass_with_transit_radius | stellar_mass | subsolar_0p7_1p0Msun | 1 | 0.010858 | 0.293571 | underpowered_slice |
| minimum_mass_with_transit_radius | stellar_radius | large_radius_ge1p5Rsun | 1 | 0.293571 | 0.010858 | underpowered_slice |
| minimum_mass_with_transit_radius | stellar_radius | solar_high_radius_1p0_1p5Rsun | 1 | 0.010858 | 0.293571 | underpowered_slice |
| true_mass_with_transit_radius | any_core_host_missing | core_host_present | 1166 | 0.157548 | 0.174934 | control_insufficient |
| true_mass_with_transit_radius | detection_method | transit | 1205 | 0.158272 | 0.074741 | control_insufficient |
| true_mass_with_transit_radius | detection_method | transit_timing_variation | 2 | 0.074741 | 0.399556 | underpowered_slice |
| true_mass_with_transit_radius | host_temperature | hot_ge7500K | 14 | 0.145129 | 0.210493 | underpowered_slice |
| true_mass_with_transit_radius | missing_host_temperature | host_temperature_present | 1166 | 0.157548 | 0.174934 | control_insufficient |
| true_mass_with_transit_radius | missing_mass_uncertainty | mass_uncertainty_present | 1077 | 0.110584 | 0.361898 | control_insufficient |
| true_mass_with_transit_radius | missing_radius_uncertainty | radius_uncertainty_missing | 12 | 0.453880 | 0.292996 | underpowered_slice |
| true_mass_with_transit_radius | missing_radius_uncertainty | radius_uncertainty_present | 1195 | 0.152317 | 0.453880 | control_insufficient |
| true_mass_with_transit_radius | missing_stellar_mass | stellar_mass_missing | 4 | 0.059226 | 0.078038 | underpowered_slice |
| true_mass_with_transit_radius | missing_stellar_mass | stellar_mass_present | 1203 | 0.158396 | 0.059226 | control_insufficient |
| true_mass_with_transit_radius | missing_stellar_radius | stellar_radius_missing | 4 | 0.059226 | 0.078038 | underpowered_slice |
| true_mass_with_transit_radius | missing_stellar_radius | stellar_radius_present | 1203 | 0.158396 | 0.059226 | control_insufficient |
| true_mass_with_transit_radius | radius_uncertainty | missing_radius_uncertainty | 12 | 0.453880 | 0.292996 | underpowered_slice |
| true_mass_with_transit_radius | radius_uncertainty | tight_le5pct | 779 | 0.133908 | 0.194720 | control_insufficient |
| true_mass_with_transit_radius | stellar_mass | missing_stellar_mass | 4 | 0.059226 | 0.078038 | underpowered_slice |
| true_mass_with_transit_radius | stellar_radius | missing_stellar_radius | 4 | 0.059226 | 0.078038 | underpowered_slice |

## Interpretation Boundary

Rows with larger residual stress are selection-effect diagnostics. The matched controls are designed to expose when sample size and local mass distribution can reproduce a slice's apparent signal. They do not estimate causal host-star physics.

The minimum-mass axis remains diagnostic-only because it is too sparse after the committed quality filters.

## Output Routing

- Task verdict: `INCONCLUSIVE`
- Canonical destination: `agent_runs/ sandbox-only plus docs/reviews note`
- Review tier: `none`
- Gate A status: `not_attempted`
- Gate B status: `not_attempted`
- Claim impact: no claim change
- Knowledge impact: no knowledge change
