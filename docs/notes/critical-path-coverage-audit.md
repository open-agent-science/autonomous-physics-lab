# Critical Path Coverage Audit

**Task:** `TASK-0215`
**Status:** report-only baseline

## Scope

This note records the first coverage posture for APL's critical paths. It does
not set a fail-under threshold and does not define 100% coverage as a goal.

Coverage should first be used to identify unprotected critical behavior:
repository validation, scientific-memory integrity checks, maintainer review,
closeout and snapshot helpers, mission control, Scientific Campaign Curator,
nuclear workflows, and proposal / agent-run registries.

## Coverage Command

Use the documented command in [../testing.md](../testing.md). It measures
`physics_lab` and the Python `scripts/` directory with branch coverage enabled.

The priority script rows to inspect first are:

- `scripts/apl_review_pr.py`
- `scripts/apl_closeout_task.py`
- `scripts/apl_closeout_sweep.py`
- `scripts/apl_mission.py`
- `scripts/apl_campaign_curator.py`
- `scripts/apl_microtask_pr_helper.py`

Shell scripts such as `scripts/apl_snapshot.sh` and
`scripts/apl_review_bundle.sh` are excluded from Python coverage and should be
covered by targeted smoke or text-regression tests where useful.

## Measured Baseline

Measured on `2026-05-13` with the command documented above.

The report-only baseline is `78%` total coverage across `physics_lab` and
Python `scripts/`, with branch coverage enabled:

- `8,481` statements
- `1,557` missing statements
- `2,442` branches
- `528` partial branches

The full coverage command produced the HTML report at `_coverage/html` but
exited non-zero because twelve pre-existing, non-coverage failures remained in
the Windows suite:

- `tests/test_anharmonic_oscillator.py::test_cli_run_anharmonic_smoke`
- `tests/test_damped_oscillator.py::test_cli_run_damped_oscillator_smoke`
- `tests/test_g2_formula_search.py::test_cli_run_artifacts_use_consistent_primary_formula`
- `tests/test_nuclear_mass_baselines.py::test_cli_run_nuclear_mass_baseline_smoke`
- `tests/test_pendulum.py::test_runner_generates_run_based_artifacts`
- `tests/test_pendulum.py::test_cli_run_smoke`
- `tests/test_pendulum.py::test_cli_validate_hypothesis_smoke`
- `tests/test_pendulum.py::test_cli_validate_result_smoke`
- `tests/test_pendulum.py::test_validate_repository_smoke`
- `tests/test_pendulum.py::test_cli_validate_repo_smoke`
- `tests/test_pendulum.py::test_cli_status_smoke`
- `tests/test_pendulum.py::test_cli_run_gauntlet_smoke`

No coverage gate was added.

## Windows Stabilization Follow-Up

`TASK-0239` re-ran the documented Windows failure set on `2026-05-14` and
converted the known failures into deterministic test behavior. With a
workspace-local pytest temp base, the full branch-aware coverage command now
exits cleanly on Windows:

```powershell
python -m pytest --basetemp=.pytest-basetemp --cov=physics_lab --cov=scripts --cov-branch --cov-report=term-missing:skip-covered --cov-report=html:_coverage/html
```

Observed result:

- `357 passed`
- `78%` total coverage across `physics_lab` and Python `scripts/`
- `9,253` statements
- `1,666` missing statements
- `2,696` branches
- `580` partial branches
- HTML report written to `_coverage/html`

Resolved Windows failure classes:

| Failure class | Tests affected | Resolution |
| --- | --- | --- |
| Temp-dir / artifact-location | CLI smoke tests that wrote to hard-coded `/tmp/...` paths | Tests now use pytest `tmp_path`, so output stays under a writable per-test directory on Windows and Unix. |
| Path-handling | `test_cli_validate_hypothesis_smoke`, `test_sync_active_board_cli_command` | CLI output for validated paths and generated task-state paths is normalized to POSIX-style relative paths. |
| Artifact encoding | `test_cli_run_artifacts_use_consistent_primary_formula` | Test reads generated Markdown, JSON, and YAML artifacts with explicit UTF-8 decoding. |
| Workspace-local git metadata | `test_runner_generates_run_based_artifacts` | The assertion now accepts either absent git metadata or a 40-character commit hash when pytest temp paths live inside the repository worktree. |
| Generated task-state freshness | Strict repository validation smoke tests | The task-state board, generated task views, and mission support actions were synchronized after moving `TASK-0239` to `REVIEW_READY`. |

Remaining Windows environment note:

- Pytest is configured to use `.pytest-basetemp/` by default so normal
  `python -m pytest` and coverage runs do not depend on the user-level temp
  root. If a tool bypasses repository pytest configuration, pass
  `--basetemp=.pytest-basetemp` explicitly. `.pytest-basetemp/` is local-only
  and ignored.

Critical rows from the baseline:

| Module | Coverage | Reading |
| --- | ---: | --- |
| `physics_lab/registry/repository.py` | 85% | Strong validation and integrity coverage. |
| `physics_lab/registry/maintainer_review.py` | 64% | Core policy paths covered; rendering and uncommon branches remain lower priority. |
| `physics_lab/registry/closeout_sweep.py` | 75% | Good sweep coverage. |
| `physics_lab/registry/mission_control.py` | 86% | Strong task-selection coverage. |
| `physics_lab/registry/campaign_curator.py` | 81% | Strong campaign-curation coverage. |
| `physics_lab/registry/review_git.py` | 53% | Moderate coverage; future git-edge tests may be useful. |
| `physics_lab/workflows/nuclear_mass_baseline.py` | 92% | Strong scientific workflow coverage. |
| `scripts/apl_review_pr.py` | 69% | Thin maintainer wrapper now has `--help` smoke coverage. |
| `scripts/apl_closeout_task.py` | 83% | Thin closeout wrapper now has `--help` smoke coverage. |
| `scripts/apl_closeout_sweep.py` | 80% | Thin sweep wrapper now has `--help` smoke coverage. |
| `scripts/apl_mission.py` | 84% | Strong script entrypoint coverage. |
| `scripts/apl_campaign_curator.py` | 84% | Strong script entrypoint coverage. |
| `scripts/apl_microtask_pr_helper.py` | 68% | Good workflow wrapper coverage. |
| `scripts/run_nuclear_pairing_batch.py` | 92% | Strong batch-runner coverage. |
| `scripts/run_nuclear_shell_batch.py` | 92% | Strong batch-runner coverage. |
| `scripts/run_nuclear_neutron_rich_batch.py` | 91% | Strong batch-runner coverage. |

## Critical Path Matrix

| Critical path | Current direct test signal | Reading |
| --- | --- | --- |
| Repository validation and scientific-memory integrity | `tests/test_damped_oscillator.py`, `tests/test_pendulum.py`, `tests/test_docs_links.py`, `tests/test_golden_results.py`, `tests/test_microtask_queue_validation.py` | Strong direct regression coverage. |
| Maintainer review helper and policy layers | `tests/test_maintainer_review.py`, `tests/test_critical_path_script_entrypoints.py` | Strong direct coverage; keep adding narrow tests when policy rules change. |
| Closeout helpers | `tests/test_task_closeout.py`, `tests/test_closeout_sweep.py`, `tests/test_critical_path_script_entrypoints.py` | Good direct coverage for report generation, blockers, metadata binding, and wrapper help output. |
| Snapshot helper | `tests/test_snapshot.py` | Moderate coverage; shell wrapper behavior remains mostly text-regression based. |
| Mission Control | `tests/test_mission_control.py` | Strong direct coverage for mode rendering and live task selection. |
| Scientific Campaign Curator | `tests/test_campaign_curator.py` | Good direct coverage plus script JSON smoke test. |
| Nuclear baseline and residual workflows | `tests/test_nuclear_mass_baselines.py`, `tests/test_nuclear_shell_batch.py`, `tests/test_nuclear_neutron_rich_batch.py`, `tests/test_nuclear_pairing_batch.py`, `tests/test_post_ame2020_time_split_metrics.py` | Strong reproducibility coverage for committed sandbox runs and post-AME2020 checks. |
| Proposal and agent-run registries | `tests/test_research_proposals.py`, `tests/test_agent_runs.py`, `tests/test_task_proposals.py` | Strong schema and repository-count coverage. |
| Prediction registry | `tests/test_nuclear_mass_prediction_registry.py` | Direct schema and entry validation coverage. |
| Microtask PR helper and queue summary | `tests/test_microtask_pr_helper.py`, `tests/test_microtask_queue_summary.py`, `tests/test_microtask_runs.py` | Good workflow coverage. |

## Known Lower-Risk Areas

- Thin CLI wrappers that delegate to tested registry/workflow functions.
- Markdown report rendering branches with no scientific decision logic.
- Generated docs and snapshot text where schema or link validation already
  checks the critical behavior.

## Recommended Next Steps

1. Measure the first branch-aware coverage baseline after installing
   `pytest-cov`.
2. Keep coverage report-only for at least one task wave.
3. Add targeted tests only for critical paths that appear uncovered in the
   baseline.
4. Consider a conservative staged threshold only after the baseline is stable
   across Windows and Unix contributors.

Do not add a coverage gate in CI until the baseline is measured and reviewed.
