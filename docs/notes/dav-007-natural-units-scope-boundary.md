# DAV-007: Natural-Unit Formulas — Out of v1 Scope

## Example Formula

Compton wavelength in natural units (ℏ = c = 1):

```
λ_C = 1/m_e
```

In SI: λ_C = ℏ/(m_e·c), with dimensions [J·s/(kg·m·s⁻¹)] = [m] ✓

## The Problem for an SI-Only Validator

In natural units, ℏ and c are set to 1 — dimensionless numbers. The formula
`λ_C = 1/m_e` then appears to have dimensions [kg⁻¹] in SI, not [m]. A strict
SI base-dimension check would classify this as **INVALID** or fail to parse it
correctly, because the suppressed factors of ℏ and c are not written.

## Why This Is a Scope Choice, Not a Truth Judgment

The v1 validator uses explicit SI base dimensions. To handle natural-unit
formulas, the validator would need to:
1. Know which natural-unit convention is in use (ℏ=c=1, or Planck units, etc.)
2. Restore suppressed dimensional factors automatically.

This is a distinct engineering problem from SI consistency checking. Excluding
it from v1 protects benchmark clarity: the v1 validator tests one thing —
whether a formula's SI dimensions balance. Natural-unit conventions test a
different property.

## Classification for v1

Formula: `λ_C = 1/m_e` (natural units, ℏ=c=1)
Expected v1 verdict: **KNOWN_LIMIT_FAIL** — dimensions do not balance in SI
because ℏ and c are suppressed.

This is not a bug in the formula; it is a scope boundary in the validator.

## Limitation Statement

Scope note only. No v1 implementation exists for natural-unit handling. The
exclusion may be revisited in a future version.
