# Microtask Scaling Readiness Note

Task: `TASK-0111`  
Status: planning note  
Scope: scientific microtask flow for low-parallelism daily agent work

## Question

Can the current scientific microtask system support a realistic flow where a
few agents may work in parallel and roughly 20 agents per day each spend
10-15 minutes on useful scientific work?

## Current Inventory

As of this note, the repository has 5 microtask queues:

| Queue | Status | Seed items | Already represented in notes/results | Remaining seed items |
| --- | --- | ---: | ---: | ---: |
| `pendulum-formula-falsification` | `active` | 10 | 3 | 7 |
| `particle-mass-relations` | `active_with_narrow_results` | 10 | 5 | 5 |
| `dimensional-analysis-validator` | `planning_complete_implementation_pending` | 10 | 5 | 5 |
| `thought-experiment-consistency` | `planning_active` | 5 | 0 | 5 |
| `diffusion-scaling` | `planning_only_future_campaign` | 5 | 0 | 5 |

Total seed items: `40`. Roughly `13` are already represented in
campaign notes or result-adjacent documentation, leaving about `27` obvious
seed items.

This is enough for a short private contributor wave, but not enough for a
steady 20-agent/day work loop unless the queues expand and completed/claimed
state becomes easier to inspect.

## Batch Size Guidance

Single microtasks are still the safest default when:

- the output is interpretation-heavy;
- the task touches claim wording, result interpretation, or source ambiguity;
- the agent is new to the repository;
- the microtask uses a medium-risk queue item.

Small batches are more efficient when context-gathering dominates the work.
Recommended batch sizes:

| Work type | Suggested batch size | Rationale |
| --- | ---: | --- |
| Dataset or challenge entries in the same queue | `3-5` items | One context pass can produce multiple homogeneous artifacts. |
| Formula-family proposals in one campaign | `2-3` items | Shared notation and benchmark context reduce overhead. |
| Candidate comparison or failure-mode notes | `1-2` items | Interpretation risk rises quickly. |
| Source-aware particle-mass audits | `1-2` items | Source ambiguity and wording risk are higher. |
| Thought-experiment formalization | `1` item | Assumption drift is easy and should stay reviewable. |
| Repeatable formula-search attempts | `3-10` attempts per PR, one campaign only | Each attempt should be mechanically logged with inputs, score, and verdict. |

A useful rule of thumb: if the PR body needs more than one short paragraph per
item to explain scope, split the batch.

## Needed Queue Expansion

The current queues should be treated as seed queues, not a durable daily
throughput pool. To support 20 short agent sessions per day, APL should target
at least:

- `150-250` ready microtasks across active campaigns;
- at least `50` low-risk items that require no external source lookup;
- at least `50` repeatable deterministic jobs where agents can try a new
  formula, dataset slice, or falsification condition and record the outcome;
- at least `20` source-aware audit tasks for humans or stronger review agents.

Recommended new or expanded queues:

1. `pendulum-repeatable-formula-search`
   - repeated candidate-family attempts;
   - deterministic scoring against existing pendulum references;
   - record failures as useful negative search memory.
2. `approximation-breakdown-probes`
   - one approximation, one exact reference, one threshold;
   - good for low-risk deterministic work.
3. `physical-constants-verification`
   - one constant, one source, one uncertainty or unit audit;
   - source-aware but mechanically bounded.
4. `hypothesis-register-expansion`
   - one hypothesis entry, one claim ceiling, one falsification route;
   - useful when no engine work is needed.
5. `negative-result-registry`
   - one failed relation or invalid candidate, one reproducible reason;
   - builds public memory without overclaiming.

## Repeatable Scientific Work Loop

APL should support a loop where an agent can:

1. inspect what was already tried;
2. propose one new candidate or parameter slice;
3. run a deterministic check;
4. store the result as either a success, limitation, or negative result;
5. open a narrow PR with machine-readable metadata.

For formula search, each attempt should record:

- campaign id;
- candidate formula or generator seed;
- input references;
- fitting or evaluation method;
- train/test range;
- metrics;
- failure mode;
- verdict;
- whether the attempt is novel relative to existing stored attempts.

This is scientifically valuable even when most attempts fail. Failed attempts
reduce rediscovery loops and help future agents avoid retrying the same idea.

## Infrastructure Gap

The current queue files do not encode execution state. Agents can read the
queue, but they cannot reliably know whether another non-local agent has
claimed the same item unless they inspect recent PRs and notes manually.

The missing layer is a microtask registry or run log with fields such as:

- `microtask_id`
- `queue_id`
- `status`
- `claimed_by`
- `claimed_at`
- `branch`
- `pr`
- `result_note`
- `verdict`
- `review_state`

The registry should avoid becoming a merge-conflict hotspot. Prefer append-only
run records or per-run files over rewriting the queue files for every claim.

## Recommendation

Create a canonical READY task to implement microtask scale readiness:

- batch-selection protocol for daily short-agent work;
- append-only run/claim registry;
- repeatable formula-search task pattern;
- expanded seed queues for deterministic repeatable work;
- validation/review helper support for detecting duplicate claimed/completed
  microtasks.

This should be infrastructure and workflow work only. It should not promote
claims, add a database, or introduce autonomous merge behavior.

Follow-up implementation task: `TASK-0112`.
