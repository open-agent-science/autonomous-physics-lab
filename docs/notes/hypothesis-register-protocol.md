# Hypothesis Register Protocol

Task: `TASK-0051`
Domain: `hypothesis_lifecycle`
Status: REVIEW_READY

---

## Lifecycle Notice

This is a legacy protocol note. The `HRE-*` artifacts have been archived under
`docs/legacy/hypothesis-register/`, and agents should not add new
`hypothesis_register/` root entries. New hypothesis ideas now route through
`hypothesis_proposals/`; reviewed hypotheses route through `hypotheses/`.

## Purpose

The hypothesis register was an early machine-readable catalog of physics
hypotheses at the `PROPOSED` or `FORMALIZED` lifecycle stage, before APL had
the current `hypothesis_proposals/`, `hypotheses/`, `results/`, and
result-promotion layers.

It lowered the contribution barrier during the early private-alpha phase. That
role is now covered by task proposals and campaign-scoped hypothesis proposals.

## Register Location

```
docs/legacy/hypothesis-register/
  HRE-0001-*.yaml
  HRE-0002-*.yaml
  ...
```

Files follow the pattern `HRE-XXXX-<short-slug>.yaml`.

## Schema

Historical schema file:
`physics_lab/schemas/hypothesis_register_entry.schema.json` (removed after the
root-level registry was archived).

The legacy schema contract is no longer active in repository validation. Treat
the field list below as historical context only; reactivation would require a
new maintainer-approved architecture task.

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

Historical transition rules are preserved below for context, but this registry
is no longer open for new entries. New work should use the current task,
proposal, result, and claim lifecycle.

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
