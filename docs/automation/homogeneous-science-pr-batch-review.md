# Homogeneous Science PR Batch Review Mode

Use this file when a many-agent pilot produces a wave of **similar** science PRs
and the maintainer wants to clear them in one efficient pass without weakening
scientific review gates.

This file is intended to be readable by a human, a coding agent, or a future
automation runner. The authoritative rules live in
[`../reviews/homogeneous-science-pr-batch-review-protocol.md`](../reviews/homogeneous-science-pr-batch-review-protocol.md);
this file is the operating mode that applies them.

## Purpose

Reduce review backlog during a high-throughput agent wave by grouping
**same-campaign, same-type, same-validation-surface, disjoint-write-path** PRs
into one review pass — while keeping every PR's own verdict, validation,
limitations, and review tier intact.

## Trigger style

Use this mode when many open PRs share a shape, for example:

- a batch of source-triage or dataset-audit PRs from one campaign;
- a batch of residual-scout or adversarial-control runs from one campaign;
- a batch of negative-result notes or evidence cards from one campaign.

Do **not** use this mode for mixed-campaign work, result promotion, prediction
reveal scoring, claim edits, or any PR flagged for deep review.

## Inputs

- current `main`;
- the open PR list filtered to one campaign lane (`campaigns/task-index.yaml`);
- each PR's review-agent verdict (`scripts/apl_review_pr.py`).

## Sweep steps

1. **Group** open PRs by campaign lane and task type using the lane index.
2. **Check batch eligibility** against the four homogeneity conditions; drop any
   PR that fails into the individual-review queue.
3. **Check forbidden conditions** (mixed campaigns/classes, result promotion,
   prediction reveal, claim edits, conflicting write surfaces, overclaim/safety
   risk); pull any matching PR out for individual deep review.
4. **Run per-PR review** so each PR still has its own verdict, validation result,
   and limitations — batching does not merge these gates.
5. **Record one batch summary** (PR, task, verdict, risk, changed artifacts,
   follow-up) using the template in the protocol doc.
6. **Decide per row**: merge only `MERGE_OK` rows with green CI; return
   `NEEDS_CHANGES` / `BLOCKED` rows to their authors; promote no claims.

## Boundaries

- No automatic claim promotion.
- No automatic merge of scientifically ambiguous PRs.
- No dashboard or external review service.
