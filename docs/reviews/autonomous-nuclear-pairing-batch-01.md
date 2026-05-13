# Autonomous Nuclear Pairing Batch 01 Review

**Task:** `TASK-0201`
**Agent run:** `AGENT-RUN-0011`
**Scope:** pairing and odd-even residual corrections
**Claim boundary:** sandbox-only

## Summary

The TASK-0201 pairing lane generated five bounded proposals, executed two, and
rejected three before execution. The run is useful as negative and
split-sensitive evidence. It does not support claim promotion, canonical result
updates, or a follow-up batch from this lane alone.

## Executed Candidates

| Candidate | Structured verdict | Post-AME2020 primary delta | Gate reading |
| --- | --- | ---: | --- |
| `HYP-PROPOSAL-0038` odd-A offset | `PARTIALLY_VALID` | +0.0796 MeV | `BLOCK_PROMOTION` |
| `HYP-PROPOSAL-0039` pairing-class offsets | `OVERFITTED` | +0.0876 MeV | `ALLOW_ONLY_AS_NEGATIVE_CONTROL` |

## Rejected Before Execution

- `HYP-PROPOSAL-0040`: free odd-even exponent on A, rejected for nonlinear
  overfit risk on the 11-row training slice.
- `HYP-PROPOSAL-0041`: per-chain odd-even correction stack, rejected for
  leakage-sensitive chain targeting.
- `HYP-PROPOSAL-0042`: pairing-class plus shell-closure interaction, rejected
  for duplicating the shell-aware lane and adding sparse region switches.

## Robustness Gate

- outcome: `BLOCK_PROMOTION` for the lane as a source of positive follow-up
- baseline: frozen `RESULT-0015`
- active holdouts: NMD-0002 four-holdout protocol and post-AME2020 primary
- split-sensitivity summary: internal structured behavior is not enough;
  `HYP-PROPOSAL-0038` improves/ties internal holdouts but fails the harder
  time-split surface
- leakage review: leakage-sensitive rejected proposals are preserved
- complexity note: executed candidates are compact, but the two-parameter
  class-offset candidate still overfits
- negative control: `HYP-PROPOSAL-0039` and the three rejected proposals
- post-AME2020 status: both executed candidates regress primary MAE
- limitations: retrospective time-split evidence, not blind prediction

## Maintainer Notes

The pairing lane should remain sandbox evidence. A future task could revisit
pairing only after a broader pinned training surface exists, but this batch
does not justify expanding the current residual search.
