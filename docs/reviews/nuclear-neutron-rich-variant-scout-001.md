# Nuclear Neutron-Rich Variant Scout 001

**Task:** TASK-0279  
**Agent run:** `agent_runs/AGENT-RUN-0013/`  
**Script:** `scripts/run_nuclear_neutron_rich_variant_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0013/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`

## Scope

This review records a sandbox-only neutron-rich/asymmetry scout. It uses only
repository-pinned datasets and does not fetch live measurements. It does not
edit the nuclear prediction registry or promote claims.

## Candidate Triage

Nine candidate ideas were generated:

- Six bounded candidates were executed.
- Three candidates were rejected before execution for leakage, duplicate-search,
  or overfit risk.
- One near-null control and one near-zero outcome were preserved as
  `INCONCLUSIVE`.

## Results

| Candidate | Description | Primary delta MAE MeV | N-Z >= 20 delta MAE MeV | Asymmetry >= 0.25 delta MAE MeV | Verdict |
| --- | --- | ---: | ---: | ---: | --- |
| `NR-SCOUT-001` | quadratic neutron-excess ramp | -0.000000 | -0.000000 | -0.000000 | `INCONCLUSIVE` |
| `NR-SCOUT-002` | cubic neutron-excess ramp | +0.025327 | +0.048296 | +0.138252 | `INCONCLUSIVE` |
| `NR-SCOUT-003` | positive asymmetry fraction | -0.024320 | -0.052276 | -0.126016 | `PARTIALLY_VALID` |
| `NR-SCOUT-004` | frontier excess after N-Z = 20 | -0.018140 | -0.046132 | -0.143094 | `PARTIALLY_VALID` |
| `NR-SCOUT-005` | matched quadratic+cubic pair | +1.368811 | +1.970989 | +4.812167 | `OVERFITTED` |
| `NR-SCOUT-006` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Negative delta means lower retrospective MAE than the frozen baseline on that
subset. Positive delta means regression.

## Rejections Preserved

- `NR-SCOUT-007`: free-power neutron-excess exponent, rejected as nonlinear overfit risk.
- `NR-SCOUT-008`: In/Sb frontier-cluster indicator, rejected as retrospective leakage risk.
- `NR-SCOUT-009`: per-threshold neutron-rich sweep, rejected as duplicate threshold search.

## Interpretation

`NR-SCOUT-003` and `NR-SCOUT-004` are small, subset-scoped sandbox signals that
may deserve later adversarial review. `NR-SCOUT-005` is a useful negative
result because the extra degree of freedom creates a large high-asymmetry
regression. `NR-SCOUT-001` is effectively dormant after fitting and is not
counted as a material improvement.

## Limitations

- Retrospective committed post-AME2020 rows are used only as a stress surface.
- Coefficients are fitted on an 11-row residual slice.
- No prediction registry entries are created or updated.
- No canonical results, claims, or knowledge entries are promoted.

## Verdict

`REVIEW_READY` as sandbox evidence. No scientific success claim is promoted.
