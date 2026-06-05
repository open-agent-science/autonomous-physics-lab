# Textbook Stellar M-L row-readiness gate

- Task: `TASK-0587`
- Campaign: `textbook_formula_audit`
- Protocol class: source and row-readiness review
- Status: no live fetch, no row curation, no metrics

## Scope

This review decides whether the Stellar Mass-Luminosity empirical lane can move
from metadata-only source packaging into row-level curation. It reviews the
planning note, source-acquisition runbook, metadata-only source manifest, and
campaign guardrails. It does not fetch Gaia data, copy literature tables,
cross-match rows, compute luminosities, fit exponents, run residual metrics,
or promote claims.

## Inputs reviewed

- `docs/campaigns/textbook-formula-audit/stellar-mass-luminosity-ood-source-baseline-plan.md`
- `docs/reviews/textbook-stellar-mass-luminosity-pinned-source-package.md`
- `docs/runbooks/textbook-stellar-ml-source-acquisition-runbook.md`
- `data/textbook_formula_audit/stellar_ml/source_manifest.yaml`
- `docs/campaigns/textbook-formula-audit.md`

## Gate checklist

| Gate | Status | Review note |
| --- | --- | --- |
| Exact source version pinned | `BLOCKED` | Gaia DR3 is named as a source family, but no exact query execution, retrieval timestamp, row count, or selected source artifact is pinned. |
| Raw artifact checksum | `BLOCKED` | No value-bearing Gaia, DEB, benchmark-star, or normalized row artifact exists yet. |
| License and redistribution decision | `BLOCKED` | Gaia and literature-anchor reuse posture is still metadata-only / to-be-verified. |
| Required Gaia/context fields | `PARTIAL` | The runbook lists required Gaia fields, but no schema-backed row table exists to verify field presence. |
| Independent mass source | `BLOCKED` | The package names literature benchmark-star / eclipsing-binary anchors, but no exact source, DOI/catalog id, checksum, or row count is selected. |
| Row-class separation | `PARTIAL` | Direct observation, derived luminosity, model-derived mass, holdout, and excluded row roles are declared, but not instantiated in rows. |
| Units and uncertainty semantics | `PARTIAL` | Required units and 1-sigma semantics are declared in planning, but source-specific uncertainty columns are not pinned. |
| Holdout/no-peek split | `PARTIAL` | The `0.5 <= M/M_sun <= 2.0` first-audit slice and no-peek requirements are declared, but cannot be frozen against rows until acquisition. |
| Main-sequence and multiplicity filters | `PARTIAL` | Stop conditions exist, but no source rows are available to check deterministic filter application. |
| Metric isolation | `PASS` | All reviewed artifacts explicitly forbid residual metrics, exponent fitting, prediction entries, result artifacts, and claim promotion. |

## Decision

`BLOCKED_SOURCE_NOT_PINNED`

Row-level curation should not begin yet. The source package is useful and
correctly preserves the audit boundary, but it is still a metadata-only
acquisition package. A row-curation task needs a maintainer-approved source
selection and an artifact package with source version, retrieval timestamp,
row count, checksums, license/attribution decision, field list, and no-peek
attestation.

The most important blocker is the independent mass axis: Gaia-derived mass
fields remain inadmissible for the primary M-L audit because they are
model-derived. A future task must pin a model-independent mass source, such as
a reviewed detached-eclipsing-binary or benchmark-star table, before any
empirical M-L row can be treated as benchmark truth.

## Allowed next task shape

A next task may be a source-acquisition task if it is limited to one of these:

- selecting and pinning a specific literature benchmark-star or detached
  eclipsing-binary source artifact;
- recording exact license, attribution, retrieval timestamp, row count, raw
  checksum, and source version;
- preparing a normalized row schema with row roles and uncertainty semantics;
- recording a no-peek attestation before any metric-bearing audit.

That task must still stop before residual metrics, exponent fitting, or
formula verdicts.

## Forbidden substitutions

- Do not use Gaia `mass_flame` or other isochrone/model-derived mass fields as
  benchmark mass truth.
- Do not run a Gaia-only M-L audit to bypass the missing independent mass
  source.
- Do not tune the mass range, filters, or holdout split after row inspection.
- Do not claim the mass-luminosity relation is validated, falsified, universal,
  or newly discovered.

## Output routing

- Task verdict: `INCONCLUSIVE` for row readiness.
- Canonical destination:
  `docs/reviews/textbook-stellar-ml-row-readiness-gate.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified.
- Publication blocker: exact source artifacts, source version, checksums,
  license/redistribution review, row counts, and independent mass rows are not
  pinned yet.
