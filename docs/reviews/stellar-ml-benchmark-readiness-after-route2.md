# Stellar M-L Benchmark Readiness After Route 2

**Task:** `TASK-0739`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Mode:** benchmark-readiness gate (planning/audit only; no metrics)
**Verdict:** `not_applicable`
**Decision:** `AUTHORIZE_ROUTE2_LOCAL_EXTRACTOR_BENCHMARK`

## Scope

This gate reviews whether the `TASK-0708` DEBCat Route 2 row package is enough
to start the first empirical Stellar M-L audit without committing the raw
`debs.dat` table or the full normalized DEBCat rows.

It uses only committed extractor, sample, provenance, storage-route,
luminosity-policy, holdout, and licensing artifacts. It does not fetch DEBCat,
fit the mass-luminosity exponent, inspect residuals, compute benchmark metrics,
create `RESULT-*` / `PRED-*` / `CLAIM-*` artifacts, or change any claim status.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `tasks/TASK-0708-curate-stellar-debcat-row-package.yaml` | Completed Route 2 row-curation contract and accepted public-safe outputs. |
| `tasks/TASK-0709-run-stellar-ml-first-empirical-audit.yaml` | Original empirical audit task, still blocked until this gate resolves the benchmark route. |
| `tasks/TASK-0740-run-stellar-ml-route2-local-benchmark.yaml` | Replacement local-extractor benchmark task waiting on this gate. |
| `docs/reviews/stellar-ml-debcat-storage-route-decision.md` | Route 2 accepted: metadata/checksum route, raw `debs.dat` not committed. |
| `docs/reviews/stellar-ml-luminosity-provenance-and-license-route.md` | Luminosity policy: catalogue `logL` first, Stefan-Boltzmann fallback when allowed, no model-derived mass truth. |
| `docs/reviews/stellar-ml-debcat-holdout-leakage-protocol.md` | System-level no-leakage split and pre-metric freeze requirements. |
| `docs/reviews/stellar-ml-debcat-row-package.md` | Extraction ledger, counts, exclusions, publication posture, and limitations from `TASK-0708`. |
| `data/textbook_formula_audit/stellar_ml/debcat_component_rows.sample.yaml` | Non-substitutive public sample plus full-set counts and source binding. |
| `data/textbook_formula_audit/stellar_ml/debcat_holdout_manifest.sample.yaml` | Non-substitutive public holdout sample plus frozen split policy. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/provenance.yaml` | Pinned locator/checksum, redistribution posture, and local regeneration contract. |
| `data/DATA_LICENSES.yaml` | Declares DEBCat committed artifacts as sample-only; full set is not redistributed. |
| `scripts/extract_debcat_stellar_ml_rows.py` | Deterministic local extractor with checksum refusal and frozen lane assignment. |
| `tests/test_stellar_ml_debcat_rows.py` | Regression and public-safety guard for extractor/sample invariants. |

## Gate Checks

| Check | Finding |
| --- | --- |
| Source/version binding | Pass. The DEBCat locator and SHA-256 are pinned in provenance and sample artifacts. The extractor refuses checksum drift. |
| Public-safe storage | Pass with constraint. The repository commits only extractor, provenance, and small samples; raw `debs.dat` and full normalized rows remain uncommitted. |
| Local reproduction path | Pass. A contributor can fetch the pinned `debs.dat`, verify the checksum, and run the deterministic extractor to regenerate full rows and the full manifest locally. |
| Luminosity policy | Pass with limitation. Catalogue `logL` and Stefan-Boltzmann fallback classes are explicit, but per-row primary-literature luminosity pointers are not exposed by `debs.dat`. |
| Mass truth policy | Pass. The package uses DEBCat direct dynamical component masses and forbids Gaia/isochrone/model-derived masses as benchmark truth. |
| Holdout/no-leakage freeze | Pass. System-level lanes are assigned by deterministic SHA-256 before residual inspection; both components of a binary share one lane. |
| Sample sufficiency | Pass for review, fail for direct scoring. The committed samples are deliberately non-substitutive and are not a benchmark dataset. |
| Metric readiness | Conditional. Metrics may run only in a task that treats full rows as local regenerated artifacts and keeps them out of git unless explicit redistribution permission is recorded. |

## Decision

`TASK-0709` should **not** become `READY` in its original generic form. The
benchmark route should be the explicit Route 2 local-extractor path represented
by `TASK-0740`.

The authorized next step is:

- keep raw `debs.dat` and full normalized DEBCat rows uncommitted;
- fetch/verify the pinned DEBCat artifact only as a local input;
- regenerate full component rows and the full holdout manifest locally through
  `scripts/extract_debcat_stellar_ml_rows.py`;
- run the first empirical Stellar M-L audit against those local artifacts with
  alpha fixed at `3.5` and the mass range/slice policy declared before scoring;
- report any per-slice positive, negative, or inconclusive outcome without
  universal-law, stellar-evolution, or discovery wording.

This gate therefore supersedes the original `TASK-0709` route and unblocks
`TASK-0740` as the executable benchmark task.

## Required Guardrails For TASK-0740

- Use `scripts/fetch_source_artifact.py` or an equivalent checksum-verified
  local copy of the pinned `debs.dat`; do not use a silent live-refresh source.
- Run `scripts/extract_debcat_stellar_ml_rows.py` and keep the full row and
  manifest outputs local-only unless a valid DEBCat redistribution marker is
  later committed.
- Treat `debcat_component_rows.sample.yaml` and
  `debcat_holdout_manifest.sample.yaml` as illustrative review artifacts, not
  scoring inputs.
- Keep the system-level holdout assignment frozen; do not tune mass bands,
  uncertainty classes, luminosity-path treatment, or exclusions after residual
  inspection.
- Report direct-luminosity and derived-luminosity sensitivity separately.
- Preserve unknown/coarse luminosity uncertainty as an explicit limitation.
- Do not create a `RESULT-*` artifact unless the benchmark task explicitly
  passes Gate A and the PR explains why publication is allowed.

## Limitations

- This gate did not fetch DEBCat or independently replay the full extraction;
  it reviewed committed artifacts only.
- DEBCat lacks an explicit open-redistribution licence for the value-bearing
  table; full rows remain local-only.
- The machine-readable `debs.dat` does not expose per-row primary-literature
  luminosity pointers, so luminosity provenance remains catalogue-level.
- No metric-bearing benchmark result exists yet; `TASK-0740` must still define
  the scoring command, ranges, uncertainty treatment, and result routing.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (benchmark-readiness gate); decision
  `AUTHORIZE_ROUTE2_LOCAL_EXTRACTOR_BENCHMARK`.
- **Canonical destination:** this review note,
  `docs/reviews/stellar-ml-benchmark-readiness-after-route2.md`, plus minimal
  task routing updates. No `results/`, `prediction_registry/`, `claims/`, or
  `knowledge/` artifact is created.
- **Review tier:** `none`; no `RESULT-*` / `PRED-*` artifact.
- **Gate A status:** not applicable because no benchmark metrics were produced.
- **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change; campaign routing only.
- **Publication blocker:** full DEBCat rows remain non-redistributable in git
  absent explicit permission; first empirical metrics must use local regenerated
  artifacts under `TASK-0740`.
