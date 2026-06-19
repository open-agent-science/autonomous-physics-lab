# CLAIM-0005 Dimensional Validator Evidence Handoff

- Task: `TASK-0768`
- Claim: `CLAIM-0005`
- Campaign: Dimensional Analysis Validator
- Prepared for: maintainer Gate C review
- Task verdict: `INCONCLUSIVE`

## Executive Decision

`CLAIM-0005` is eligible for a maintainer decision, but the evidence does not
support an automatic or unqualified promotion.

The conservative default is **keep `DRAFT`**. The frozen 50-item
`RESULT-0007` baseline supports the claim's current benchmark-limited statement,
but it is a pre-tier `LEGACY_UNTIERED` result rather than explicitly
`AGENT_VALIDATED` evidence. The newer 74-item `RESULT-0020` result cannot be
used as validated claim support: Gate A passed, its dimensional-consistency
metrics replayed with zero numeric drift, but Gate B returned
`CONTESTED_RESULT` because the recorded command does not regenerate three
hand-authored publication checks.

No claim, result, knowledge, or golden-result artifact is changed by this
handoff.

## Evidence Inventory

| Evidence | Scope and result | Review tier | Gate state | Eligible use |
| --- | --- | --- | --- | --- |
| [`RESULT-0007`](../../results/EXP-0006/RUN-0006/result.yaml) | Frozen internally curated 50-item MVP; 49/50 agreement (98%); `VALID` | `LEGACY_UNTIERED` | Predates explicit Gate A/B records; current-source replay is documented against the frozen input | Primary evidence for the existing 50-item claim scope, subject to maintainer acceptance |
| [`RESULT-0020`](../../results/EXP-0006/RUN-0007/result.yaml) | Frozen 74-item live snapshot; 74/74 agreement (100%); `VALID` | `AGENT_PUBLISHED` | Gate A pass; Gate B `CONTESTED_RESULT` | Context only; replay-needed and not eligible as `AGENT_VALIDATED` claim support |
| [`TASK-0766` replay note](dimensional-result-0020-gate-b-contested-replay.md) | Independent replay reproduced 16 numeric metrics with maximum absolute drift `0.0` and unchanged verdict | Review note; result tier unchanged | Gate B contested on packaging provenance | Supports the distinction between reproduced scientific core and incomplete end-to-end artifact reproduction |

### AGENT_VALIDATED Evidence

None is currently recorded for `CLAIM-0005`.

`RESULT-0007` must not be relabelled `AGENT_VALIDATED`: it is classified as
`LEGACY_UNTIERED` in the scientific-memory review-tier index. `RESULT-0020`
must not be relabelled `AGENT_VALIDATED`: its Gate B attempt was contested and
the result remains `AGENT_PUBLISHED`.

### Replay-Needed Evidence

`RESULT-0020` remains replay-needed. Its deterministic dimensional-classification
core reproduced cleanly:

- 74 parsed items;
- 74/74 agreement with curated expected labels;
- zero inconclusive rows;
- unchanged `VALID` verdict;
- zero numeric drift across the 16 compared metrics.

The blocker is packaging provenance. The committed result contains
`zero_disagreement_ledger`, `frozen_input_checksum`, and
`protected_result_not_rewritten` checks that its recorded run command does not
emit. Gate B therefore cannot establish end-to-end reproduction of the
published artifact.

## Claim Scope Check

The current claim references only `RESULT-0007` and is explicitly restricted
to the 50-item `DA-CHALLENGE-001` benchmark. That scope matches its primary
evidence.

The 74-item `RESULT-0020` snapshot is a different frozen scope. It must not be
silently added to the claim, used to replace the 49/50 metric, or treated as a
generalization result. Any future claim edit that references `RESULT-0020`
requires a successful Gate B resolution and a separate maintainer review of the
scope change.

## Wording Ceiling

The strongest currently supportable wording is:

> On the frozen, internally curated 50-item DA-CHALLENGE-001 benchmark, the
> APL SI-focused dimensional-analysis validator agreed with 49 of 50 expected
> labels (98%). This is benchmark-limited evidence for dimensional-consistency
> classification, not evidence that formulas are empirically correct or
> physically valid.

Do not claim that the validator:

- proves empirical or numerical correctness;
- catches arbitrary invalid physics formulas;
- generalizes beyond the frozen curated benchmark;
- performs general symbolic reasoning;
- supports natural-unit or Gaussian-unit formulas;
- detects semantically empty but dimensionally balanced formulas unaided.

## Maintainer Options

### Option 1: Keep `DRAFT` (recommended)

Use this option while no explicitly `AGENT_VALIDATED` result supports the
claim. It preserves the current accurate 50-item scope and avoids treating a
legacy tier or a contested Gate B replay as stronger evidence than recorded.

### Option 2: Clarify wording while keeping `DRAFT`

Replace broad phrases such as "correctly classifies physics formulas" with the
benchmark-limited wording above. This is a semantic cleanup only and does not
change evidence strength.

### Option 3: Move to `PARTIALLY_SUPPORTED` in a maintainer-authored change

This is defensible only if the maintainer independently accepts
`RESULT-0007`'s frozen replay chain and keeps the statement limited to the
internally curated 50-item SI-focused benchmark. `RESULT-0020` must not be
cited as validated support for this decision.

`SUPPORTED` is not recommended. The benchmark is internally curated, contains
a documented semantic limitation, excludes natural/Gaussian-unit formulas,
and has no external replication.

### Option 4: Request replay repair before any status change

Choose a reproducible packaging path for `RESULT-0020`, re-run Gate B, and
return to claim review only after the result is either upgraded to
`AGENT_VALIDATED` or remains explicitly contested.

## Limitations And Blockers

- Both challenge sets are internally curated; no external laboratory or
  independent external benchmark validation is recorded.
- Dimensional agreement is a software/convention benchmark, not a measurement
  of physical truth.
- The validator cannot reject all semantically empty dimensionless formulas.
- The supported unit surface is SI base units plus common derived units.
- `RESULT-0007` has no explicit modern Gate B tier.
- `RESULT-0020` is blocked from `AGENT_VALIDATED` by non-reproducible
  publication-check packaging.
- Gate C claim status transitions remain maintainer-only.

## Output Routing

- Task verdict: `INCONCLUSIVE` for claim promotion readiness; the evidence is
  sufficient for a maintainer decision but not for automatic promotion.
- Canonical destination: this review note.
- Review tier: no artifact tier change; `RESULT-0007` remains
  `LEGACY_UNTIERED`, and `RESULT-0020` remains `AGENT_PUBLISHED`.
- Gate A: `RESULT-0020` passed its publication gate.
- Gate B: `RESULT-0020` is `CONTESTED_RESULT`; replay is still needed after
  packaging repair.
- Claim impact: evidence handoff only; `CLAIM-0005` remains unchanged and
  `DRAFT`.
- Knowledge impact: none.
- Result and golden impact: none.
- Publication blocker: no explicitly `AGENT_VALIDATED` result supports a
  stronger claim, and the 74-item artifact is not reproducible end to end from
  its recorded command.

## Verdict

`KEEP_DRAFT_RECOMMENDED`: maintain the exact 50-item benchmark ceiling unless
the maintainer accepts a narrowly worded `PARTIALLY_SUPPORTED` transition based
only on `RESULT-0007`. Treat `RESULT-0020` as reproduced-core but
replay-needed evidence until its packaging provenance is repaired and Gate B
passes.
