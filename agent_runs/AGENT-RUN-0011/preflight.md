# AGENT-RUN-0011 Preflight

Task: `TASK-0201`

Lane: pairing and odd-even residual corrections

Status: `PASS`

## Checks

| Check | Status | Notes |
| --- | --- | --- |
| Campaign scope | PASS | `nuclear-mass-surface` is limited to sandbox residual work. |
| Proposal count | PASS | Five proposals were generated. |
| Execution cap | PASS | Two candidates were executed; three were rejected before execution. |
| Duplicate review | PASS | Executed candidates do not duplicate `HYP-PROPOSAL-0021`, `HYP-PROPOSAL-0022`, or the shell/neutron-rich lanes. |
| Leakage review | PASS | Per-chain and shell-interaction variants were rejected before execution. |
| Promotion boundary | PASS | No canonical result, claim, knowledge, experiment, or dataset artifact is modified. |

## Executed Candidates

- `HYP-PROPOSAL-0038`: odd-A residual offset.
- `HYP-PROPOSAL-0039`: even-even and odd-odd pairing-class offsets.

## Rejected Before Execution

- `HYP-PROPOSAL-0040`: free odd-even exponent on A.
- `HYP-PROPOSAL-0041`: per-chain odd-even correction stack.
- `HYP-PROPOSAL-0042`: pairing-class plus shell-closure interaction.

The preflight result permits sandbox execution only. It does not permit claim
promotion or canonical result updates.
