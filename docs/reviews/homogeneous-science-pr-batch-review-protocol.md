# Homogeneous Science PR Batch Review Protocol (TASK-0423)

A protocol for reviewing **batches of similar science PRs** efficiently during a
many-agent pilot **without weakening scientific review gates**. It lets a
maintainer process a homogeneous batch in one pass while preserving each PR's
own evidence, limitations, review tier, and review-agent verdict.

This protocol does **not** introduce automatic claim promotion, automatic merge
of scientifically ambiguous PRs, a dashboard, or an external review service. It
is a manual/agent-readable review discipline, layered on
[`../maintainer-review-agent.md`](../maintainer-review-agent.md) and
[`../result-promotion-protocol.md`](../result-promotion-protocol.md).

## What counts as a homogeneous batch

A batch is eligible for batch review only when **all** of the following hold:

- **Same campaign / lane** — every PR maps to the same campaign lane (see
  `campaigns/task-index.yaml`, TASK-0460).
- **Same task type** — e.g. all source triage, all residual-scout audits, all
  adversarial-control runs, all negative-result notes, or all evidence cards.
- **Same validation surface** — the PRs run the same validation commands against
  the same kind of artifact, so a reviewer can apply one mental model.
- **Disjoint write paths** — no two PRs in the batch modify the same file. Write
  surfaces must be non-overlapping (check `path_conflicts` in the lane index).

If any condition fails, review the PRs individually.

## Per-PR requirements (never relaxed in a batch)

Every PR in the batch must independently carry:

1. its own **review-agent verdict** (`MERGE_OK` / `NEEDS_CHANGES` / `BLOCKED`)
   from `scripts/apl_review_pr.py`;
2. its own **validation result** (commands reported and green, or CI green for
   the ci-aware lane);
3. its own **limitations** section;
4. its own task/proposal status correctness and accepted-output match.

Batch review changes only how the maintainer *sequences and records* these — it
never merges their gates.

## When batch review is forbidden

Do not batch-review when any PR in the set:

- mixes **artifacts from different campaigns** or different artifact classes;
- performs a **result promotion** to a higher review tier;
- performs a **prediction reveal / scoring** (`PRED-*` reveal);
- **edits a claim** (`claims/*.md`) or promotes claim status;
- has a **conflicting write surface** with another PR in the set;
- carries **overclaim** or repository-safety risk flagged by review.

Any such PR leaves the batch and gets individual deep review.

## Publication PRs in a batch

Result/prediction **publication** PRs may be batched **only** when they all share:

- the **same artifact class** (e.g. all `RESULT-*` negative results, or all
  `PRED-*` registrations — never mixed);
- the **same review tier** (e.g. all `AGENT_PUBLISHED`);
- **separate Gate A / Gate B evidence blocks** per PR, each self-contained.

Mixed-class, mixed-tier, or reveal-scoring publication PRs are never batched.

## Batch summary artifact

A batch review produces one lightweight summary (a PR comment or a
`docs/reviews/<lane>-batch-<date>.md` note). One row per PR:

```markdown
# Homogeneous Science PR Batch Review — <lane> — <YYYY-MM-DD>

- Batch eligibility: same campaign / same task type / same validation surface / disjoint write paths — confirmed
- Forbidden conditions present: none

| PR | Task | Verdict | Risk | Changed artifacts | Follow-up action |
| --- | --- | --- | --- | --- | --- |
| #123 | TASK-0xxx | MERGE_OK | low | docs/campaigns/.../source-card.md | merge after CI green |
| #124 | TASK-0yyy | NEEDS_CHANGES | medium | results/EXP-00zz/... | request limitations detail |

- Batch decision: merge MERGE_OK rows after CI green; return NEEDS_CHANGES/BLOCKED rows to authors
- Claims promoted in this batch: none (claim endorsement stays out of batch scope)
```

## Decision rules

- Merge only the rows whose individual verdict is `MERGE_OK` **and** whose CI is
  green; never merge a row to "keep the batch together".
- Any `NEEDS_CHANGES` / `BLOCKED` row is returned to its author and does not hold
  up the rest of the batch.
- No claim is promoted and no scientifically ambiguous PR is merged as a side
  effect of batch processing.
