# Agent Research Log

This log records compact, repository-facing summaries of agent research runs.
It is not a claim registry. Entries here should point to reviewable artifacts
and preserve limitations.

## Nuclear Mass Pilot Evidence Funnel

**Task:** `TASK-0174`
**Source run:** `AGENT-RUN-0005`
**Replay run:** `AGENT-RUN-0006`
**Status:** sandbox-only evidence summary

The first nuclear-mass autonomous pilot generated `8` residual hypotheses,
rejected `5` before execution, executed `2` positive or comparator sandbox
candidates plus `1` overfit negative control, and promoted `0` claims.

The strongest pilot candidate, `HYP-PROPOSAL-0021`, improved all active pilot
holdouts in `AGENT-RUN-0005`. The split replay in `AGENT-RUN-0006` found
`28/48` improved same-shape splits, `13/48` regressed splits, and `7/48` ties.
That makes the result useful as guarded sandbox evidence and insufficient for
claim promotion.

Repository-facing artifact:

- [Nuclear Mass Pilot Evidence Summary](./results/nuclear-mass-pilot-summary.md)
- [Nuclear Mass Pilot Evidence Card Review](./reviews/nuclear-mass-pilot-evidence-card-review.md)
