# Thought-Experiment Consistency Suite — Planning Document

Task: `TASK-0014`  
Type: `benchmark_planning`  
Domain: relativity  
Status: planning only — no implementation yet

---

## Purpose

This document covers all four required outputs for TASK-0014:

1. [Task spec](#task-spec) — scope and constraints
2. [Consistency-suite plan](#consistency-suite-plan) — benchmark design
3. [Candidate thought-experiment inventory](#candidate-thought-experiment-inventory) — six cases
4. [Future validation outline](#future-validation-outline) — implementation path

---

## Task Spec

### Goal

Plan a benchmark suite that tests whether APL can formalize, verify, and
falsify classical relativistic thought experiments deterministically.

Thought experiments differ from formula-fitting benchmarks:

- the ground truth is an exact analytical consequence of stated axioms, not
  empirical data;
- verification means checking internal consistency against those axioms;
- failure means a candidate model violates a stated invariant, not that it
  exceeds a numerical fit threshold.

### Scope

- Special Relativity thought experiments only in the first version.
- Flat spacetime, inertial or uniformly-accelerating frames only.
- No General Relativity, curved spacetime, or quantum effects.
- No tidal-force effects (uniform fields only for elevator cases).

### Non-goals for this planning task

- No implementation in this task.
- No new Python modules, schemas, or workflows.
- No new hypotheses, experiments, claims, or results files.

### Scientific constraints

- All checks must reduce to deterministic numerical evaluations.
- Every check must have a clear pass/fail criterion with tolerance bounds.
- Assumptions must be stated explicitly; a check that silently assumes an
  unstated axiom is invalid.
- The suite should be falsifiable: a wrong candidate must fail at least one
  check.

---

## Consistency-Suite Plan

### Benchmark identity

Proposed future experiment: `EXP-0003` (or next available ID)  
Proposed task: new `TASK-EXP-0003-*` implementation task

### Design principle

Each thought experiment is modeled as a **consistency scenario** with:

| Field | Description |
|---|---|
| `scenario_id` | unique identifier, e.g. `TE-001` |
| `name` | human-readable label |
| `framework` | physical theory assumed (e.g. `special_relativity`) |
| `assumptions` | explicit list of axioms accepted as true |
| `invariants` | quantities that must be preserved |
| `checks` | list of deterministic numerical tests |
| `known_limits` | conditions under which the scenario is undefined or breaks |
| `verdict_vocabulary` | allowed outcomes per check |

### Verdict vocabulary

| Verdict | Meaning |
|---|---|
| `CONSISTENT` | candidate satisfies all checks within tolerance |
| `INCONSISTENT` | candidate violates at least one invariant |
| `RANGE_LIMITED` | consistent only within a restricted parameter range |
| `UNDEFINED` | scenario is ill-posed for the given parameters |
| `PLACEHOLDER` | check not yet implemented for this scenario |

### Candidate family structure

Candidates are not fitted models — they are explicit analytical formulations
of each thought experiment, derived from a stated set of assumptions.

A candidate passes if its predictions match the exact analytical reference
within a configurable relative tolerance (default: `1e-9`).

A candidate fails if it uses an incorrect formula, drops a factor of γ, or
violates any stated invariant.

### Relation to existing infrastructure

The suite reuses existing APL concepts:

- `VerificationCheck` — each scenario check maps directly onto this type
- `verify_candidate_model` pattern — same pass/fail/diagnostic structure
- result artifacts — `result.yaml`, `report.md`, `metrics.json` unchanged
- severity vocabulary — existing `PASS`/`FAIL`/`PLACEHOLDER` maps onto
  `CONSISTENT`/`INCONSISTENT`/`PLACEHOLDER`

No schema changes are required in the first implementation iteration.

---

## Candidate Thought-Experiment Inventory

### TE-001 — Light Clock (Time Dilation)

**Physical principle:** a clock built from a light pulse bouncing between two
mirrors runs slow when moving.

**Framework:** Special Relativity

**Assumptions:**
- speed of light c is constant in all inertial frames
- no acceleration; purely inertial motion at velocity v
- mirrors separated by proper length L in the rest frame

**Key invariant:**

```
T_moving = T_rest * γ
γ = 1 / sqrt(1 - v²/c²)
```

**Checks:**

| Check | Expression | Expected |
|---|---|---|
| `time_dilation_factor` | `T_moving / T_rest` | `γ` |
| `light_path_length` | transverse path in moving frame | `2L·γ` |
| `low_velocity_limit` | `γ → 1` as `v → 0` | `T_moving → T_rest` |
| `high_velocity_limit` | `γ → ∞` as `v → c` | diverges |

**Known limits:** v < c; formula undefined at v = c.

---

### TE-002 — Relativity of Simultaneity

**Physical principle:** two events simultaneous in one inertial frame are not
simultaneous in a frame moving relative to it.

**Framework:** Special Relativity (Lorentz transformation)

**Assumptions:**
- inertial frames S and S′; S′ moves at velocity v relative to S
- events A and B occur at `(t=0, x=x_A)` and `(t=0, x=x_B)` in S
- Lorentz transformation applies

**Key invariant:**

```
Δt′ = γ (Δt − v·Δx / c²)
```

For `Δt = 0`, `Δx ≠ 0`, `v ≠ 0`:

```
Δt′ = −γ v Δx / c²  ≠  0
```

**Checks:**

| Check | Expression | Expected |
|---|---|---|
| `simultaneity_broken` | `Δt′` for `Δt=0, Δx≠0, v≠0` | `≠ 0` |
| `sign_of_desynchronization` | sign of `Δt′` | `−sign(v·Δx)` |
| `magnitude` | `|Δt′|` | `γ·|v|·|Δx|/c²` |
| `zero_velocity_limit` | `v=0` | `Δt′ = 0` |
| `zero_separation_limit` | `Δx=0` | `Δt′ = 0` |

**Known limits:** applies only to spatially separated events in inertial frames.

---

### TE-003 — Twin Paradox (Proper Time Along Worldlines)

**Physical principle:** the traveling twin who accelerates and decelerates ages
less than the stay-at-home twin.

**Framework:** Special Relativity, with an acceleration phase

**Assumptions:**
- twin A stays at rest in an inertial frame
- twin B travels at constant speed v for time T/2, then returns at speed v
  for another T/2 (instantaneous turnaround for simplicity)
- proper time is integrated along each worldline

**Key invariant:**

```
τ_B = T · sqrt(1 − v²/c²) = T / γ
τ_A = T
τ_A > τ_B  for v > 0
```

**Checks:**

| Check | Expression | Expected |
|---|---|---|
| `proper_time_B` | `∫ sqrt(1 − v²/c²) dt` over worldline | `T/γ` |
| `age_difference` | `τ_A − τ_B` | `T (1 − 1/γ) > 0` |
| `zero_velocity_limit` | `v → 0` | `τ_A = τ_B` |
| `high_velocity_limit` | `v → c` | `τ_B → 0` |

**Known limits:** instantaneous turnaround is an idealization; the acceleration
phase is neglected. A candidate that tries to compute this more carefully (with
finite acceleration) will need a different check set.

---

### TE-004 — Einstein Elevator (Equivalence Principle)

**Physical principle:** a uniformly accelerating elevator is locally
indistinguishable from a gravitational field.

**Framework:** Equivalence Principle (bridge between SR and GR)

**Assumptions:**
- uniform gravitational acceleration g, no tidal forces
- elevator accelerates upward at a = g
- test particle released from rest inside the elevator

**Key invariant:**

Equations of motion of a free particle inside a freely falling elevator
(an inertial frame) are identical to equations of motion in the absence of
gravity:

```
z''(t) = 0  in free-fall frame
```

In the accelerating elevator (equivalent to gravity):

```
z''(t) = −a  in elevator frame  (same as  z''(t) = −g)
```

**Checks:**

| Check | Expression | Expected |
|---|---|---|
| `free_fall_inertial` | `z(t)` in freely falling frame | straight line |
| `elevator_gravity_equivalence` | `z''(t)` in elevator vs gravity field | equal |
| `trajectory_match` | trajectory in elevator matches uniform gravity | max error < tol |

**Known limits:** strict equivalence only for infinitesimally small spatial
regions (tidal forces break it at finite scale).

---

### TE-005 — Rotating Disk (Ehrenfest Paradox)

**Physical principle:** a rigidly rotating disk has a non-Euclidean spatial
geometry as measured by co-rotating observers.

**Framework:** Special Relativity with rotation

**Assumptions:**
- disk of coordinate radius R rotates at angular velocity ω
- rim velocity v = ωR < c
- circumference measured by co-rotating rulers is Lorentz-contracted

**Key invariant:**

Each small circumference element `dl` at rim is Lorentz-contracted by factor
`1/γ` in the lab frame, so co-rotating observers measure:

```
C_measured = 2πR · γ  >  2πR
```

The ratio `C/R` exceeds `2π` for any co-rotating observer with v > 0.

**Checks:**

| Check | Expression | Expected |
|---|---|---|
| `circumference_ratio` | `C_measured / (2πR)` | `γ` |
| `radial_ruler` | radial rulers are not contracted | `R_measured = R` |
| `geometry_deviation` | `C_measured / R_measured` | `> 2π` |
| `zero_rotation_limit` | `ω → 0` | `C / R → 2π` |

**Known limits:** the Ehrenfest paradox cannot be resolved purely within SR
without invoking Born rigidity or GR; this check suite tests the geometry
prediction only, not the stress-strain dynamics of the disk material.

---

### TE-006 — Falling Elevator (Local Weightlessness)

**Physical principle:** an observer in free fall in a uniform gravitational
field is locally weightless.

**Framework:** Newtonian gravity plus equivalence principle

**Assumptions:**
- uniform gravitational field g
- two objects released simultaneously from rest inside a freely falling elevator
- no tidal forces

**Key invariant:**

Relative acceleration between two freely-falling objects inside the elevator
is zero:

```
a_rel = a_1 − a_2 = g − g = 0
```

**Checks:**

| Check | Expression | Expected |
|---|---|---|
| `relative_acceleration` | `|a_1 − a_2|` inside elevator | `0` |
| `absolute_acceleration` | `a_1` in lab frame | `g` |
| `weightlessness_condition` | normal force on object from elevator floor | `0` |

**Known limits:** tidal forces produce nonzero relative accelerations for
non-uniform fields or finite spatial extent; this check is only valid in the
uniform-field approximation.

---

## Summary Table

| ID | Name | Framework | Key Invariant | Complexity |
|---|---|---|---|---|
| TE-001 | Light Clock | SR | `T_moving = γ·T_rest` | low |
| TE-002 | Simultaneity | SR | `Δt′ = γ(Δt − vΔx/c²)` | low |
| TE-003 | Twin Paradox | SR + acceleration | `τ_B = T/γ` | medium |
| TE-004 | Einstein Elevator | Equivalence Principle | `z''=0` in free fall | medium |
| TE-005 | Rotating Disk | SR + rotation | `C/R = 2π·γ` | high |
| TE-006 | Falling Elevator | Newtonian + EP | `a_rel = 0` | low |

Recommended implementation order: TE-001, TE-002, TE-006, TE-003, TE-004,
TE-005 (complexity ascending).

---

## Future Validation Outline

### Phase 1 — Schema and infrastructure (one implementation task)

1. Define `ThoughtExperimentSpec` as a new YAML schema under
   `physics_lab/schemas/thought_experiment.schema.json`.
2. Add `ThoughtExperimentCandidate` and `ConsistencyCheck` types analogous
   to `CandidateModel` and `VerificationCheck`.
3. No changes to existing benchmark infrastructure.

### Phase 2 — First two checks (TE-001 and TE-002)

1. Implement verifiers for light clock and simultaneity — both reduce to
   closed-form Lorentz factor evaluations.
2. Integrate into a new `EXP-0003` workflow module
   `physics_lab/workflows/thought_experiments.py`.
3. Produce `result.yaml` and `report.md` artifacts in
   `results/EXP-0003/RUN-0001/`.
4. Verify: ruff, pytest, validate-repo.

### Phase 3 — Proper-time and elevator checks (TE-003, TE-004, TE-006)

1. Implement proper-time integration for TE-003 using numerical quadrature
   and compare against exact formula.
2. Implement elevator equivalence checks for TE-004 and TE-006 using
   trajectory integration.
3. Extend result schema with `consistency_summary` field analogous to
   existing `verification` field.

### Phase 4 — Rotating disk (TE-005)

1. Treat as advanced check; implement geometry deviation calculation.
2. Document Ehrenfest paradox scope limitation explicitly in the result
   artifact.

### Definition of done for the full suite

- all six scenarios produce deterministic CONSISTENT/INCONSISTENT verdicts;
- at least one scenario has a deliberate wrong-candidate case that produces
  INCONSISTENT as a regression test;
- `validate-repo --strict --fail-on-warnings` passes;
- no speculative claim about GR, tidal effects, or non-inertial dynamics is
  introduced without a separate hypothesis file.

### Limitations of this plan

- Thought-experiment checks test consistency within a framework, not
  discovery of new physics.
- SR is self-consistent by construction; the suite validates that APL
  correctly implements SR, not that SR is correct.
- Ehrenfest paradox requires careful simultaneity conventions for rotating
  observers; the plan above is correct for the geometry check only.
- Twin paradox with instantaneous turnaround is an idealization; a finite-
  acceleration variant would require a separate scenario.
- Relativistic rotating disk and GR effects are out of scope for phase 1-3.
