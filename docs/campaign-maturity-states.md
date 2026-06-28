# Campaign Maturity States

This vocabulary gives APL agents and maintainers a shared way to describe
where a campaign sits before source intake, row curation, benchmark work,
prediction freeze, reveal work, or claim review.

These states are readiness labels, not scientific verdicts. A campaign may
hold useful negative memory while still being blocked on fresh data. A later
state does not authorize claim promotion, live data fetching, source
redistribution, benchmark execution, prediction registration, or reveal
scoring unless a canonical task explicitly allows that work.

Use this vocabulary with:

- [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md)
- [Fresh-Data Stop Conditions](fresh-data-stop-conditions.md)
- [Source Manifest Minimum Schema](source-manifest-minimum-schema.md)
- [Fresh-Data Readiness Matrix](fresh-data-readiness-matrix.md)

## State Definitions

| State | Meaning | Minimum evidence | What it allows next |
| --- | --- | --- | --- |
| `SOURCE_SURFACE` | Candidate sources, source classes, schemas, or source policies exist, but row-level benchmark data are not ready. | Campaign page, source-candidate notes, schema sketch, source manifest template, or source-class review. | Source artifact pinning, blocker preservation, extraction planning, or row-readiness review. |
| `PINNED_DATASET` | A source artifact, snapshot, or metadata-only locator package is frozen enough for row or loader review. | Retrieval or archive date, checksum or archive policy, license/reuse note, row-class intent, and live-fetch policy. | Extraction, row curation, loader validation, or blocked source review. |
| `BASELINE_READY` | Curated rows and schema/loader validation are mature enough for a conservative baseline task. | Row schema validation, source references, row-class separation, uncertainty or limitation notes, and holdout or reveal boundary. | Baseline reproduction task with conservative null or reference comparison. |
| `FAILURE_MAP_READY` | A baseline or benchmark exists and can be summarized as residual regions, failure modes, exclusions, and negative controls. | Baseline metrics, residual slices or review note, limitations, and no claim promotion. | Failure-map packaging, bounded residual-slice audits, or narrow hypothesis-pilot scoping. |
| `HYPOTHESIS_PILOT_READY` | The campaign has enough validated baseline or failure-map structure to run bounded sandbox hypotheses with controls. | Baseline or failure map, admissible features, negative controls, holdout policy, and overclaim guardrails. | Sandbox-only hypothesis tests or adversarial audits. |
| `PREDICTION_FREEZE_READY` | A campaign has enough no-peek discipline to freeze prospective predictions before future source comparison. | Frozen model state, target set, source-state note, no-peek or holdout protocol, and claim ceiling. | Prediction registry entry or freeze package if the task explicitly authorizes it. |
| `REVEAL_READY` | A future source comparison may proceed because source preflight, no-peek audit, eligibility, and maintainer approval are complete. | Source manifest, checksums or archive policy, registry snapshot, no-peek audit, eligibility rules, and approved comparison command. | Reveal comparison on eligible rows only. |
| `CLAIM_CANDIDATE` | Reviewed benchmark or reveal evidence may be proposed for claim review, but is not yet knowledge. | Deterministic evidence, limitations, negative results, reviewer notes, and a separate claim-promotion task. | Maintainer-reviewed claim or knowledge proposal. |
| `NEGATIVE_MEMORY` | A blocker, failed source attempt, failed model family, or inconclusive benchmark is preserved as useful memory. | Review note, stop-condition code or verdict, attempted method, and allowed follow-up. | Avoid repeated weak paths, refine blockers, or design narrower follow-up tasks. |

## Status Codes For Readiness Cells

Use these cell statuses in campaign matrices:

| Status | Meaning |
| --- | --- |
| `READY` | The required artifact or policy exists and can be cited by the next task. |
| `PARTIAL` | Some evidence exists, but a blocker, missing field, weak row class, or unresolved review condition remains. |
| `BLOCKED` | The cell cannot support downstream work until a named unblock task or maintainer decision resolves it. |
| `NOT_STARTED` | No reviewed artifact exists yet. |
| `NOT_APPLICABLE` | The cell is outside the campaign's current scope or only relevant after a later state. |

## Current Campaign State Snapshot

| Campaign | Current state | Next allowed state | Boundary |
| --- | --- | --- | --- |
| Nuclear Mass Surface | `PREDICTION_FREEZE_READY` | `REVEAL_READY` only after source preflight, no-peek review, and maintainer approval; otherwise `HYPOTHESIS_PILOT_READY` for no-leakage diagnostic tasks. | Frozen `PRED-*` registry entries are not reveal evidence and not claims. |
| Quantum Size Effects | `BASELINE_READY` for the source-scoped Almeida InP surface; transfer remains source-gated | Second-material `PINNED_DATASET` only after source/license approval, otherwise `NEGATIVE_MEMORY` for failed transfer routes. | The Almeida sandbox baseline does not authorize cross-material claims, correction search, or archived pilot restart. |
| Atomic-Clock Residuals | `SOURCE_SURFACE` | `PINNED_DATASET` after Beloy 2021 artifact, covariance, and version-drift gates pass. | No real clock rows should be committed before source/covariance gates clear. |
| Exoplanet Mass-Radius | `FAILURE_MAP_READY` | `HYPOTHESIS_PILOT_READY` for a narrow residual-family task after failure-map review. | Residual maps are benchmark diagnostics, not planet-law or habitability claims. |

## Nonlinear Notes

- `NEGATIVE_MEMORY` can coexist with every other state. It is not a demotion.
- `REVEAL_READY` is stricter than `PREDICTION_FREEZE_READY`; frozen predictions
  alone never make a reveal legitimate.
- `BASELINE_READY` and `FAILURE_MAP_READY` do not make a campaign
  `CLAIM_CANDIDATE`.
- A source manifest or artifact package by itself is not row readiness.
