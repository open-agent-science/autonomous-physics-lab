# Testing

APL keeps validation deterministic and local. Run the normal test suite before
handoff:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

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
python3 -m pytest \
  --cov=physics_lab \
  --cov=scripts \
  --cov-branch \
  --cov-report=term-missing:skip-covered \
  --cov-report=html:_coverage/html
```

On Windows PowerShell, use the same command on one line:

```powershell
python -m pytest --cov=physics_lab --cov=scripts --cov-branch --cov-report=term-missing:skip-covered --cov-report=html:_coverage/html
```

If the system temporary directory is not writable, add a workspace-local
temporary base:

```powershell
python -m pytest --basetemp=.pytest-basetemp --cov=physics_lab --cov=scripts --cov-branch --cov-report=term-missing:skip-covered --cov-report=html:_coverage/html
```

The command reports line and branch coverage for `physics_lab` plus the Python
`scripts/` directory. The critical-path audit interprets the script rows by
priority instead of requiring every wrapper or generator to be covered. The
HTML output is local-only and should not be committed.
