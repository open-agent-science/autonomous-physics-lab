---
id: CLAIM-0011
title: Textbook Exact-Reference Software Fixture Validation
domain: textbook_formula_audit
status: DRAFT
hypothesis_id: HYP-0013
evidence:
  experiments:
    - EXP-0013
  results:
    - RESULT-0019
scope: APL software/units/convention validation over committed synthetic exact-reference fixtures only; not an empirical statement about Stefan-Boltzmann, Wien displacement, blackbody physics, stellar observations, or laboratory spectra.
---

# CLAIM-0011: Textbook Exact-Reference Software Fixture Validation

## Statement

APL reproduces the declared synthetic reference values of the committed
Textbook Formula Audit exact-reference fixtures within their declared tolerance,
and rejects their declared convention negative controls. This is a statement
about repository software, units, constants, and convention plumbing, not about
the empirical truth of any textbook formula.

## Evidence Status

`RESULT-0019` (`results/EXP-0013/RUN-0001/result.yaml`, review_tier
`AGENT_PUBLISHED`) records the deterministic Stefan-Boltzmann exact-reference
run: 16 synthetic rows, max exact-reference relative error `0.0` under a
`1e-12` tolerance, all software gates `PASS` (dimensional consistency, CODATA
2022 constant convention, `T^4` and `R^2` scaling, monotonicity), and both
declared negative controls rejected. The Wien wavelength-domain fixture is
supporting software evidence verified by `tests/test_textbook_wien.py`.

The claim remains `DRAFT`. It is agent-published, not independently validated or
maintainer-reviewed. A maintainer-only transition may change its status after
review.

## Scope

Current scope: the committed synthetic exact-reference fixtures for
Stefan-Boltzmann SI arithmetic and Wien wavelength-domain arithmetic, their
declared CODATA 2022 constant conventions, and their declared negative-control
gates. No empirical rows are ingested.

## Caution

This claim is about deterministic software and convention behavior only. It does
not validate or falsify Stefan-Boltzmann, Wien displacement, blackbody
radiation, stellar observations, or any textbook formula as empirical physics,
and it implies no universal-law statement.
