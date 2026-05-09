# Claim Promotion Policy

## Purpose

This document defines when a `CLAIM-*` file may move beyond `DRAFT`.

The repository already generates `claim_update.md` and
`claim_update.patch.md` artifacts from validated results, but those artifacts
are suggestions, not automatic repository edits.

Claim promotion is a deliberate maintainer review step.

## Core Rule

No claim is promoted automatically.

A generated suggestion may recommend `PARTIALLY_SUPPORTED` or `SUPPORTED`, but a
human maintainer must still review:

- the referenced `RESULT-*` artifacts;
- the benchmark scope;
- the wording inside the claim file itself;
- whether the claim text matches the actual strength of evidence.

Sandbox-only autonomous research is never claim-promotion evidence by itself.
Agent-run summaries may justify rejection, retention as sandbox memory, or a
follow-up canonical task, but they must pass through a later reviewed canonical
experiment/result path before any `CLAIM-*` status changes.

## Allowed Claim Statuses

### `DRAFT`

Use `DRAFT` when any of the following is true:

- no reproducible `RESULT-*` artifact exists yet;
- referenced verification checks still fail;
- the claim wording has not yet been reviewed by a human;
- the evidence exists but the scope language is still unclear;
- the benchmark is still too narrow to justify stronger language.

### `PARTIALLY_SUPPORTED`

Use `PARTIALLY_SUPPORTED` when:

- at least one reproducible `RESULT-*` artifact exists;
- the referenced result passes its in-scope verification gate;
- the support is still range-limited, benchmark-limited, or assumption-limited;
- the claim text explicitly says so.

Typical cases:

- pendulum approximations that are valid only on configured amplitude ranges;
- benchmark slices with known non-gating failures outside the validated scope;
- evidence that supports a phenomenon but not a universal formulation.

Required wording patterns:

- "valid only within the tested range"
- "supported on the configured benchmark"
- "within the sampled scope"
- "for the linear, unforced case"

### `SUPPORTED`

Use `SUPPORTED` only when all of the following are true:

- reproducible `RESULT-*` evidence exists;
- referenced verification checks pass without unresolved failures;
- the claim scope matches the verified benchmark scope;
- the evidence is not merely a narrow approximation with known out-of-scope failures that would mislead a reader;
- a human maintainer has reviewed the wording and agrees that the claim is still appropriately scoped.

Typical case:

- the linear damped harmonic oscillator regime structure, when supported by exact in-scope analytic verification.

### `REFUTED`

Use `REFUTED` when:

- reproducible result evidence directly contradicts the claim as written;
- the contradiction is strong enough that the claim should no longer remain an open placeholder.

### `SUPERSEDED`

Use `SUPERSEDED` when:

- a newer claim replaces the older formulation more precisely;
- the old claim should remain in history but is no longer the preferred object.

## Review Checklist

Before promoting a claim, confirm:

1. `claim_update.md` and `claim_update.patch.md` have been reviewed but not copied blindly.
2. Every referenced `RESULT-*` exists and passes repository validation.
3. The claim `scope` field matches the evidence scope.
4. The body text does not overclaim beyond the referenced benchmark.
5. Range-limited evidence is described explicitly.
6. The claim still reads as scientific memory, not marketing language.

## Evidence Mapping Rules

- `CLAIM-*` files must reference concrete `RESULT-*` ids, not only `EXP-*`.
- `EXP-*` explains the procedure; `RESULT-*` is the evidence object.
- If multiple results are referenced, the claim must remain limited by the weakest relevant scope.

## Maintainer Responsibility

Maintainers should prefer under-claiming.

If there is uncertainty between `DRAFT` and `PARTIALLY_SUPPORTED`, keep
`DRAFT`.

If there is uncertainty between `PARTIALLY_SUPPORTED` and `SUPPORTED`, keep
`PARTIALLY_SUPPORTED`.

Promotion is not a reward for passing tests. It is a statement about evidence
quality and scope discipline.
