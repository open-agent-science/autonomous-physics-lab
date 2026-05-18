# Nuclear Mid-Mass And Isotope-Chain Gap Scout 001

**Task:** TASK-0286  
**Agent run:** `agent_runs/AGENT-RUN-0015/`  
**Script:** `scripts/run_nuclear_midmass_isotope_gap_scout.py`  
**Metrics:** `agent_runs/AGENT-RUN-0015/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`

## Scope

This review records a sandbox-only mid-mass and isotope-chain residual scout
that probes the registry coverage gaps surfaced by TASK-0272 (thin mid-mass
coverage and isotope-chain slices). It uses only repository-pinned datasets
and does not fetch live measurements. It does not edit the nuclear prediction
registry or promote claims.

## Candidate Triage

Eight candidate ideas were generated:

- Five bounded candidates were executed (four mid-mass / isotope-chain
  hypotheses plus one near-null control).
- Three candidates were rejected before execution for row-memorization,
  degree-of-freedom inflation, or duplicate-search risk on the 11-row
  NMD-0002 training slice.
- The near-null control was preserved.

| Candidate | Decision | Reason |
| --- | --- | --- |
| `MIDMASS-SCOUT-001` | executed | mid-mass Gaussian peak (sigma 20, center A=100); single bounded linear feature |
| `MIDMASS-SCOUT-002` | executed | mid-mass indicator times (N-Z)/A asymmetry; single bounded linear feature |
| `MIDMASS-SCOUT-003` | executed | isotope-chain slope using N minus per-Z median N; single bounded linear feature |
| `MIDMASS-SCOUT-004` | executed | mid-mass gated shell-distance Gaussian fall-off; single bounded linear feature |
| `MIDMASS-SCOUT-005` | executed | near-null sanity control, `r_corr = 0.0` |
| `MIDMASS-SCOUT-006` | rejected_before_execution | per-Z fitted intercepts memorize rows on an 11-row training slice |
| `MIDMASS-SCOUT-007` | rejected_before_execution | 8-bin A-step function inflates degrees of freedom on an 11-row training slice |
| `MIDMASS-SCOUT-008` | rejected_before_execution | free-sigma Gaussian adds a nonlinear knob and duplicates the fixed-sigma probe |

## Results

| Candidate | Description | Primary delta MAE MeV | Mid-mass delta MAE MeV | Light delta MAE MeV | Heavy delta MAE MeV | Frontier contrast MeV | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `MIDMASS-SCOUT-001` | mid-mass Gaussian peak | +0.372488 | +0.569391 | -0.011737 | -0.011416 | +0.580967 | `OVERFITTED` |
| `MIDMASS-SCOUT-002` | mid-mass times asymmetry | +0.796498 | +1.204959 | +0.000000 | +0.000000 | +1.204959 | `OVERFITTED` |
| `MIDMASS-SCOUT-003` | isotope-chain slope | +18.639764 | +13.203721 | +4.731626 | +34.619944 | -6.472064 | `OVERFITTED` |
| `MIDMASS-SCOUT-004` | mid-mass shell fall-off | +0.256400 | +0.387888 | +0.000000 | +0.000000 | +0.387888 | `OVERFITTED` |
| `MIDMASS-SCOUT-005` | near-null sanity control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `INCONCLUSIVE` |

Isotope-chain deltas (Z=20, Z=28, Z=50; small subsets, fragile):

| Candidate | Z=20 delta MAE MeV | Z=28 delta MAE MeV | Z=50 delta MAE MeV |
| --- | ---: | ---: | ---: |
| `MIDMASS-SCOUT-001` | +0.066016 | +0.552516 | +2.007636 |
| `MIDMASS-SCOUT-002` | +1.301361 | +1.785661 | +0.292400 |
| `MIDMASS-SCOUT-003` | -1.873882 | +4.810704 | +6.791602 |
| `MIDMASS-SCOUT-004` | +0.000000 | +3.055241 | +5.241494 |
| `MIDMASS-SCOUT-005` | +0.000000 | +0.000000 | +0.000000 |

Negative delta means lower retrospective MAE than the frozen baseline on that
subset. Positive delta means regression. The primary holdout has 2 rows at
Z=20, 3 rows at Z=28, and 1 row at Z=50, so per-chain numbers are highly
fragile.

## Rejections Preserved

- `MIDMASS-SCOUT-006`, per-Z fitted intercepts: rejected because per-Z intercepts on an 11-row slice memorize individual training rows.
- `MIDMASS-SCOUT-007`, 8-bin A-step function: rejected as a degree-of-freedom inflation overfit risk on an 11-row residual training slice.
- `MIDMASS-SCOUT-008`, free-sigma Gaussian: rejected as a nonlinear free-parameter overfit risk on an 11-row training slice that also duplicates the fixed-sigma probe.

## Interpretation

This lane produced no `PARTIALLY_VALID` sandbox candidate. Every executed
mid-mass hypothesis regresses the mid-mass band relative to the frozen
baseline, and the isotope-chain slope candidate `MIDMASS-SCOUT-003` blows up
on the heavy band (+34.6 MeV delta MAE). That blow-up is the most useful
single negative result: per-Z-median centering of the N axis fitted on the
11-row training slice does not generalize to the 295-row retrospective
holdout, especially for Z values absent from training.

The frontier-contrast metric flags the mid-mass features: `MIDMASS-SCOUT-001`,
`MIDMASS-SCOUT-002`, and `MIDMASS-SCOUT-004` all have positive frontier
contrast, meaning the mid-mass subset regresses more than the light and heavy
bands. They do not generalize away from the overrepresented frontier-next-row
targets that already drive the prediction registry.

The near-null control `MIDMASS-SCOUT-005` lands at exactly zero deltas on
every subset, as expected, and is preserved as `INCONCLUSIVE`.

## Limitations

- Retrospective committed post-AME2020 rows are used only as a stress surface.
- Coefficients are fitted on an 11-row residual slice.
- Isotope-chain subsets are very small (Z=20: 2 rows, Z=28: 3 rows, Z=50: 1 row in the primary holdout).
- No prediction registry entries are created or updated.
- No canonical results, claims, or knowledge entries are promoted.

## Verdict

`REVIEW_READY` as sandbox evidence. No scientific success claim is promoted.
The mid-mass and isotope-chain lane is recorded as a useful negative result
for the campaign rather than a discovery candidate.
