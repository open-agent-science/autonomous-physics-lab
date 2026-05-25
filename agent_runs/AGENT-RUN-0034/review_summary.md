# Review Summary

`AGENT-RUN-0034` audits the true-mass residual slice from the TASK-0361
exoplanet mass-radius benchmark.

The true-mass/transit-radius axis has 1207 eligible rows and beats the
per-class median null overall (`0.158170` CK log10 RMSE versus `0.242713`
null log10 RMSE). The audit keeps the overall verdict `INCONCLUSIVE` because
minimum-mass rows remain sparse and are not headline evidence.

Strongest supported failure surfaces:

- compact-radius rows: `0.263350` CK log10 RMSE on 92 rows;
- sub-Neptune-radius rows: `0.204175` CK log10 RMSE on 340 rows;
- neptunian mass-class rows: `0.182790` CK log10 RMSE on 588 rows;
- K-host rows: `0.197335` CK log10 RMSE on 235 rows.

Blocked or weak surfaces:

- minimum-mass rows: two rows, null beats CK;
- transit-timing rows: two rows;
- hot-host rows: fourteen rows;
- uncertainty-missing rows: eight rows.

No claims, canonical results, prediction entries, habitability outputs,
biosignature outputs, or target-priority outputs are authorized.
