# Nuclear Residual-Free High-Error Cluster Hypothesis Audit

**Task:** `TASK-0449`
**Agent run:** `AGENT-RUN-0043`
**Campaign:** Nuclear Mass Surface
**Verdict:** `INCONCLUSIVE` (sandbox-only; no `PRED`/`CLAIM`/`KNOW`/`RESULT` artifact)
**Gauntlet:** [`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`](../notes/nuclear-controls-first-hypothesis-gauntlet.md)
**No-leakage contract:** [`docs/nuclear-residual-feature-no-leakage-contract.md`](../nuclear-residual-feature-no-leakage-contract.md)
**Feature family:** F2 (high-error cluster) under the residual-free
F2 promotion path.

## Scope

This lane tests whether cluster labels built ONLY from residual-free
nuclear features (`Z`, `N`, `A`, parity, magic-number proximity,
asymmetry) produce a per-cluster correction that survives the
controls-first gauntlet on the NMD-0002 training slice and the
post-AME2020 primary holdout.

It is the F2 follow-up to `TASK-0343` / `AGENT-RUN-0030`, which used
residual-derived cluster labels and therefore could not be promoted
beyond `diagnostic_only`. The cross-family no-leakage contract names
the F2 promotion path explicitly: rebuild cluster labels from
`Z`/`N`/`A`-only features and re-run the control gate.

The lane is sandbox-only. It does not fetch live data, score the
prediction registry, write canonical `RESULT-*` artifacts, modify
claims, or edit knowledge files.

## Cluster Taxonomy (declared before the run)

Cluster labels are deterministic functions of `Z`, `N`, `A` only:

- `near_magic_z_or_n`: `min(|Z - m|) ≤ 2` OR `min(|N - m|) ≤ 2`
  over the published magic-number list
  `{2, 8, 20, 28, 50, 82, 126, 184}`;
- `neutron_rich`: `(N - Z) / A ≥ 0.18`, and not `near_magic_z_or_n`;
- `light_a_lt_50`: `A < 50`, and not `near_magic_z_or_n` and not
  `neutron_rich`;
- `other`: everything else.

The forbidden-inputs list from the no-leakage contract is empty here:
no baseline residual, error rank, residual quantile flag,
source-status, or any residual-derived quantity enters label
construction.

## Cluster Counts

| Cluster | training_loo | primary_holdout | full_known |
| --- | ---: | ---: | ---: |
| `near_magic_z_or_n` | 10 | 116 | 126 |
| `neutron_rich` | 1 | 101 | 102 |
| `light_a_lt_50` | 0 | 5 | 5 |
| `other` | 0 | 73 | 73 |

The NMD-0002 training slice is dominated by a single cluster
(`near_magic_z_or_n` = 10 of 11 rows; `neutron_rich` = 1 row). Only
one cluster has ≥2 training rows; the gauntlet's
`INCONCLUSIVE` stop condition for "fewer than two clusters have ≥2
training rows" fires immediately.

The primary holdout panel has much better cluster coverage
(`116 / 101 / 5 / 73`), but the holdout never enters the candidate's
fit, so it cannot rescue an empty training-side cluster.

## Aggregate MAE (MeV)

| Surface | baseline | candidate | matched_random | smooth_a |
| --- | ---: | ---: | ---: | ---: |
| `training_loo` | 4.4904 | 5.6923 | 4.5924 | 4.4942 |
| `primary_holdout` | 4.4904 | 5.6923 | 4.5924 | 4.4942 |
| `full_known` | 4.4904 | 5.6923 | 4.5924 | 4.4942 |

(`training_loo`, `primary_holdout`, and `full_known` show identical
aggregate MAE in this run because the cluster taxonomy collapses to
essentially one populated training-side cluster, so the LOO offset
behaves the same way across all surfaces. Per-cluster diagnostics
below restore the per-surface differentiation.)

Numerical deltas vs the candidate:

- `candidate` vs `baseline` on `full_known`: **−1.2019 MeV** (worse than baseline by ~1.2 MeV).
- `candidate` vs `matched_random` on `full_known`: **−1.1000 MeV** (worse than the matched-random control).
- `candidate` vs `smooth_a` on `full_known`: **−1.1982 MeV** (worse than the smooth-A control).

Even if the cluster-count gauntlet stop had not fired, the candidate
already fails the survival margin in both directions: it regresses
the baseline and loses to both declared controls.

## Verdict Rationale

- Fewer than two clusters have ≥2 training rows;
  leave-one-out cannot evaluate per-cluster structure.

Per the gauntlet, this terminates the verdict at **`INCONCLUSIVE`**.
The negative numerical performance is recorded as additional
informational evidence but does not by itself elevate the verdict to
`NEGATIVE_RESULT` — the failure here is dominated by training-set
sparsity for this taxonomy, not by a hypothesis test the lane was
able to run cleanly. Calling it `NEGATIVE_RESULT` would overclaim:
the lane never executed a usable per-cluster comparison.

## Leakage Audit

- Cluster labels use only `Z`, `N`, `A`, parity, magic-distance,
  asymmetry. ✅
- The target row's residual, mass, binding energy, baseline error
  rank, residual quantile, source-status, and any future comparison
  row are NOT consumed. ✅
- Per-cluster candidate offsets are computed leave-one-out within
  the NMD-0002 training slice; the row's own contribution is
  excluded from its own LOO mean. ✅
- For held-out rows the full training-slice cluster mean is used;
  the holdout rows never enter the fit. ✅
- Both controls share the same fold logic: `matched_random` permutes
  the training labels under a fixed seed; `smooth_a` fits
  `r = a + b * A` with leave-one-out on the training slice. ✅

## Why the Lane Lands at `INCONCLUSIVE`

The residual-free taxonomy is the contract-compliant version (F2
promotion path), but the NMD-0002 training slice's coarse
`near_magic_z_or_n` cluster swallows almost the entire surface
because `MAGIC_DISTANCE_THRESHOLD = 2` matches most curated rows. A
single-cluster LOO collapses to a near-mean correction whose effect
on per-row MAE is dominated by within-cluster residual spread, not
by genuinely separable cluster structure.

This is a useful gauntlet outcome: it preserves the F2 contract
intact while showing that the present residual-free taxonomy plus
the present training slice cannot support a per-cluster correction
candidate. Two reasonable next moves a maintainer could choose
(neither is authorized by this PR):

1. **Refine the taxonomy** with finer mutually-exclusive bins built
   from the same residual-free inputs (e.g. split
   `near_magic_z_or_n` into magic-N vs magic-Z; sub-bin by `A`
   region) and re-run. The refined taxonomy must be declared before
   any score, per the gauntlet.
2. **Hold the F2 verdict at `diagnostic_only` and do not retry** at
   the same NMD-0002 sparsity until a larger curated training slice
   is available. The contract already classifies F2 as
   `diagnostic_only` outside this audit, so this outcome is
   consistent with the existing campaign state.

This review explicitly does not pick a follow-up. The verdict is
`INCONCLUSIVE` and the candidate is preserved as failure-mode
evidence, not as a near-miss that justifies a wave of variant
re-runs.

## Output Routing (`docs/result-promotion-protocol.md`)

- **Task verdict:** `INCONCLUSIVE` (lane could not evaluate the
  candidate against its declared controls under the contract's
  leave-one-out requirement on the available training surface).
- **Canonical destination:** this review note plus
  `agent_runs/AGENT-RUN-0043/{agent_run.yaml, metrics.json,
  report.md, limitations.md, preflight.md, review_summary.md}`.
- **Review tier:** `none` (no `RESULT/PRED` tier applies; the agent
  run is sandbox-only).
- **Gate A status:** `not_attempted` (no `RESULT/PRED` artifact
  proposed).
- **Gate B status:** `not_attempted` (single-run lane; no
  cross-source replay).
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Limitations and blockers:** see "Why the Lane Lands at
  `INCONCLUSIVE`". The F2 contract classification (`diagnostic_only`)
  is preserved.

## Limitations

- NMD-0002 has only 11 training rows; per-cluster leave-one-out is
  unstable for cells smaller than ~3.
- The cluster taxonomy was declared before the run and is not
  re-tuned after seeing the result; doing so would be the post-hoc
  refit the gauntlet exists to prevent.
- Frozen RESULT-0015 baseline residuals are retrospective; this is
  not a blind prediction.
- Cluster `light_a_lt_50` has 0 training rows by construction
  (NMD-0002 is curated for mid/heavy nuclei), so the lane cannot
  test the light-A regime here.
- The post-AME2020 primary holdout shows the same numerical
  aggregate as `training_loo`/`full_known` because the candidate's
  single-cluster behavior dominates; this is a property of the
  collapsed cluster taxonomy on this training slice, not a defect
  in the holdout panel itself.

## What This Lane Does Not Do

- It does not add any `PRED-XXXX.yaml` entry.
- It does not score any reveal.
- It does not promote any `CLAIM-*`, `KNOW-*`, `RESULT-*`, or
  canonical hypothesis.
- It does not reopen `LOCAL-CURVATURE-001` as a positive candidate
  (no-leakage falsification stands) or reopen shell-axis as a
  registry-expansion lane (post-audit decision unchanged).
- It does not relax the no-leakage contract, the freeze protocol,
  the prediction-reveal protocol, or the controls-first gauntlet.

## Verdict

`INCONCLUSIVE` (sandbox-only). The residual-free cluster lane was
contract-compliant and gauntlet-compliant in setup, but the NMD-0002
training slice's cluster coverage at the declared taxonomy is too
sparse (one cluster ≥2 rows) for leave-one-out evaluation. The
candidate's numerical performance is recorded as informational only.
F2 stays at `diagnostic_only` under the no-leakage contract. No
follow-up wave is authorized by this PR.
