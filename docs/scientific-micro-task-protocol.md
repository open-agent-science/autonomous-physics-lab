# Scientific Micro-Task Protocol

## Purpose

A scientific micro-task is an atomic, self-contained scientific contribution
that any compatible agent can complete in approximately 5–30 minutes.

Unlike canonical `TASK-XXXX` tasks (which may span hours and produce
multiple artifacts), micro-tasks are designed to be:

- completed in a single focused agent session;
- independently verifiable by deterministic code;
- additive — many micro-tasks build toward a larger benchmark or dataset;
- overclaim-safe by design.

This protocol defines how micro-tasks are scoped, executed, and stored as
scientific memory.

## Relationship to Canonical Tasks

Micro-tasks are **not** standalone canonical `TASK-XXXX` items.

They are sub-atomic units. A canonical task may authorize a batch of
micro-tasks. Multiple micro-tasks may be bundled into one canonical task PR.

Example flow:

1. Canonical task `TASK-XXXX: Build physical constants verification track`
   authorizes 10 micro-tasks.
2. An agent picks one micro-task (e.g., verify fine-structure constant α).
3. The result is committed as a dataset entry or result artifact.
4. The canonical task is complete when all authorized micro-tasks pass.

## Output Types

A micro-task produces exactly one primary output:

| Type | Description |
|---|---|
| `formula-check` | Verify a known formula or constant numerically or symbolically |
| `hypothesis-entry` | Propose a new testable hypothesis in machine-readable form |
| `dataset-entry` | Add verified items to an existing challenge dataset |
| `approximation-probe` | Quantify where a known approximation breaks down |
| `empirical-catalog-entry` | Document an empirical regularity with falsification status |

## Micro-Task Specification Template

Each micro-task is described in a lightweight YAML block (not a full
canonical task file):

```yaml
micro_task_id: "<track-slug>/<short-id>"
track: "<track name>"
type: "<output type from table above>"
title: "<short title>"
status: READY  # READY | IN_PROGRESS | REVIEW_READY | DONE

input:
  description: "<what data or formula this task works with>"
  references:
    - "<dataset file, knowledge doc, or external standard>"

output:
  artifact: "<file path where result will be stored>"
  format: "<result format: yaml | md | json>"

acceptance_criteria:
  - "<deterministic check 1>"
  - "<deterministic check 2>"

claim_ceiling: "<maximum allowed claim — e.g. 'verified to 1e-6 from CODATA 2018'>"
```

## Execution Rules

1. Read the parent canonical task to understand track scope.
2. Pick one `READY` micro-task from the track's micro-task list.
3. Set status to `IN_PROGRESS`.
4. Produce the required output — code must be deterministic with no external
   API calls at runtime.
5. Verify the output satisfies all `acceptance_criteria`.
6. Set status to `REVIEW_READY` and record limitations.

Agents must not:

- execute more than one micro-task per session unless explicitly authorized;
- promote a micro-task result to a project-level claim automatically;
- claim discovery or global validity from a single micro-task result;
- skip deterministic code verification for `formula-check` or
  `approximation-probe` outputs.

## Verdict Vocabulary

For `formula-check` and `approximation-probe` outputs use:

- `VERIFIED` — result matches reference to stated tolerance;
- `FAILS_AT_TOLERANCE` — result diverges beyond tolerance; document where;
- `INVALID_DERIVATION` — symbolic derivation contains an error;
- `INCONCLUSIVE` — insufficient data or ambiguous reference.

For `hypothesis-entry` outputs use the lifecycle states from `AGENTS.md`:

- `PROPOSED` — new hypothesis, no code verification yet;
- `FORMALIZED` — hypothesis stated in testable mathematical form;
- `TESTING` — deterministic test is being run.

A hypothesis micro-task result must **never** use `VALID_IN_RANGE` or
`INTEGRATED` without a separate canonical verification task being completed
first.

## Claim Restrictions

All restrictions from `AGENTS.md` and `docs/agent-task-protocol.md` apply.

Additional micro-task restrictions:

- Every `formula-check` result must state the reference source and tolerance.
- Every `hypothesis-entry` must state falsification conditions explicitly.
- Every `empirical-catalog-entry` must include a known counter-example search
  or state why none was performed.
- Range limits and assumptions must be explicit in every output.

## Tracks

Tracks group related micro-tasks. Each track is proposed and authorized as a
canonical task. Current planned tracks:

| Track slug | Domain | Status |
|---|---|---|
| `constants-verification` | Fundamental physical constants | proposed |
| `approximation-probes` | Approximation breakdown quantification | proposed |
| `hypothesis-register` | New testable hypotheses | proposed |
| `empirical-regularities` | Empirical patterns with falsification status | proposed |

## Validation

Before committing a micro-task result run:

```bash
./scripts/validate_quick.sh
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

Micro-task PRs that only add dataset entries or planning docs may use the
lightweight validation path from `docs/task-proposal-protocol.md`.
