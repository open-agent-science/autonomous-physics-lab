# AGENT-RUN-0043 Limitations

- NMD-0002 has 11 training rows; per-cluster leave-one-out can be sparse for small cells.
- Frozen baseline residuals are retrospective; this is not a blind prediction.
- The cluster taxonomy is fixed before the run and may not exhaust useful residual-free partitions.
- The post-AME2020 primary holdout has limited cluster coverage; some cluster verdicts are dominated by training_loo behavior alone.
- Matched-random and smooth-A controls are decisive for interpretation; the candidate may not survive both.
- Verdict: `INCONCLUSIVE`. See `report.md` rationale.
