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
- limitations;
- verdict or review state.

If the result is uncertain, use `REVIEW_NEEDED` rather than forcing a stronger
scientific conclusion.

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
python3 -m physics_lab.cli sync-active-board .
./scripts/apl_review_bundle.sh
git diff --exit-code
```

For future micro-task execution PRs, use the validation appropriate to the
changed artifacts, but keep the same safety posture: deterministic checks, no
claim promotion, and explicit review notes.

## PR Packaging

For a single micro-task item, use:

`agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug>`

For one small batch from one queue, use:

`agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>`

In both cases, keep the PR title in the same queue-oriented form:

`microtask(<queue-id>): <short description>`

When opening the PR, use the repository PR template, delete unused sections,
and fill in queue metadata explicitly. Do not leave `TASK-XXXX` placeholders or
generic fake branch examples in a microtask PR body.
