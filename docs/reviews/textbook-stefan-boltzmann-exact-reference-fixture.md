# Textbook Stefan-Boltzmann exact-reference fixture

**Task:** `TASK-0527`
**Fixture:** `textbook-stefan-boltzmann-exact-reference-001`
**Verdict:** `VALID_IN_RANGE` for the declared software fixture only.

## Scope

This task adds a deterministic synthetic blackbody fixture for checking APL's
Stefan-Boltzmann SI units and verification gates. It does not ingest stellar or
laboratory rows, fit any parameter, compute empirical residuals, or make a
statement about physical emitters outside the fixture.

## Input References

- `docs/reviews/textbook-stefan-boltzmann-source-baseline-plan.md`
- `data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml`
- NIST CODATA 2022 Stefan-Boltzmann constant:
  `https://physics.nist.gov/cgi-bin/cuu/Value?sigma`

## Method

The fixture generates `16` synthetic spherical-emitter rows from four radii and
four temperatures in SI units. The frozen baseline is:

```text
L = 4 * pi * R^2 * sigma * T^4
sigma = 5.670374419e-8 W m^-2 K^-4
```

Alternating radius-temperature grid cells are labeled as reference and holdout
rows for software parity only. Fitting is forbidden. The runner checks
dimensional consistency, the frozen constant convention, exact-reference
reproduction, `T^4` scaling, `R^2` area scaling, monotonicity, a wrong-`T^3`
control, and a wrong-area control.

## Code Reference

- `physics_lab/engines/stefan_boltzmann.py`
- `scripts/run_textbook_stefan_boltzmann_exact_reference.py`
- `tests/test_textbook_stefan_boltzmann_exact_reference.py`

## Metrics

| Check | Outcome |
| --- | --- |
| synthetic rows | `16` |
| reference rows | `8` |
| holdout rows | `8` |
| dimensional consistency | `PASS` |
| CODATA 2022 constant convention | `PASS` |
| exact-reference reproduction | `PASS` |
| temperature `T^4` scaling | `PASS` |
| radius `R^2` area scaling | `PASS` |
| monotonicity | `PASS` |
| wrong-temperature-exponent control | rejected as expected |
| wrong-area control | rejected as expected |

## Replay

```bash
python3 scripts/run_textbook_stefan_boltzmann_exact_reference.py \
  --config data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml \
  --output-dir .validation/stefan-boltzmann
```

## Limitations

- This is an exact-reference software fixture, not empirical evidence.
- The fixture cannot assess stellar atmospheres, extinction, bolometric
  correction, circular catalog values, or laboratory calibration quality.
- A later empirical task must pin source files and prove non-circular row
  provenance before computing observational metrics.
- No claim or knowledge status changes are authorized.

## Output Routing

- Task verdict: `VALID_IN_RANGE`
- Canonical destination: this review note plus sandbox-only runner output
- Review tier: `none`
- Gate A: not attempted; no RESULT or PRED artifact was created
- Gate B: not attempted
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Publication blocker: fixture behavior is reviewable, but empirical
  interpretation remains blocked until a separate source-curation and audit
  task exists
