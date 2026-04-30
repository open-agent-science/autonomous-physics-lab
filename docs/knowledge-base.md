# Knowledge Base

## Goal

The repository should act as a public scientific memory, not just as a codebase.

Every important scientific artifact should have a stable, reviewable, versioned
representation in Git.

## Primary Directories

```text
hypotheses/
claims/
experiments/
results/
knowledge/
tasks/
agents/
```

## Object Types

### Hypothesis

An unverified or partially verified proposal.

Contains:

- id;
- title;
- domain;
- status;
- statement;
- formula;
- assumptions;
- variables;
- linked evidence;
- verdict summary.

### Claim

A statement supported by one or more results.

Contains:

- claim statement;
- evidence references;
- scope or validity range;
- confidence or caution note;
- links to experiments and knowledge notes.

### Experiment

A reproducible procedure for testing a hypothesis.

Contains:

- experiment id;
- target hypothesis;
- method;
- parameter ranges;
- candidate model families;
- artifact output locations.

### Result

The output of a specific experiment run.

Contains:

- metrics;
- report;
- plots or tables;
- engine version;
- method summary;
- verdict;
- limitations.

### Knowledge

Reviewed, reusable project memory for a topic.

Contains:

- concise explanation of known facts;
- linked hypotheses and claims;
- known limits of current models;
- next open questions.

### Task

A structured unit of future work that can be executed by humans or agents.

Contains:

- task id;
- title;
- type;
- status;
- inputs;
- requirements;
- accepted outputs;
- references.

### Agent

A capability manifest for a contributor agent.

Contains:

- agent id;
- capabilities;
- allowed task types;
- constraints;
- accepted output formats.

## Hypothesis Lifecycle

Use these states:

- PROPOSED
- FORMALIZED
- TESTING
- VALID_IN_RANGE
- PARTIALLY_VALID
- FALSIFIED
- OVERFITTED
- INCONCLUSIVE
- INTEGRATED

These states matter because most useful physical models are valid only inside a
defined regime, not universally.

## Repository Conventions

- Use stable ids such as `HYP-0001`, `EXP-0001`, `TASK-0001`.
- Keep scientific source files human-readable.
- Prefer YAML for structured registry objects.
- Prefer Markdown for claims, knowledge notes, and reports.
- Link artifacts explicitly by id.
- Avoid implicit state hidden in code or notebooks.

## Public-Alpha Starter Set

The current public memory set should include:

- `HYP-0001` for pendulum amplitude correction;
- `EXP-0001` for pendulum formula discovery;
- `CLAIM-0001` for pendulum period amplitude correction;
- `TASK-0001` for the original pendulum approximation search;
- `TASK-0003` for the theory-aware near-separatrix pendulum extension;
- `RESULT-0001` for the first canonical pendulum run;
- `RESULT-0003` for the theory-aware pendulum comparison run;
- a pendulum knowledge note under `knowledge/classical_mechanics/`;
- `HYP-0002` for damped oscillator regime verification;
- `EXP-0002` for damped oscillator regimes;
- `CLAIM-0002` for damped oscillator regime structure;
- `TASK-0002` for exact damped-oscillator verification;
- `RESULT-0002` for the first canonical damped-oscillator run;
- a damped-oscillator knowledge note under `knowledge/classical_mechanics/`.
