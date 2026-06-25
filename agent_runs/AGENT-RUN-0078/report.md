# FIRAS Wien-Peak Consistency Slice

- Task: `TASK-0802`
- Benchmark: `textbook-firas-wien-peak-consistency-slice`
- Verdict: `CONSISTENT_IN_SCOPE`
- Engine: `physics_lab/engines/textbook_wien_firas_peak.py` (version `0.1.0`)
- Scope: bounded spectral-domain consistency audit only; not a universal validation of Wien displacement, blackbody physics, or CMB physics.

## Reference

- Reference temperature `T_ref = 2.72548 K` (`Fixsen 2009, ApJ 707, 916`).
- Textbook wavelength-domain peak `lambda_peak = b / T = 1.0632 mm` (= 9.405 cm^-1).

## Primary metric (wavelength-domain, Jacobian applied)

| quantity | value |
| --- | --- |
| raw-bin peak | 1.0493 mm (9.53 cm^-1) |
| interpolated peak | 1.0642 mm |
| raw-bin relative difference | 0.01307 (tol 0.02) |
| interpolated relative difference | 0.00092 (tol 0.005) |

## Domain-conversion handling (reported separately)

- Jacobian: `B_lambda = B_nu * nu^2 / c (nu = c * k_m, lambda = 1 / k_m)`.
- Frequency-domain peak: 5.45 cm^-1 (163.4 GHz) — distinct from the wavelength-domain peak by the Planck Jacobian.
- No-Jacobian relabel control: 1.8349 mm (relative difference 0.7258) — correctly wrong.

## Controls

| control | passed |
| --- | --- |
| `absolute_product_gate` | `True` |
| `no_jacobian_relabel_rejected` | `True` |
| `frequency_domain_peak_distinct` | `True` |
| `wrong_temperature_rejected` | `True` |

## Limitations

- Single pinned FIRAS monopole product; one reference temperature.
- The reference temperature is FIRAS-derived, so this is a blackbody self-consistency check in scope, not independent validation.
- Sandbox evidence only; no canonical RESULT/CLAIM/KNOW/PRED is created.

## Output Routing

- Canonical destination: sandbox agent-run package plus `docs/reviews/` consistency note.
- Review tier: none (sandbox-only).
- Gate A: not attempted (sandbox-by-default).
- Gate B: not attempted.
- Claim impact: none. Knowledge impact: none.
