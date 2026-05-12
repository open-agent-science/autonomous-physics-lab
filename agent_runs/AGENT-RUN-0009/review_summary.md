# Review Summary - AGENT-RUN-0009

Verdict: `SANDBOX_PASS` for the run.

Two continuous Gaussian shell-proximity candidates were executed:

- `HYP-PROPOSAL-0028` (Z+N): structured `OVERFITTED`; post-AME2020 primary
  delta MAE `+0.047 MeV` (regression).
- `HYP-PROPOSAL-0029` (N only): structured `OVERFITTED`; post-AME2020
  primary delta MAE `-0.062 MeV` (marginal improvement, with `+0.22 MeV`
  proton-rich subset regression).

Three further proposals were rejected before execution
(`HYP-PROPOSAL-0030` duplicate-strict-shell, `HYP-PROPOSAL-0031`
post-hoc-N=82-leakage, `HYP-PROPOSAL-0032` nonlinear-free-sigma).

Recommended action: keep both executed families as negative-control
sandbox evidence under `docs/nuclear-mass-robustness-gate.md`
(`ALLOW_ONLY_AS_NEGATIVE_CONTROL`). Do not promote, do not open a third
shell-aware batch from this run alone, and require a separate
maintainer-reviewed task before any broader-dataset follow-up. The lane
has produced useful diagnostic evidence: the dormant-feature failure mode
from `AGENT-RUN-0008` is no longer the operative limitation, but the
remaining structured-holdout instability and one-way subset trade prevent
any stronger reading.
