# Autonomous Physics Lab

Generate. Simulate. Falsify. Reuse.

Autonomous Physics Lab (APL) is an open-source infrastructure for generating,
testing, simulating, falsifying, and reusing physics hypotheses.

APL is not a chatbot. It is a public verification engine for physics ideas.

## Positioning

The long-term goal is not to claim a "theory of everything" from day one.
The goal is to build infrastructure for systematic theory search in physics.

The project combines three cores:

1. A hypothesis engine for proposing and testing candidate formulas or models.
2. A public knowledge base for storing hypotheses, claims, experiments, and results.
3. An open agent task network so humans and external agents can contribute reproducible work.

## First MVP

The first MVP is `Pendulum Formula Discovery`.

It should:

1. Generate exact pendulum period ratio data.
2. Fit simple approximation families.
3. Compare candidate models.
4. Score accuracy and complexity.
5. Produce a reproducible Markdown report.

## Repository Shape

```text
autonomous-physics-lab/
  AGENTS.md
  CODEX_TASK.md
  README.md

  physics_lab/
    engines/
    registry/
    schemas/
    workflows/

  hypotheses/
  claims/
  experiments/
  results/
  knowledge/
  tasks/
  agents/
  docs/
  tests/
```

## Status

The repository is currently in foundation stage:

- architecture and documentation are being set up;
- the public knowledge layout is defined;
- the first scientific workflow is the next implementation target.

See [docs/architecture.md](/Users/roman/Documents/Autonomous%20Physics%20Lab/docs/architecture.md),
[docs/roadmap.md](/Users/roman/Documents/Autonomous%20Physics%20Lab/docs/roadmap.md), and
[docs/implementation-plan.md](/Users/roman/Documents/Autonomous%20Physics%20Lab/docs/implementation-plan.md).
