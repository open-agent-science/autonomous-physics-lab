# MD-0002 Formation-Energy Baseline Benchmark

## Decision

`TASK-0703` is `REVIEW_READY`. The frozen MD-0002 formation-energy benchmark
returns `VALID_IN_RANGE` for the exact cation-pair mean on the committed
computed-DFT slice.

## Evidence

- Rows: 362 total; 253 train, 55 validation, 54 holdout.
- Best global null: global median, holdout MAE `0.506092` eV/atom.
- Best composition baseline: exact cation-pair mean, holdout MAE `0.200606`
  eV/atom.
- Improvement: `0.305486` eV/atom absolute and `0.603618` relative.
- Shuffle controls: real baseline beats all five seeds for both declared
  control families.
- Split sensitivity: cation-pair baseline wins all five seeds; mean margin
  `0.350085` eV/atom exceeds noise `0.015359` eV/atom.
- Row-order invariance: PASS.

## Interpretation

The result supports only a scoped benchmark statement: exact cation-pair
grouping is a strong train-only comparator for formation energy on this
checksum-pinned Materials Project stable ternary-oxide slice. It does not
establish a universal materials relation, experimental-property result, or
actionable material recommendation.

## Routing

- Agent run: `agent_runs/AGENT-RUN-0072/`
- Canonical destination: future task-authorized result packaging
- Review tier: none
- Gate A: blocked before packaging
- Gate B: not attempted
- Claim impact: none
- Knowledge impact: none
- Publication blocker: TASK-0703 does not authorize new protected
  `hypotheses/` or `experiments/` identities; a separate publication task is
  required
