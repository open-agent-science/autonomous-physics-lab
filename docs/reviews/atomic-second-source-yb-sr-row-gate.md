# Atomic Second-Source Yb/Sr Row Gate

**Task:** `TASK-0525`
**Campaign:** Atomic-Clock Residuals
**Status:** source/row-gate review (no values curated)
**Decision:** `BLOCKER_SECOND_SOURCE_ROW_NOT_COMMITTED`

## Scope

This review runs the second-source direct-row gate for a Yb/Sr cross-check
against the committed Beloy 2021 reference row (`ACR-0001-ROW-003`). It reviews
Nemitz 2016 / RIKEN first and the Pizzocaro 2020 / INRIM fallback, and either
curates a compliant `ACR-0002` row package or records the precise blocker.

It does **not** copy row values, run cross-source benchmark metrics, fit
constants drift, create prediction entries, or promote claims. It keeps Atomic
at `PINNED_DATASET` (per `TASK-0455`).

## Inputs Reviewed

- `TASK-0525`
- `docs/reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md`
- `docs/reviews/atomic-direct-vs-derived-row-separation-audit.md`
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`
- `docs/reviews/atomic-holdout-no-peek-manifest.md`
- `docs/reviews/atomic-nemitz-2016-source-artifact-and-row-readiness.md`
- `data/atomic_clocks/schema.md`
- `data/atomic_clocks/acr-0001-beloy-2021-direct-ratios.yaml`
- `data/atomic_clocks/source_manifest.yaml`

## Method

1. Re-read the second-source gate requirements (`TASK-0525`) and the prior
   Nemitz source-artifact review (`TASK-0452`).
2. Checked the live source manifest for the current readiness state and the
   declared ingestion blockers for each candidate.
3. Evaluated Nemitz 2016 against the source, version-drift, uncertainty,
   covariance, and holdout gates using committed repository evidence only.
4. Evaluated the Pizzocaro 2020 fallback for source-artifact readiness.
5. Declared the covariance state a future cross-source Yb/Sr metric would carry.

No live external fetch was performed. No `ACR-0002` row was created.

## Candidate 1 — Nemitz 2016 / RIKEN (preferred)

The source manifest records Nemitz 2016 as
`source_artifact_pinned_rows_blocked`: the corrected arXiv preprint
(`arXiv:1601.04582`, SHA-256 `9835ebc2...`) is pinned with provenance, but no
value-bearing `ACR-0002` row exists. The `TASK-0452` review
(`atomic-nemitz-2016-source-artifact-and-row-readiness.md`) recorded the gate
status below; this review re-confirms it against committed evidence.

| Gate | Status | Why it is (not) cleared here |
| --- | --- | --- |
| Correct source identity | `PASS_WITH_CORRECTION` | arXiv:1601.04582 (not the earlier 1403.5836 typo, which is Akamatsu 2014). |
| Redistributable artifact | `PASS` | arXiv preprint PDF + checksum sidecar committed. |
| Public abstract value check | `PASS` | Public ratio statement R = 1.207507039343337749(55), fractional uncertainty 4.6e-17. |
| Table-level arXiv-vs-Nature drift check | `BLOCKER` | The Nature Photonics version-of-record PDF is not committed (copyright) and not available to this agent; the public Nature page does not expose the full Table 1 uncertainty budget. The load-bearing row-defining cross-check cannot be completed without the maintainer-held version-of-record. |
| Campaign-window lock | `BLOCKER_FOR_ROW` | arXiv text says ten measurements over four months but does not state exact calendar start/end; epoch semantics cannot be locked from prose without guessing. |
| Per-systematic budget transcription (TASK-0344) | `PARTIAL` | arXiv Table 1 exposes total/statistical/systematic and per-component terms, but transcription is gated behind the version-drift and window locks above. |
| Direct-vs-derived separation | `REQUIRES_CARE` | The paper also discusses alpha-variation sensitivity as interpretation; that must stay out of the direct-row value (`TASK-0487` boundary). |
| Holdout / freeze-manifest binding | `BLOCKER` | The row would be `cross_source_target` bound to Beloy `ACR-0001-ROW-003`, but the active schema cannot yet express manifest-backed `holdout.split`/`freeze_manifest` cleanly (`TASK-0526` finding). |

**Nemitz verdict:** rows remain blocked. The single load-bearing missing
artifact is the **Nature Photonics version-of-record table** needed for the
arXiv-vs-Nature drift cross-check, plus an exact campaign-window lock. Neither
can be produced by this LLM agent without live fetch or a maintainer-supplied
version-of-record PDF.

## Candidate 2 — Pizzocaro 2020 / INRIM (fallback)

The source manifest holds Pizzocaro 2020 (INRIM Yb/Sr) only as
`source_family_member_planning_only`: no source artifact is pinned, no
checksum, no provenance, no readiness review. It is therefore **further** from
row readiness than Nemitz 2016.

Before any Pizzocaro row could be considered, a separate source-artifact task
must first:

- pin a redistributable artifact (e.g. an arXiv preprint) with checksum and
  provenance, following the Nemitz 2016 / `TASK-0452` pattern;
- record the publication-of-record DOI and confirm it is not redistributed;
- expose a recoverable Table-1-class uncertainty budget and campaign window.

**Pizzocaro verdict:** not ingestible. It cannot substitute for Nemitz in this
task because it has no pinned source artifact yet.

## Covariance State For A Future Cross-Source Yb/Sr Metric

Per `atomic-first-benchmark-covariance-policy.md`, a future 1:1 Yb/Sr
consistency check between Beloy `ACR-0001-ROW-003` (NIST+JILA BACON 2018) and an
independent second source (RIKEN Nemitz or INRIM Pizzocaro) would be:

- `COV_DIAGONAL_ONLY_DECLARED` for the **cross-source** pair: the two labs are
  fully independent, so there is no shared clock, network link, or geopotential
  systematic to couple them; the off-diagonal between the two sources is
  defensibly zero, with each source's published total on the diagonal.
- Note: Beloy's *within-campaign* shared-clock systematics (Yb and Sr clocks
  reused across `ACR-0001` rows) are intra-source and do not couple to the
  independent second source. They matter only if Beloy rows are combined among
  themselves, which this gate does not do.

Important consequence from the covariance policy table: under
`COV_DIAGONAL_ONLY_DECLARED`, a **cross-source consistency verdict is not
allowed** — only diagonal-only exploratory diagnostics with an independence
banner. So even once a second row lands, the first cross-source check must be
exploratory, not a headline consistency claim, unless a stronger covariance
state is justified.

## Decision

`BLOCKER_SECOND_SOURCE_ROW_NOT_COMMITTED`

No `ACR-0002` Yb/Sr row is curated. The exact missing conditions are:

1. **Nemitz 2016:** the Nature Photonics version-of-record table for the
   arXiv-vs-Nature drift cross-check, and an exact campaign-window lock. Both
   require a maintainer-held version-of-record PDF; live fetch is not permitted
   and the version-of-record is not committed.
2. **Pizzocaro 2020:** a pinned, checksum-and-provenance source artifact does
   not exist yet; a prior source-artifact task is required before any row gate.
3. **Holdout binding:** the `cross_source_target` ↔ `cross_source_reference`
   binding cannot be expressed cleanly in the active schema until the
   `TASK-0526` minimal schema follow-up lands.

The dataset scope flags stay false: `benchmark_allowed`,
`drift_fitting_allowed`, `claim_promotion_allowed`, and
`prediction_registry_allowed` remain disabled. `TASK-0456` stays blocked.

## Required Unblock Path

A future row-curation task may commit an `ACR-0002` Yb/Sr row only after:

- a maintainer completes the Nemitz arXiv-vs-Nature table-level drift
  cross-check and supplies (or confirms) the row-defining fields, **or** a new
  Pizzocaro 2020 source-artifact task pins a compliant artifact; and
- the campaign window, transition labels, and per-systematic budget are locked
  from committed artifacts (not prose); and
- the row carries direct-vs-derived separation (no alpha-variation
  interpretation in the value), an explicit covariance state, and a
  manifest-backed holdout role (after the `TASK-0526` schema follow-up).

## What This Review Did Not Do

- It did not copy or transcribe any Nemitz or Pizzocaro row value.
- It did not add or edit `data/atomic_clocks/acr-*.yaml`.
- It did not change the source manifest (the source state did not change).
- It did not run a cross-source benchmark, drift fit, prediction, claim, or
  knowledge artifact.

## Limitations

- This review uses committed repository evidence only; it does not fetch live
  papers, publisher pages, supplements, or the Nature version-of-record PDF.
- The Nemitz arXiv PDF is committed and exposes a recoverable uncertainty
  table, but the version-drift gate is load-bearing and cannot be cleared from
  the arXiv preprint alone.
- The covariance-state declaration is a forward-looking gate input, not a
  benchmark result.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `INCONCLUSIVE` for second-source row production; `VALID` as
  a precise source/row-gate blocker review.
- **Canonical destination:** this review note,
  `docs/reviews/atomic-second-source-yb-sr-row-gate.md`. No `acr-*.yaml`,
  `results/`, `prediction_registry/`, `claims/`, or `knowledge/` change.
- **Review tier:** `none` (no RESULT/PRED artifact).
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change. **Knowledge impact:** no knowledge change.
- **Limitations / blockers:** Nemitz row blocked on the maintainer-held Nature
  version-of-record table and campaign-window lock; Pizzocaro fallback has no
  pinned source artifact; holdout binding awaits the `TASK-0526` schema
  follow-up. No live fetch available to this agent.
