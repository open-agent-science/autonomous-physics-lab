# Textbook Wien Displacement Exact-Reference Fixture

Task: `TASK-0537`

## Summary

This task adds a deterministic, synthetic exact-reference fixture for the
wavelength-domain Wien displacement law convention:

```text
lambda_peak = b / T
```

The fixture uses the declared CODATA 2022 Wien wavelength displacement constant
`b = 0.002897771955 m*K` and a fixed Kelvin temperature grid. It is a software
and verification-gate artifact only.

## Method

Implemented surfaces:

- `examples/textbook_wien_displacement_exact_reference.yaml`
- `data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml`
- `physics_lab/engines/textbook_wien.py`
- `physics_lab/registry/examples.py`
- `tests/test_textbook_wien.py`

The checker verifies:

1. Kelvin temperature scaling through `lambda_peak = b / T`.
2. Strictly decreasing peak wavelength as temperature increases.
3. Fixture reference values against the declared constant.
4. Negative-control behavior for:
   - wrong displacement constant;
   - wrong temperature unit;
   - frequency-domain/wavelength-domain peak-convention confusion.

The `examples/` copy is classified as `textbook_wien_exact_reference_fixture`
by the examples registry so repository validation does not treat it as a normal
runnable benchmark config that must point at a new canonical result.

## Scope Boundaries

This task does not ingest empirical spectra, fit blackbody curves, or claim that
APL has validated or falsified Wien displacement against observations. The
artifact is limited to deterministic plumbing and convention checks before any
future empirical Textbook Formula Audit work.

## Result-Promotion Routing

- Canonical destination: sandbox-only software/benchmark fixture.
- Review tier: maintainer review required before reuse as campaign baseline
  infrastructure.
- Gate A status: not requested; no claim-bearing result is published.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blockers: empirical source ingestion, observational validation,
  and formula-audit interpretation remain future tasks.

## Verdict

`VALID_IN_RANGE` for the narrow deterministic fixture scope: the fixture checks
wavelength-domain Wien exact-reference arithmetic, unit convention, monotonicity,
and declared negative controls over the committed synthetic temperature grid.
