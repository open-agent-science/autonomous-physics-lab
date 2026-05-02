# Pendulum Gauntlet 100 — Short Summary

## Headline

APL evaluated 100 deterministic candidate formulas for the ideal pendulum
period ratio and produced a reproducible, range-aware result package rather
than a one-off approximation claim.

## Five Key Points

- The benchmark tested 100 deterministic formulas against the exact
  elliptic-integral reference for the ideal pendulum period ratio.
- The top leaderboard candidate was `model_t4_x1`, validated in the configured
  range with about `3.1e-4` mean relative residual on the test split.
- A separate precision audit classified that `~3.1e-4` scale as model
  residual, not numerical reference noise.
- All candidates remained range-limited: the near-separatrix diagnostic checks
  still fail for the leaderboard winner and for the broader gauntlet.
- No symbolic exactness claim and no global validity claim are made.

## Key Numbers

| Item | Value |
| --- | --- |
| Result | `RESULT-0004` |
| Run | `RUN-0003` |
| Candidates tested | `100` |
| Top leaderboard model | `model_t4_x1` |
| Top leaderboard test mean residual | `3.0524596412228103e-04` |
| Top leaderboard test max residual | `9.480571262666894e-04` |
| Precision-audit classification | `model_residual` |
| Verdict summary | `32 VALID`, `8 PARTIALLY_VALID`, `60 OVERFITTED` |

## Important Nuance

The leaderboard winner is chosen by composite score, which includes complexity.
Some 3-term models achieved lower raw test residuals than `model_t4_x1`, but
ranked lower once complexity was penalized. The safest external wording is
"top leaderboard candidate" or "best composite-score candidate."

## Canonical Artifacts

- [result.yaml](../../results/EXP-0001/RUN-0003/result.yaml)
- [leaderboard.md](../../results/EXP-0001/RUN-0003/leaderboard.md)
- [metrics.json](../../results/EXP-0001/RUN-0003/metrics.json)
- [precision_audit.md](../../results/EXP-0001/RUN-0003/precision_audit.md)
- [report.md](../../results/EXP-0001/RUN-0003/report.md)
- [pendulum-gauntlet-100.md](../notes/pendulum-gauntlet-100.md)

## Limitations

- ideal pendulum only;
- fixed train/test split;
- fixed atom basis;
- linear-in-coefficients candidates only;
- no symbolic exactness claim;
- no global validity claim;
- separatrix behavior remains unresolved.
