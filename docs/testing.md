# Testing

APL keeps validation deterministic and local. Run the normal test suite before
handoff:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

Normal pytest runs use the operating system temporary directory for `tmp_path`
fixtures and disable pytest's cache provider. This keeps Windows validation
from writing test scratch state into a repository checkout that may be locked by
Git, antivirus, or another agent session.

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
