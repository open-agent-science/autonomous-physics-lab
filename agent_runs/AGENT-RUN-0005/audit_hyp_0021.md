# Audit Note - HYP-PROPOSAL-0021

## Scope

This note records an independent audit replay for `HYP-PROPOSAL-0021` against
the frozen `RESULT-0015` baseline and the stored `AGENT-RUN-0005` sandbox
evidence.

It does not promote any canonical result or claim.

## Replay Outcome

- The stored per-holdout `delta_mae_mev` values replay exactly from the frozen
  residual surface.
- The candidate still improves all four active holdout families used in the
  pilot package.
- The stored `VALID_IN_RANGE` sandbox verdict is reproducible as sandbox
  evidence only.

## Audit Caveat

The extra `odd_a` term is not uniformly informative across the whole pinned
slice.

It improves the selected pilot package by helping the two holdouts that expose
odd-A nuclei:

- `random_stratified` through `Fe-57`
- `oxygen_chain` through `O-17`

For the heavy magic and neutron-rich holdouts, `HYP-PROPOSAL-0021` matches the
simpler `HYP-PROPOSAL-0020` behavior exactly because those revealed subsets do
not activate the odd-A feature.

## Split-Sensitivity Summary

Audit replay over all `48` same-shape stratified random splits shows:

- `HYP-PROPOSAL-0021` improves baseline MAE on `28/48` splits
- it regresses on `13/48` splits
- it ties baseline MAE on `7/48` splits
- the pilot random split ranks `18/48` by `delta_mae_mev`, so it is not the
  most favorable possible same-shape split
- the odd-A extension beats `HYP-PROPOSAL-0020` on `18/48` splits and is never
  worse on this split family
- every gain over `HYP-PROPOSAL-0020` occurs when the revealed split contains
  `O-17` or `Fe-57`

This supports a conservative reading:

- the candidate is real enough to replay;
- it is not a pure artifact of one maximally lucky random split;
- but the apparent all-holdout success is still sensitive to which odd-A rows
  are revealed.

## Review Boundary

Treat `HYP-PROPOSAL-0021` as:

- stronger than the explicit negative control `HYP-PROPOSAL-0022`;
- a plausible follow-up candidate for maintainer review;
- still sandbox-only evidence until a canonical comparison task uses the same
  discipline on a broader pinned surface.
