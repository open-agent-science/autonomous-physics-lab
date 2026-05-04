# Approximation Breakdown Probes Track

Task: `TASK-0050`
Domain: `classical_mechanics_and_approximation_theory` (multi-domain)
Status: REVIEW_READY
Protocol: `docs/scientific-micro-task-protocol.md`

---

## Purpose

The approximation-breakdown probes track gives any agent a deterministic,
overclaim-safe contribution path: each micro-task quantifies the parameter
value at which a well-known physics approximation first exceeds a stated
relative-error threshold against an exact (or higher-order) reference.

Because the ground truth is either a closed-form exact solution or a
high-precision numerical reference, every probe is strictly verifiable and
reproduces a textbook result. This track generalises the separatrix-aware
pendulum follow-up (`docs/notes/pendulum-separatrix-followup.md`,
`results/EXP-0001/RUN-0002/`) into a systematic micro-task pattern.

## Track Location

```
approximation_probes/
  AP-0001-small-angle-pendulum.yaml
  AP-XXXX-*.yaml
  ...
```

Files follow the pattern `AP-XXXX-<short-slug>.yaml`.

## Result Artifact Format

Schema file: `physics_lab/schemas/approximation_probe.schema.json`

Registered in `physics_lab/registry/validation.py` under key
`"approximation_probes"` -> `"approximation_probe"`.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `id` | string `AP-XXXX` | Unique entry id |
| `probe_name` | string | Short slug (e.g. `small_angle_pendulum_period`) |
| `approximation` | string | The approximation being tested (e.g. `sin(theta) ~ theta`) |
| `domain` | string | Physics domain (e.g. `classical_mechanics`, `special_relativity`) |
| `exact_reference` | string | Description of exact / higher-order reference used |
| `error_threshold` | number | Maximum allowed relative error (e.g. `0.01` = 1%) |
| `parameter_range` | string | Range over which the probe sweeps |
| `derivation` | object | `{symbolic_form, assumptions, parameters}` |
| `check` | object | `{code_reference, breakdown_point, breakdown_units, computed_value, threshold_used}` |
| `verdict` | enum | `VERIFIED` / `FAILS_AT_TOLERANCE` / `INVALID_DERIVATION` / `INCONCLUSIVE` |
| `claim_ceiling` | string | Conservative range-limited claim if verdict is `VERIFIED` |
| `notes` | string | Caveats, re-verification triggers |

## Probe Specification Rules

- The `exact_reference` field must name the exact-solution method or
  higher-order numerical routine and (if relevant) the SciPy / mpmath / etc.
  function used.
- The `error_threshold` field stores the relative error threshold as a
  floating-point number (e.g. `0.01` for 1%).
- The `parameter_range` field must explicitly state the swept variable and
  its physical range, including units.
- The `check.breakdown_point` field stores the parameter value at which the
  approximation first exceeds the threshold, with units.
- The `check.computed_value` field stores the numerical breakdown value
  preserving meaningful precision (typically 6-10 significant digits).

## Verdict Vocabulary

| Verdict | Meaning |
|---|---|
| `VERIFIED` | Breakdown point matches textbook value within reproducibility tolerance |
| `FAILS_AT_TOLERANCE` | Probe never crosses the threshold within the stated parameter range |
| `INVALID_DERIVATION` | Symbolic derivation contains an algebraic / unit error |
| `INCONCLUSIVE` | Exact reference unavailable or definition ambiguous |

## Claim Restrictions

- Each artifact must state an explicit `claim_ceiling` no broader than
  "approximation X exceeds threshold Y at parameter Z".
- Do not claim novelty unless the breakdown value deviates from textbook.
- A verdict of `VERIFIED` does not promote any project-level claim.
- Re-verify whenever the underlying SciPy / numerical routine changes.

## Candidate Micro-Task List

The following 10 micro-tasks are scoped and ready for any agent to execute.
They span at least two physics domains: classical mechanics, special
relativity, statistical mechanics, thermodynamics, optics, quantum.
AP-0001 is implemented in this track-launch task as a worked example.

| ID | Approximation | Exact Reference | Threshold | Domain |
|---|---|---|---|---|
| AP-0001 | Small-angle pendulum: `T = 2*pi*sqrt(L/g)` | Elliptic integral `K(sin^2(theta_0/2))` | 1% period | classical mechanics |
| AP-0002 | Newtonian KE: `KE = (1/2)*m*v^2` | Relativistic KE `(gamma - 1)*m*c^2` | 1% energy | special relativity |
| AP-0003 | Stirling: `ln(n!) ~ n*ln(n) - n` | `lgamma(n+1)` | 1% absolute | combinatorics / stat mech |
| AP-0004 | Ideal gas: `P = n*R*T/V` | Van der Waals at fixed `(a, b)` for CO2 | 1% pressure | thermodynamics |
| AP-0005 | Paraxial optics: `sin(theta) ~ theta` for ray bend | Exact `sin(theta)` lens equation | 1% focal length | optics |
| AP-0006 | Non-relativistic Doppler: `delta_f / f = v/c` | Relativistic Doppler `sqrt((1+beta)/(1-beta)) - 1` | 1% frequency | wave / relativity |
| AP-0007 | Rayleigh-Jeans: `B(nu, T) = 2*nu^2*k_B*T/c^2` | Planck `(2*h*nu^3/c^2) * 1/(exp(h*nu/k_B/T) - 1)` | 1% spectral radiance | thermal / quantum |
| AP-0008 | Linear-drag terminal velocity vs quadratic-drag exact | Quadratic-drag closed-form `v_t = sqrt(2*m*g/(rho*C_d*A))` | 1% velocity | classical mechanics |
| AP-0009 | Taylor expansion of `e^x` to N terms | Exact `math.exp(x)` for given N | 1% absolute | numerical methods |
| AP-0010 | Linearized Boltzmann factor `1 - x` for `exp(-x)` | `math.exp(-x)` at small `x` | 1% absolute | stat mech / numerical |

Each micro-task should:

- pick a sensible threshold (default 1% unless physics motivates otherwise);
- state the swept parameter range with units;
- store the breakdown point with units;
- cite the exact reference (closed form, SciPy function, or higher-order series).

Additional candidates that fit the schema but are **not** part of the initial
batch (because they need more careful exact references):

- WKB approximation breakdown near classical turning points
- Paraxial Gaussian beam approximation vs full diffraction integral
- Second-order Born approximation vs partial-wave method (low energy)
- Dipole approximation in QED vs full multipole expansion

## Worked Example: AP-0001 Small-Angle Pendulum

- **Artifact:** `approximation_probes/AP-0001-small-angle-pendulum.yaml`
- **Code:** `physics_lab/engines/approximation_probes.py:small_angle_pendulum_breakdown`
- **Test:** `tests/test_approximation_probes.py::test_small_angle_pendulum_breakdown_one_percent`

### Approximation

`T_approx = 2 * pi * sqrt(L / g)` (period independent of amplitude).

### Exact Reference

`T_exact(theta_0) = (4 / omega_0) * K(sin^2(theta_0 / 2))` where `K` is the
complete elliptic integral of the first kind (`scipy.special.ellipk`).

### Method

Compute relative error `(2 / pi) * K(sin^2(theta_0 / 2)) - 1` and root-find
with `scipy.optimize.brentq` for the smallest `theta_0` where this exceeds
the threshold.

### Result

- Threshold: 1% relative period error.
- Breakdown amplitude: `theta_0 = 0.398 rad (22.81 deg)`.
- Tighter-tolerance check: `0.1%` threshold gives `7.24 deg` (also matches textbook).

### Verdict

`VERIFIED`.

### Claim Ceiling

Reproduces a textbook result; no novelty claim. The small-angle pendulum
period approximation `T = 2*pi*sqrt(L/g)` exceeds 1% relative period error
at amplitude `~22.8 deg`. No claim about pendulum dynamics outside this
amplitude range.

## Execution Workflow for One Micro-Task

1. Pick one AP-XXXX from the candidate list (or propose a new one consistent with the schema).
2. Implement a function in `physics_lab/engines/approximation_probes.py` that
   returns the breakdown point given a threshold.
3. Add a pytest in `tests/test_approximation_probes.py` asserting the
   breakdown matches the textbook value.
4. Create the YAML artifact in `approximation_probes/AP-XXXX-<slug>.yaml`
   following the schema, filling all required fields.
5. Run `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`.
6. Open a PR with the conventional commit prefix `feat(task-XXXX):` linking to
   the parent execution task.

## Limitations

- Some approximations have multiple breakdown definitions (e.g. amplitude
  vs phase error for the pendulum). Each artifact must state which error
  measure it uses in `derivation.symbolic_form`.
- For approximations whose exact reference itself is iterative (e.g.
  van der Waals roots), the artifact must record the numerical method and
  convergence tolerance.
- This track records **where** approximations break down; it does not
  produce new physics. Any claim about novel breakdown behaviour requires
  a separate canonical task.
- Relativistic and quantum probes that depend on `c`, `h`, `k_B` use the
  same `scipy.constants` source as the constants-verification track
  (`docs/notes/physical-constants-verification-track.md`); both tracks
  must be re-verified together when CODATA publishes a new edition.
