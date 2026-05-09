# Pendulum Gauntlet Replay Freeze

## Scope

This note records the `TASK-0135` audit of replay drift for the canonical
pendulum gauntlet runs:

- `EXP-0001/RUN-0003` (`RESULT-0004`) unconstrained 100-candidate gauntlet;
- `EXP-0001/RUN-0004` (`RESULT-0008`) physics-constrained follow-up;
- `EXP-0001/RUN-0005` (`RESULT-0013`) asymptotic-refined follow-up.

## Root Cause

`RUN-0003` and `RUN-0004` were generated with the original ten-atom gauntlet
basis:

`t2, t4, t6, t8, x1, x2, x3, x4, l1, l2`

Later `TASK-0110` added a standalone log atom `l0` and changed the default
core basis to eleven atoms:

`t2, t4, t6, t8, x1, x2, x3, x4, l0, l1, l2`

The gauntlet always evaluates exactly 100 deterministic candidates by
enumerating size-1, size-2, and then size-3 atom combinations. Adding `l0`
therefore did more than add one candidate: it changed which size-3 candidates
fit inside the first 100. Old configs did not record the intended basis, so
current-source replay silently used the newer candidate set and drifted away
from canonical `RUN-0003` and `RUN-0004` leaderboard invariants.

This was engine evolution without explicit versioning, not stochastic
instability.

## Prevention Rule

Canonical gauntlet configs must pin their candidate set:

- `gauntlet_atom_set: legacy_10` for `RUN-0003` and `RUN-0004`;
- default `gauntlet_atom_set: current_11` for newer runs unless they need a
  different reviewed freeze.

Future candidate-basis changes should create a new atom-set id or an explicit
rebaseline task. They should not alter replay semantics for existing canonical
configs.

## Replay Invariants

The regression coverage added for this audit checks:

- `legacy_10` still produces exactly 100 unique candidates;
- `RUN-0003` replay selects `model_t4_x1` with `VALID_IN_RANGE`;
- `RUN-0004` replay selects `model_t2_x4_l2` with `OVERFITTED`;
- replay result payloads record `gauntlet_candidate_set: legacy_10`.

## Maintainer Guidance

Treat gauntlet candidate-set changes as scientific-method changes, not only
implementation refactors. If the candidate basis changes, the review should
state whether the change creates a new run, a rebaseline, or a frozen replay
compatibility path.
