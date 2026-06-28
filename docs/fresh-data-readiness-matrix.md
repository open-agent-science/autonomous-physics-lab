# Fresh-Data Readiness Matrix

Task: `TASK-0378`

This matrix summarizes fresh-data readiness across four active APL campaign
surfaces. It is a planning and blocker map only. It does not change any other
task statuses, ingest data, run benchmarks, score reveals, add prediction
entries, or promote claims.

Status vocabulary is defined in
[Campaign Maturity States](campaign-maturity-states.md). Fresh-data workflow
gates are defined in the [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md).

## Campaign Maturity

| Campaign | Current maturity | Next allowed maturity | Next gate |
| --- | --- | --- | --- |
| [Nuclear Mass Surface](campaigns/nuclear-mass-surface.md) | `PREDICTION_FREEZE_READY` | `REVEAL_READY` only after source/no-peek approval; otherwise bounded `HYPOTHESIS_PILOT_READY` diagnostics. | `TASK-0305` remains blocked for reveal scoring; `TASK-0367` can stress high-error cluster diagnostics. |
| [Quantum Size Effects](campaigns/quantum-size-effects.md) | `BASELINE_READY` for the source-scoped Almeida InP surface; transfer remains source-gated | Second-material `PINNED_DATASET` only after source/license approval, otherwise `NEGATIVE_MEMORY` for failed transfer routes | `TASK-0870` verifies the ZnSe/Toufanian source-license route; `TASK-0871` routes the failed effective-mass transfer check as negative/control memory. |
| [Atomic-Clock Residuals](campaigns/atomic-clock-residuals.md) | `SOURCE_SURFACE` | `PINNED_DATASET` | `TASK-0371` may curate Beloy 2021 rows only if source artifact, covariance, and version-drift gates pass. |
| [Exoplanet Mass-Radius](campaigns/exoplanet-mass-radius.md) | `FAILURE_MAP_READY` | `HYPOTHESIS_PILOT_READY` | Use the completed failure map and true-mass slice audit to scope a later narrow correction task; do not make habitability or planet-law claims. |

## Readiness Matrix

| Gate | Nuclear | Quantum Size Effects | Atomic-Clock Residuals | Exoplanet Mass-Radius |
| --- | --- | --- | --- | --- |
| Source candidates | `READY` | `READY` | `READY` | `READY` |
| Source artifact pinned | `PARTIAL` | `PARTIAL` | `PARTIAL` | `READY` |
| Checksum policy | `PARTIAL` | `PARTIAL` | `PARTIAL` | `READY` |
| Direct rows | `PARTIAL` | `PARTIAL` | `BLOCKED` | `READY` |
| Row schema | `READY` | `READY` | `PARTIAL` | `READY` |
| Extraction ledger | `PARTIAL` | `PARTIAL` | `PARTIAL` | `READY` |
| Covariance/correlation policy | `PARTIAL` | `NOT_APPLICABLE` | `PARTIAL` | `PARTIAL` |
| Holdout/reveal boundary | `PARTIAL` | `PARTIAL` | `PARTIAL` | `READY` |
| Baseline readiness | `READY` | `PARTIAL` | `BLOCKED` | `READY` |
| Benchmark readiness | `READY` | `PARTIAL` | `BLOCKED` | `READY` |

## Cell Notes And Unblock Tasks

### Nuclear Mass Surface

| Gate | Status | Evidence | Next unblock task |
| --- | --- | --- | --- |
| Source candidates | `READY` | Campaign has source-policy, post-AME2020, and reveal-source scaffolds. | None. |
| Source artifact pinned | `PARTIAL` | Committed baseline and retrospective data exist; no approved post-registration source exists for `PRED-0063` through `PRED-0068`. | `TASK-0305` stays blocked until a future source-manifest task clears the source gate. |
| Checksum policy | `PARTIAL` | Existing source and reveal templates describe checksum expectations, but no approved reveal source checksum exists. | Future source-manifest task before `TASK-0305`. |
| Direct rows | `PARTIAL` | Baseline measured slice exists; prospective reveal rows do not. | Future reveal-source task before `TASK-0305`. |
| Row schema | `READY` | Nuclear mass dataset and prediction registry schema paths are established. | None. |
| Extraction ledger | `PARTIAL` | Existing source manifests and synthetic reveal plumbing exist; real reveal extraction is absent. | Future reveal-source task before `TASK-0305`. |
| Covariance/correlation policy | `PARTIAL` | Uncertainty and measured/extrapolated semantics are tracked, but reveal-source uncertainty semantics remain source-dependent. | Future reveal-source task before `TASK-0305`. |
| Holdout/reveal boundary | `PARTIAL` | Holdout and reveal protocols exist; `registry_summary.yaml` reports 0 reveal-ready entries. | `TASK-0305` remains blocked until source preflight, no-peek review, and maintainer approval pass. |
| Baseline readiness | `READY` | `EXP-0012` and `RESULT-0015` form the current baseline surface. | None. |
| Benchmark readiness | `READY` | Multiple sandbox and audit lanes can cite the committed baseline. | None for benchmark work; `TASK-0367` is the current high-error diagnostic stress task. |

### Quantum Size Effects

| Gate | Status | Evidence | Next unblock task |
| --- | --- | --- | --- |
| Source candidates | `READY` | `TASK-0347` ranks open direct-table candidates. | None. |
| Source artifact pinned | `PARTIAL` | Almeida InP is source-pinned and benchmarked as a source-scoped sandbox surface; Jasieniak remains metadata-only, and the best ZnSe/Toufanian second-material route is license-limited. | `TASK-0870` for ZnSe license/source verification; create a new row-curation task only after an admissible source artifact exists. |
| Checksum policy | `PARTIAL` | Direct source-artifact intake and minimum source-manifest policy exist; the ZnSe/Toufanian route still needs license and checksum-policy review. | `TASK-0870`. |
| Direct rows | `PARTIAL` | Six direct Almeida InP rows are admitted, but no license-clear independent second-material rows are admitted. | `TASK-0870` before any ZnSe row task. |
| Row schema | `READY` | Quantum dot dataset schema and row-level validation exist. | None. |
| Extraction ledger | `PARTIAL` | Digitisation and intake protocols exist; no deterministic extraction artifact exists for the current second-material route. | `TASK-0870` before any later row-curation task. |
| Covariance/correlation policy | `NOT_APPLICABLE` | Current blocker is direct measurement/source provenance rather than covariance. | None at current stage. |
| Holdout/reveal boundary | `PARTIAL` | The Almeida baseline has a one-row largest-size holdout; independent-source holdout remains blocked. | `TASK-0870` before any second-material row or holdout task. |
| Baseline readiness | `PARTIAL` | `TASK-0225` produced a source-scoped Almeida sandbox baseline, but it is single-source and not a cross-material benchmark. | Use `TASK-0870` and `TASK-0871`; do not open correction search from this baseline alone. |
| Benchmark readiness | `PARTIAL` | A source-scoped sandbox baseline exists, while transfer/generalization remains source- and negative-memory gated. | `TASK-0870` and `TASK-0871`; no autonomous pilot unblock. |

### Atomic-Clock Residuals

| Gate | Status | Evidence | Next unblock task |
| --- | --- | --- | --- |
| Source candidates | `READY` | Atomic source candidates and Beloy 2021 source-class reviews exist. | None. |
| Source artifact pinned | `PARTIAL` | Beloy 2021 source-artifact and covariance preflight exists, but value-bearing artifact and checksum sidecars are not complete. | `TASK-0371`. |
| Checksum policy | `PARTIAL` | Source manifest template and artifact policy exist; concrete Beloy checksum is still conditional. | `TASK-0371`. |
| Direct rows | `BLOCKED` | `TASK-0332` says real rows are not ready before source/covariance/version checks. | `TASK-0371` if gates pass. |
| Row schema | `PARTIAL` | Schema sketch and synthetic loader exist; real-row validator coverage depends on first curated rows. | `TASK-0371`. |
| Extraction ledger | `PARTIAL` | Extraction shape is preflighted, but no real per-ratio extraction ledger is committed. | `TASK-0371`. |
| Covariance/correlation policy | `PARTIAL` | Covariance semantics and version-drift stop conditions exist, but Beloy covariance evidence must still pass. | `TASK-0371`. |
| Holdout/reveal boundary | `PARTIAL` | Direct-versus-derived boundaries exist; no freeze/reveal package exists. | Future no-peek/freeze task after real rows. |
| Baseline readiness | `BLOCKED` | No real direct rows are admitted yet. | `TASK-0371`, then a future baseline-readiness task. |
| Benchmark readiness | `BLOCKED` | Source surface is not yet row/loader validated with real rows. | Future benchmark task after baseline readiness. |

### Exoplanet Mass-Radius

| Gate | Status | Evidence | Next unblock task |
| --- | --- | --- | --- |
| Source candidates | `READY` | NASA Exoplanet Archive PSCompPars snapshot path is already selected. | None. |
| Source artifact pinned | `READY` | `TASK-0353` pinned `exo-0001-pscomppars-snapshot.yaml` with source manifest and checksums. | None. |
| Checksum policy | `READY` | Snapshot and manifest checksum policy are committed. | None. |
| Direct rows | `READY` | Snapshot rows are curated with inclusion/exclusion and mass-provenance flags. | None. |
| Row schema | `READY` | Loader and schema validation landed with `TASK-0354`. | None. |
| Extraction ledger | `READY` | Snapshot query, normalized rows, and loader dry-run make extraction reviewable. | None. |
| Covariance/correlation policy | `PARTIAL` | Per-row uncertainties and provenance are tracked, but catalog-level correlation/systematic treatment is not a full covariance model. | Future hypothesis/baseline follow-up before any uncertainty-heavy claim. |
| Holdout/reveal boundary | `READY` | Holdout protocol and source-date boundary exist for the snapshot. | None. |
| Baseline readiness | `READY` | `TASK-0361` executed the first frozen baseline benchmark. | None. |
| Benchmark readiness | `READY` | `TASK-0362` and `TASK-0369` package failure-map and true-mass residual evidence. | None; next task should be a narrow hypothesis-pilot scope if maintainer approves. |

## Cross-Campaign Queue Guidance

- Prefer `TASK-0870` when Quantum needs a second-material source/license
  decision; use `TASK-0871` when preserving the failed effective-mass transfer
  path as negative/control memory.
- Prefer `TASK-0371` when Atomic needs its first admissible real-row attempt.
- Prefer `TASK-0367` when Nuclear needs diagnostic stress evidence, not reveal scoring.
- For Exoplanet, do not start broad formula search from readiness alone; use
  the failure-map outputs to define a narrow, control-heavy follow-up task.

## Claim Boundary

No campaign in this matrix is `CLAIM_CANDIDATE`. Exoplanet and Nuclear have
useful benchmark or sandbox evidence, but they still require separate
maintainer-reviewed claim-promotion tasks before any claim or knowledge status
can change.
