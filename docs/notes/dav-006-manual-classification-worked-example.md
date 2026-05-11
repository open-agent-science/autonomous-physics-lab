# DAV-006: Manual Dimensional Classification — Stokes Drag Law

## Formula

F = 6π·η·r·v

where:
- F = drag force [N] = [kg·m·s⁻²] = [M·L·T⁻²]
- η = dynamic viscosity [Pa·s] = [kg·m⁻¹·s⁻¹] = [M·L⁻¹·T⁻¹]
- r = sphere radius [m] = [L]
- v = velocity [m·s⁻¹] = [L·T⁻¹]
- 6π = dimensionless

## SI Base Dimension Trace

LHS: F → [M¹·L¹·T⁻²]

RHS: η·r·v → [M·L⁻¹·T⁻¹]·[L]·[L·T⁻¹]
           = [M·L⁻¹⁺¹⁺¹·T⁻¹⁻¹]
           = [M¹·L¹·T⁻²]

LHS = RHS → **Verdict: VALID**

## What This Example Tests

- Cross-term cancellation: η carries L⁻¹ which is cancelled by r·v carrying L².
- Mixed M·L·T product — the viscosity dimension [M·L⁻¹·T⁻¹] is non-obvious.

## What This Example Does NOT Test

- Dimensionless coefficient 6π: pure number, does not affect verdict.
- Physical correctness: Stokes drag assumes laminar flow (Re ≪ 1), no-slip
  boundary condition, and incompressible fluid. Dimensional balance does not
  validate these physical assumptions.
- No automated validator was run against this example.

## Limitation Statement

Manual trace only. A single worked example does not demonstrate full validator
coverage. All domains are not covered by this note.
