# Exoplanet mass-radius frozen-baseline benchmark

- Agent run: AGENT-RUN-0032
- Task: TASK-0361
- Campaign profile: exoplanet-mass-radius
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **INCONCLUSIVE**

## Purpose

This note records the first executed residual surface for the Exoplanet Mass-Radius campaign. It compares a frozen Chen-Kipping 2017 piecewise median baseline against a per-class median null baseline on the committed PSCompPars snapshot. No segment of the CK17 relation is refit on the snapshot, and no habitability, biosignature, target-priority, prediction registry, or canonical result artifact is produced.

## Data scope

- Total rows: 6291
- Pre-filter included: 6157
- Post-filter included: 4301
- Quality thresholds: sigma_M/M <= 0.3, sigma_R/R <= 0.15

## Axis outcomes

| axis | CK log10 RMSE | null log10 RMSE | delta (null - CK) | CK beats null |
| --- | --- | --- | --- | --- |
| true_mass_with_transit_radius | 0.158170 | 0.242713 | 0.084543 | True |
| minimum_mass_with_transit_radius | 0.207728 | 0.031917 | -0.175811 | False |

## Reading the verdict

- SANDBOX_PASS: CK17 beats the per-class median null on log10 RMSE on every eligible axis. The frozen baseline survives this floor.
- INCONCLUSIVE: CK17 beats the null on at least one axis but not all. The result is preserved and not retried with a tuned baseline.
- FALSIFIED: CK17 does not beat the per-class median on any axis. The negative outcome is preserved as a first-class result.

## Follow-up boundary

The maintainer is asked to decide whether to preserve this benchmark as the campaign's first frozen comparison baseline or to scope a narrower follow-up (for example a hot-Jupiter inflation subset, a sub-Neptune transition subset, or a high-uncertainty hold-back set). No prediction registry, claim, knowledge, RESULT-*, or habitability/target-prioritization output is authorised by this run.
