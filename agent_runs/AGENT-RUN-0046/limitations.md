# AGENT-RUN-0046 Limitations

- NMD-0002 has 11 training rows; LOO coefficient stability has only 11 refit folds.
- Frozen baseline residuals are retrospective; this is not a blind prediction.
- The pairing-asymmetry interaction family is declared before the run and not retuned.
- Custom verdict vocabulary caps at BOUNDED_DIAGNOSTIC; no registry expansion is authorized regardless of outcome.
- Nuclear controls-first gauntlet (TASK-0333) remains in force; this lane does not reopen registry expansion.
- Verdict: `NEGATIVE_RESULT` (schema: `FALSIFIED`). See `report.md` rationale.
