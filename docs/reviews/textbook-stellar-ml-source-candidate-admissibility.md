# Textbook Stellar M-L Source Candidate Admissibility

Task: `TASK-0610`
Domain: Textbook Formula Audit / Stellar mass-luminosity
Mode: planning only
Verdict: `DEBCAT_SELECTED_FOR_SOURCE_ARTIFACT_PACKAGE`

## Scope

This review starts from the landed `TASK-0604` source-selection note and checks
whether one candidate source is admissible for a future source-artifact package.
It does not fetch, transcribe, normalize, or checksum value-bearing rows. It
does not compute luminosities, fit mass-luminosity exponents, inspect residuals,
or promote a formula verdict.

Inputs reviewed:

- `docs/reviews/textbook-stellar-ml-independent-mass-source-selection.md`
- `docs/reviews/textbook-stellar-ml-row-readiness-gate.md`
- `docs/reviews/textbook-stellar-mass-luminosity-source-baseline-plan.md`
- `docs/campaigns/textbook-formula-audit.md`
- `data/textbook_formula_audit/stellar_ml/source_manifest.yaml`

## Candidate Gate

| Candidate | Locator Stability | Reuse and Checksum Posture | Mass Semantics | Luminosity Requirements | Holdout Implications | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| DEBCat | Stable public catalogue page at `https://www.astro.keele.ac.uk/jkt/debcat/`; exact download endpoint and retrieval timestamp still need artifact-task pinning. | Reuse terms must be verified before row values are copied; checksum is feasible once the downloaded raw and normalized artifacts are selected. | Best available fit for the benchmark goal because detached eclipsing binaries provide direct dynamical component masses rather than Gaia or isochrone model-derived masses. | Luminosity is not benchmark-ready by default; a later task must define admissible photometry, parallax, extinction, bolometric correction, or directly reported luminosity rules. | Split by physical binary system first, with optional reference or mass-band diagnostics, so paired components cannot leak across train/test lanes. | First source selected for a source-artifact package only. |
| Torres, Andersen, and Gimenez 2010 | Stable literature target, but the exact article/table artifact and any machine-readable table path must be pinned. | Reuse terms and table checksum path need a source-artifact decision before rows are copied. | Strong benchmark-star provenance with accurate masses and radii, but smaller and more static than a catalogue lane. | Useful as an audit cross-check after a luminosity policy exists; not enough to replace the first catalogue package by itself. | Can validate quality cuts and main-sequence filtering, but row scarcity makes it weaker as the first holdout surface. | Secondary audit/cross-check candidate. |
| Eker et al. detached-binary mass-luminosity tables | Literature target is identifiable, but source rows, fitted relations, and table artifacts need separation. | Reuse terms and checksums remain unresolved. | Potentially relevant detached-binary source family, but circularity risk is high if the benchmark tests an M-L relation against that relation's curated training surface. | Component luminosities must be sourced or reconstructed without importing fitted relation coefficients as truth. | Holdout is only meaningful after rows are separated from relation parameters and training surfaces. | Comparator only; not first source. |

## Selection

Selected first source for the next source-artifact task: `DEBCat`.

DEBCat is admissible for packaging because it is the cleanest match to the
direct-mass requirement and should support a reproducible raw-artifact,
checksum, source timestamp, and component-schema workflow. This selection is
not row acquisition approval. The next task must still pin the exact artifact,
license/reuse posture, retrieval timestamp, row count, checksum policy,
component identifiers, uncertainty semantics, and no-peek holdout rule.

The recommended next package should keep the source slice narrow:

- detached eclipsing-binary component masses only;
- component and system identifiers required;
- explicit mass uncertainty fields required;
- Gaia `mass_flame`, isochrone-derived masses, and all other model-derived mass
  fields excluded as benchmark truth;
- luminosity rows deferred until an admissible luminosity derivation or directly
  reported luminosity policy is reviewed;
- holdout split by binary system before any exponent fit or residual metric.

## Blockers Preserved

The Stellar M-L empirical benchmark remains blocked on value-bearing rows until
a source-artifact package records a committable source artifact or reviewed
metadata-only alternative. In particular:

- no DEBCat rows have been fetched or copied;
- no row count has been frozen;
- no checksum has been created;
- no luminosity derivation policy has been accepted;
- no mass-luminosity exponent has been fit;
- no train/test split has been populated.

`TASK-0628` is the appropriate follow-up route once maintainers accept this
selection: package the DEBCat source artifact, or preserve a precise blocker if
the source endpoint, reuse terms, or checksum path fails.

## Output Routing

Canonical destination: this review note.

Review tier: source-readiness planning. Gate A and Gate B are not attempted
because no dataset rows, predictions, or benchmark metrics are produced.

Claim impact: none. This review does not claim a Stellar M-L law, exponent,
residual pattern, benchmark result, or source-derived empirical finding.

Knowledge impact: none. DEBCat is selected as the first source-artifact path,
not promoted to reviewed APL knowledge.

Publication blocker: value-bearing publication remains blocked until a later
source-artifact package pins source metadata, checksum, row schema, uncertainty
semantics, reuse posture, and no-peek split policy.
