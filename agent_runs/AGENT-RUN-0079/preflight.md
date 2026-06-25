# Preflight

- Task: `TASK-0802`
- `committed_inputs_only`: consumed the checksum-pinned FIRAS rows and the frozen Wien exact-reference fixture; no live fetch, no source re-pin.
- `temperature_pinned_upstream`: used the TASK-0815 reference temperature `2.72548 K`; not chosen after seeing output.
- `domain_conversion_declared`: applied the `B_lambda = B_nu * nu^2 / c` Jacobian before locating the wavelength peak; no-Jacobian relabel kept as a negative control.
- `no_fitted_free_parameters`: no blackbody fit; the parabolic refinement is a fixed deterministic interpolation.
- `single_evaluation`: one consistency metric; no added bins or spectra.
