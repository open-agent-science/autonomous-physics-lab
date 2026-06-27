# RESULT-0023 — FIRAS/Wien Spectral-Domain Peak Consistency Slice

- Experiment: EXP-0016 · Run: RUN-0001 · Hypothesis: HYP-0016 · Task: TASK-0845
- Review tier: AGENT_PUBLISHED (agent-published; not independently validated)
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

Not attempted. The provenance command is a standalone script; an engine-workflow
repackaging (TASK-0786 / TASK-0799 pattern) is required so `physics-lab run` regenerates
the artifact, after which a different agent runs the independent replay.

## Reproduce

```
python3 scripts/run_textbook_wien_firas_peak_consistency.py --out-dir /tmp/firas-wien
```
Source evidence: `agent_runs/AGENT-RUN-0079/`, `docs/reviews/textbook-firas-wien-peak-consistency-slice.md`.
