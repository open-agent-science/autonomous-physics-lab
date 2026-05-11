# TEC-005: Elevator Scenario — Verdict Mapping Proposal (Planning Only)

## Scenario

The Einstein elevator thought experiment: an observer inside a closed,
windowless elevator cannot distinguish between uniform gravitational
acceleration g (on Earth's surface) and constant upward acceleration a = g
(in empty space). This is the equivalence principle (local form).

## Proposed Assumption Map

| Assumption | Statement |
|---|---|
| A1 | Elevator is small: tidal effects negligible (L ≪ R_grav) |
| A2 | Acceleration is constant and spatially uniform within the elevator |
| A3 | No electromagnetic fields, rotation, or gravitational gradients |

## Proposed Check Map

| Check | Condition | Pass criterion |
|---|---|---|
| C1 | Newton's second law: F = ma | |F_measured − ma| < ε |
| C2 | Tidal effects below threshold | (∂g/∂x)·L ≪ g for elevator size L |
| C3 | Equivalence not exploitable | Gravitational gradient undetectable at scale L |

## Proposed Verdict Mapping

| Outcome | Verdict |
|---|---|
| C1 passes, C2 passes, C3 passes | VALID — local equivalence holds |
| C2 fails (tidal forces detectable) | INVALID — equivalence broken at this scale |
| C3 triggers (gradient detectable) | KNOWN_LIMIT_FAIL — local principle, not global |

## What Remains Out of First-Version Scope

- General relativistic curved spacetime
- Frame dragging and gravitomagnetic effects
- Equivalence principle at cosmological scales
- Quantum gravity corrections
- Any scenario where the equivalence principle must be tested non-locally

## Limitation Statement

Planning proposal only. No implementation exists. This verdict mapping is for
future design reference and requires maintainer review before adoption.
