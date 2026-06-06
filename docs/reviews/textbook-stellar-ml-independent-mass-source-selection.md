# Textbook Stellar M-L Independent Mass-Source Selection

Task: `TASK-0604`
Domain: Textbook Formula Audit / Stellar mass-luminosity
Mode: planning only
Verdict: `SOURCE_CANDIDATES_SELECTED_ROWS_BLOCKED`

## Context

The Stellar M-L lane remains blocked because Gaia model-derived mass fields are
not admissible benchmark truth. The next row package needs independent mass
measurements, preferably dynamical masses from detached binaries or other
well-characterized benchmark-star sources. This review selects candidate source
families only; it does not fetch value-bearing rows.

Inputs reviewed:

- `docs/reviews/textbook-stellar-ml-row-readiness-gate.md`
- `docs/reviews/textbook-stellar-mass-luminosity-source-baseline-plan.md`
- `docs/campaigns/textbook-formula-audit/stellar-mass-luminosity-ood-source-baseline-plan.md`
- `data/textbook_formula_audit/stellar_ml/source_manifest.yaml`

## Candidate Sources

### 1. DEBCat

Locator: `https://www.astro.keele.ac.uk/jkt/debcat/`

Citation: Southworth detached-eclipsing-binary catalogue, cited in the existing
Stellar M-L source/baseline plan as the representative public DEB compilation.

Source type: curated detached eclipsing-binary catalogue.

Reuse posture: candidate only. A source-artifact task must verify the catalogue
download/reuse terms before values are copied into APL.

Use posture: first-choice acquisition candidate. Detached eclipsing binaries
provide direct dynamical masses and radii, making them the cleanest starting
point for a public Stellar M-L benchmark. The source is table-like, maintained
as a named catalogue, and should support a reproducible artifact/checksum task.

Expected row scale: enough systems to plausibly support a first empirical row
package after main-sequence and quality filtering; exact count must be frozen by
the artifact task.

Main blockers for the artifact task:

- Confirm download endpoint, source timestamp, checksum path, and reuse terms.
- Preserve component-level mass/radius uncertainty semantics.
- Define crossmatch policy for luminosity inputs without using Gaia mass fields.
- Decide whether the holdout split is by binary system, source reference, or
  mass regime.

### 2. Torres, Andersen, and Gimenez 2010 Benchmark Sample

Locator: journal article and publisher artifact for "Accurate masses and radii
of normal stars: modern results and applications".

Citation: Torres, Andersen, and Gimenez 2010 benchmark-star review.

Source type: literature benchmark sample of stars with accurate masses and
radii, including detached eclipsing binaries and related dynamical systems.

Reuse posture: candidate only. The article/table artifact and publisher reuse
terms must be pinned before any row package.

Use posture: second-choice seed or audit cross-check. It is smaller and more
static than DEBCat but has strong literature provenance and can help validate
whether the first source package is selecting clean main-sequence rows.

Expected row scale: smaller than DEBCat; suitable for a seed benchmark or
source-consistency check rather than the only OOD campaign surface.

Main blockers for the artifact task:

- Pin the exact article/table artifact and checksum.
- Confirm table reuse posture.
- Preserve the paper's accuracy cuts and exclude rows outside the intended
  main-sequence scope.

### 3. Eker et al. Detached-Binary Mass-Luminosity Tables

Locator: journal article and supplementary/table artifacts for the detached
binary mass-luminosity relation work.

Citation: Eker et al. detached-binary mass-luminosity relation tables, already
named in the existing Stellar M-L source/baseline plan as an alternate published
parameterization family.

Source type: literature table derived from detached binaries.

Reuse posture: candidate only. It is not row-admissible until the artifact task
separates source rows, fitted parameters, and reuse rights.

Use posture: comparator candidate, not first source. This family is useful
because it is directly tied to mass-luminosity work, but it must be handled
carefully so the benchmark does not circularly test a fitted relation against
the same relation's curated training surface.

Expected row scale: potentially larger than a small benchmark-star article, but
exact usable rows depend on artifact availability and filtering.

Main blockers for the artifact task:

- Separate source rows from any fitted relation parameters.
- Exclude relation coefficients from benchmark truth.
- Verify whether component luminosities can be reconstructed without importing
  the publication's fitted formula as ground truth.

## First Source Recommendation

Recommended first source: DEBCat.

Rationale:

- It best matches the direct-mass requirement.
- It is table-oriented and likely easier to freeze as a source artifact.
- It leaves room for a source-level holdout by system, reference, or mass band.
- It can be paired with Gaia only for luminosity/context data, not mass truth.

The first acquisition task should pin the DEBCat artifact, checksum, row count,
license/reuse posture, and component schema. It should not compute luminosities
or fit the Stellar M-L exponent.

## Holdout and Semantics

Required before row curation:

- Direct mass source field with uncertainty and provenance.
- Explicit component/system identifiers.
- Main-sequence inclusion policy.
- Luminosity derivation policy from admissible photometry/parallax/context
  sources.
- Holdout split that prevents both components of the same physical system from
  leaking across train/test lanes.
- Exclusion of Gaia `mass_flame` and all other isochrone/model-derived mass
  fields as benchmark truth.

## Output Routing

This review selects source candidates only. It does not create dataset rows,
source manifests with checksums, formulas, fitted exponents, metrics, canonical
results, or claims.

Recommended follow-up: a DEBCat source-artifact package task after maintainers
accept this source order.
