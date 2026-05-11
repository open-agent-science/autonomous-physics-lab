# TEC-003: Twin Paradox Simplified Model — Parameter Domain Note

## Simplified Model

One twin stays in inertial frame S. The other travels at constant velocity v
to distance d, then instantaneously reverses and returns at velocity v.

- Traveller elapsed time: T_traveller = 2d/(γv)
- Stay-at-home elapsed time: T_stay = 2d/v
- Time dilation: T_traveller = T_stay / γ < T_stay for v > 0

## Turnaround Idealization

The "instantaneous reversal" is a deliberate simplification. In a physical
scenario the turnaround requires a finite acceleration phase. This model treats
the turnaround as a zero-duration impulse, removing the need for accelerated-
frame analysis or general relativity within the simplified model.

## Allowed Parameter Domain

| Parameter | Allowed range | Reason |
|---|---|---|
| v | (0, c) exclusive | v = 0 is degenerate; v ≥ c is undefined |
| d | d > 0 | d = 0 means no trip |
| γ | (1, ∞) | Follows from v ∈ (0, c) |

## Undefined or Degenerate Values

- **v = 0:** γ = 1, both twins age equally. Degenerate — no time dilation.
- **v ≥ c:** γ becomes imaginary or diverges. Physically undefined.
- **d → 0:** trip duration → 0, no resolution power.
- **Acceleration phase:** intentionally excluded. The simplified model does
  not cover the turnaround physics; the result is valid only for the inertial
  legs of the journey.

## Why the Asymmetry Is Resolved

The situation is NOT symmetric between the twins: the traveller changes inertial
frames at the turnaround (even in the idealized model, the impulse breaks time-
reversal symmetry). The stay-at-home twin remains in one inertial frame
throughout. This asymmetry resolves the apparent paradox.

## Limitation Statement

The time dilation result T_traveller < T_stay is robust within the allowed
domain. The acceleration phase is explicitly excluded; general-relativistic
treatment of the turnaround is out of scope.
