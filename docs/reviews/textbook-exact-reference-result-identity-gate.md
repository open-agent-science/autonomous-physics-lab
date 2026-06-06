# Textbook Exact-Reference Result Identity Gate

Task: `TASK-0603`

Verdict: `SCOPED_IDENTITIES_DEFINED_RESULT_STILL_BLOCKED_BY_FIXTURE_BOUNDARIES`

## Decision

This task defines the missing scoped canonical identities for a future
Textbook Formula Audit exact-reference software/convention result:

- Hypothesis identity: `HYP-0013`
- Experiment identity: `EXP-0013`

No `RESULT-*`, claim, knowledge, prediction, empirical dataset, or
public-discovery wording is created.

## Scope

The identities are limited to APL software and convention validation over
already committed synthetic exact-reference fixtures:

- Stefan-Boltzmann SI arithmetic with the declared CODATA 2022 constant
  convention;
- Wien wavelength-domain arithmetic with the declared CODATA 2022 displacement
  constant convention;
- monotonicity, scaling, and declared negative-control gates.

The identities do not claim empirical truth of Stefan-Boltzmann, Wien
displacement, blackbody physics, stellar observations, laboratory spectra, or
any textbook formula.

## Inputs

- `docs/reviews/textbook-exact-reference-scoped-result-packaging.md`
- `docs/reviews/textbook-exact-reference-fixture-result-preflight.md`
- `docs/reviews/textbook-stefan-boltzmann-exact-reference-fixture.md`
- `docs/reviews/textbook-wien-displacement-exact-reference-fixture.md`
- `data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml`
- `data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml`
- `physics_lab/schemas/result.schema.json`
- `docs/result-promotion-protocol.md`

## Identity Boundary

`HYP-0013` says only that the committed fixture runners can reproduce declared
synthetic values and reject declared convention controls within the repository's
software-fixture scope.

`EXP-0013` defines the experiment surface for a later scoped result packaging
task. It is marked `PLANNED` because this PR does not publish the canonical
run/result artifact.

The result-publishing task must treat `EXP-0013` and `HYP-0013` as fixture
identities, not as empirical physics identities.

## Fixture Boundary Changes Required Before RESULT Publication

A later RESULT packaging task may proceed only after these metadata boundaries
are changed in the same PR as the result or in a prior reviewed PR:

1. Stefan-Boltzmann fixture boundary:
   - keep `empirical_rows_allowed: false`;
   - keep `claim_promotion_allowed: false`;
   - change the result route from sandbox-only to scoped software-result
     packaging for `EXP-0013` / `HYP-0013`;
   - allow canonical result writing only for the exact-reference software
     fixture route.
2. Wien fixture boundary:
   - keep empirical spectrum ingestion blocked;
   - keep claim and knowledge impact as `none`;
   - change `publication_scope.route` from sandbox-only to scoped
     software-result packaging for `EXP-0013` / `HYP-0013`;
   - preserve the blocked actions against observational validation, formula
     falsification, and universal-law wording.
3. Result artifact boundary:
   - publish under a new `results/EXP-0013/RUN-XXXX/result.yaml`;
   - use `review_tier: AGENT_PUBLISHED` only if Gate A passes;
   - include input hashes, replay commands, report, metrics, review metadata,
     limitations, and no claim/knowledge promotion;
   - run the repository result-publication gate or its current equivalent.

## Routing

Canonical destination: `docs/reviews/textbook-exact-reference-result-identity-gate.md`

Review tier: not applicable; no result artifact was created.

Gate A status: blocked until fixture metadata boundaries are changed and a
result-packaging task writes a schema-valid artifact.

Gate B status: not applicable.

Claim impact: none.

Knowledge impact: none.

Publication blocker: fixture metadata still declares sandbox-only result
boundaries.

## Limitations

- This task defines identities only.
- This task does not replay fixture runners.
- This task does not modify fixture metadata.
- This task does not publish a result artifact.
- This task does not create or endorse any empirical Textbook Formula Audit
  claim.
