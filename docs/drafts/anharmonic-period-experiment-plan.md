# Draft Experiment Plan — Anharmonic Oscillator Period Correction

**HRE entry:** `HRE-0002`
**Status:** DRAFT — not yet a canonical EXP-XXXX task
**Produced by:** TASK-0081 hypothesis register pilot

> This is a draft plan, not an approved experiment. A maintainer must open a
> canonical task and assign an EXP number before this can be executed.

---

## Hypothesis

The leading-order period of a weakly anharmonic oscillator
V(x) = ½kx² + ¼λx⁴ is:

```
T(A) ≈ T₀ · (1 + (3λ / 4k²) · A²)
```

where T₀ = 2π√(m/k) is the harmonic period and A is the amplitude.

The hypothesis claims this approximation holds to within 1% relative error
for λA²/k < 0.1 (perturbative regime).

**Source:** Classical perturbation theory (leading-order Lindstedt-Poincaré).

---

## Scope

- One-dimensional, undamped, undriven oscillator.
- Potential: V(x) = ½kx² + ¼λx⁴ (softening/hardening controlled by sign of λ).
- Perturbative regime: λA²/k ∈ [0.01, 0.3] (includes near and beyond boundary).
- Amplitude A ∈ [0.1, 2.0] (in units where k = m = 1).
- Anharmonicity ratio λ/k ∈ {0.1, 0.3, 0.5, 1.0}.

---

## Proposed Method

1. **Reference:** Numerically integrate the equation of motion
   m·x'' + k·x + λ·x³ = 0 using `scipy.integrate.solve_ivp` with RK45
   and tight tolerances (rtol=1e-10, atol=1e-12). Extract the period T_ref
   from the zero-crossing of x(t).

2. **Formula:** Compute T_approx = T₀ · (1 + (3λ/4k²) · A²).

3. **Error metric:** Relative error ε = |T_approx − T_ref| / T_ref.

4. **Verdict rule:**
   - `VALID_IN_RANGE` if ε < 0.01 for all (A, λ/k) with λA²/k < 0.1.
   - `PARTIALLY_VALID` if valid only for a strict subset of the perturbative range.
   - `OVERFITTED` is not applicable (no fitting is performed).
   - `INVALID` if ε ≥ 0.01 anywhere in the claimed perturbative regime.

---

## Claim Ceiling

If `VALID_IN_RANGE`:

> The formula T(A) ≈ T₀ · (1 + 3λA²/4k²) approximates the period of the
> weakly anharmonic oscillator V(x) = ½kx² + ¼λx⁴ to within 1% relative
> error for λA²/k < 0.1, for the parameter range tested. No claim is made
> about large amplitudes, higher-order terms, or damped/driven cases.

---

## Connection to Existing Infrastructure

- The APL ODE engine used in `EXP-0002` (damped oscillator) provides a
  starting template for numerical integration.
- The pendulum gauntlet workflow (`EXP-0001/RUN-0003`) provides the
  verdict-assignment and metrics format.
- No new dependencies are required beyond `numpy` and `scipy`.

---

## Proposed Experiment ID

`EXP-0008` (next available after EXP-0007)

---

## Limitations to Document

- Formula is first-order in λ/k. Second-order corrections are not included.
- Negative λ (double-well potential) is outside scope.
- No driving or damping; nonlinear resonance effects are not modelled.
- Period extraction via zero-crossing assumes no chaos or quasi-periodicity
  (valid in the perturbative regime).

---

## Required Before Execution

1. Maintainer opens a canonical `TASK-XXXX` with `EXP-0008` allocated.
2. `HRE-0002` is moved from `FORMALIZED → PROMOTED` with a `HYP-XXXX` assigned.
3. An experiment YAML is created at `experiments/EXP-0008-anharmonic-period.yaml`.
