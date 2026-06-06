# Stellar M-L Campaign Promotion Gate

Task: `TASK-0611`
Domain: Textbook Formula Audit / Stellar mass-luminosity
Mode: planning only
Verdict: `PROMOTION_GATE_DEFINED_CAMPAIGN_NOT_CREATED`

## Purpose

Stellar M-L should remain a Textbook Formula Audit slice until its source,
dataset, baseline, and holdout rules are explicit. This gate defines when it can
be promoted to a standalone campaign. It does not create campaign profile files,
canonical experiments, canonical results, claims, knowledge entries, or row
datasets.

Inputs reviewed:

- `TASK-0604`
- `docs/campaigns/textbook-formula-audit.md`
- `docs/campaigns/README.md`
- `docs/reviews/textbook-stellar-ml-row-readiness-gate.md`
- `docs/result-promotion-protocol.md`

## Minimum Promotion Conditions

All conditions below must be satisfied before a standalone Stellar M-L campaign
is created:

1. Source artifact: at least one independent mass source is selected, pinned,
   checksummed, and allowed for APL use.
2. Row schema: component/system identifiers, source provenance, mass, mass
   uncertainty, luminosity inputs, luminosity uncertainty, and filter flags are
   defined before ingestion.
3. Direct mass semantics: Gaia `mass_flame`, isochrone-derived masses, and other
   model-derived mass fields are excluded from benchmark truth.
4. Luminosity policy: luminosities are derived from admissible photometry,
   parallax, bolometric correction, or literature luminosity fields under a
   documented uncertainty policy.
5. Baseline family: the textbook M-L baseline and any piecewise/reference
   alternatives are declared before metrics. No formula search is allowed inside
   the first benchmark task.
6. Holdout policy: splits prevent leakage across components of the same physical
   system and across source references where relevant.
7. Public wording: outputs are framed as benchmark residuals and range limits,
   not discovery claims about stellar evolution or HR-diagram physics.
8. Result routing: any future result follows `docs/result-promotion-protocol.md`
   and cannot become `AGENT_PUBLISHED` without the required promotion evidence.

## Depends On TASK-0604 / TASK-0610

These conditions require source-selection and source-evaluation outputs:

- Which independent source is first.
- Exact artifact locator, checksum, timestamp/version, and reuse posture.
- Expected and usable row count after main-sequence filtering.
- Direct-mass uncertainty semantics.
- Whether luminosity can be derived without importing model-derived mass truth.
- Whether the source supports a defensible holdout split.

If TASK-0604/TASK-0610 do not clear these conditions, the campaign must not be
promoted.

## Decidable Before Source Selection

These rules can stand now:

- Gaia model-derived mass fields are forbidden as benchmark truth.
- Formula search, fitted exponent discovery, and HR-diagram discovery claims are
  forbidden before promotion.
- The first benchmark must use a predeclared baseline family.
- Public wording must stay in audit/residual language.
- Campaign files should not be created until the promotion gate passes.

## Forbidden Before Promotion

- Formula search or exponent optimization.
- Gaia model-derived mass truth.
- HR-diagram discovery claims.
- Stellar evolution claims.
- Public result wording.
- Canonical results, predictions, claims, or knowledge entries.
- Row dataset creation outside a source-artifact and row-readiness task.

## First Post-Gate Tasks

Only after the gate passes, create these tasks in order:

1. Campaign scaffold: create the standalone campaign profile, scope, routing,
   and public wording rules.
2. Dataset/source manifest: pin the accepted source artifacts and define row
   schema, source checksums, and uncertainty fields.
3. Baseline/failure-map benchmark: run the first predeclared M-L baseline and
   produce residual/failure-map outputs under the holdout policy.

## Output Routing

This note defines a quality gate only. It does not promote Stellar M-L to a
standalone campaign and does not authorize any rows, metrics, canonical results,
claims, or public summaries.
