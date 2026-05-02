# Project Status

## Current Stage

`v0.1-private-alpha` in validation

## Current Goal

Private contributor pilot plus one measurable scientific result, without making
the repository public yet.

Current working slices:

- `Pendulum Formula Discovery`
- `Damped Oscillator Regime Verification`

## Completed

- pendulum formula discovery workflow;
- exact pendulum reference simulator;
- deterministic candidate formula fitting and scoring;
- verification-backed pendulum checks;
- theory-aware pendulum candidate family with canonical `RUN-0002` comparison artifacts;
- run-based result artifact generation;
- public memory registry for hypothesis, experiment, claim, task, result, and knowledge;
- repository-wide validation, referential integrity checks, result input-hash drift detection, and immutable run-input snapshots;
- strict repository validation with severity-based integrity checks for orphan results, canonical run artifacts, input snapshots, and hygiene issues;
- basic CI configuration with lint, tests, example run, and repository validation;
- damped-oscillator exact-solution benchmark with run-based artifacts;
- contributor workflow documentation and GitHub issue and PR templates.
- patch-style claim and knowledge review artifacts with maintainer-facing review summaries.
- machine-readable `review_metadata.yaml` companion files for patch-style artifacts with a JSON Schema contract.
- shared agent task board, strategy file, and operating model for multi-agent handoff.
- canonical `docs/agent-task-protocol.md` execution rules for task pickup, branch naming, commit messages, PR titles, validation, and task-state transitions across Codex, Claude Code, humans, and other agents.
- pendulum hypothesis gauntlet: 100 deterministic candidates (`RUN-0003` / `RESULT-0004`) with full leaderboard, failure-mode classification, and best model `model_t4_x1` at VALID_IN_RANGE.
- numerical accuracy and tolerance policy documenting the difference between approximation residuals, coefficient-rounding effects, and reference-computation error.
- `TASK-0011` precision-audit artifacts for `RUN-0003`, classifying the reported `3.1e-4` in-range error as model residual rather than elliptic-reference precision drift or six-decimal coefficient rounding.
- private-alpha contribution and release-gating documentation for invited
  branch-based contributors.

## Current Verification Checks

Pendulum:

- small-angle limit;
- small-angle exact-window agreement;
- small-angle curvature agreement;
- upper-range exact-window agreement;
- near-separatrix extrapolation diagnostic (non-gating);
- separatrix asymptotic-alignment diagnostic (non-gating);
- separatrix logarithmic growth-rate diagnostic (non-gating);
- evenness;
- monotonicity;
- dimensional consistency;
- known small-angle coefficient comparison.

Damped oscillator:

- regime classification;
- initial-condition recovery;
- underdamped energy decay;
- oscillatory vs non-oscillatory behavior;
- dimensional consistency;
- `c -> 0` undamped-limit check;
- underdamped envelope decay-rate check;
- critical damping boundary check;
- overdamped asymptotic tail check.

## Ready Now

- `python3 -m ruff check .`
- `python3 -m pytest`
- `python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum`
- `python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped`
- `python3 -m physics_lab.cli validate-repo .`
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`
- `python3 -m physics_lab.cli status .`
- [architecture-index.md](./architecture-index.md) for fast contributor and LLM handoff.
- [strategy.md](./strategy.md), [agent-operating-model.md](./agent-operating-model.md), and [../tasks/ACTIVE.md](../tasks/ACTIVE.md) for the shared task protocol.
- [agent-task-protocol.md](./agent-task-protocol.md) for the canonical branch, commit, PR, and task-state rules.
- verification-first contributor workflow and GitHub issue templates.
- maintainer-facing claim promotion policy.
- [private-contributor-pilot.md](./private-contributor-pilot.md) for invited contributors.
- [public-release-gates.md](./public-release-gates.md) for the conditions required before going public.
- [github-branch-protection-plan.md](./github-branch-protection-plan.md) for staged PR discipline.

## Not Ready Yet

- automated external agent execution and review flow;
- literature ingestion;
- public dashboard;
- theory graph.

## Current Risks

- `runner.py` must stay a thin dispatcher so workflow logic does not drift back into one file.
- Canonical artifacts under `results/` can become stale if contributors run examples without `--output-dir`.
- The result schema is shared by both benchmarks, so benchmark-specific semantics still need careful wording.
- Public alpha is stable for two slices, but not yet broad enough for a wider “many benchmark” claim.
- The private contributor workflow still needs a dry run across multiple PRs before public exposure.
- Claim files still need deliberate human review before moving from draft text to stronger public statuses.
- Claim suggestions are generated automatically, but promotion decisions still rely on maintainer judgment.
- Theory-aware pendulum candidates improve separatrix behavior, but the overall best verdict still remains range-limited rather than globally valid.
- Public-facing pendulum wording should continue to preserve the distinction between approximation residual, range-limited validation, and symbolic exactness.

## Public Repo Status

Repository is still private while the contributor pilot and the next visible
scientific result are being tested.

Future public-facing updates should stay gated by:

- local validation;
- GitHub Actions;
- `python3 -m physics_lab.cli validate-repo .`;
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`;
- [public-release-gates.md](./public-release-gates.md);
- honest roadmap, status, and task-board docs.

## Snapshot Utility

Use the repository snapshot script when you want a compact project state dump:

```bash
./scripts/apl_snapshot.sh
RUN_EXPERIMENT=1 ./scripts/apl_snapshot.sh
PYTHON_BIN=python3.11 ./scripts/apl_snapshot.sh
```

Recommended times to run it:

- after a meaningful Codex task;
- before making the repository public;
- before a tag or release;
- after roadmap or architecture changes;
- after schema or result-format changes;
- after adding a new benchmark.
