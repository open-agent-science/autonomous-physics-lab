# Textbook Wien/FIRAS Temperature And Domain Contract

Task: `TASK-0815`

Verdict: `WIEN_TEMPERATURE_DOMAIN_CONTRACT_READY_FOR_TASK_0802`

## Purpose

This note closes the remaining pre-metric contract for the empirical
Textbook Formula Audit Wien/FIRAS slice. It pins the temperature provenance,
the spectral-domain rule, the controls, and the admissible verdicts that
`TASK-0802` must use.

No Wien peak residual was computed. No blackbody spectrum was fit. No
`RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact was created.

## Inputs

- FIRAS source artifact:
  `data/textbook_formula_audit/wien_firas/source_artifacts/cobe-firas-monopole/firas_monopole_spec_v1.txt`
- Normalized FIRAS rows:
  `data/textbook_formula_audit/wien_firas/firas_monopole_rows.yaml`
- Source-pinning review:
  `docs/reviews/textbook-wien-firas-source-pinning.md`
- Source-route review:
  `docs/reviews/textbook-wien-firas-source-artifact.md`

The committed FIRAS rows are an absolute monopole spectrum on the native
wavenumber/frequency axis. The residual column remains diagnostic only and is
not the audited ordinate.

## Reference Temperature

`TASK-0802` must use the literature-combined Fixsen 2009 CMB temperature
reported in the source-route review:

- `T_ref = 2.72548 K`
- `sigma_T = 0.00057 K`
- source citation: Fixsen 2009, ApJ 707, 916
- provenance role: separately cited reference temperature, not a fitted
  parameter chosen from the committed FIRAS rows

The alternative FIRAS-recalibrated value noted in the route review
(`2.7260 +/- 0.0013 K`) is reserved for a sensitivity appendix only. It must
not be substituted as the primary reference after seeing metric output.

If a later maintainer decides that the Fixsen 2009 source itself must be
committed as a value-bearing artifact before metrics, `TASK-0802` should stop
with `WIEN_TEMPERATURE_DOMAIN_CONTRACT_BLOCKED` rather than choosing a
temperature ad hoc.

## Domain Contract

The primary audit is wavelength-domain Wien displacement:

```text
lambda_peak = b / T_ref
```

where `b` is the frozen CODATA/NIST wavelength displacement constant already
used by the Textbook Wien exact-reference fixture. The empirical FIRAS product
is on a native frequency/wavenumber axis, so `TASK-0802` must convert the
audited ordinate before locating a wavelength-domain peak.

Required conversion:

```text
nu = c * k
lambda = 1 / k
B_lambda(lambda) = B_nu(nu) * c / lambda^2
```

Here `k` is the native wavenumber in inverse metres after converting the
committed `cm^-1` axis. Equivalent algebra using `B_lambda = B_nu * nu^2 / c`
is acceptable if the unit conversion is explicit and tested.

The frequency-domain peak is a control surface, not the target metric. A
bare axis relabel from wavenumber to wavelength without the Jacobian is the
predeclared wrong-domain control.

## Controls For TASK-0802

`TASK-0802` must pre-run these deterministic controls before interpreting the
primary metric:

1. `absolute_product_gate`: fail if the committed product is treated as
   residual-only or model-normalized.
2. `no_jacobian_axis_relabel_control`: fail the consistency check when the
   axis is relabelled without the `B_nu -> B_lambda` Jacobian.
3. `frequency_domain_control`: report the native frequency/wavenumber-domain
   peak separately and require it to differ from the wavelength-domain target.
4. `sampling_resolution_control`: compare raw-bin maximum against a declared
   local interpolation or fit near the converted peak.
5. `wrong_temperature_control`: reject an intentionally offset reference
   temperature.
6. `unit_roundtrip_control`: test `cm^-1 -> m^-1 -> Hz -> m` conversions.
7. `circularity_caveat`: state that a FIRAS-derived temperature makes the
   audit a blackbody self-consistency check, not independent empirical proof
   of Wien displacement.

## Admissible Verdicts

`TASK-0802` may return only these scoped verdicts:

- `CONSISTENT_IN_SCOPE`
- `DOMAIN_CONVERSION_MISMATCH`
- `INCONCLUSIVE_PRODUCT_SEMANTICS`
- `INCONCLUSIVE_SAMPLING_RESOLUTION`
- `WIEN_TEMPERATURE_DOMAIN_CONTRACT_BLOCKED`

A positive result must be described as a FIRAS spectral-domain consistency
audit. It must not be described as a universal validation of Wien displacement,
blackbody physics, CMB physics, or textbook formula truth.

## TASK-0802 Readiness

`TASK-0802` is ready to run the deterministic metric if it consumes exactly
the committed FIRAS rows, the `T_ref` value above, and the domain/control
contract above. It remains blocked for any workflow that would fetch live data,
choose a different temperature after seeing metrics, fit the blackbody
spectrum as part of the audit, or omit the Jacobian mismatch control.

## Output Routing

- Task verdict: `not_applicable` for formula validity; source/metric-contract
  verdict `WIEN_TEMPERATURE_DOMAIN_CONTRACT_READY_FOR_TASK_0802`.
- Canonical destination: `docs/reviews/` source/metric readiness note.
- Review tier: `none`.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: none.
- Knowledge impact: none.
- Remaining blocker: only maintainer policy, if a separately committed
  Fixsen 2009 source artifact is required before the metric task.
