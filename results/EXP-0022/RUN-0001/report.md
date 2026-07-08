# RESULT-0029: Quantum ZnSe No-Refit Contract Transfer

This AGENT_PUBLISHED result packages AGENT-RUN-0090 through a replayable `physics_lab.cli run` workflow.
The primary outcome is `FAIL_TO_CLEAR_PREDECLARED_MARGIN`: the transferred model beats the best control but misses the frozen 0.05 eV survival margin.

## Primary Judge

| Quantity | Value |
| --- | ---: |
| Transferred InP-to-ZnSe MAE | 0.099216320 eV |
| Best control (`per_material_mean`) MAE | 0.145800000 eV |
| Margin over best control | 0.046583680 eV |
| Required margin | 0.050000000 eV |

Frozen primary model:
`conf = 1.364819 * d^(-0.749421)`.

## Verdict

`INCONCLUSIVE`. The primary margin is positive but short by 0.00341632 eV. The reverse direction clears as a secondary diagnostic, but the TASK-0914 contract forbids using it to change the primary verdict.

## Output Routing

- Canonical destination: `results/EXP-0022/RUN-0001/result.yaml`.
- Review tier: `AGENT_PUBLISHED`.
- Gate A: passed by deterministic workflow, verification block, input hashes, and no-claim limitations.
- Gate B: pending independent replay.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: none for this AGENT_PUBLISHED result; maintainer review is still required for endorsement.
