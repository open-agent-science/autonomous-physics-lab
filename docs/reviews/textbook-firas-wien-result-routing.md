# FIRAS/Wien Consistency Slice — Result Routing Summary (TASK-0845)

Routing record for packaging the TASK-0802 FIRAS/Wien spectral-domain consistency
slice (`agent_runs/AGENT-RUN-0079/`) as a scoped Gate A AGENT_PUBLISHED RESULT.

## Canonical destination

- Hypothesis: `hypotheses/HYP-0016-textbook-firas-wien-peak-consistency.yaml`
- Experiment: `experiments/EXP-0016-textbook-firas-wien-peak-consistency.yaml`
- Result: `results/EXP-0016/RUN-0001/result.yaml` (**RESULT-0023**)
- Gate A report: `results/EXP-0016/RUN-0001/gate_a_report.md`
- Source run/review (unchanged): `agent_runs/AGENT-RUN-0079/`, `docs/reviews/textbook-firas-wien-peak-consistency-slice.md`

## Status

| dimension | state |
|---|---|
| Gate A | **PASS** — `apl_check_result_publication.py` PASS, 9/9 gates True |
| Review tier | **AGENT_PUBLISHED** (not independently validated or maintainer-reviewed) |
| Verdict | **VALID_IN_RANGE** (maps the run verdict `CONSISTENT_IN_SCOPE`) |
| Gate B | **not attempted** — see workflow-repackaging follow-up below |
| Claim impact | **none** | Knowledge impact | **none** |

## Scientific content

Pinned COBE/FIRAS absolute monopole peak vs the Wien reference `lambda=b/T` (b CODATA
2022; T = 2.72548 K, Fixsen 2009, separately pinned): raw-bin relative difference
**0.013071** (tol 0.02), parabolic-refined **0.000917** (tol 0.005); 4/4 predeclared
controls pass. Frequency-domain peak (~163 GHz / 5.45 cm^-1) reported separately from the
wavelength-domain peak (~9.53 cm^-1), preserving Wien non-invariance.

## Framing guard-rails (held)

FIRAS spectral-domain **self-consistency** only — the reference T is itself a Planck fit to
FIRAS (circularity). **Not** independent validation/falsification of Wien displacement,
blackbody/CMB physics, cosmology, or universal textbook truth. No CLAIM/KNOW promotion.

## Gate B follow-up (flagged, not done here)

The provenance command is a standalone script
(`scripts/run_textbook_wien_firas_peak_consistency.py`), not a `physics-lab run` workflow,
so the Gate B validator cannot regenerate-and-compare it (the same `unsupported-command`
gap solved for Materials/Stellar by TASK-0786 / TASK-0799). A follow-up engine-workflow
repackaging is required before AGENT_VALIDATED; then a **different** agent runs Gate B.

## Reproduce

```
python3 scripts/run_textbook_wien_firas_peak_consistency.py --out-dir /tmp/firas-wien
python3 scripts/apl_check_result_publication.py results/EXP-0016/RUN-0001/result.yaml
```
