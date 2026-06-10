# Stellar M-L Luminosity Provenance And DEBCat License Route

**Task:** `TASK-0688`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Mode:** planning only (no live fetch, no row transcription, no metrics)
**Decision:** `LUMINOSITY_PROVENANCE_DEFINED_ROUTE2_RECOMMENDED`
**Task verdict:** `not_applicable` (planning gate)

## Scope

This review resolves the load-bearing Stellar M-L blocker identified by
`TASK-0658`: luminosity is the dependent variable of
`L/L_sun = (M/M_sun)^alpha`, but no admissible luminosity source,
conversion, or uncertainty semantics were pinned. It also recommends one
DEBCat licence/storage route for maintainer decision.

It uses committed repository evidence only. It does **not** fetch `debs.dat`,
transcribe DEBCat values, compute luminosities, fit exponents, create
`RESULT-*` / `PRED-*` artifacts, or promote Stellar M-L claims.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/stellar-ml-debcat-row-readiness-gate.md` | `TASK-0658`; `SOURCE_PINNED_ROWS_BLOCKED`; luminosity and licence blockers. |
| `docs/reviews/stellar-ml-debcat-holdout-leakage-protocol.md` | `TASK-0657`; system-level no-leakage; luminosity inadmissible until policy defined. |
| `docs/reviews/textbook-stellar-ml-debcat-source-artifact-package.md` | `TASK-0628`; metadata-only DEBCat package; field groups include log-luminosity. |
| `docs/reviews/textbook-stellar-ml-source-candidate-admissibility.md` | `TASK-0610`; DEBCat selected; luminosity deferred. |
| `data/textbook_formula_audit/stellar_ml/source_manifest.yaml` | DEBCat candidate entry and row-class policy. |
| `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/*` | Locator, checksum, licence review, extraction and blocker notes. |

## Luminosity Provenance Decision

### Primary path — catalogue-reported log luminosity

**Use DEBCat's catalogue-reported log-luminosity field when populated.**

Committed evidence expects a log-luminosity column in the planned normalized
surface (`log_luminosity_solar` in the manifest field groups; extraction notes
require preserving "luminosity/log-luminosity field semantics if used"). The
DEBCat package describes the catalogue as compiling component masses, radii,
effective temperatures, and literature source references — the standard DEBCat
posture is that log luminosity values are **literature-reported or
catalogue-compiled**, not recomputed from dynamical mass.

| Field | Policy |
| --- | --- |
| Admitted quantity | `log10(L/L_sun)` as reported in DEBCat when the field is populated and finite. |
| Row class | `direct_observation` — catalogue/literature-reported luminosity, not APL-computed. |
| Conversion to benchmark axis | `L/L_sun = 10^(log10(L/L_sun))` for the textbook relation audit. |
| Provenance required per row | DEBCat `source_reference_notes` (or equivalent literature pointer) must identify the luminosity source; rows without traceable luminosity provenance go to `excluded`. |
| Mass coupling | **Forbidden.** Luminosity admission must not use dynamical mass, Gaia model mass, isochrone mass, or any fitted M-L coefficient in its derivation. |

### Fallback path — Stefan-Boltzmann reconstruction

**When the catalogue log-luminosity field is missing, null, or flagged
non-admissible, reconstruct luminosity from DEBCat radius and effective
temperature only.**

| Field | Policy |
| --- | --- |
| Admitted inputs | DEBCat `radius_solar` and `effective_temperature_k` only (plus their uncertainties when present). |
| Row class | `derived_luminosity`. |
| Conversion (log form) | `log10(L/L_sun) = 2 log10(R/R_sun) + 4 log10(Teff/Teff_sun)`. |
| Pinned solar reference | `Teff_sun = 5772 K` (IAU 2015 nominal solar effective temperature; record in extraction ledger). |
| Linear form (for audit checks) | `L/L_sun = (R/R_sun)^2 * (Teff/5772 K)^4`. |
| Mass coupling | **Forbidden.** Radius and temperature must come from DEBCat catalogue fields, not from mass-inferred models. |
| Exclusion | Rows missing admissible `R`, `Teff`, or both after the primary path fails → `excluded` with `exclusion_reason`. |

The fallback is methodologically acceptable for an M-L benchmark because it
derives the dependent variable from independently measured structure parameters
while keeping dynamical mass as the independent variable. It must not be used
when a populated, provenance-traceable catalogue log-luminosity field is
available — the primary path takes precedence to avoid unnecessary
recomputation.

### Uncertainty semantics

| Path | Uncertainty policy |
| --- | --- |
| Primary (`direct_observation`) | Preserve DEBCat/literature luminosity uncertainty when recorded. If uncertainty is absent, assign an `uncertainty_class: unknown` flag and route to a diagnostic lane or `excluded` per predeclared thresholds in the holdout protocol — do not invent uncertainties. |
| Fallback (`derived_luminosity`) | Propagate radius and temperature uncertainties in log space, treating `R` and `Teff` errors as independent: `sigma_logL = sqrt((2 sigma_R / (R ln 10))^2 + (4 sigma_T / (Teff ln 10))^2)`. Rows missing both `sigma_R` and `sigma_T` → `uncertainty_class: unknown` with the same diagnostic/exclusion rule as above. |
| Cross-axis rule | Mass uncertainty semantics remain separate from luminosity uncertainty; never merge or pool them into one benchmark error model. |

### Row-class summary

| Row class | When used | Benchmark truth role |
| --- | --- | --- |
| `direct_observation` | Populated DEBCat log-luminosity with traceable literature provenance | Dependent variable |
| `derived_luminosity` | SB reconstruction from DEBCat `R` and `Teff` when log-luminosity absent | Dependent variable |
| `direct_observation` (mass) | DEBCat dynamical component mass | Independent variable |
| `model_derived_mass` | Gaia, isochrone, or other model masses | **Forbidden** as benchmark truth |
| `excluded` | Missing luminosity path, missing provenance, licence block, or ambiguous system id | Not scored |

## Licence / Storage Route Recommendation

**Recommended route for maintainer decision: Route 2 — metadata-only checksum
pinning with a reviewed extraction ledger and normalized row commit (no raw
`debs.dat`).**

| Route | Assessment |
| --- | --- |
| **Route 2: metadata-only checksum + extraction ledger** | **Recommended.** Aligns with the existing `TASK-0628` posture (`raw_artifact_commit_allowed: false`), avoids committing the 95 KB ASCII table under an unclear licence, and still permits a reproducible row package: normalized component rows in `data/textbook_formula_audit/stellar_ml/*.yaml`, pinned to the recorded `sha256` checksum, with an extraction ledger documenting column mapping, luminosity path per row, and citation. |
| Route 1: explicit permission for DEBCat-derived rows | Valid if the maintainer obtains written redistribution permission from the catalogue author; would additionally allow raw `debs.dat` commit if desired. Not recommended as the default because it adds an external dependency before any row work can start. |
| Route 3: replacement source | Rejected as the primary route. Would forfeit DEBCat's direct dynamical mass advantage and restart source selection; keep as a contingency only if Route 1 fails and Route 2 is rejected. |

This task **does not** make the licence determination. The maintainer must
confirm Route 2 (or select Route 1/3) before value-bearing rows are committed.

## Interaction With Holdout Protocol

`TASK-0657` barred luminosity inputs until this policy existed. With
luminosity provenance now pinned:

- the holdout protocol's luminosity inadmissibility clause is **superseded for
  DEBCat rows that follow this policy**;
- system-level splitting (`physical_binary_system`) remains mandatory;
- luminosity path (`direct_observation` vs `derived_luminosity`) must be
  recorded per row in the extraction ledger before lane assignment;
- post-score tuning of mass bands, uncertainty classes, or exclusion rules
  remains forbidden.

Licence/storage remains a separate blocker until the maintainer confirms the
recommended route.

## What Would Reopen Row Curation

Both conditions must be satisfied before a DEBCat row-curation task runs:

1. **Maintainer licence/storage confirmation** — accept Route 2 (or Route 1/3)
   and update `provenance.yaml` / manifest redistribution fields accordingly.
2. **This luminosity-provenance policy merged** — row curation may then:
   - parse `debs.dat` under the confirmed storage route;
   - apply the tiered luminosity policy (primary log-luminosity, SB fallback);
   - build the system-to-lane manifest under `TASK-0657`;
   - freeze the manifest before any exponent fit or residual inspection.

A licence decision alone still leaves luminosity undefined without this policy;
this policy alone still leaves rows uncommittable without licence confirmation.

## Guardrails

- No Gaia `mass_flame`, isochrone masses, or model-derived masses as benchmark
  truth.
- Do not pool primary and fallback luminosity paths without per-row
  `luminosity_provenance_class` labelling.
- Do not fit or audit the textbook exponent `alpha` in this task.
- Do not treat Stefan-Boltzmann reconstruction as validation of the
  Stefan-Boltzmann law on real stars; it is a luminosity derivation convention
  only.

## Limitations

- No live inspection of `debs.dat` column headers or row-level fill rates was
  performed; the tiered policy assumes DEBCat provides log-luminosity, radius,
  and temperature fields as planned in the manifest. A row-curation task must
  report actual column presence and primary-vs-fallback counts.
- Solar `Teff` reference is pinned to `5772 K`; a later task may document an
  alternate bolometric zero point only if it does not import model-derived mass.
- Licence recommendation is advisory; redistribution permission is not confirmed.
- No holdout lanes were assigned and no metrics were computed.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (planning gate); decision
  `LUMINOSITY_PROVENANCE_DEFINED_ROUTE2_RECOMMENDED`.
- **Canonical destination:** this review note,
  `docs/reviews/stellar-ml-luminosity-provenance-and-license-route.md`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact.
- **Gate A status:** not applicable (no rows ingested).
- **Gate B status:** not applicable (no metrics or replay).
- **Claim impact:** none.
- **Knowledge impact:** campaign routing only — luminosity policy defined;
  licence route recommended pending maintainer decision.
- **Publication blocker:** row curation remains blocked until maintainer
  confirms licence/storage route; luminosity provenance blocker is cleared by
  this review.
