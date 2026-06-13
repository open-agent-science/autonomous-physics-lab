# Stellar M-L DEBCat Row Package

**Task:** `TASK-0708`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Mode:** row curation (fetch + checksum-verify + normalize; no fit, no residuals)
**Verdict:** `not_applicable` (dataset curation gate)
**Decision:** `ROW_PACKAGE_CURATED_ROUTE2_FROZEN_HOLDOUT`

## Scope

This task curates the first empirical row dataset for the Textbook Formula Audit
campaign: normalized DEBCat detached-eclipsing-binary component rows pairing
direct dynamical masses with catalogue or Stefan-Boltzmann luminosities, plus a
frozen, value-blind, system-level holdout manifest.

It runs only after `TASK-0707` accepted DEBCat **Route 2** (metadata-only
checksum pinning) and `TASK-0731` narrowed the public-safe shape to an
extractor plus a small non-substitutive sample unless explicit redistribution
permission is recorded. It applies the `TASK-0688` luminosity provenance policy
and the `TASK-0657` holdout and no-leakage protocol.

It does **not** fit the mass-luminosity exponent `alpha`, compute residuals,
create `RESULT-*` / `PRED-*` / `CLAIM-*` artifacts, or claim M-L validity.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| [`stellar-ml-debcat-storage-route-decision.md`](stellar-ml-debcat-storage-route-decision.md) | `TASK-0707`; Route 2 accepted for row curation, with `TASK-0731` public-safe publication limits. |
| [`stellar-ml-luminosity-provenance-and-license-route.md`](stellar-ml-luminosity-provenance-and-license-route.md) | `TASK-0688`; primary `logL`, Stefan-Boltzmann fallback, uncertainty semantics. |
| [`stellar-ml-debcat-holdout-leakage-protocol.md`](stellar-ml-debcat-holdout-leakage-protocol.md) | `TASK-0657`; system-level split, freeze before residuals. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/provenance.yaml` | Pinned locator, checksum, licence posture. |

## Method

1. **Fetch + verify.** Fetched `debs.dat` from the pinned locator
   `https://astro.keele.ac.uk/jkt/debcat/debs.dat` to a local temp path only and
   verified it byte-for-byte against the pinned checksum
   `326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`
   (95297 bytes, 374 system records). The raw table is not committed; the
   extraction script refuses to run on a checksum mismatch.
2. **Parse.** Whitespace-tokenized the fixed-column table (28 fields/row, all 374
   rows consistent) via `scripts/extract_debcat_stellar_ml_rows.py`.
3. **Mass.** `logMn`/`logMne` -> `log_mass_solar`/`log_mass_solar_unc`,
   `mass_provenance_class: direct_observation`. No model-derived (Gaia/isochrone)
   mass is used as truth.
4. **Luminosity (tiered, TASK-0688).** Catalogue `logLn` first
   (`direct_observation`); when `logLn` is the `-9.99` sentinel, reconstruct from
   `logRn`, `logTn` (`derived_luminosity`):
   `log10(L/Lsun) = 2*logR + 4*(logT - log10(5772))`,
   `sigma_logL = sqrt((2*sigma_logR)^2 + (4*sigma_logT)^2)`. Mass and luminosity
   uncertainties are kept on separate axes (never pooled).
5. **Exclusions.** A component is excluded when it has no admissible luminosity
   path; an ambiguous duplicate system id excludes all of that id's components.
6. **Freeze holdout lanes.** Each physical binary system is assigned to one lane
   by a deterministic, value-blind hash
   `bucket = int(sha256(system_id), 16) % 10` (0-4 train, 5-6 validation,
   7-9 holdout), frozen before any residual inspection. Because the rule is
   deterministic, the full frozen manifest is reproducible locally and only a
   sample is committed. Both components of a system always share one lane.

## Results

| Quantity | Value |
| --- | --- |
| System records in `debs.dat` | 374 |
| Unique physical systems | 373 |
| Systems admitted (lane-assigned) | 372 |
| Systems excluded | 1 |
| Component rows total | 748 |
| Component rows admitted | 742 |
| - luminosity `direct_observation` | 597 |
| - luminosity `derived_luminosity` (Stefan-Boltzmann) | 145 |
| Component rows excluded | 6 |

**Lane distribution (systems):** train 191, validation 81, holdout 100,
excluded 1 (target proportions 50/20/30; realized ~51/22/27 from the value-blind
hash).

**Exclusions:**

| Reason | Component rows | Detail |
| --- | --- | --- |
| `ambiguous_duplicate_system_id` | 4 | `Gaia_DR3_4658237043035232256` appears twice; both occurrences (2 components each) excluded per the no-leakage protocol. |
| `no_admissible_luminosity_path` | 2 | `HD_135671` C2 and `TYC_459-771-1` C2 have neither catalogue `logL` nor an admissible `logR`+`logT` fallback. |

## Accepted Outputs (public-safe shape, TASK-0731)

- `scripts/extract_debcat_stellar_ml_rows.py` (deterministic extractor)
- `data/textbook_formula_audit/stellar_ml/debcat_component_rows.sample.yaml`
  (small non-substitutive sample, all row classes)
- `data/textbook_formula_audit/stellar_ml/debcat_holdout_manifest.sample.yaml`
- `tests/test_stellar_ml_debcat_rows.py` (formula + leakage + sample + no-full-dataset guard)
- this review note
- ledger and provenance updates under
  `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/`

The full 742-row dataset and full holdout manifest are **not** committed (see
Publication Posture). The counts and results below describe the full set as
produced by the extractor; reproduce them locally.

## Provenance And Licensing Posture

DEBCat is public and asks users to cite the DEBCat paper (Southworth 2015), but
**no explicit open-redistribution licence was found** for the value-bearing
data. Under the TASK-0731 publication policy this repository therefore does
**not** redistribute the full normalized catalogue: neither the raw `debs.dat`
nor the full normalized `debcat_component_rows.yaml`/`debcat_holdout_manifest.yaml`
are committed. Committed instead are the deterministic extractor, a small
illustrative sample, the pinned checksum, and provenance.

**Reproduce the full rows locally:** fetch `debs.dat`
(`scripts/fetch_source_artifact.py` against the pinned SHA-256), then run
`scripts/extract_debcat_stellar_ml_rows.py`. The holdout split is frozen by the
deterministic rule `bucket = sha256(system_id) % 10`, so the full frozen
manifest is reconstructed identically without committing the membership list.
Cite Southworth, J. (2015), ASP Conf. Ser. 496, 164.

### Permission flip (near-zero rework after DEBCat grants permission)

The guard is forward-compatible: the test allows the full files **iff** a valid
redistribution marker is present. To publish the full dataset once permission is
granted, no code or test changes are needed:

1. Add `debcat_component_rows.yaml.license.yaml` and
   `debcat_holdout_manifest.yaml.license.yaml` with
   `redistribution_status: cc_by_4_0` (or `explicit_permission_recorded`) and a
   `permission_evidence:` reference to the grant (e.g. the maintainer email).
2. Run `scripts/extract_debcat_stellar_ml_rows.py` to the canonical paths and
   `git add -f` the two full files (they are `.gitignore`-d by default).
3. Flip `full_dataset_committed: true` in the DEBCat `provenance.yaml`.

The extractor already writes the canonical paths and the split is deterministic,
so the committed full set is identical to the locally-reproduced one.

## Limitations

- **Per-row luminosity provenance is catalogue-level, not per-row literature.**
  The machine-readable `debs.dat` exposes no per-row primary-source pointer, so
  luminosity provenance is recorded as DEBCat catalogue-reported (Southworth
  2015) rather than the original measurement paper per row. The `TASK-0688`
  policy's "rows without traceable luminosity provenance go to `excluded`" was
  read as satisfied by catalogue-level provenance; a maintainer may tighten this.
- **Derived luminosity is a derivation convention, not a measurement.** The 145
  `derived_luminosity` rows are Stefan-Boltzmann reconstructions from DEBCat
  radius and temperature; they must not be treated as independent luminosity
  measurements, and the reconstruction is not a validation of the
  Stefan-Boltzmann law on real stars.
- **Unknown luminosity uncertainty** is flagged (`luminosity_uncertainty_class:
  unknown`) for derived rows missing a log-space `R` or `T` error; such rows are
  retained with the flag rather than excluded. A downstream benchmark must decide
  how to weight them.
- **Spectral-type / evolutionary flags are best-effort metadata** parsed from
  the `SpT` luminosity class and are `unknown` when not unambiguous; they do not
  drive lane assignment.
- **No benchmark readiness asserted.** `accepted_for_benchmark` remains false.
  This package freezes lanes; it does not authorize an `alpha` fit.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` (dataset curation gate); decision
  `ROW_PACKAGE_CURATED_ROUTE2_FROZEN_HOLDOUT`.
- **Canonical destination:** the deterministic extractor plus committed
  `*.sample.yaml` artifacts under `data/textbook_formula_audit/stellar_ml/`, and
  this review note. The full normalized rows/manifest are not committed
  (regenerate locally). No `results/`, `prediction_registry/`, `claims/`, or
  `knowledge/` change.
- **Review tier:** `none` (no `RESULT-*` / `PRED-*` artifact).
- **Gate A status:** not applicable (no RESULT ingested). **Gate B status:** not
  applicable (no metrics or replay).
- **Claim impact:** no claim change. **Knowledge impact:** campaign routing only
  - first empirical Stellar M-L row package curated and frozen.
- **Limitations / blockers:** catalogue-level (not per-row) luminosity
  provenance; derived-luminosity convention; raw `debs.dat` intentionally not
  committed under Route 2. Benchmark readiness and `alpha` fitting remain out of
  scope pending maintainer review.
