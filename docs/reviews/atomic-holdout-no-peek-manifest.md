# Atomic Holdout/No-Peek Manifest for Atomic First Benchmark

**Task:** `TASK-0454`  
**Status:** review-ready protocol definition  
**Verdict:** `READY` for protocol-only use

## Scope

This review records the campaign-level holdout/no-peek package for the first
Atomic-Clock benchmark cycle and the allowed row roles before any value-bearing
model selection.  
No benchmark scores, prediction-registry writes, claims, knowledge, or results
are produced in this task.

## Inputs

- `TASK-0454`
- `data/atomic_clocks/schema.md`
- `data/atomic_clocks/source_manifest.yaml`
- `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`
- `docs/reviews/atomic-beloy-2021-row-readiness-recheck.md`
- `docs/reviews/atomic-second-direct-ratio-source-triage.md`

## Manifest artifact

- Added: `data/atomic_clocks/atomic_holdout_manifest.yaml`
- Artifact type: campaign-wide freeze boundary only (metadata contract)
- Scope flags: benchmark results/promotion forbidden; claims and prediction
  registry updates forbidden until follow-up gating tasks complete.

## Split Role Contract (Row-Level)

The manifest defines four non-terminal split classes for this cycle:

- `train` — scoring-eligible in the first-party residual axis.
- `holdout` — reserved for future benchmark designs; not used by default in
  single-source phase.
- `cross_source_reference` — Beloy reference-side rows in a future cross-source
  benchmark.
- `cross_source_target` — future second-source rows used as direct replay targets.
- `excluded` — rows that are not allowed into scored residual metrics.

### Role mapping from the manifest

| Role family | Row class | Default split | Cross-source use |
| --- | --- | --- | --- |
| `beloy_reference_family` | `direct_measurement` | `train` (all Beloy ratio rows) | Yb/Sr may be moved to `cross_source_reference` once a second source lands |
| `nemitz_future_ratio_family` | `direct_measurement` | `Yb/Sr` → `cross_source_target` | intended replay target for Yb/Sr only |
| `excluded_replay_insufficient` | any | `excluded` | unresolved campaign/clock/covariance cases |

## Shared-row handling

- **Shared campaign geometry** (`campaign_window`, `covariance_group`,
  `source_locator`) is handled as a block:
  - block-aware splits are allowed only when the task explicitly documents a
    shared-campaign covariance policy;
  - otherwise, rows must be set `excluded`.
- **Shared clock geometry** requires explicit sign convention in the task notes
  before rows are combined:
  - supported via
    `data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml`,
  - otherwise rows must be set `excluded`.
- **Approximate covariance** is accepted only if explicitly named and only with
  a documented warning that it is a lower-bound approximation.

## Future row-population guidance

For any future task populating real rows under this manifest:

- each row should set:
  - `holdout.split`
  - `holdout.freeze_manifest: data/atomic_clocks/atomic_holdout_manifest.yaml`
- non-benchmark row classes (`review_summary`, `derived_constraint`,
  `synthetic_dry_run`) remain non-scored and are pre-routed to excluded-like
  handling unless separately justified in a later manifest revision.

## No-peek and benchmark readiness intent

- The manifest unblocks BLOCKER 2-like holdout/reveal boundary checks by defining
  a pre-commit split contract.
- It still intentionally does **not**:
  - remove the single-source replay blocker;
  - authorize production scoring;
  - replace the real-row-loader requirement;
  - imply any data-fit or benchmark claim.

## Limitations

- No row edits were made in this task.
- The manifest is a first-benchmark contract and assumes a future second source
  (TASK-0452 / TASK-0456 path) before cross-source scoring.
- All cross-source use remains contingent on explicit task-level split and
  covariance notes.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for scientific claim; `READY` for protocol
  artifact generation.
- **Canonical destination:** `data/atomic_clocks/atomic_holdout_manifest.yaml`
  and `docs/reviews/atomic-holdout-no-peek-manifest.md`.
- **Review tier:** `none` (no result/prediction artifact).
- **Limitations/blockers:** no second source committed, no real-row loader, no
  baseline-ready gate pass.
