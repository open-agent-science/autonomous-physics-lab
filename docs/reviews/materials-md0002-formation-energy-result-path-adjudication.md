# Materials MD-0002 Formation-Energy Result-Path Adjudication (TASK-0761)

**Task:** `TASK-0761`
**Campaign:** Materials Property Residuals
**Scores:** `TASK-0703` / `AGENT-RUN-0072` MD-0002 formation-energy retest
**Verdict:** `READY_FOR_GATE_A_REUSABLE_DATASET_BENCHMARK_RESULT` (maintainer-gated)
**Scope note:** dated result-path adjudication, not a live board or a RESULT
promotion. Gate A and claim status remain maintainer-only.

## What The Retest Established

The wider-slice retest (checksum-pinned, holdout-frozen 362-row MD-0002 slice;
253 train / 55 validation / 54 holdout) on the formation-energy axis:

| Quantity | Value |
| --- | ---: |
| Best global null (global median), holdout MAE | `0.506092` eV/atom |
| Best composition baseline (exact cation-pair mean), holdout MAE | `0.200606` eV/atom |
| Absolute improvement | `0.305486` eV/atom |
| Relative improvement | `60.4%` |
| Seeded split checks won (cation-pair) | `5 / 5` (mean margin `0.350` >> across-seed noise `0.015`) |
| Shuffle controls (label + cation-label) | beaten on the real holdout for all five seeds |
| Verdict | `SANDBOX_PASS` / `VALID_IN_RANGE` |

This **replicates and strengthens** the MD-0001 composition-baseline finding
(MD-0001: `cation_group_mean` 0.646 vs 0.967 eV/atom) on a wider, independent
slice, with a stronger relative margin.

## Gate A Readiness Checklist

| Criterion | State |
| --- | --- |
| Reproducible, deterministic (committed dataset + checksum + engine) | ✅ |
| Predeclared baselines, controls, split policy (TASK-0701) before scoring | ✅ |
| No-peek holdout frozen + validated (TASK-0702) | ✅ |
| Beats null out-of-sample, split-robust, survives shuffle controls | ✅ |
| Independent wider-slice replication of MD-0001 | ✅ |
| Source provenance + license (CC BY 4.0, DATA_LICENSES) | ✅ |
| Conservative, scope-limited framing (no overclaim) | ✅ (see below) |
| Gate A RESULT packaging + claim status | ❌ maintainer-only (not done here) |

## Verdict And Framing

`READY_FOR_GATE_A_REUSABLE_DATASET_BENCHMARK_RESULT`. The evidence clears every
agent-side bar for a first source-readiness-frontier RESULT candidate. It should
be packaged (by the maintainer) as a **reusable-dataset + conservative-baseline
benchmark RESULT**, explicitly:

- **what it is**: the pinned, holdout-frozen MD-0002 dataset plus a disciplined,
  replicated, control-surviving characterization that a composition-aware
  baseline (exact cation-pair mean) reduces formation-energy holdout MAE ~60%
  vs a global-median null on this slice;
- **what it is not**: not a materials discovery, not a new materials-science law,
  not a design/synthesis/device claim, not an experimental result. A
  composition-aware baseline beating a global null is *expected*; the value is
  the reusable dataset and the honest, reproducible benchmark discipline, not
  novelty.

## Scope And Limitations

- Computed DFT only; stable alkali/alkaline-earth + first-row-transition ternary
  oxides only (`VALID_IN_RANGE` for this frozen slice, not universal).
- 362 rows (maintainer-accepted below the 600 pre-fetch target); holdout 54.
- Band gap stays diagnostic-only (MD-0001 found it split-fragile).

## Recommended Next Step (maintainer-gated)

Package a `RESULT-*` for the MD-0002 formation-energy reusable-dataset benchmark
via `docs/result-promotion-protocol.md` (Gate A), with the framing above. This
would be APL's **first promoted source-readiness-frontier RESULT**. Agents must
not promote it; this adjudication only finds it ready.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (result-path adjudication).
- **Result-path verdict:** `READY_FOR_GATE_A_REUSABLE_DATASET_BENCHMARK_RESULT`.
- **Canonical destination:** this dated adjudication; `TASK-0761` → `REVIEW_READY`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` promoted here.
- **Gate A status:** ready, not attempted (maintainer-only). **Gate B status:** not applicable.
- **Claim impact:** no claim change (claim status maintainer-only).
- **Knowledge impact:** none; no knowledge entry or canonical campaign route changed.
- **Limitations / blockers:** Gate A packaging is maintainer-gated; promotion must keep the reusable-dataset/benchmark framing and the computed-DFT, slice-limited scope.
