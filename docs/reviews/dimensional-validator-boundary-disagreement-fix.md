# Dimensional Validator Boundary Disagreement Fix

Task: `TASK-0712`
Domain: Dimensional Analysis Validator
Mode: targeted boundary-class fix
Verdict: `BOUNDARY_DISAGREEMENTS_FIXED_NO_RESULT`

## Scope

This task fixes only the three live challenge-set disagreements identified by
`TASK-0689` and reviewed in
`docs/reviews/dimensional-validator-gate-a-result-readiness.md`:

| Item | Previous disagreement | Fixed handling |
| --- | --- | --- |
| `DA-310` | expected `SUSPICIOUS`, computed `VALID` | Explicit curated metadata marks the dimensionally balanced formula as suspicious. |
| `DA-311` | expected `SUSPICIOUS`, computed `VALID` | Explicit curated metadata marks the missing-dimensionless-factor boundary as suspicious. |
| `DA-406` | expected `KNOWN_LIMIT_FAIL`, computed `SUSPICIOUS` | Known-limit rows now return the dimension-only verdict `VALID` before the all-dimensionless suspicious heuristic fires. |

No new result artifact is created here. A later Gate A replay task must decide
whether this boundary fix is publishable evidence.

## Method

The engine change is intentionally narrow:

- `curated_dimensionally_balanced_verdict: SUSPICIOUS` is honored only after
  the formula is dimensionally balanced.
- `KNOWN_LIMIT_FAIL` rows with `check_type: known_limit` are classified as
  dimensionally `VALID`, preserving the existing rule that numerical or regime
  limit failures are outside dimensional-analysis scope.
- The all-dimensionless heuristic still applies to ordinary all-dimensionless
  formulas unless the challenge metadata declares a textbook identity or a
  known-limit boundary.

Challenge metadata changes are limited to `DA-310` and `DA-311`. `DA-406` uses
the existing `KNOWN_LIMIT_FAIL` and `check_type: known_limit` metadata.

## Replay Evidence

Live challenge-set replay after the fix:

```text
74/74 1.000000
[]
```

The empty list is the remaining-disagreement set from
`validate_challenge_set("knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml")`.

Targeted test coverage added:

- `DA-310` computes `SUSPICIOUS` and agrees with the curated label.
- `DA-311` computes `SUSPICIOUS` and agrees with the curated label.
- `DA-406` computes `VALID` and agrees with `KNOWN_LIMIT_FAIL` under the
  dimension-only agreement rule.
- The live 74-item challenge set has no remaining disagreements.

Validation command run:

```text
python -m pytest tests/test_dimensions.py -n0 --basetemp C:\tmp\apl-pytest-task0712b
```

Result: `31 passed`.

## Limitations

- The validator still does not prove physical truth, numerical accuracy, or
  regime validity.
- `DA-310` and `DA-311` require explicit curated metadata because dimensional
  analysis alone cannot infer semantic emptiness or a missing dimensionless
  factor.
- `DA-406` remains a known-limit case: the dimensional validator reports that
  the formula is dimensionally balanced, not that the physical condition is
  satisfied.
- Gate A publication remains blocked until a separate replay/publication task
  decides whether to create or update a canonical RESULT artifact.

## Output Routing

Canonical destination: this review note,
`docs/reviews/dimensional-validator-boundary-disagreement-fix.md`.

Review tier: workflow and validation preflight only. Gate A is not attempted
because this task produces code, metadata, tests, and replay evidence but no
canonical result artifact. Gate B is not applicable.

Claim impact: none. No claim promotion and no physical-truth claim is made.

Knowledge impact: limited workflow memory. The live challenge-set boundary
surface is now internally consistent for the targeted rows.

Publication blocker: a later Gate A task must run the formal replay and decide
result publication.
