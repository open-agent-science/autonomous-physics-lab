# DAV-011 Pressure-Work Assumption Boundary

**Run:** `MICROTASK-RUN-0037`
**Run verdict:** `REVIEW_NEEDED`
**Curated item classification:** `SUSPICIOUS`

## Input

The boundary item is:

`E = p * V`

with `E` in joules, `p` in pascals, and `V` in cubic metres.

## Label-Blind Dimensional Method

`physics_lab.engines.dimensions.infer_item` was called with only the formula
and variable dimensions:

- `[E] = J = M L^2 T^-2`
- `[p] = Pa = M L^-1 T^-2`
- `[V] = m^3 = L^3`
- `[pV] = M L^2 T^-2`

The engine returned:

- computed verdict: `VALID`
- detail: `LHS = RHS = M L^2 T^-2`
- warnings: none

That is the correct dimensional result.

## Physical-Assumption Review

The unqualified equation is not a general pressure-work or energy law.
Boundary work is normally

`W = integral(p_external dV)`.

It reduces to `W = p_external * Delta V` only for a constant external pressure
over the stated volume change, with an explicit sign convention. Replacing
`Delta V` by a current-state volume `V`, or identifying arbitrary energy `E`
with `pV`, silently drops the process path and thermodynamic model.

The item is therefore **SUSPICIOUS**, not dimensionally invalid: dimensions
balance, while the physical interpretation requires assumptions not present in
the formula.

## Boundary And Failure Mode

- `INVALID`: dimensions do not balance or the expression cannot represent the
  declared quantity even before physical assumptions are considered.
- `SUSPICIOUS`: dimensions balance, but a missing process, limit, or semantic
  assumption can make an unqualified physical reading unsafe.

The failure mode is conflating the engine's `VALID` output with physical
correctness. This example is intentionally left for human review because the
label-blind v2 engine does not consume curated semantics.

## Novelty And Limitations

The previous `DAV-011` run tested missing area in a fluid-power expression and
produced an explicit dimensional mismatch. This attempt instead tests a
dimensionally balanced pressure-work boundary. It is one thermodynamic example;
it does not change the canonical challenge set, settle all `SUSPICIOUS`
semantics, or imply that dimensional analysis validates thermodynamic models.

## Output Routing

- Destination: this boundary note and `MICROTASK-RUN-0037`.
- Gate A / Gate B: not attempted.
- Result, claim, and knowledge impact: none.
- Publication blocker: human judgment is required for the curated
  `SUSPICIOUS` classification.
