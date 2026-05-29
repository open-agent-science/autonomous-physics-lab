# Nuclear Residual-Free High-Error Cluster Hypothesis Audit

**Task:** `TASK-0449`
**Agent run:** `AGENT-RUN-0043`
**Campaign:** `nuclear-mass-surface`
**Verdict:** `INCONCLUSIVE`
**Sandbox only:** true

## Cluster Taxonomy (residual-free)

Cluster labels are deterministic functions of `Z`, `N`, `A` only:

- `near_magic_z_or_n`: `min(|Z - m|) ≤ 2` or `min(|N - m|) ≤ 2`
- `neutron_rich`: `(N - Z) / A ≥ 0.18` (and not near-magic)
- `light_a_lt_50`: `A < 50` (and not near-magic or neutron-rich)
- `other`: everything else

Magic numbers: `{2, 8, 20, 28, 50, 82, 126, 184}`.

## Cluster Counts

| Cluster | training_loo | primary_holdout | full_known |
| --- | ---: | ---: | ---: |
| `near_magic_z_or_n` | 10 | 116 | 126 |
| `neutron_rich` | 1 | 101 | 102 |
| `light_a_lt_50` | 0 | 5 | 5 |
| `other` | 0 | 73 | 73 |

## Aggregate Metrics (MAE, MeV)

| Surface | baseline | candidate | matched_random | smooth_a |
| --- | ---: | ---: | ---: | ---: |
| `training_loo` | 2.8245 | 3.1595 | 3.1256 | 4.0252 |
| `primary_holdout` | 4.5526 | 5.7868 | 4.6471 | 4.5117 |
| `full_known` | 4.4904 | 5.6923 | 4.5924 | 4.4942 |

## Verdict Rationale

- Fewer than two clusters have ≥2 training rows; leave-one-out cannot evaluate per-cluster structure.

## Per-Cluster Candidate vs Baseline (full_known)

| Cluster | count | baseline MAE | candidate MAE | delta |
| --- | ---: | ---: | ---: | ---: |
| `near_magic_z_or_n` | 126 | 4.5468 | 4.4089 | 0.1380 |
| `neutron_rich` | 102 | 4.5961 | 8.3722 | -3.7761 |
| `light_a_lt_50` | 5 | 1.2715 | 1.2715 | 0.0000 |
| `other` | 73 | 4.4660 | 4.4660 | 0.0000 |

## Leakage Audit (per the no-leakage contract)

- Cluster labels use only `Z`, `N`, `A`, parity, magic-distance, asymmetry. No baseline residual, error rank, or any residual-derived quantity enters label construction.
- Per-cluster candidate offsets are computed leave-one-out within the NMD-0002 training slice; for held-out rows the full training-slice mean is used (the holdout rows never enter the fit).
- Both controls share the same fold logic: matched_random permutes the training labels under a fixed seed; smooth_a fits `r = a + b * A` with leave-one-out on the training slice.
- No candidate-fit residuals feed any aggregate. No future comparison row contributes to label construction.

## Promotion Boundary

- `sandbox_only: true`
- `writes_canonical_result: false`
- `claim_promotion_allowed: false`
- `prediction_registry_allowed: false`
- Required next step: maintainer review before any follow-up. No `PRED-XXXX`, `RESULT-XXXX`, `CLAIM-XXXX`, or `KNOW-XXXX` artifact is created by this run.

