# AGENT-RUN-0045 Limitations

- NMD-0002 has 11 training rows; LOO coefficient stability has only 11 refit folds.
- Frozen baseline residuals are retrospective; this is not a blind prediction.
- Gaussian width (two-sigma^2 = 8) is declared before the run and not retuned.
- Custom verdict vocabulary caps at SHELL_ADJACENT_DIAGNOSTIC; no registry expansion is authorized regardless of outcome.
- Shell-axis post-audit decision (TASK-0333) remains in force; this lane does not reopen registry expansion.
- Verdict: `NEGATIVE_RESULT` (schema: `FALSIFIED`). See `report.md` rationale.
