# Hypothesis Register Protocol

Task: `TASK-0051`
Domain: `hypothesis_lifecycle`
Status: REVIEW_READY

---

## Purpose

The hypothesis register is a machine-readable catalog of physics hypotheses
at the `PROPOSED` or `FORMALIZED` lifecycle stage — before they are backed
by a full experiment (`HYP-XXXX`).

It lowers the contribution barrier: any agent can add a well-scoped
hypothesis in 5–15 minutes without running a benchmark. The hypothesis is
explicitly `PROPOSED` and may not be promoted to a project-level claim until
a separate canonical verification task runs.

## Register Location

```
hypothesis_register/
  HRE-0001-*.yaml
  HRE-0002-*.yaml
  ...
```

Files follow the pattern `HRE-XXXX-<short-slug>.yaml`.

## Schema

Schema file: `physics_lab/schemas/hypothesis_register_entry.schema.json`

Registered in `physics_lab/registry/validation.py` under key
`"hypothesis_register"` → `"hypothesis_register_entry"`.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `id` | string `HRE-XXXX` | Unique register entry id |
| `title` | string | Short human-readable title |
| `domain` | string | Physics domain |
| `mathematical_form` | string | Symbolic or algebraic statement |
| `assumptions` | array | List of explicit assumptions |
| `falsification_test` | string | Concrete deterministic test that would falsify this |
| `claim_ceiling` | string | Maximum allowed claim if test passes |
| `status` | enum | See lifecycle below |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `notes` | string | Caveats, context, overclaim warnings |
| `related_objects` | array | Task ids, hypothesis ids, doc paths |

## Lifecycle States

| State | Meaning |
|---|---|
| `PROPOSED` | New entry, no code verification yet |
| `FORMALIZED` | Mathematical form refined and assumptions explicit |
| `PROMOTED` | Promoted to a full `HYP-XXXX` hypothesis with an experiment |
| `REJECTED` | Entry withdrawn or found to be a duplicate / overclaim |

Transition rules:
- Any agent may add a `PROPOSED` entry.
- Any agent may move `PROPOSED → FORMALIZED` if they sharpen the math.
- Only a maintainer-approved canonical task may move `FORMALIZED → PROMOTED`.
- `PROMOTED` entries should reference their `HYP-XXXX` successor in `related_objects`.
- Agents must not skip `FORMALIZED` when promoting a hypothesis that has not
  had its mathematical form reviewed.

## Claim Restrictions

- A `PROPOSED` entry must never be presented as a verified result.
- `claim_ceiling` must be conservative and range-limited.
- Entries in `fundamental_constants` or `particle_physics` domains must
  reference the relevant numerology guardrails
  (`docs/notes/particle-mass-numerology-guardrails.md`).
- Do not use language like "new physics", "discovery", or "proof" in any
  register entry.

## Seed Entries (after TASK-0081 pilot)

| ID | Domain | Title | Status |
|---|---|---|---|
| HRE-0001 | particle_physics | Koide-like mass relation candidate for neutrinos | REJECTED |
| HRE-0002 | classical_mechanics | Leading-order period correction for weakly anharmonic oscillator | FORMALIZED |
| HRE-0003 | thermodynamics | Wien displacement law generalisation for modified Planck spectrum | PROPOSED |
| HRE-0004 | special_relativity | Relativistic KE correction exceeds 1% at beta > 0.115 | PROPOSED |
| HRE-0005 | fundamental_constants | Fine-structure constant alpha derivable from e, hbar, c, epsilon_0 to 1e-9 | PROPOSED |

## Limitations

- HRE-0001 is now closed as a rejected entry because EXP-0007 / RESULT-0009
  already falsified the algebraically equivalent neutrino Koide form.
- HRE-0002 is now the first `FORMALIZED` entry and links to a draft experiment
  plan created by the TASK-0081 pilot.
- HRE-0003–0005 remain deterministically testable with current code
  infrastructure, but have not yet been promoted.
- The schema does not currently enforce that `claim_ceiling` is conservative —
  this is a human-review responsibility.
