# Scientific Micro-Task Protocol

## Purpose

Scientific micro-tasks are the smallest campaign-facing scientific work units
that APL wants humans and coding agents to complete safely.

They exist to make spare token budgets and short contributor sessions useful
without requiring a new full benchmark implementation every time.

A micro-task should be:

- small enough to complete in one focused session;
- tied to an existing campaign or planning surface;
- explicit about limits, assumptions, and claim ceiling;
- safe to review in batches;
- useful even when it produces only a note, classification, or dataset entry.

## Relationship to Canonical Tasks

Micro-tasks do **not** replace canonical `TASK-XXXX` governance.

Rules:

- the queue files under `tasks/microtasks/` are campaign backlogs, not
  canonical task files;
- a maintainer may direct an agent to work from these queues when using spare
  time or token budget;
- one canonical task or one maintainer-approved PR may complete a small batch
  of related micro-tasks from the same campaign;
- agents should not create a new canonical `TASK-XXXX` for every tiny
  scientific subproblem.

Use canonical tasks for broad implementation, new benchmark machinery, schema
changes, or anything that materially changes repository architecture.

## Where The Queues Live

Campaign micro-task queues live in:

- `tasks/microtasks/README.md`
- `tasks/microtasks/pendulum-formula-falsification.yaml`
- `tasks/microtasks/particle-mass-relations.yaml`
- `tasks/microtasks/dimensional-analysis-validator.yaml`
- `tasks/microtasks/thought-experiment-consistency.yaml`
- `tasks/microtasks/diffusion-scaling.yaml`

These files are seed queues for contributor-facing scientific work.

## Append-Only Run Registry

Micro-task claims and outcomes are recorded separately from queue files so daily
parallel agents do not rewrite the same backlog entries. The registry lives in:

- `microtask_runs/README.md`
- `microtask_runs/MICROTASK-RUN-TEMPLATE.yaml`
- `microtask_runs/<queue-id>/MICROTASK-RUN-0001.yaml`

Before selecting a micro-task, check the queue file, recent open PRs, existing
`microtask_runs/` records, and related notes or results. Do not take an item
that is already claimed, in review, completed, or clearly duplicated by a
recent note.

Use the helper status view before starting a micro-task so agents do not repeat
work that is already represented by append-only run records:

```bash
python3 scripts/apl_microtask_pr_helper.py status --queue-id <queue-id>
python3 scripts/apl_microtask_pr_helper.py status --queue-id <queue-id> --json
```

Treat only `status: available` rows as selectable. Completed non-repeatable
items are unavailable even if the queue YAML does not carry an inline
`status: completed`; the helper derives that state from `microtask_runs/`.
Repeatable items should use `repeatable: true` or a `type` beginning with
`repeatable-`, and still need a novelty check before each new run.

Each run record should name the queue id, microtask id, status, claimant,
branch, PR when available, result note, verdict, review state, and metadata for
repeatable attempts. Keep records append-only; add a new run file instead of
editing queue entries for routine claims.

## Required Micro-Task Format

Each queue entry should include the fields below:

```yaml
- id: "PFF-001"
  campaign: "pendulum-formula-falsification"
  title: "Propose one even pendulum candidate family in x = sin^2(theta/2)"
  type: "formula-family-proposal"
  estimated_effort: "15-30 minutes"
  recommended_for:
    - codex
    - claude
    - human
  autonomy_level:
    - agent_can_complete
    - human_review_required
  expected_output: "Short markdown note or PR summary with assumptions, limits, and next deterministic check."
  validation:
    - "State why the candidate is dimensionless."
    - "State where the family is expected to fail or remain untested."
  risk_level: "low"
  forbidden_claims:
    - "exact symbolic proof"
    - "universal validity"
    - "discovery-level physics conclusion"
```

Recommended interpretation:

- `agent_can_complete` means a coding agent can finish the scoped work without
  waiting on a new engine feature;
- `human_review_required` means the result still needs maintainer or reviewer
  judgment before being treated as stable repository memory.

## Execution Rules

1. Start from one queue file only.
2. Prefer one small batch from one campaign per PR.
3. Keep the batch narrow enough that a reviewer can understand it quickly.
4. Do not widen the work into a new benchmark implementation.
5. Report limitations in every output.
6. If uncertainty remains, mark the output `REVIEW_NEEDED`.

Agents should prefer micro-tasks when:

- a human explicitly asks to use spare token or time budget;
- the session is too small for a large implementation task;
- the best next contribution is a campaign note, dataset addition, formula
  classification, or falsification-ready hypothesis stub.

Agents should avoid micro-tasks when:

- the work needs a new benchmark engine or validator implementation;
- the work changes canonical result artifacts;
- the work would implicitly promote a claim;
- the work crosses many campaigns at once.

## Batching Rules

One PR may complete a small batch of related micro-tasks when all of the
following are true:

- the micro-tasks come from the same campaign queue;
- the outputs fit one coherent review story;
- limitations stay explicit;
- no result artifact churn is introduced.

Good batch examples:

- three pendulum candidate-family notes;
- two particle-mass data audits plus one narrow baseline comparison note;
- five dimensional-analysis challenge entries from the same topic family.

Bad batch examples:

- mixing pendulum, Koide, and thought-experiment work in one PR;
- mixing queue work with a new validator implementation;
- treating a batch of notes as evidence for a stronger claim.

## Output Discipline

Micro-task outputs should usually be one of:

- a queue-driven note or planning artifact;
- a narrow dataset or challenge-set addition;
- a scoped classification note;
- a deterministic calculation summary;
- a falsification-ready proposal with explicit assumptions.

Every output should include:

- input references;
- method;
- code references when executable checks were used;
- metrics or qualitative review criteria;
- failure mode;
- limitations;
- novelty check against existing notes, results, and `microtask_runs/`;
- verdict or review state.

If the result is uncertain, use `REVIEW_NEEDED` rather than forcing a stronger
scientific conclusion.

For repeatable formula-search or benchmark attempts with withheld targets, use
[blind-holdout-benchmark-protocol.md](./blind-holdout-benchmark-protocol.md).
Even a small microtask can preserve a pre-reveal note, frozen command, reveal
record, metrics, and limitations.

## Claim Restrictions

Micro-task work must not:

- promote a `CLAIM-*` status automatically;
- treat a local observation as a repository-level conclusion;
- present narrow benchmark notes as universal theory statements;
- use marketing language in place of scientific scope.

The safe default is conservative wording plus explicit limitations.

## Validation

For queue-definition and documentation work, run:

```bash
./scripts/validate_quick.sh
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
./scripts/apl_review_bundle.sh
git diff --exit-code
```

Generated task-view synchronization (`docs/task-views/*.md`)
runs automatically via the post-merge `Sync Active Board` GitHub Action;
agents do not need to commit regenerated versions of those files from a
micro-task PR. `python3 -m physics_lab.cli sync-active-board .` remains
available for explicit maintainer audits.

For future micro-task execution PRs, use the validation appropriate to the
changed artifacts, but keep the same safety posture: deterministic checks, no
claim promotion, and explicit review notes.

## PR Packaging

For a single micro-task item, use:

`agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug>`

For one small batch from one queue, use:

`agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>`

Use the lowercased GitHub username as `contributor-id` when available;
otherwise use a stable maintainer-approved short id.

In both cases, keep the PR title in the same queue-oriented form:

`microtask(<queue-id>): <short description>`

If you want a deterministic scaffold instead of writing the branch, title, and
PR body by hand, use:

```bash
python3 scripts/apl_microtask_pr_helper.py scaffold \
  --queue-id <queue-id> \
  --contributor-id <contributor-id> \
  --agent-id <agent-id> \
  --slug <short-slug> \
  --description "<short description>"
```

For a single microtask item, also pass `--microtask-id <microtask-id>`. For a
small batch from one queue, pass `--microtask-ids <id1> <id2> ...`.

When opening the PR, use the repository PR template, delete unused sections,
and fill in queue metadata explicitly. Do not leave `TASK-XXXX` placeholders or
generic fake branch examples in a microtask PR body.

Before asking for maintainer review, you can run a local preflight check on the
prepared PR metadata:

```bash
python3 scripts/apl_microtask_pr_helper.py preflight \
  --branch "<current-branch>" \
  --title "microtask(<queue-id>): <short description>" \
  --body-file /tmp/pr-body.md
```

This preflight does not replace repository validation or maintainer review. It
only checks common microtask PR mistakes: branch/title shape, leftover template
placeholders, and missing review-bundle reminder/context.
