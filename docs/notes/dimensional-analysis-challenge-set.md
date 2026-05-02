# Dimensional Analysis Challenge Set — Planning Document

Task: `TASK-0017`  
Type: `benchmark_planning`  
Domain: `physics_validation`  
Status: planning only — no implementation yet

---

## Purpose

This document covers all four required outputs for TASK-0017:

1. [Task spec](#task-spec) — scope and constraints
2. [Challenge-set plan](#challenge-set-plan) — benchmark design
3. [Formula category inventory](#formula-category-inventory) — 50 labelled formulas
4. [Future public-result angle](#future-public-result-angle) — path to a visible result

The machine-readable dataset is at:
`knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`

---

## Task Spec

### Goal

Define a benchmark challenge set where APL can be evaluated on its ability to
detect dimensionally invalid, physically suspicious, or unit-inconsistent
physics formulas using deterministic symbolic checks.

This is a *validation* benchmark: the ground truth is whether a formula is
dimensionally consistent with stated assumptions, not whether it fits data.

### Scope

- SI base units: length (m), time (s), mass (kg), current (A),
  temperature (K), amount (mol), luminous intensity (cd).
- Five physics domains: mechanics, electromagnetism, thermodynamics,
  waves/optics, statistical physics.
- Five formula categories (see inventory).
- No quantum field theory, natural units, or Planck units in v1.

### Non-goals for this planning task

- No implementation of a symbolic checker.
- No new Python modules, schemas, workflows, or result artifacts.
- No new hypotheses, experiments, claims, or knowledge files.

### Scientific constraints

- Every formula must have an unambiguous verdict (`VALID`, `INVALID`,
  `SUSPICIOUS`, or `KNOWN_LIMIT_FAIL`) derivable by SI dimensional analysis
  and known-limit reasoning alone.
- Verdicts must not depend on numerical values — only on unit structure or
  well-known physical limits.
- A `SUSPICIOUS` formula is dimensionless but physically nonsensical.
- A `KNOWN_LIMIT_FAIL` formula is dimensionally valid but violates a
  well-established physical limit (e.g. v > c, T < 0).

---

## Challenge-Set Plan

### Benchmark identity

Proposed future experiment: `EXP-0004`  
Proposed implementation task: new `TASK-EXP-0004-*`

### Formula record schema

Each challenge entry contains:

| Field | Description |
|---|---|
| `id` | unique identifier, e.g. `DA-001` |
| `name` | human-readable label |
| `domain` | physics sub-field |
| `formula` | expression as a string |
| `variables` | symbol → SI dimension mapping |
| `expected_verdict` | `VALID`, `INVALID`, `SUSPICIOUS`, `KNOWN_LIMIT_FAIL` |
| `failure_mode` | how the formula fails (if not VALID) |
| `check_type` | `dimensional` or `known_limit` |
| `difficulty` | `easy`, `medium`, `hard` |
| `reason` | brief explanation |

### Verdict vocabulary

| Verdict | Meaning |
|---|---|
| `VALID` | LHS and RHS dimensions match exactly |
| `INVALID` | LHS and RHS dimensions do not match |
| `SUSPICIOUS` | dimensionless but physically meaningless |
| `KNOWN_LIMIT_FAIL` | dimensionally valid but violates a known physical limit |

### Relation to existing infrastructure

- `VerificationCheck` — each formula check maps directly onto this type
- `physics_lab/engines/symbolic.py` — existing SymPy integration is the
  natural base for a future dimensional parser
- result artifacts — same `result.yaml` / `report.md` / `metrics.json`
  layout; no schema changes required

---

## Formula Category Inventory

### Category 1 — Valid formulas (10 items, expected: all VALID)

Correct textbook formulas. A checker must pass these without false positives.

| ID | Name | Domain | Formula | Key dimension check |
|---|---|---|---|---|
| DA-001 | Newton's second law | mechanics | `F = m * a` | kg·m·s⁻² both sides |
| DA-002 | Kinetic energy | mechanics | `E = (1/2) * m * v**2` | kg·m²·s⁻² |
| DA-003 | Gravitational potential energy | mechanics | `U = m * g * h` | kg·m²·s⁻² |
| DA-004 | Ohm's law | electromagnetism | `V = I * R` | kg·m²·s⁻³·A⁻¹ |
| DA-005 | Ideal gas law | thermodynamics | `p * V = n * R_gas * T` | kg·m²·s⁻² both sides |
| DA-006 | Lorentz time dilation | mechanics/SR | `t_prime = t / sqrt(1 - v**2/c**2)` | s |
| DA-007 | Power | mechanics | `P = F * v` | kg·m²·s⁻³ |
| DA-008 | Wave speed | waves | `v_wave = f * lambda` | m·s⁻¹ |
| DA-009 | Stefan-Boltzmann radiated power | thermodynamics | `P = sigma * A * T**4` | kg·s⁻³·m² → W |
| DA-010 | Boltzmann entropy | statistical physics | `S = k_B * ln(Omega)` | kg·m²·s⁻²·K⁻¹ (J/K) |

### Category 2 — Invalid unit formulas (15 items, expected: all INVALID)

Formulas with unit errors — missing factor, wrong exponent, or swapped
variable. A checker must reject all of them.

| ID | Name | Domain | Broken formula | Failure mode |
|---|---|---|---|---|
| DA-101 | Force without acceleration | mechanics | `F = m` | missing s⁻² |
| DA-102 | Energy with wrong velocity power | mechanics | `E = m * v` | v not squared; kg·m·s⁻¹ ≠ kg·m²·s⁻² |
| DA-103 | Ohm's law with missing R | electromagnetism | `V = I` | missing Ω (kg·m²·s⁻³·A⁻²) |
| DA-104 | Pressure with area in numerator | mechanics | `p = F * A` | area should divide; kg·m³·s⁻² ≠ kg·m⁻¹·s⁻² |
| DA-105 | Gravitational force missing r² | mechanics | `F = G * m1 * m2` | missing m⁻²; units: m³·kg·s⁻² |
| DA-106 | Power as force only | mechanics | `P = F` | missing velocity; kg·m·s⁻² ≠ kg·m²·s⁻³ |
| DA-107 | Momentum confused with energy | mechanics | `p = m * v**2` | kg·m²·s⁻² ≠ kg·m·s⁻¹ |
| DA-108 | Charge times field as energy | electromagnetism | `E = q * E_field` | q·E = force (kg·m·s⁻²), not energy |
| DA-109 | Temperature as mass times velocity | thermodynamics | `T = m * v` | K ≠ kg·m·s⁻¹ |
| DA-110 | Current as charge squared | electromagnetism | `I = q**2 / t` | A ≠ C²·s⁻¹ |
| DA-111 | Wavelength as frequency | waves | `lambda = f` | m ≠ s⁻¹ |
| DA-112 | Gravitational PE missing g | mechanics | `U = m * h` | kg·m ≠ kg·m²·s⁻² |
| DA-113 | Ideal gas law missing R | thermodynamics | `p * V = n * T` | kg·m²·s⁻² ≠ mol·K |
| DA-114 | Magnetic force missing B | electromagnetism | `F = q * v` | C·m·s⁻¹ ≠ kg·m·s⁻² |
| DA-115 | Wien's law without constant | thermodynamics | `lambda_max = T` | m ≠ K |

### Category 3 — Formulas with missing constants (10 items, expected: all INVALID)

Conceptually correct but missing a required dimensional constant.

| ID | Name | Domain | Broken formula | Missing constant |
|---|---|---|---|---|
| DA-201 | Gravitational force without G | mechanics | `F = m1 * m2 / r**2` | G (m³·kg⁻¹·s⁻²) |
| DA-202 | Coulomb force without k_e | electromagnetism | `F = q1 * q2 / r**2` | k_e (kg·m³·s⁻⁴·A⁻²) |
| DA-203 | Photon energy without h | waves/QM | `E = f` | h (kg·m²·s⁻¹) |
| DA-204 | Stefan-Boltzmann without sigma | thermodynamics | `P = A * T**4` | σ (kg·s⁻³·K⁻⁴) |
| DA-205 | Magnetic field without mu_0 | electromagnetism | `B = I / r` | μ₀ (kg·m·s⁻²·A⁻²) |
| DA-206 | Wien's law without b | thermodynamics | `lambda_max = 1 / T` | b (m·K) |
| DA-207 | Biot-Savart without mu_0 | electromagnetism | `B = I * dl / r**2` | μ₀/4π |
| DA-208 | Thermal de Broglie without h | statistical physics | `lambda = 1 / sqrt(m * k_B * T)` | h (kg·m²·s⁻¹) |
| DA-209 | Escape velocity without G | mechanics | `v_esc = sqrt(M / r)` | G (m³·kg⁻¹·s⁻²) |
| DA-210 | Electric field without k_e | electromagnetism | `E_field = q / r**2` | k_e |

### Category 4 — Dimensionless but suspicious (10 items, expected: VALID or SUSPICIOUS)

Includes both legitimate dimensionless ratios (calibration) and physically
meaningless ones. The checker must distinguish them.

| ID | Name | Domain | Formula | Expected | Why |
|---|---|---|---|---|---|
| DA-301 | Mach number | fluid mechanics | `Ma = v / v_sound` | VALID | standard dimensionless ratio |
| DA-302 | Lorentz beta factor | SR | `beta = v / c` | VALID | standard SR ratio |
| DA-303 | Ratio of two energies | any | `r = E1 / E2` | VALID | generic dimensionless ratio |
| DA-304 | Mixing mass with time | — | `r = m / t` | INVALID | kg·s⁻¹, not dimensionless |
| DA-305 | Gravity-to-EM force ratio | mechanics/EM | `r = (G*m1*m2) / (k_e*q1*q2)` | VALID | physically meaningful comparison |
| DA-306 | Reynolds mimic with temperature | fluid mechanics | `Re_fake = rho * L * T / mu` | SUSPICIOUS | T (K) in place of velocity breaks physics |
| DA-307 | Fine structure constant mimic | QM | `alpha_fake = e**2 / (h_bar * c * m_e)` | SUSPICIOUS | extra m_e in denominator; real α has no mass |
| DA-308 | Mass over charge | — | `r = m / q` | INVALID | kg·A⁻¹·s⁻¹, not dimensionless |
| DA-309 | Reynolds number | fluid mechanics | `Re = rho * v * L / mu` | VALID | standard dimensionless ratio |
| DA-310 | Mixing incompatible ratios | — | `r = (v/c) / (m/kg)` | SUSPICIOUS | second ratio is trivially 1 with no physics |

### Category 5 — Dimensionally valid but known-limit violations (5 items, expected: KNOWN_LIMIT_FAIL)

Formulas that pass dimensional analysis but violate a well-established
physical constraint.

| ID | Name | Domain | Formula / Condition | Violated limit |
|---|---|---|---|---|
| DA-401 | Superluminal velocity | SR | `v > c` applied in `E = m*c**2 / sqrt(1-v**2/c**2)` | v < c required; γ becomes imaginary |
| DA-402 | Negative absolute temperature | thermodynamics | `S = n * R * ln(V) + ... ` with `T < 0` in ideal gas | T ≥ 0 K by third law (in classical regime) |
| DA-403 | Negative mass | mechanics | `F = m * a` with `m < 0` | mass is non-negative in classical mechanics |
| DA-404 | Speed of sound exceeds c | waves | `v_sound > c` in `Ma = v / v_sound` | v_sound < c always |
| DA-405 | Energy below ground state | statistical physics | `E < 0` for kinetic energy `E = p**2 / (2m)` | kinetic energy is non-negative |

### Summary

| Category | Count | Expected verdicts |
|---|---|---|
| Valid formulas | 10 | all VALID |
| Invalid unit formulas | 15 | all INVALID |
| Missing constants | 10 | all INVALID |
| Dimensionless / suspicious | 10 | mixed VALID / SUSPICIOUS / INVALID |
| Known-limit violations | 5 | all KNOWN_LIMIT_FAIL |
| **Total** | **50** | — |

---

## Future Public-Result Angle

### What makes this result public-facing

A dimensional analysis checker run over 50 formulas with a verifiable
classification rate is a concrete, falsifiable, reproducible result:

- not speculative — it catches a real, well-defined class of physics errors;
- explainable to a non-specialist (wrong units = wrong formula);
- sets a quality floor that future formula-discovery results must meet.

### Proposed public framing

> APL's dimensional verifier correctly classified all 50 formulas in the
> challenge set: 10 VALID, 25 INVALID (unit errors or missing constants),
> 10 dimensionless (3 SUSPICIOUS flagged for review), and 5 KNOWN_LIMIT_FAIL.
> Zero false positives on the valid set.

### Path to a public result

| Step | Output |
|---|---|
| 1. Implement `physics_lab/engines/dimensional.py` | symbolic SI checker using SymPy |
| 2. Add `EXP-0004` experiment and `HYP-0003` hypothesis files | |
| 3. Run checker over all 50 formulas | `results/EXP-0004/RUN-0001/` |
| 4. Produce standard artifacts | `result.yaml`, `report.md`, `metrics.json` |
| 5. Run `validate-repo --strict` | confirm no regressions |
| 6. Write `CLAIM-0003` | narrow claim about classification accuracy |
| 7. Maintainer review | do not auto-promote claim |

### Limitations to disclose

- Challenge set is manually curated; it covers known failure modes, not an
  exhaustive sampling of all possible errors.
- The checker requires known variable→dimension mappings; it cannot infer
  dimensions from variable names alone.
- `SUSPICIOUS` verdicts require human review; the checker flags but does not
  condemn.
- Natural-unit formulas (ℏ = c = 1) will appear INVALID under SI — out of
  scope for v1.
- `KNOWN_LIMIT_FAIL` checks require domain knowledge beyond dimensional
  analysis and must be implemented as separate verifiers.
