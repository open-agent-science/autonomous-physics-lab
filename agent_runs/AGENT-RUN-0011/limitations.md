# AGENT-RUN-0011 Limitations

**Task:** `TASK-0201`
**Lane:** pairing and odd-even residual corrections
**Scope:** sandbox-only; configured range only

## Data Limitations

1. **NMD-0002 is a small curated slice (11 nuclides).** Structured-holdout
   coefficients are fitted on 8-9 rows. Pairing-class corrections that depend
   on nuclear parity (even-even, odd-odd, odd-A) are severely underdetermined
   because NMD-0002 contains only 1 odd-odd nucleus (N-14) and 2 odd-A nuclei
   (O-17, Fe-57).

2. **HYP-PROPOSAL-0038 odd-odd coefficient is a single-point fit.**
   In every holdout fold, the odd-odd indicator η_oo either has 1 training row
   (N-14 retained) or 0 training rows (N-14 removed). The resulting c_oo
   coefficient is unreliable. The OVERFITTED verdict is a direct consequence of
   this data structure, not a physics result.

3. **Post-AME2020 evaluation is retrospective.** Candidate coefficients are
   fitted on the full NMD-0002 training surface, then applied to the 295-row
   post-AME2020 holdout without any further tuning. This is not strict blind
   prediction; the holdout was constructed after the training data.

4. **HYP-PROPOSAL-0039 Wigner activation is near-zero on the holdout.** Of
   295 primary holdout rows, only 3 have N=Z. The Wigner correction is
   effectively dormant on the neutron-rich AME2020-era mass surface. The
   INCONCLUSIVE verdict reflects near-zero sensitivity, not a physically
   meaningful null result for the Wigner energy in general.

## Methodological Limitations

5. **Linear-in-coefficients protocol.** All correction families are restricted
   to linear residual corrections. Nonlinear pairing parameterizations (e.g.,
   a free pairing exponent) are out of scope and were rejected before execution.

6. **No uncertainty propagation on fitted coefficients.** Coefficient
   uncertainties are not reported; the small NMD-0002 sample size means all
   coefficients have large relative uncertainties that are not formally tracked.

7. **Split-sensitivity check not applicable.** Both executed candidates fail
   or produce near-null results on the primary structured holdout; no
   same-shape split replay was warranted given the clear failure modes.

## Scope Limitations

8. **Sandbox-only.** No canonical results, claims, hypotheses, accepted
   knowledge, or datasets are updated by this batch.

9. **Configured-range conclusions only.** Conclusions apply to the NMD-0002
   slice and the post-AME2020 primary holdout as configured. No universal claim
   is made about pairing corrections to semi-empirical mass formulas.

10. **No pairing theory connection.** The differential pairing and Wigner
    features are phenomeological residual corrections; no connection to a
    specific nuclear pairing Hamiltonian or shell-model calculation is claimed.
