# Public Release Validation Signoff

Task: `TASK-0206`
Branch: `agent/master/codex/task-0206-release-signoff-artifact`
Base reviewed: `origin/main` at `e06deac151bfa8056bee4300c35e4e81bf8170c3`
Generated: 2026-05-17

## Verdict

`REVIEW_READY`

The release-time technical and wording checks passed after one public path leak
wording fix. This artifact is evidence for maintainer review; it does not make
the repository public and does not approve a release by itself.

## GitHub CI

Latest default-branch CI observed for `main`:

- Workflow: `CI`
- Run: `25988603916`
- Commit: `e06deac151bfa8056bee4300c35e4e81bf8170c3`
- Status: `completed`
- Conclusion: `success`
- URL: `https://github.com/gladunrv/autonomous-physics-lab/actions/runs/25988603916`

## Local Validation

All commands below were run from the task branch unless noted.

| Check | Command | Result |
| --- | --- | --- |
| Ruff | `.venv\Scripts\python.exe -m ruff check .` | PASS |
| Full tests | `.venv\Scripts\python.exe -m pytest --basetemp C:\tmp\apl-pytest-task-0206-full` | PASS, `611 passed`, one local `.pytest_cache` permission warning |
| Repository validation | `.venv\Scripts\python.exe -m physics_lab.cli validate-repo .` | PASS, 446 files validated |
| Strict repository validation | `.venv\Scripts\python.exe -m physics_lab.cli validate-repo . --strict --fail-on-warnings` | PASS, 0 errors, 0 warnings, 10 informational draft-claim notes |
| Mission JSON | `.venv\Scripts\python.exe scripts\apl_mission.py --json` | PASS |
| Docs-link and path-leak tests | `.venv\Scripts\python.exe -m pytest --basetemp C:\tmp\apl-pytest-task-0206-doclinks tests\test_docs_links.py tests\test_public_path_leaks.py` | PASS, `6 passed`, one local `.pytest_cache` permission warning |
| Public path leak checker | `.venv\Scripts\python.exe scripts\check_public_path_leaks.py` | PASS after wording fix |
| Tracked cache check | `git ls-files .pytest_cache .ruff_cache` | PASS, no tracked cache paths |
| Pendulum smoke | `.venv\Scripts\python.exe -m physics_lab.cli run examples\pendulum.yaml --output-dir C:\tmp\apl-pendulum-task-0206` | PASS, sandbox-only output |
| Damped oscillator smoke | `.venv\Scripts\python.exe -m physics_lab.cli run examples\damped_oscillator.yaml --output-dir C:\tmp\apl-damped-task-0206` | PASS, sandbox-only output |
| Snapshot | `PYTHON_BIN=.venv/Scripts/python.exe PYTEST_ADDOPTS="--basetemp=C:/tmp/apl-snapshot-task-0206-pytest" ./scripts/apl_snapshot.sh` | PASS; snapshot written to `_snapshots/apl_snapshot_20260517_130047.md` |

Snapshot note: the Windows checkout contains an untracked, locked
`.pytest-basetemp` directory from earlier local runs. The snapshot command
therefore printed a `find` permission warning while enumerating the working
tree. The snapshot's embedded `ruff`, `pytest`, and `validate-repo` sections
passed when `PYTEST_ADDOPTS` pointed pytest at `C:/tmp/apl-snapshot-task-0206-pytest`.
The locked local directory is not tracked and is not part of the release
artifact surface.

## Public Path Leak Check

Initial check found two maintainer-local path literals in
`docs/notes/claude-code-permissions-allowlist.md`, both describing macOS
private temp mirrors. The wording was changed to a generic platform-temp
description.

Rerun result:

```text
No public path leaks found.
```

## External Reviewer Replication Guide

Reviewed: `docs/external-reviewer-replication-guide.md`

Status: `PASS`

Evidence:

- `scripts/reproduce_core_results.py --list` still lists the bounded public
  replay surface and explicitly excludes `EXP-0010` / Muon g-2 from the default
  public-success path.
- The guide still points reviewers to strict validation and full pytest.
- The guide preserves out-of-scope wording for discovery-level claims, exact
  symbolic formulas, universal validity, particle-mass explanations, and broad
  nuclear-theory interpretation.
- Full bounded replay passed with sandbox-only output:
  `.venv\Scripts\python.exe scripts\reproduce_core_results.py --output-dir C:\tmp\apl-core-reproduction-task-0206 --python .\.venv\Scripts\python.exe`

Replay result:

```text
Core reproduction PASS.
```

## Public Wording Audit

Reviewed surfaces:

- `README.md`
- `docs/status.md`
- `docs/mission-control.md`
- `docs/next-steps.md`
- `docs/public-release-gates.md`
- `docs/release-checklist.md`
- `docs/releases/v0.1-public-alpha.md`
- `docs/releases/v0.2-public-alpha.md`
- `docs/v0.2-launch-pack.md`
- `docs/reviews/v0.2-public-readiness.md`
- `docs/external-reviewer-replication-guide.md`

Result:

- No public-opening decision is implied.
- No claim, knowledge, or canonical result status was promoted.
- `EXP-0010` remains framed as a guarded stress-test surface, not a flagship
  public success.
- Nuclear Mass Surface remains framed as benchmark, sandbox, retrospective, or
  prospective-registry evidence, not as a finished theory or public claim.
- The external reviewer guide is current enough for release-gate review after
  this signoff.

## Remaining Maintainer Decision

This signoff clears the release-time validation packaging task for maintainer
review. The repository should remain private until a maintainer accepts this
artifact, confirms any current branch/PR state they intend to release from, and
explicitly makes the public-opening decision.
