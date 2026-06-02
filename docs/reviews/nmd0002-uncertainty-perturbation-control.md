# NMD-0002 Uncertainty Perturbation Control — Review (TASK-0518)

Review note for [AGENT-RUN-0054](../../agent_runs/AGENT-RUN-0054/report.md).
The control perturbs the committed NMD-0002 atomic masses and re-evaluates the
top TASK-0507 factory candidates against the frozen baseline.

## Result

- **Verdict:** `INCONCLUSIVE` sandbox control evidence.
- Declared uncertainty: `CAND-0001` remains top-ranked in 200/200 trials.
- 10x coarse-floor stress: `CAND-0001` remains top-ranked in 184/200 trials;
  `CAND-0037` becomes top-ranked in 16/200 trials.
- Route verdicts remain `INCONCLUSIVE` for all tracked candidates in both
  perturbation modes.

## Scientific Meaning

The committed uncertainty values do not erase the apparent TASK-0507 top
candidate ordering. The deliberately amplified coarse-floor stress does expose
rank fragility, but it still does not produce a shortlist or prediction-freeze
candidate. This preserves TASK-0507 as underpowered/control evidence rather
than promotion evidence.

## Output Routing

- **Canonical destination:** sandbox evidence in `agent_runs/AGENT-RUN-0054/`
  and this review note.
- **Review tier:** none.
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** NMD-0002 remains an 11-row control surface with a
  coarse curated uncertainty floor, not source-grade per-row uncertainty.

## Follow-Up

No candidate should be promoted from this control. Any renewed Nuclear factory
work should use the larger NMD-0003 surface or a future broad-surface frozen
baseline task rather than treating NMD-0002 perturbation survival as evidence.
