# Testing

APL keeps validation deterministic and local. Run the normal test suite before
handoff:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

## Interpreter Discovery

Validation helpers use the repository Python resolver before launching child
Python commands. The selection order is:

1. the active interpreter, when it is already the repository `.venv`;
2. the checkout-local `.venv` interpreter;
3. the main checkout `.venv` interpreter when running from a git worktree;
4. the active interpreter as a compatibility fallback.

On Windows, `python3` may resolve to a launcher or Store alias. Before a local
validation run looks suspicious, agents can report the selected interpreter
without mutating the environment:

```bash
python3 scripts/apl_agent_doctor.py --worktree-runtime-preflight --no-gh-auth-check
```

Use the printed `selected validation python` for pytest, Ruff, repository
validation, and helper scripts when the active shell launcher differs from the
repository `.venv`. Linux and macOS keep the same resolver path and fall back to
the active interpreter when no repository `.venv` exists.

Normal pytest runs use the operating system temporary directory for `tmp_path`
fixtures and disable pytest's cache provider. This keeps Windows validation
from writing test scratch state into a repository checkout that may be locked by
Git, antivirus, or another agent session.

## Fast Feedback Lane

For an inner-loop check, run:

```bash
python3 scripts/validate_fast.py
```

The validation queue has explicit layers:

1. `preflight`: cheap deterministic gates, with Ruff first and strict
   repository validation second.
2. `fast_parallel`: parallel non-`full_repo` pytest using xdist `loadgroup`.
3. `resource_groups`: measured resource-sensitive tests share one worker per
   declared `xdist_group` while overlapping with unrelated tests.
4. `broad_ci`: the cross-platform PR lane.
5. `full_repo`: slow smoke tests for final or explicitly required validation.

The helper runs the local layers and prints its ten slowest pytest durations so
maintainers can tune the long tail from measured data. Add a shared
`pytest.mark.xdist_group` only after a parallel run demonstrates resource
sensitivity; do not use grouping as a general escape hatch.

On Windows, the fast helper excludes tests marked `resource_sensitive` from
the parallel layer and runs them as a final `-n0` layer. Linux and macOS keep
the overlapping `loadgroup` path. This narrow platform fallback is for measured
whole-suite worker contention, not a reason to run every Windows test serially.

Do not encode dependencies between tests merely to force a global execution
order under xdist. When parallel pytest fails on Windows, use the opt-in doctor
probe from `docs/cross-platform-compatibility.md`. A successful workspace-local
fallback should use a unique path such as `.pytest-basetemp/session-<unique-id>`
for that session. On Windows, `validate_fast.py` prefers a short unique
`C:/tmp/apl-pytest-*` path because deep worktree paths can hit path-length
limits. Override its root with `APL_PYTEST_BASETEMP_ROOT` when needed.
If the short system root is unavailable, the helper falls back to the ignored
workspace-local `.pytest-basetemp/session-*` path instead of weakening the test
lane.

## Coverage Reporting

Coverage is report-only. Do not treat the first measured percentage as a merge
gate, and do not pursue 100% coverage for thin CLI wrappers, generated reports,
or low-risk glue code.

Install the development extras first:

```bash
python3 -m pip install -e ".[dev]"
```

Then run:

```bash
python3 scripts/apl_coverage_report.py
```

The helper prints the exact pytest command before executing it. It measures
line and branch coverage for `physics_lab` plus the Python `scripts/`
directory, writes terminal missing-line output, and writes the HTML report to
`_coverage/html`. It does not set `--cov-fail-under` or add any coverage gate.

To inspect the command without running pytest:

```bash
python3 scripts/apl_coverage_report.py --dry-run
```

On Windows PowerShell, use the same helper with the active environment's Python:

```powershell
python scripts\apl_coverage_report.py
```

The helper uses `.pytest-basetemp/` as a dedicated temporary base by default so
coverage runs can be inspected without mixing with ordinary pytest scratch
state. To pass additional pytest selectors, append them after `--`:

```bash
python3 scripts/apl_coverage_report.py -- tests/test_maintainer_review.py
```

The critical-path audit interprets the script rows by priority instead of
requiring every wrapper or generator to be covered. The HTML output,
`.coverage`, and `.pytest-basetemp/` are local-only and should not be committed.
