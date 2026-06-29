# RESULT-0023 — FIRAS/Wien Spectral-Domain Peak Consistency Slice

- Experiment: EXP-0016 · Run: RUN-0001 · Hypothesis: HYP-0016 · Task: TASK-0845
- Review tier: AGENT_VALIDATED (agent-validated by independent replay; not maintainer-reviewed)
- Verdict: VALID_IN_RANGE (maps the run verdict CONSISTENT_IN_SCOPE)

## Headline

On the checksum-pinned COBE/FIRAS absolute monopole spectrum (43 rows), the
wavelength-domain spectral-radiance peak (after the declared `B_nu->B_lambda`
Jacobian) agrees with the textbook Wien reference `lambda_peak = b/T`:

- reference peak `b/T = 1.063215 mm`; raw-bin relative difference **0.013071** (tol 0.02);
  parabolic-refined **0.000917** (tol 0.005).
- All four predeclared controls pass (absolute-product gate, frequency-vs-wavelength
  distinctness, no-Jacobian-relabel rejection, wrong-temperature rejection).

## Scope / no-claim

This is a **FIRAS spectral-domain self-consistency** check on one pinned slice, **not**
independent validation or falsification of Wien displacement, blackbody/CMB physics, or
universal textbook truth. The reference temperature is itself a Planck fit to FIRAS
(circularity). No CLAIM/KNOW promotion.

## Gate B

Independent Gate B replay passed through the committed `physics-lab run` workflow. The replay reproduced 27 numeric RESULT fields within tolerance `1e-09`, with maximum absolute drift `9.275010772434589e-20`, and preserved `VALID_IN_RANGE`. This validates deterministic reproduction of `RESULT-0023`; it is still not maintainer endorsement or independent empirical validation of Wien displacement.

## Reproduce

```
physics-lab run examples/textbook_firas_wien_peak_consistency.yaml
```
Source evidence: `agent_runs/AGENT-RUN-0079/`, `docs/reviews/textbook-firas-wien-peak-consistency-slice.md`.
