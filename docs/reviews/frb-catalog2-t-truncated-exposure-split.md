# FRB Catalog 2 T-Truncated Pre-T Exposure Split

Task: `TASK-0877`
Domain: Radio transients astrophysics (FRB repeater selection-effect audit)
Mode: T-truncated pre-T exposure view specification + leakage/readiness diagnostic
Outcome: `SPECIFIED` (not constructed; not blocked)
Verdict: `T_TRUNCATED_SPLIT_SPECIFIED_NO_LEAKAGE_CONSTRUCTION_PENDING_EXPOSURE_MAPS`
Run date: `2026-06-30`

## Scope And Non-Goals

This task advances the FRB repeater selection-effect audit by exactly one bounded
step on top of the merged `TASK-0852` baseline. `TASK-0852` landed
`SPLIT_AND_EXPOSURE_BASELINE_READY`: it pinned the public CHIME/FRB Catalog 2 CSV
locator and checksum, recorded a version-locked no-leakage temporal split
specification, and froze an aggregate exposure-only baseline gate built from
Catalog 2 full-window exposure summaries. That baseline is explicitly a
selection-effect gate, not a predictive split: full-window exposure is only
knowable after the observing window closes, so it cannot enter a pre-T feature
view without leaking future observing time.

This task therefore specifies the missing predictive ingredient: a T-truncated
pre-T exposure view with no leakage. It does **not** build or score a morphology
model, freeze a `PRED` entry, create a `RESULT` artifact, create an
`agent_runs/AGENT-RUN-*`, promote a claim, vendor catalog bytes, or fetch catalog
rows.

Inputs reviewed:

- [frb-catalog2-temporal-split-exposure-baseline.md](frb-catalog2-temporal-split-exposure-baseline.md)
- [frb-chime-source-readiness-temporal-split-scout.md](frb-chime-source-readiness-temporal-split-scout.md)
- [frb-chime-access-reverify-readiness.md](frb-chime-access-reverify-readiness.md)
- [../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md)
- [../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md)
- `TASK-0852`

Committed outputs:

- [../../data/radio_transients/frb_catalog2_t_truncated_exposure_split.yaml](../../data/radio_transients/frb_catalog2_t_truncated_exposure_split.yaml)
- this review note
- one metadata-only entry in [../../data/DATA_LICENSES.yaml](../../data/DATA_LICENSES.yaml)

## 1. Constructed Or Specified? Specified, And Why

The deliverable is a precise **specification**, not a numeric construction.

The decisive fact is in the released data product. The pinned `chimefrbcat2.csv`
exposes per-source exposure only as **full-window** `exp_up` / `exp_low`
(upper-/lower-transit exposure integrated over the whole 2018-2023 observing
window). It contains **no per-epoch or time-resolved exposure column**. A
truncated-at-T exposure value therefore cannot be derived from the CSV at all. The
only released materials that can be integrated up to an arbitrary split time T at
single-source sky granularity are the **time-resolved / full-sky exposure-map
products** at dataset DOI `10.11570/25.0066` — and `TASK-0852` pinned only the CSV
table, not those maps.

Because this task is metadata/spec-only and forbids fetching rows, vendoring
bytes, or scoring, it cannot construct the numeric truncated values here. It
stops at a complete, replayable construction recipe plus a structural readiness
diagnostic from the committed baseline.

This is a `SPECIFIED` outcome, **not** `BLOCKED`. The recipe is well-defined and
leakage-safe, and it is reconstructible without leakage the moment the
exposure-map input is pinned under a separate source-clearance step. Nothing about
the leakage geometry is unresolved; only one additional pinned input (the maps) is
out of this task's scope.

## 2. The T-Truncated Pre-T Exposure View

For each pre-T source (a source whose first-detection time is at or before T),
the feature is:

```text
score_pre_t = log1p(exp_up(<=T) + exp_low(<=T))
```

where `exp_up(<=T)` and `exp_low(<=T)` are the upper-/lower-transit exposure on
that source's localized sky position accumulated only over observing epochs with
timestamp `<= T`. First-detection time and the source key match the `TASK-0852`
baseline exactly (minimum finite `mjd_inf` falling back to `mjd_400` over the
source's bursts; key `repeater_name` else `tns_name`; eligibility
`excluded_flag == '0'`). T is a split design parameter, not a fixed constant, so a
future reviewed pilot can choose T (a Catalog 1 boundary epoch, or a fixed UTC
cutoff under the blind-holdout protocol) and reconstruct the view deterministically.

Construction recipe once the exposure maps are pinned (locator + SHA-256, no map
bytes vendored unless redistribution is cleared): take each pre-T source's
localized position and 90% confidence region, integrate the time-resolved exposure
map over that region but only over epochs `<= T` to get `exp_up(<=T)` /
`exp_low(<=T)`, set `score_pre_t` as above, then freeze and version-lock the view
before any label is read or any model is scored. The full recipe and field-level
detail live in the committed spec artifact.

## 3. Leakage-Safety Argument

The pre-T view must contain only information knowable at time T. Each of the four
leakage channels the task names is closed by construction:

| Leakage channel | Risk | Control in this spec |
| --- | --- | --- |
| Late repeater labels | `repeater_name` reflects repeat bursts that may all arrive after T | `repeater_name` is never a pre-T feature; the label is read only from a strictly later catalog version or external reveal record, positive only when repeat evidence is published after T |
| Later source associations | Catalog 2 re-groups bursts with a later framework; post-T associations move bursts | Pre-T membership uses only bursts with arrival `<= T` under the T-fixed knowledge state; post-T association changes are outcomes, never inputs |
| Morphology reprocessing | Catalog 2 reprocesses morphology for earlier bursts with the later pipeline | No morphology feature is added; morphology is out of scope for the exposure view, and any future morphology feature must itself be T-reconstructed, not late-reprocessed |
| Full-window exposure | Full-window `exp_up`/`exp_low` integrate observing time accrued after T | The view uses `exposure_truncated_at_T` only; full-window exposure is forbidden in the pre-T view and appears solely inside the diagnostic |

Forbidden pre-T features are recorded explicitly: late-catalog `repeater_name`
labels, post-T source-association updates, post-T morphology reprocessing products,
full-window `exp_up`/`exp_low` (or any full-window exposure summary), and
full-window completeness thresholds (`low_ft_68`, `up_ft_68`, `low_ft_95`,
`up_ft_95`). The repeat/no-repeat label comes only from a strictly later catalog
version or an external reveal record (CHIME repeater-discovery paper, ATel, or TNS)
with a publication timestamp strictly after T, mirroring the no-peek logic in the
[blind-holdout benchmark protocol](../blind-holdout-benchmark-protocol.md) and the
[nuclear prediction reveal protocol](../nuclear-prediction-reveal-protocol.md).

### Versioning prevents reprocessing-drift leakage

Date-locking alone is insufficient. Reading pre-T features from the single late
Catalog 2 table embeds post-T reprocessing (DM, morphology, exposure accumulation,
source grouping, and repeater classification done with the later framework); the
values themselves are late-framework values even if the rows are date-filtered. The
spec keeps the `TASK-0852` version-lock rule: the pre-T feature version contains
only information available at T (Catalog 1-native fields or a T-reconstructed
Catalog 2 view are allowed; late Catalog 2 morphology / source-association /
full-window-exposure fields are not), and the label version is a strictly later
catalog version or reveal record. Pinning the exposure-map product by SHA-256 and
recording the integration pipeline/version freezes the pre-T knowledge state, so
any later reprocessing produces a new pinned artifact rather than silently
changing the frozen pre-T values — future reprocessing cannot leak backward into
an already frozen view. A naive "Catalog 1 as pre-T, Catalog 2 as post-T" split
also risks a framework-shift confound (different pipelines), so the truncated
integration should use a single consistent exposure pipeline.

## 4. Full-Window vs Truncated Readiness Diagnostic

This is a leakage / readiness diagnostic only. It uses the committed `TASK-0852`
baseline metadata and structural reasoning — not fetched rows and not a constructed
truncated value (which is unavailable here).

The key structural relationship is a monotone bound: for any source and any T,

```text
exposure_truncated_at_T <= full_window_exposure
```

because truncated exposure integrates a subset of observing epochs (those `<= T`)
of the same non-negative exposure. Truncation can only remove exposure, never add
it.

**Headline:** the committed full-window exposure gate is a strict **upper bound**
on every source's pre-T exposure; the gap `full_window - truncated` is exactly the
post-T exposure the predictive view must not see. Because eligibility and ranking
can only move **down** under truncation, the full-window quintile ranking is not a
safe proxy for the pre-T ranking and must be reconstructed, not reused.

The cohort most at risk of re-ranking is the **24 repeater sources in the top
full-window exposure quintile** (from the `TASK-0852` calibration). Repeaters often
accrue extra targeted follow-up exposure after an interesting first burst
(follow-up / monitoring bias), which couples morphology to *later* exposure for
exactly the sources later labeled repeaters. Truncating exposure at T is the
control that breaks this coupling in the pre-T view.

Diagnostic surface:

| Metric | Status | Basis |
| --- | --- | --- |
| Full-window exposure is an upper bound on pre-T exposure | available now: `true` | monotone subset-integration of non-negative exposure |
| Direction of eligibility change under truncation | available now: down-only | truncation removes post-T epochs |
| Top full-window quintile repeater sources at re-rank risk | available now: `24` | `TASK-0852` quintile-5 repeater count + follow-up bias |
| Per-source truncated / full-window exposure ratio | needs exposure maps | requires integrating the time-resolved maps up to T |
| Count of sources changing quintile / eligibility under truncation | needs exposure maps | same |
| Recomputed AUC / quintile rate-ratio on truncated exposure | needs exposure maps | same |

For reference, the committed full-window baseline reports source rows with finite
exposure `3338` (81 repeater, 3257 non-repeater), rank AUC for
`log1p(full-window exposure)` `0.581459875596`, and a top/bottom quintile
repeat-rate ratio `2.178511`. Direction and at-risk cohorts are establishable now;
exact magnitudes (how many sources change quintile or eligibility) are not
computable without the exposure maps, which is out of this metadata-only task's
scope.

## 5. Source-Rights Boundary Preserved

The metadata-only boundary from `TASK-0852` is preserved. Nothing new is vendored:
the spec records the CSV locator + SHA-256 + fetch/verify command and an
APL-authored specification only. No catalog rows, no exposure-map bytes, no numeric
truncated values, and no derived dataset are committed. The upstream dataset has
public read access and is citable, but the DataCite `rightsList` is empty and there
is no explicit open-data redistribution license on the catalog rows, so raw bytes
and bulk derived rows remain not cleared for commit. The new spec artifact is
declared in `data/DATA_LICENSES.yaml` under the metadata-only-source-manifest
convention even though it carries no third-party data, matching the existing
metadata-only locator precedent in that registry. The time-resolved exposure-map
products needed to construct the truncated values are an **additional**
source-clearance item (locator + SHA-256 + redistribution decision) that a future
step must pin before construction.

## 6. Verdict

`T_TRUNCATED_SPLIT_SPECIFIED_NO_LEAKAGE_CONSTRUCTION_PENDING_EXPOSURE_MAPS`.

A leakage-safe T-truncated pre-T exposure view is fully specified on top of the
`TASK-0852` baseline: the four leakage channels are closed by construction, the
version-lock rule prevents reprocessing drift from leaking future information, and
the full-window-vs-truncated diagnostic establishes that the committed gate is a
strict upper bound with a 24-source top-quintile repeater cohort at re-rank risk.
Numeric construction is deferred (not blocked): it needs the time-resolved
exposure-map products at DOI `10.11570/25.0066`, which `TASK-0852` did not pin and
which this metadata-only task does not fetch. The task remains bounded — it
produces a split-readiness specification and a diagnostic, not a morphology model,
`PRED`, `RESULT`, `AGENT-RUN`, claim, or campaign scaffold.

## Output-Routing Summary

- Task verdict: `T_TRUNCATED_SPLIT_SPECIFIED_NO_LEAKAGE_CONSTRUCTION_PENDING_EXPOSURE_MAPS` (source/split readiness; `not_applicable` to the VALID/FALSIFIED benchmark vocabulary because no benchmark was run).
- Canonical destination: a metadata/spec-only T-truncated exposure split artifact under `data/radio_transients/`, this review note, and one metadata-only `data/DATA_LICENSES.yaml` entry.
- Review tier: `none`. Gate A: not attempted. Gate B: not attempted.
- Morphology benchmark impact: none. No model fitted, no metric scored.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result / PRED impact: no `results/` artifact, no `prediction_registry/` entry, no `agent_runs/AGENT-RUN-*`.
- Data boundary: public-readable source; no catalog rows, exposure-map bytes, numeric truncated values, or derived rows committed because redistribution rights are not explicit.
- Limitations / blockers: the truncated exposure feature is specified, not constructed; numeric values require the time-resolved exposure-map products at DOI `10.11570/25.0066` (an additional source-clearance item `TASK-0852` did not pin); the diagnostic gives direction and at-risk cohorts but not exact re-ranking counts without those maps; Catalog 1 vs Catalog 2 framework-shift remains a confound to control when the view is built.
