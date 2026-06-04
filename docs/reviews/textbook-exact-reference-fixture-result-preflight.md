# Textbook Exact-Reference Fixture Result Preflight

**Task:** `TASK-0568`
**Campaign:** Textbook Formula Audit
**Fixtures reviewed:** Stefan-Boltzmann exact-reference fixture and Wien
displacement exact-reference fixture
**Status:** result-routing preflight complete
**Decision:** ready for a scoped software-result packaging task; no `RESULT-*`
artifact is created in this preflight PR

## Reviewed Evidence

Reviewed inputs:

- `docs/reviews/textbook-stefan-boltzmann-exact-reference-fixture.md`
- `docs/reviews/textbook-wien-displacement-exact-reference-fixture.md`
- `data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml`
- `data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml`
- `physics_lab/engines/stefan_boltzmann.py`
- `physics_lab/engines/textbook_wien.py`
- `tests/test_textbook_stefan_boltzmann_exact_reference.py`
- `tests/test_textbook_wien.py`
- `docs/result-promotion-protocol.md`

No empirical spectra, stellar rows, laboratory rows, or formula-audit datasets
were fetched or scored.

## Replay Performed

Commands run for this preflight:

```bash
python3 scripts/run_textbook_stefan_boltzmann_exact_reference.py \
  --config data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml \
  --output-dir /tmp/apl-stefan-fixture

python3 -m pytest tests/test_textbook_wien.py \
  tests/test_textbook_stefan_boltzmann_exact_reference.py
```

Replay result:

- Stefan-Boltzmann exact-reference runner returned `VALID_IN_RANGE` for the
  synthetic software fixture, with all declared gates passing.
- Stefan-Boltzmann fixture rows: `16` total, `8` reference rows, `8` holdout
  rows.
- Stefan-Boltzmann max exact-reference relative error: `0.0`.
- Stefan-Boltzmann `T^4`, `R^2`, monotonicity, wrong-temperature-exponent
  control, and wrong-area control checks passed.
- Wien displacement fixture tests passed for wavelength-domain arithmetic,
  monotonicity, exact constant reproduction, wrong constant, wrong temperature
  unit, and frequency/wavelength peak-convention controls.

## Routing Decision

The fixtures are suitable for **scoped exact-reference software-result
packaging** after a follow-up task assigns a canonical `EXP/RUN` result
identity and writes a `RESULT-*` artifact whose scope is explicitly limited to
software/convention validation.

This preflight PR does not create that `RESULT-*` artifact because the existing
fixture manifests still declare sandbox-only boundaries:

- Stefan-Boltzmann: `promotion_boundary.sandbox_only: true` and
  `writes_canonical_result: false`.
- Wien: `publication_scope.route: sandbox_only`.

Changing those boundaries should be a narrow result-packaging task, not a
quiet side effect of this routing preflight.

## Interpretation Boundary

The fixtures validate deterministic software plumbing and exact-reference
conventions only:

- Stefan-Boltzmann: SI units, CODATA 2022 constant convention, exact synthetic
  arithmetic, scaling gates, monotonicity, and negative controls.
- Wien displacement: wavelength-domain convention, CODATA 2022 displacement
  constant, exact synthetic arithmetic, monotonicity, and negative controls.

They do **not** validate or falsify Stefan-Boltzmann, Wien displacement,
blackbody physics, stellar observations, empirical spectra, or any real-world
dataset slice.

## Recommended Follow-Up

Open a narrow result-packaging task that:

1. assigns a canonical experiment/run identity for exact-reference software
   fixtures;
2. writes a `RESULT-*` artifact with `review_tier: AGENT_PUBLISHED`;
3. scopes the result to software/convention validation only;
4. preserves claim and knowledge impact as `none`;
5. keeps empirical Textbook Formula Audit rows blocked until source, schema,
   holdout, and audit gates are pinned.

## Output Routing Summary

- Task verdict: `READY_FOR_SCOPED_RESULT_PACKAGING`
- Canonical destination:
  `docs/reviews/textbook-exact-reference-fixture-result-preflight.md`
- Review tier: `none`
- Gate A status: replay evidence passes for software-fixture scope, but
  canonical result publication is deferred because the committed fixture
  manifests remain sandbox-only and no result identity is assigned by this
  task.
- Gate B status: not applicable; no prediction or reveal artifact.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: no `RESULT-*` artifact created or modified.
- Limitation: exact-reference fixtures are synthetic convention checks, not
  empirical formula audits.
