# Exoplanet regime residual scout

- Agent run: AGENT-RUN-0035
- Task: TASK-0370
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**

## Purpose

Bounded sandbox scout that tests interpretable residual hypotheses around three known regime boundaries on the committed PSCompPars snapshot: the super-Earth / sub-Neptune transition, the Jovian-radius plateau, and the high-irradiation / hot-Jupiter regime. Every hypothesis is evaluated against the frozen CK17 baseline plus per-class median, shuffled-regime, and sample-size-matched controls.

## Bounds

- Minimum regime row count: 30 (smaller slices flagged and excluded from the verdict).
- Survival margin: 0.022 log10 RMSE (≈ 5% RMSE improvement).
- Shuffle seed: 20260524 (deterministic).

## Executed regime outcomes

| regime | label | count | log10 RMSE | strongest control | delta vs control |
| --- | --- | --- | --- | --- | --- |
| REGIME-001 | super_earth_to_sub_neptune_transition | 225 | 0.156078 | shuffled_regime | -0.024004 |
| REGIME-002 | jovian_radius_plateau | 515 | 0.128217 | matched_size_neighbor | -0.007709 |
| REGIME-003 | hot_jupiter_high_irradiation | 212 | 0.097906 | per_class_median | 0.004891 |

## Generated-but-not-executed hypotheses (review surface)

- `REGIME-004` (ultra_short_period_irradiation): generated only; slice size = 49.
- `REGIME-005` (cold_host_transit_subset): generated only; slice size = 156.
- `REGIME-006` (warm_host_long_period_subset): generated only; slice size = 39.

## Follow-up boundary

Maintainer review only. No PRED entry, no RESULT-*, no claim, no knowledge edit, no habitability / biosignature / target-prioritization output authorised by this run. A future task may scope a narrower per-regime correction; this scout does not author that task.
