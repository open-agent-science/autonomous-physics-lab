# Contributing

Autonomous Physics Lab is a verification-first research codebase.

Contributions are welcome, but every scientific claim must stay reproducible,
reviewable, and linked to repository artifacts.

## Before Opening a PR

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml
python3 -m physics_lab.cli validate-repo .
```

For larger milestones, schema changes, roadmap updates, or public-release
prep, generate a repository snapshot:

```bash
./scripts/apl_snapshot.sh
RUN_EXPERIMENT=1 ./scripts/apl_snapshot.sh
PYTHON_BIN=python3.11 ./scripts/apl_snapshot.sh
```

## Contribution Rules

1. Do not submit unverifiable scientific claims.
2. Every result must link back to a hypothesis, experiment, and task.
3. Claims must not be promoted without reproducible evidence.
4. Prefer narrow, testable improvements over broad speculative changes.
5. Keep repository memory consistent: update `hypotheses/`, `claims/`,
   `experiments/`, `results/`, `knowledge/`, or `tasks/` when your change
   affects them.

## What To Avoid

- dashboards or web APIs in the current alpha phase;
- LLM-only reasoning without deterministic validation;
- overclaiming scientific significance;
- unrelated infrastructure expansion before verification quality improves.

## Helpful Starting Points

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [docs/status.md](docs/status.md)
- [docs/next-steps.md](docs/next-steps.md)
