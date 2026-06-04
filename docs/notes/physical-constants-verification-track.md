# Physical Constants Verification Track

Task: `TASK-0049`
Domain: `fundamental_constants`
Status: REVIEW_READY
Protocol: `docs/scientific-micro-task-protocol.md`

---

## Lifecycle Notice

This is a legacy track note. `CV-0001` has been archived under
`docs/legacy/constants-verification/`, and agents should not recreate
`constants_verification/` at repository root by default. Future constants or
formula checks should route through Textbook Formula Audit, source artifacts,
canonical `results/`, or reviewed `knowledge/` when appropriate.

## Purpose

The constants-verification track was an early deterministic, overclaim-safe
contribution path: each micro-task verified one derived physical constant from
base CODATA values using `scipy.constants` and returned a structured result
artifact.

Because the ground truth is published by CODATA / BIPM, every micro-task is
strictly verifiable. This track also exercises the scientific micro-task
protocol in a well-bounded domain before applying that pattern to riskier
hypothesis work.

## Track Location

```
docs/legacy/constants-verification/
  CV-0001-fine-structure-constant.yaml
```

The current archive preserves `CV-0001`. Do not add new root-level
`constants_verification/` entries without a maintainer-approved architecture
task.

## Result Artifact Format

Historical schema file:
`physics_lab/schemas/constant_verification.schema.json` (removed after the
root-level registry was archived).

The legacy schema contract is no longer active in repository validation. Treat
the field list below as historical context only; reactivation would require a
new maintainer-approved architecture task.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `id` | string `CV-XXXX` | Unique entry id |
| `constant_symbol` | string | LaTeX-style symbol, e.g. `alpha` |
| `constant_name` | string | Human-readable name |
| `domain` | string | `fundamental_constants` (default) or domain-specific |
| `source` | object | `{edition, reference_value, uncertainty, units}` |
| `derivation` | object | `{symbolic_form, assumptions, input_constants}` |
| `check` | object | `{code_reference, computed_value, relative_error, tolerance}` |
| `verdict` | enum | `VERIFIED` / `FAILS_AT_TOLERANCE` / `INVALID_DERIVATION` / `INCONCLUSIVE` |
| `claim_ceiling` | string | Conservative range-limited claim allowed if verdict is VERIFIED |
| `notes` | string | Caveats, re-verification triggers |

## Source / Uncertainty Metadata Rules

- `source.edition` must name a specific edition (e.g. `CODATA 2018`,
  `CODATA 2014`, `BIPM 2019`) plus the input access path (e.g.
  `via scipy.constants`).
- `source.reference_value` must preserve published precision; store as a string.
- `source.uncertainty` must be present; if zero (defined constant after the
  2019 SI redefinition), state that explicitly (e.g. `"0 (defined constant)"`).
- `source.units` must be SI base units or explicitly `"dimensionless"`.

## Verdict Vocabulary

| Verdict | Meaning |
|---|---|
| `VERIFIED` | Computed value matches reference within stated `tolerance` |
| `FAILS_AT_TOLERANCE` | Deviation exceeds `tolerance`; document where in `notes` |
| `INVALID_DERIVATION` | Symbolic derivation contains an algebraic or unit error |
| `INCONCLUSIVE` | Required input constant unavailable or definition ambiguous |

## Claim Restrictions

- Each artifact must state an explicit `claim_ceiling` no broader than
  "verified to tolerance X from <source edition>".
- Do not claim that a constant has a "deeper meaning" or "natural origin"
  based on a numerical match.
- A verdict of `VERIFIED` does not promote any project-level claim.
- Re-verify whenever `scipy.constants` is updated or CODATA publishes a new edition.

## Candidate Micro-Task List

The following 10 micro-tasks are scoped and ready for any agent to execute.
CV-0001 is implemented in this track-launch task as a worked example.

| ID | Constant | Symbol | Derivation |
|---|---|---|---|
| CV-0001 | Fine-structure constant | alpha | e^2 / (4*pi*epsilon_0*hbar*c) |
| CV-0002 | Bohr radius | a_0 | (4*pi*epsilon_0*hbar^2) / (m_e*e^2) |
| CV-0003 | Rydberg constant | R_inf | (m_e*e^4) / (8*epsilon_0^2*h^3*c) |
| CV-0004 | Stefan–Boltzmann constant | sigma | (2*pi^5*k_B^4) / (15*h^3*c^2) |
| CV-0005 | Wien displacement constant | b | h*c / (k_B * W), where W solves x = 5*(1 - e^-x) |
| CV-0006 | Bohr magneton | mu_B | e*hbar / (2*m_e) |
| CV-0007 | Nuclear magneton | mu_N | e*hbar / (2*m_p) |
| CV-0008 | Compton wavelength of electron | lambda_C | h / (m_e*c) |
| CV-0009 | Classical electron radius | r_e | e^2 / (4*pi*epsilon_0*m_e*c^2) |
| CV-0010 | Hartree energy | E_h | m_e*c^2*alpha^2 |

Additional candidates (not part of the initial batch but compatible with the
schema): Faraday constant F = N_A*e, gas constant R = N_A*k_B,
Avogadro-derived Loschmidt constant n_0, von Klitzing constant R_K = h/e^2,
Josephson constant K_J = 2e/h, conductance quantum G_0 = 2e^2/h.

## Worked Example: CV-0001 Fine-Structure Constant

- **Artifact:** `docs/legacy/constants-verification/CV-0001-fine-structure-constant.yaml`
- **Code:** `physics_lab/engines/constants_verifier.py:fine_structure_constant`
- **Test:** `tests/test_constants_verifier.py::test_fine_structure_constant_within_tolerance`

### Derivation

```
alpha = e^2 / (4 * pi * epsilon_0 * hbar * c)
```

### Reference

`scipy.constants.alpha = 7.2973525693e-3` (CODATA 2018).

### Check

The verifier function reads `e`, `epsilon_0`, `hbar`, `c` from
`scipy.constants` and computes alpha symbolically. The relative error vs
`scipy.constants.alpha` is below floating-point precision (< 1e-15), well
within the 1e-9 tolerance.

### Verdict

`VERIFIED`.

### Claim Ceiling

The formula reproduces `scipy.constants.alpha` (CODATA 2018) to within 1e-9
relative error using `scipy.constants` input values. No claim about
physical origin or theoretical significance.

## Execution Workflow for One Micro-Task

1. Prefer a current campaign/task path instead of creating a new CV artifact.
2. Implement a function in `physics_lab/engines/constants_verifier.py` that
   computes the constant from base inputs and returns
   `(computed, reference, relative_error)`.
3. Add a pytest in `tests/test_constants_verifier.py` asserting the
   tolerance.
4. If a maintainer explicitly reactivates this path, use a dedicated task to
   define where the artifact belongs and how it is validated.
5. Run `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`.
6. Open a PR with the conventional commit prefix `feat(task-XXXX):` linking to
   the parent execution task.

## Limitations

- Some constants (Wien's b, Stefan–Boltzmann sigma) require numerical
  root-finding rather than a closed-form expression. The schema allows this:
  the `derivation.symbolic_form` field can describe the implicit equation,
  and the `code_reference` does the numerical work.
- Constants defined after the 2019 SI redefinition (e.g. `e`, `h`, `k_B`) have
  zero uncertainty by definition; this must be stated explicitly in the
  `source.uncertainty` field.
- The `scipy.constants` values are the project's source of truth for now.
  When CODATA publishes a new edition, all CV-XXXX artifacts must be
  re-verified and the `source.edition` field updated.
