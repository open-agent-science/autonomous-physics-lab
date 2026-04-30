# Architecture Index

## Purpose

This file is the fastest orientation map for the repository.

Use it when you need to understand:

- where to start reading;
- where benchmark logic lives;
- how public scientific memory is structured;
- which files matter when changing workflows, validation, or artifacts.

## Start Here

For a new contributor or a new LLM session, read in this order:

1. [README.md](../README.md)
2. [AGENTS.md](../AGENTS.md)
3. [docs/status.md](./status.md)
4. [docs/next-steps.md](./next-steps.md)
5. [CONTRIBUTING.md](../CONTRIBUTING.md)
6. [docs/contributing-workflow.md](./contributing-workflow.md)
7. [docs/claim-promotion-policy.md](./claim-promotion-policy.md)

## Core Code

### CLI

- `physics_lab/cli.py`
  - entrypoints for `run`, `validate`, `validate-repo`, and `status`

### Workflow Dispatch

- `physics_lab/workflows/runner.py`
  - thin dispatcher only
- `physics_lab/workflows/artifacts.py`
  - shared artifact paths, input hashing, immutable run snapshots

### Benchmark Workflows

- `physics_lab/workflows/pendulum.py`
  - `EXP-0001`
  - formula discovery, verification summaries, report generation
- `physics_lab/workflows/damped_oscillator.py`
  - `EXP-0002`
  - exact regime verification, report generation
- `physics_lab/workflows/claim_semantics.py`
  - cautious claim-status suggestion logic

### Scientific Engines

- `physics_lab/engines/simulation.py`
  - exact pendulum reference simulator
- `physics_lab/engines/formula_discovery.py`
  - deterministic pendulum candidate fitting
- `physics_lab/engines/verification.py`
  - pendulum verification checks
- `physics_lab/engines/damped_oscillator.py`
  - exact damped-oscillator dynamics
- `physics_lab/engines/symbolic.py`
  - symbolic and dimensional checks
- `physics_lab/engines/scoring.py`
  - error metrics and model scoring
- `physics_lab/engines/critic.py`
  - verdict classification helpers

## Registry and Validation

### Registry Loaders

- `physics_lab/registry/hypotheses.py`
- `physics_lab/registry/claims.py`
- `physics_lab/registry/experiments.py`
- `physics_lab/registry/examples.py`
- `physics_lab/registry/knowledge.py`
- `physics_lab/registry/results.py`
- `physics_lab/registry/tasks.py`
- `physics_lab/registry/agents.py`

### Validation

- `physics_lab/registry/validation.py`
  - schema-kind inference and shared validation helpers
- `physics_lab/registry/repository.py`
  - repository-wide validation
  - strict validation mode
  - referential integrity checks
  - canonical artifact integrity checks

### Schemas

- `physics_lab/schemas/`
  - JSON schemas for all structured artifacts

## Public Scientific Memory

### Registry Directories

- `hypotheses/`
- `experiments/`
- `claims/`
- `knowledge/`
- `tasks/`
- `agents/`
- `results/`

### Current Canonical Results

- `results/EXP-0001/RUN-0001/`
  - original pendulum benchmark run
- `results/EXP-0001/RUN-0002/`
  - theory-aware pendulum follow-up run
- `results/EXP-0002/RUN-0001/`
  - damped-oscillator regime verification run

Each canonical run should contain:

- `result.yaml`
- `metrics.json`
- `report.md`
- `claim_update.md`
- `knowledge_update.md`
- `inputs/`

## Examples

- `examples/pendulum.yaml`
- `examples/damped_oscillator.yaml`

Use `--output-dir` for routine runs so committed canonical artifacts stay clean.

## Tests

- `tests/test_pendulum.py`
  - pendulum workflow, CLI smoke, repo validation smoke
- `tests/test_damped_oscillator.py`
  - damped workflow, strict validation fixtures, claim/evidence semantics

## Documentation by Purpose

### Project State

- [docs/status.md](./status.md)
- [docs/next-steps.md](./next-steps.md)
- [docs/backlog.md](./backlog.md)
- [docs/implementation-plan.md](./implementation-plan.md)
- [docs/roadmap.md](./roadmap.md)

### Contribution and Review

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [docs/contributing-workflow.md](./contributing-workflow.md)
- [docs/claim-promotion-policy.md](./claim-promotion-policy.md)
- [docs/release-checklist.md](./release-checklist.md)

### Benchmark-Specific Notes

- [docs/notes/pendulum-separatrix-followup.md](./notes/pendulum-separatrix-followup.md)

## Adding a Benchmark

When planning a new benchmark, use this order:

1. Add `HYP-*`
2. Add `EXP-*`
3. Add `TASK-*`
4. Add or extend a workflow module under `physics_lab/workflows/`
5. Add or extend scientific engine helpers under `physics_lab/engines/`
6. Add an `examples/*.yaml` config
7. Add tests
8. Generate canonical `results/<experiment>/<run>/`
9. Update `claims/`, `knowledge/`, and status docs deliberately

## Rules of Thumb

- Keep `runner.py` thin.
- Prefer deterministic code over generated prose.
- Prefer range-aware claims over stronger-sounding but sloppy claims.
- Use `validate-repo --strict` before calling a structural change complete.
- Treat canonical artifacts as public scientific memory, not temporary output.
