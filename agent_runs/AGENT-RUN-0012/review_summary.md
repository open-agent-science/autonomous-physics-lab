# AGENT-RUN-0012 Review Summary

The shell-neighborhood scout generated nine bounded candidates. Six were
executed; three were rejected before execution for leakage or overfit risk.

Primary aggregate MAE baseline on the pinned post-AME2020 holdout is
`4.552568580201034 MeV`.

Executed candidate outcomes:

- `SHELL-SCOUT-001`: `OVERFITTED`, primary delta `+0.046661 MeV`.
- `SHELL-SCOUT-002`: `PARTIALLY_VALID`, primary delta `-0.061969 MeV`.
- `SHELL-SCOUT-003`: `PARTIALLY_VALID`, primary delta `-0.091504 MeV`.
- `SHELL-SCOUT-004`: `OVERFITTED`, primary delta `+0.072127 MeV`.
- `SHELL-SCOUT-005`: `PARTIALLY_VALID`, primary delta `-0.071641 MeV`.
- `SHELL-SCOUT-006`: `INCONCLUSIVE`, near-null control with zero deltas.

The result is useful as scout triage only. It should not be converted into a
registry entry, result artifact, or claim without a separate reviewed task.
