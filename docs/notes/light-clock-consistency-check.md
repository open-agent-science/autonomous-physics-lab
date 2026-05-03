# Light-Clock Consistency Check — Planning Document

Task: `TASK-0028`
Type: `thought_experiment_planning`
Domain: relativity
Status: planning only — no implementation yet
Parent suite: `docs/notes/thought-experiment-consistency-suite.md` (TE-001)

---

## Purpose

This document provides a standalone, scoped planning artifact for the
light-clock thought experiment.  It extracts and extends the TE-001 entry from
the broader thought-experiment consistency suite so that a future implementation
task has a self-contained specification with no ambiguity about scope, variables,
checks, failure modes, or accepted outputs.

---

## Physical Premise

A light clock consists of two parallel mirrors separated by proper length `L`.
A light pulse bounces between the mirrors.  In the rest frame of the clock one
tick takes time `T_rest = 2L/c`.

When the clock moves at velocity `v` relative to an observer the light pulse
travels a longer diagonal path.  The observer measures a longer tick time
`T_moving`.  This is **time dilation**.

---

## Assumptions

1. The speed of light `c` is constant and equal in all inertial frames
   (Einstein's second postulate).
2. The two mirrors are rigid and maintain separation `L` in the clock's rest
   frame.
3. Motion is purely inertial — no acceleration, no rotation, no gravity.
4. Space is flat (Minkowski); no curved-spacetime effects.
5. The transverse mirror separation is `L` (perpendicular to motion); length
   contraction acts only along the direction of motion and does not affect `L`.
6. Classical electrodynamics: light travels in a straight line between
   reflections.

---

## Variables

| Symbol | Meaning | SI unit |
|--------|---------|---------|
| `c`    | speed of light in vacuum | m s⁻¹ |
| `L`    | proper mirror separation (rest frame) | m |
| `v`    | clock velocity relative to observer | m s⁻¹ |
| `β`    | `v / c` | dimensionless |
| `γ`    | Lorentz factor `1 / sqrt(1 − β²)` | dimensionless |
| `T_rest`   | tick period in clock rest frame | s |
| `T_moving` | tick period as measured by observer | s |
| `d`    | diagonal path length of light pulse in observer frame | m |

---

## Invariant: Speed of Light

In every inertial frame the light pulse travels at exactly `c`.

- Rest frame: pulse travels `2L` in time `T_rest = 2L/c`.
- Observer frame: pulse travels diagonal distance `d` in time `T_moving = d/c`.

This invariant is the only postulate needed to derive the time-dilation formula.
It must hold numerically for every candidate to within the configured tolerance.

---

## Expected Relation

From Pythagoras on the light path in the observer frame:

```
d/2 = sqrt(L² + (v · T_moving / 2)²)
```

Substituting `d = c · T_moving` and `T_rest = 2L/c`:

```
T_moving = T_rest · γ
```

where:

```
γ = 1 / sqrt(1 − v²/c²)
```

Equivalently, the diagonal path length is:

```
d = 2L · γ
```

A candidate that derives or assumes any other scaling factor is inconsistent
with Special Relativity and must fail the benchmark.

---

## Consistency Checks

| Check ID | Expression | Expected value | Tolerance |
|----------|-----------|----------------|-----------|
| `LC-001` | `T_moving / T_rest` | `γ` | `1e-9` (relative) |
| `LC-002` | `d / (2L)` | `γ` | `1e-9` (relative) |
| `LC-003` | light speed in observer frame: `d / T_moving` | `c` | `1e-12` (relative) |
| `LC-004` | low-velocity limit: `γ` as `v → 0` | `1.0` | `1e-9` (absolute) |
| `LC-005` | `T_moving ≥ T_rest` for all `v ≥ 0` | `True` | — |

Verdict vocabulary inherited from the consistency suite:

- `CONSISTENT` — all checks pass within tolerance
- `INCONSISTENT` — at least one check fails
- `RANGE_LIMITED` — consistent only for a restricted velocity range
- `UNDEFINED` — scenario parameters violate assumptions (e.g. `v ≥ c`)
- `PLACEHOLDER` — check not yet implemented

---

## Known Limits

| Condition | Consequence |
|-----------|-------------|
| `v = c` | `γ → ∞`; clock period diverges; scenario undefined |
| `v > c` | β > 1; `γ` is imaginary; scenario undefined |
| `v ≈ c` | numerical precision of `sqrt(1 − β²)` degrades; use compensated formula or `gamma = 1/sqrt(1-beta**2)` with double precision |
| Non-inertial motion | constant-velocity formula inapplicable; requires proper-time integration |
| `L → 0` | degenerate clock; `T_rest → 0`; ratio still valid if `v` is fixed |
| Finite mirror reflectivity | not modeled; physical loss is outside scope |

The benchmark must reject any input with `v ≥ c` before running checks.

---

## Possible Failure Modes for Candidate Models

A candidate is any formula or derivation that attempts to predict `T_moving`
given `(L, v, c)`.

| Failure pattern | Symptom | Check that catches it |
|-----------------|---------|-----------------------|
| Missing `γ` factor — Newtonian assumption `T_moving = T_rest` | `LC-001` ratio = 1.0 | LC-001 |
| Wrong exponent — `γ²` or `γ^(1/2)` | ratio off by power of γ | LC-001, LC-002 |
| Dropped factor of 2 — `d = L·γ` instead of `2L·γ` | `LC-002` ratio = γ/2 | LC-002 |
| Incorrect speed-of-light check — `d/T ≠ c` | light travels at wrong speed | LC-003 |
| Formula diverges at `v = 0` | low-velocity limit broken | LC-004 |
| `T_moving < T_rest` for some `v` | time runs faster when moving | LC-005 |
| Division by zero at `v = c` without guard | runtime error | pre-check |

---

## Future Benchmark Plan

### Step 1 — Implementation task (next READY candidate after TASK-0028)

Create a new canonical implementation task that:

- adds `experiments/EXP-00XX-light-clock.yaml` (next available experiment id,
  do not assume EXP-0003 automatically);
- implements `physics_lab/engines/thought_experiments.py` with a
  `LightClockScenario` class;
- runs checks LC-001 through LC-005 for a sweep of `v/c ∈ {0, 0.1, 0.5, 0.9, 0.99}`;
- produces `results/EXP-00XX/RUN-0001/{result.yaml, report.md, metrics.json}`.

### Step 2 — Wrong-candidate regression test

Add a deliberate wrong candidate (`NewtonianClock` with `T_moving = T_rest`)
and assert that it returns `INCONSISTENT` on LC-001.  This prevents silent
regressions where the checker always returns `CONSISTENT`.

### Step 3 — Integration with consistency suite

Wire the light-clock scenario into `EXP-0003` (or next available id for the
broader thought-experiment suite) alongside TE-002 (simultaneity) and TE-006
(falling elevator) as the first three low-complexity scenarios.

### Validation required before closing the implementation task

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

### Definition of done for this planning document

This document is complete when:

- it can serve as the sole specification handed to an implementation agent;
- every variable is named, every check has an id and tolerance, and every
  known limit and failure mode is listed;
- no implementation code or result artifacts are introduced in this task.

---

## Relation to Broader Suite

The thought-experiment consistency suite
(`docs/notes/thought-experiment-consistency-suite.md`) lists six scenarios.
This document covers TE-001 only.  The recommended implementation order from
that document is: TE-001 → TE-002 → TE-006 → TE-003 → TE-004 → TE-005.

Do not implement TE-002 through TE-006 in the same task as TE-001.  Keep
implementation tasks atomic.

---

## Limitations of This Plan

- Thought-experiment checks test internal consistency within Special Relativity,
  not discovery of new physics.
- SR is self-consistent by construction; this suite validates that APL
  implements SR correctly, not that SR is empirically correct.
- The light-clock derivation assumes idealized mirrors and a single spatial
  dimension of motion.  Polarization, diffraction, and finite beam width are
  outside scope.
- Length contraction along the direction of motion is not tested here; that
  belongs to a separate scenario (e.g. a longitudinal light clock).
- No claim of new physics is made or implied.
