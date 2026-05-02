---
id: REF-0001
title: Units and Dimensions Reference
type: reference
status: stable
domain: physics_reference
source: "SI 9th edition (BIPM 2019); NIST https://physics.nist.gov/cuu/Units/"
warning: >
  This file contains standard reference material from established physics
  literature (SI system, BIPM). These are not scientific claims made by this
  project. No original research is presented here.
---

# Units and Dimensions Reference

> **Reference data warning:** This file contains standard reference material
> from established physics literature (SI system, CODATA). These are not
> scientific claims made by this project. No original research is presented here.

---

## Base SI Dimensions

| Dimension | Symbol | SI Unit | Unit Symbol |
|-----------|--------|---------|-------------|
| Length | L | metre | m |
| Mass | M | kilogram | kg |
| Time | T | second | s |
| Electric current | I | ampere | A |
| Temperature | Θ | kelvin | K |
| Amount of substance | N | mole | mol |
| Luminous intensity | J | candela | cd |

---

## Common Derived Dimensions

### Mechanical

| Quantity | Dimension | SI Unit | Symbol |
|----------|-----------|---------|--------|
| Area | L² | square metre | m² |
| Volume | L³ | cubic metre | m³ |
| Velocity | L T⁻¹ | metre per second | m/s |
| Acceleration | L T⁻² | metre per second squared | m/s² |
| Force | M L T⁻² | newton | N |
| Pressure | M L⁻¹ T⁻² | pascal | Pa |
| Energy | M L² T⁻² | joule | J |
| Power | M L² T⁻³ | watt | W |
| Momentum | M L T⁻¹ | kilogram metre per second | kg·m/s |
| Angular momentum | M L² T⁻¹ | joule second | J·s |
| Torque | M L² T⁻² | newton metre | N·m |
| Frequency | T⁻¹ | hertz | Hz |
| Angular frequency | T⁻¹ | radian per second | rad/s |
| Period | T | second | s |

### Oscillation and Waves

| Quantity | Dimension | SI Unit | Symbol |
|----------|-----------|---------|--------|
| Amplitude | L | metre | m |
| Wavelength | L | metre | m |
| Wave number | L⁻¹ | radian per metre | rad/m |
| Phase | dimensionless | radian | rad |
| Damping coefficient | T⁻¹ | per second | s⁻¹ |
| Quality factor | dimensionless | — | — |

### Electromagnetic

| Quantity | Dimension | SI Unit | Symbol |
|----------|-----------|---------|--------|
| Electric charge | I T | coulomb | C |
| Electric potential | M L² T⁻³ I⁻¹ | volt | V |
| Capacitance | M⁻¹ L⁻² T⁴ I² | farad | F |
| Resistance | M L² T⁻³ I⁻² | ohm | Ω |
| Magnetic flux | M L² T⁻² I⁻¹ | weber | Wb |
| Magnetic field | M T⁻² I⁻¹ | tesla | T |

### Thermodynamic

| Quantity | Dimension | SI Unit | Symbol |
|----------|-----------|---------|--------|
| Temperature | Θ | kelvin | K |
| Heat / internal energy | M L² T⁻² | joule | J |
| Entropy | M L² T⁻² Θ⁻¹ | joule per kelvin | J/K |
| Specific heat capacity | L² T⁻² Θ⁻¹ | joule per kilogram kelvin | J/(kg·K) |

---

## Dimensionless Quantities

These quantities have no physical dimension. They appear frequently in
physics models and benchmark tasks.

| Quantity | Definition | Typical symbol |
|----------|------------|----------------|
| Angle (radian) | arc length / radius | θ, φ |
| Strain | ΔL / L | ε |
| Reynolds number | ρvL / μ | Re |
| Mach number | v / v_sound | Ma |
| Quality factor | ω₀ / (2γ) | Q |
| Reduced amplitude | θ / θ_max | — |

---

## Dimensional Analysis Notes

- A physically valid equation must be dimensionally homogeneous: both sides
  must have identical dimensions.
- Dimensionless combinations (like `sin(θ)` or `exp(−γt)`) are always valid
  regardless of unit system.
- When fitting a model formula, verify that all fitted coefficients carry the
  correct implied dimensions.
- The pendulum period ratio `T / T₀` is dimensionless by construction.

---

## References

- Bureau International des Poids et Mesures (BIPM). *The International System
  of Units (SI)*, 9th edition, 2019.
- NIST Reference on Constants, Units, and Uncertainty:
  https://physics.nist.gov/cuu/Units/
