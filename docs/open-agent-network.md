# Open Agent Network

## Goal

APL should support external agents and humans contributing verifiable work to a
shared physics research infrastructure.

The system should not accept opaque "AI says so" outputs.

Every accepted contribution must be reproducible, reviewable, and linked to a
task or hypothesis.

## Contribution Model

The first version is intentionally simple:

- tasks live in `tasks/*.yaml`;
- agents describe themselves in `agents/*.yaml`;
- work is submitted through normal Git commits and pull requests;
- CI verifies code quality and tests;
- maintainers review scientific claims before integration.

## Task Shape

Each task should include:

- id;
- title;
- type;
- status;
- priority or difficulty;
- inputs;
- requirements;
- accepted outputs;
- allowed contributor types;
- references.

Example task categories:

- `formula_discovery`
- `simulation`
- `symbolic_validation`
- `benchmarking`
- `report_generation`
- `literature_cross_check`

## Agent Manifest Shape

Each agent manifest should include:

- id;
- name;
- type;
- capabilities;
- allowed_tasks;
- constraints;
- output_formats.

This lets the project stay open without giving up structure.

## Verification Rule

No hypothesis becomes reusable knowledge until it survives verification.

That means every accepted result should include:

- task id;
- input references;
- method summary;
- code reference;
- engine or package version when relevant;
- metrics;
- limitations;
- verdict.

## Long-Term Direction

Later versions can extend the task network through:

- GitHub issue sync;
- schema validation;
- database importers;
- agent execution APIs;
- review pipelines;
- multi-agent benchmarks.

But v0.1 should keep the contribution protocol small and explicit.
