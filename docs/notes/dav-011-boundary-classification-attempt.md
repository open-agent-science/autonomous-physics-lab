# DAV-011: Repeatable Validator-Boundary Classification — SUSPICIOUS vs INVALID

## Classification Target

Two related wind-turbine power formulas:

**Formula A (incomplete):** `P = ρ·v³`
**Formula B (Betz baseline):** `P = (1/2)·ρ·A·v³`

## Manual SI Classification

### Formula A: P = ρ·v³

- P = [M·L²·T⁻³]
- ρ = [M·L⁻³]
- v³ = [L³·T⁻³]
- RHS: [M·L⁻³]·[L³·T⁻³] = [M·T⁻³]

LHS = [M·L²·T⁻³] ≠ RHS = [M·T⁻³] → missing [L²]

**Verdict: INVALID** (dimension mismatch)

### Formula B: P = (1/2)·ρ·A·v³

- A = rotor area [m²] = [L²]
- RHS: [M·L⁻³]·[L²]·[L³·T⁻³] = [M·L²·T⁻³]

LHS = RHS → **Verdict: VALID**

## SUSPICIOUS vs INVALID Boundary

This example illustrates the distinction:
- **INVALID** (Formula A): dimensions do not balance — a required physical
  quantity (area A) is simply missing. No physical assumption can save it.
- **SUSPICIOUS** would apply if dimensions balanced but the physics was
  questionable (e.g., a formula that is dimensionally correct but ignores
  important physics).

Formula A is not SUSPICIOUS; it is structurally wrong at the dimensional level.

## Limitation Statement

Manual classification only. Boundary rule is illustrative, not exhaustive. No
automated validator was run. A single example does not cover all SUSPICIOUS/
INVALID boundary cases.
