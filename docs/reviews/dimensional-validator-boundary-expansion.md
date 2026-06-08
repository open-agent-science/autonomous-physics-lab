# Dimensional Validator Boundary Expansion

- Task: `TASK-0681`
- Surface: Dimensional Validator live challenge set
- Verdict: `BOUNDARY_SURFACE_EXPANDED_NOT_PROMOTED`

## Scope

This task applies the targeted follow-up from
[`dimensional-validator-boundary-result-preflight.md`](dimensional-validator-boundary-result-preflight.md).
It expands the live dimensional-analysis challenge set around three boundary
classes: dimensionless constants, all-dimensionless textbook relations, and
known-limit cases.

The frozen 50-item MVP challenge set and historical result artifacts are not
modified.

## Changes

- Added `pi` as a built-in dimensionless expression constant for formulas such
  as `2 * pi * r` and `2 * pi * sqrt(L / g)`.
- Added a curated `dimensionless_relation_policy:
  accepted_textbook_identity` metadata path for all-dimensionless textbook
  identities that should pass instead of being auto-flagged as suspicious.
- Added three live challenge items:
  - `DA-022` circle circumference with `pi`;
  - `DA-023` small-angle pendulum period with `pi`;
  - `DA-312` normalized Snell-law ratio as an all-dimensionless textbook
    identity;
  - `DA-408` Lorentz `beta > 1` as a known-limit boundary.

## Readiness Assessment

The live curation surface is closer to Gate A readiness because the specific
`pi` parsing blocker from `DA-407` is removed and all-dimensionless textbook
relations can now be explicitly curated rather than treated as suspicious by
default.

It remains a dimensional quality gate only. Known-limit failures still rely on
curated metadata and are not numerical or empirical validation. Dimensional
consistency does not prove physical correctness.

## Output Routing

- Task verdict: `BOUNDARY_SURFACE_EXPANDED_NOT_PROMOTED`.
- Canonical destination:
  `docs/reviews/dimensional-validator-boundary-expansion.md`.
- Review tier: `none`.
- Gate A status: closer but not promoted; this is a live challenge-set and
  validator-handling improvement, not a new `RESULT-*`.
- Gate B status: not applicable.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no `results/` artifact created or modified.
- Limitations: dimensional validity remains a formula-quality preflight only;
  semantic row-class checks and numerical known-limit scoring remain outside
  this validator.
