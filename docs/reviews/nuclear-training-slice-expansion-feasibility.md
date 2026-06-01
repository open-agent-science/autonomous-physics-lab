# Nuclear Training-Slice Expansion Feasibility Review

**Task:** `TASK-0479`  
**Campaign:** Nuclear Mass Surface  
**Review type:** source-gated dataset feasibility review  
**Verdict:** `BLOCKED_FOR_SOURCE_SAFE_EXPANSION`  
**Claim ceiling:** Dataset planning / source-readiness only. No candidate
metrics, prediction entry, reveal score, claim, knowledge entry, or canonical
result is promoted by this review.

## Summary

The current Nuclear training slice should not be expanded in this PR.
The repository has one committed pre-existing measured training surface,
`data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`, with 11 curated
measured rows. It also has a much larger reviewed row-level
`post_ame2020_holdout.yaml` surface with 296 committed post-AME2020 rows, but
that file is explicitly a retrospective time-split holdout surface and must not
be silently absorbed into training.

The source-safe path is therefore not "move post-AME2020 rows into the training
slice." The safe path is a separate source-curation task that imports or pins a
broader AME2020-era measured training table with checksums, measured versus
extrapolated semantics, and a frozen split boundary against the existing
post-AME2020 holdout.

## Input References

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `data/nuclear_masses/post_ame2020_sources.yaml`
- `data/nuclear_masses/README.md`
- `data/nuclear_masses/schema.md`
- `docs/nuclear-mass-holdout-protocol.md`
- `docs/nuclear-local-curvature-no-leakage-freeze-protocol.md`
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/research-factory-protocol.md`
- `docs/nuclear-residual-factory-sprint-protocol.md`
- `docs/reviews/nuclear-residual-free-high-error-cluster-hypothesis-audit.md`

## Method

I reviewed the committed Nuclear dataset surfaces and protocols without adding
new measurement values and without running candidate metrics. The review asked
three source-gating questions:

1. Is there a committed broader pre-AME2020 or AME2020 measured row table that
   can safely replace or extend `NMD-0002` as training input?
2. Are the larger committed post-AME2020 rows eligible for training expansion,
   or are they reserved by holdout / reveal boundaries?
3. If expansion is blocked, what exact source artifacts and schema guarantees
   must a future dataset task add before candidate fitting resumes?

## Current Dataset Inventory

| Surface | Role | Row count / scope | Expansion relevance |
| --- | --- | ---: | --- |
| `nmd-0002-curated-measured-slice.yaml` | Current training / baseline slice | 11 measured rows | Source-safe as current training, but too sparse for several structured audits. |
| `post_ame2020_holdout.yaml` | Reviewed retrospective time-split holdout | 296 committed rows; 295 primary holdout rows after frozen-overlap exclusion; 1 overlap audit exclusion (`U-238`) | Source-rich, but not training-safe. It must remain separate from training. |
| `post_ame2020_sources.yaml` | Reviewed source manifest | NST 2025 compilation plus AME2020 source references | Supports the holdout and future AME2020 import planning; does not itself import AME2020 rows. |
| `factory_target_batches.yaml` | Prospective target-batch support | Reviewed target batches, not measured training rows | Useful for factory stress planning, not training expansion. |

The previous residual-free high-error cluster audit shows the practical effect
of the small training slice: under that declared taxonomy, `NMD-0002` produced
10 `near_magic_z_or_n` training rows and 1 `neutron_rich` row, with no training
coverage for `light_a_lt_50` or `other`. That sparsity, not a candidate-fitting
bug, blocked a meaningful leave-one-out cluster comparison.

## Feasibility Finding

Immediate training-slice expansion is **not source-safe**.

The repo records AME2020 as the intended training / comparison baseline source
in the post-AME2020 manifest, but the AME2020 row table itself is not committed
as a parsed dataset with row values, extraction method, checksum, and
measured/extrapolated row semantics. The nuclear dataset README also says a
broader pinned AME-style table remains a later task.

The post-AME2020 holdout is not a substitute for that missing training import.
The holdout protocol explicitly requires later measurements to remain a
separate time-split surface and says not to silently merge later measurements
into the training surface. The reveal protocol also preserves before/after
boundaries: measurement sources must be pinned before comparison, and registry
or reveal tasks must not rewrite frozen training or prediction state.

## Exact Blocker List

1. **No committed broad AME2020 training table.** The repo has AME2020
   references and source names, but no parsed AME2020 measured-row dataset with
   checksums and row-level values suitable for training expansion.
2. **No committed AME2020 source artifact checksum for a parsed training
   surface.** `post_ame2020_sources.yaml` says a future AME2020 import must pin
   the exact AMDC ASCII file checksum before rows are parsed directly.
3. **Holdout boundary would be weakened by absorbing post-AME2020 rows.**
   `post_ame2020_holdout.yaml` is already a reviewed holdout / retrospective
   time-split surface, not a training reservoir.
4. **Measured versus extrapolated semantics must be preserved.** Any broader
   training import must label AME2020 measured, extrapolated, or unspecified
   status per `data/nuclear_masses/schema.md`; it cannot collapse them into an
   unlabeled pool.
5. **Split definitions must be frozen before candidate metrics.** A future
   `NMD-0003`-style dataset must declare train / validation / holdout / stress
   boundaries before any residual-law, local-curvature, or factory candidate
   sees metrics.
6. **No-leakage neighbor caches are not yet available for a larger slice.**
   Any future local-curvature or residual-neighbor feature family must compute
   per-fold caches from admissible training rows only, not from full-known rows
   or post-AME2020 holdout rows.

## Source-Safe Expansion Path

A future source-gated dataset task can unblock this lane by adding a new
training dataset, tentatively `NMD-0003`, with the following minimum contract:

1. Pin the exact AME2020 source file or immutable retrieval manifest, including
   checksum, access date, citation, and redistribution note.
2. Parse row-level values into a new dataset file under
   `data/nuclear_masses/`, preserving `nuclide_id`, `Z`, `N`, `A`,
   `evaluation`, source row id, numeric value pair, uncertainty, and unit
   semantics.
3. Keep measured and extrapolated rows separable. Default candidate training
   should use measured rows only unless a later task explicitly authorizes a
   mixed measured/extrapolated diagnostic.
4. Freeze split manifests before any candidate fitting:
   training from AME2020-era measured rows, retrospective time-split validation
   from `post_ame2020_holdout.yaml`, and prospective registry targets only from
   separately frozen `PRED-*` entries.
5. Preserve overlap rules. Rows already in `NMD-0002` may be retained as
   overlap audit rows or included in a superseding training surface only if the
   supersession is explicit and checksum-backed.
6. Add loader / validation tests that assert row-count stability,
   `A == Z + N`, non-missing evaluation labels, no duplicated nuclide ids in a
   split, and no post-AME2020 primary holdout ids in the training split.

## Recommended Follow-Up

Open a separate source-curation task rather than a candidate-fitting task:

> **Proposed follow-up:** Add a broader AME2020 measured-row Nuclear training
> dataset with pinned source checksum and frozen split manifest.

Suggested accepted outputs:

- `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- `data/nuclear_masses/nmd-0003-split-manifest.yaml`
- parser or normalization helper, if needed
- tests for schema, row-count stability, measured/extrapolated separation, and
  holdout exclusion
- review note documenting source checksum, extraction method, and allowed
  training / validation boundaries

That task should land before any new residual-law factory sprint, local
curvature registry-freeze attempt, or cluster-taxonomy re-run that depends on a
larger training surface.

## Output Routing

- **Canonical destination:** this review note under `docs/reviews/`.
- **Review tier:** none; no `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*`
  artifact is proposed.
- **Gate A status:** not attempted. This is source-readiness review, not a
  deterministic benchmark result.
- **Gate B status:** not attempted. No independent replay artifact is proposed.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** missing source-safe broader AME2020 row dataset and
  frozen split manifest.

## Limitations

- This review does not fetch AME2020 or NST sources live.
- This review does not parse new rows, add measurements, or modify dataset
  loaders.
- This review does not run candidate metrics, residual-law factory candidates,
  prediction reveals, or source promotion gates.
- The recommended follow-up is intentionally source-curation first; it may
  still be blocked by licensing or redistribution constraints when the exact
  AME2020 artifact is pinned.

## Verdict

`BLOCKED_FOR_SOURCE_SAFE_EXPANSION`.

The small `NMD-0002` training slice is a real bottleneck for structured Nuclear
diagnostics, but the repo does not yet contain the broader AME2020 row-level
training artifact needed to expand it safely. The already committed
post-AME2020 rows are valuable validation / time-split evidence and must remain
separate from training.
