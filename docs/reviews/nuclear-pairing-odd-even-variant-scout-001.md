# Nuclear Pairing And Odd-Even Variant Scout 001

**Task:** TASK-0280  
**Agent run:** `agent_runs/AGENT-RUN-0014/`  
**Script:** `scripts/run_nuclear_pairing_odd_even_variant_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0014/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`

## Scope

This review records a sandbox-only pairing and odd-even scout. It uses only
repository-pinned datasets and does not fetch live measurements. It does not
edit the nuclear prediction registry or promote claims.

## Candidate Triage

Nine candidate ideas were generated:

- Six bounded candidates were executed.
- Three candidates were rejected before execution for leakage, duplicate-search,
  or overfit risk.
- Near-null and regressive controls were preserved.

## Results

| Candidate | Description | Primary delta MAE MeV | Even-even delta MAE MeV | Odd-odd delta MAE MeV | Odd-A delta MAE MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `PAIR-SCOUT-001` | pairing inverse-A | +0.006678 | +0.013737 | +0.014590 | +0.000000 | `INCONCLUSIVE` |
| `PAIR-SCOUT-002` | baseline-shape pairing | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |
| `PAIR-SCOUT-003` | pairing cube-root | -0.008470 | -0.014776 | -0.021041 | +0.000000 | `PARTIALLY_VALID` |
| `PAIR-SCOUT-004` | odd-A offset | +0.079643 | +0.000000 | +0.000000 | +0.150607 | `INCONCLUSIVE` |
| `PAIR-SCOUT-005` | per-parity-class offsets | +0.167279 | +0.032583 | +0.332913 | +0.150607 | `OVERFITTED` |
| `PAIR-SCOUT-006` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Negative delta means lower retrospective MAE than the frozen baseline on that
subset. Positive delta means regression.

## Rejections Preserved

- `PAIR-SCOUT-007`: free-power pairing exponent, rejected as nonlinear overfit risk.
- `PAIR-SCOUT-008`: N=82 gated pairing override, rejected as retrospective shell-cluster leakage risk.
- `PAIR-SCOUT-009`: per-nuclide parity memorization stack, rejected as row-memorization risk.

## Interpretation

`PAIR-SCOUT-003` is a small, subset-scoped sandbox signal that may deserve
later adversarial review. `PAIR-SCOUT-005` is a useful negative result because
the extra class-offset degrees of freedom regress primary and pairing-sensitive
subsets. `PAIR-SCOUT-002` is effectively dormant because it reuses the baseline
pairing shape.

## Limitations

- Retrospective committed post-AME2020 rows are used only as a stress surface.
- Coefficients are fitted on an 11-row residual slice.
- NMD-0002 has only one odd-odd training row.
- No prediction registry entries are created or updated.
- No canonical results, claims, or knowledge entries are promoted.

## Verdict

`REVIEW_READY` as sandbox evidence. No scientific success claim is promoted.
