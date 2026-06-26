# FIRAS Wien-Peak Consistency Review Summary

- Task: `TASK-0802`
- Verdict: `CONSISTENT_IN_SCOPE`
- Wavelength-domain peak (interpolated): 1.0642 mm vs reference 1.0632 mm (relative difference 0.00092).
- Domain conversion handled with the explicit `B_lambda = B_nu * nu^2 / c` Jacobian; frequency-domain peak and no-Jacobian relabel reported separately as controls.
- All predeclared controls passed: `True`.
- Boundary: consistency-in-scope only; sandbox evidence; no canonical promotion and no universal Wien/blackbody claim.
