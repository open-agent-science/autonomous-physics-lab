# Textbook Stellar Mass-Luminosity Source/Baseline Plan

Task: `TASK-0555`

## Summary

This planning note defines the source, baseline, schema, holdout, and verification-gate posture for a future empirical audit of the textbook stellar mass-luminosity relation. It is a planning artifact only. It does not fetch Gaia data, ingest rows, run residual metrics, tune exponents, validate or falsify the relation, or promote any scientific claim.

## Scope

The future empirical lane should be limited to declared main-sequence slices with explicit mass, luminosity, source provenance, and uncertainty metadata. The audit must treat the textbook relation as range-aware rather than universal.

Out of scope for this task:

- live catalog fetches;
- row-value ingestion;
- metric runs or model fitting;
- claim promotion;
- benchmark publication.

## Candidate Source Surfaces

| Surface | Candidate role | Required posture before ingestion |
| --- | --- | --- |
| Gaia DR3 or derived cross-match | astrometry and photometry surface | pinned snapshot proposal and maintainer-approved acquisition |
| Literature benchmark stars | mass/luminosity anchors | source review, license posture, and row-role classification |
| Curated cross-match table | normalized ingestion surface | schema, checksum, holdout mask, and row provenance |

Recommended acquisition lane: `T4_snapshot_approval`. If licensing, query reproducibility, or row provenance cannot be documented, the lane should remain blocked.

## Minimum Row Fields

Future rows should provide:

- stable source identifier;
- source table and version;
- URL or DOI;
- row checksum;
- star name when available;
- mass in solar units plus uncertainty status;
- luminosity in solar units plus uncertainty status;
- parallax or distance fields with uncertainty when relevant;
- effective temperature when available;
- photometric band and conversion notes if luminosity is derived;
- spectral type when available;
- main-sequence or evolutionary-class flag;
- multiplicity flag;
- row role such as `direct_source`, `derived_input`, `holdout`, or `excluded`;
- exclusion reason for rows outside the declared range.

Units must be explicit. Normalized solar units can be used for comparison, but source units and conversion notes should remain auditable.

## Baseline Formula Convention

The future audit should freeze one baseline before inspecting residuals:

```text
L / L_sun = (M / M_sun)^alpha
```

The exponent and mass range must be declared before metrics. A classroom exponent may be useful as a baseline, but the audit should avoid universal wording and should define slice boundaries before holdout evaluation.

Planning slices:

- low-mass slice below the lower declared boundary;
- solar-like slice for the first classroom-baseline audit;
- higher-mass slice only if a separate convention is declared;
- rows outside the declared range are exclusions, not failures.

## Exclusion Rules

Exclude rows when source metadata indicates that the row is outside the declared main-sequence range, has unresolved multiplicity concerns, lacks sufficient uncertainty metadata, lacks source/license posture, uses model-derived values without a declared row role, or falls outside the frozen audit range.

Every excluded row should preserve an `exclusion_reason` so the boundary is reviewable.

## Holdout Plan

A future ingestion task should split rows before metrics into:

- baseline/schema-check rows;
- holdout rows;
- excluded rows.

No exponent fitting, slice-boundary tuning, or filtering should be changed after holdout inspection. Any fitted model must be a separate task and not the textbook baseline audit.

## Verification Gates

Future work should pass these gates before result promotion:

1. Source gate: pinned artifact, checksum, license posture, and acquisition approval.
2. Schema gate: required fields, units, row roles, and exclusions validated.
3. Replay gate: deterministic load from pinned files.
4. Baseline gate: formula convention, exponent, and slice range frozen before metrics.
5. Holdout gate: no-peek split committed before residual evaluation.
6. Result-promotion gate: route through `docs/result-promotion-protocol.md`.

## Output Routing

- Task verdict: `INCONCLUSIVE`
- Canonical destination: `docs/reviews/textbook-stellar-mass-luminosity-source-baseline-plan.md`
- Review tier: maintainer review required before source acquisition.
- Gate A status: not attempted.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.

## Follow-Up Candidate

If accepted, the next task should propose a small pinned-source acquisition with source query, checksum, schema mapping, row count, and holdout split. It should still avoid residual metrics until the baseline convention is frozen.
