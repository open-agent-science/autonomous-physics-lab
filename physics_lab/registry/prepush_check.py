"""Pre-push CI-parity gate (TASK-0726).

A task's declared ``validation.commands`` is often narrower than what CI actually
runs, so a PR can pass locally and then fail the CI "fast tests" job (for example
on ``tests/test_task_reference_convention.py``), costing a 3-6 minute round-trip.

This module runs the *always-on* CI gates locally before push:

- ``ruff check .``;
- the targeted docs/task tests the CI fast-tests job runs;
- strict repository validation.

``--full`` swaps the targeted set for the whole fast suite (``validate_fast.py``).
All checks run with the repository venv interpreter (via the TASK-0725 resolver),
so a bare system python below the project minimum does not produce false
failures.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

from physics_lab.registry.repo_python import resolve_validation_python

# The docs/task tests the CI "fast tests" job runs as a dedicated step. Keeping
# this list in sync with that step is what makes the pre-push gate catch the
# convention/structure failures a narrow task validation misses.
TARGETED_TEST_FILES: tuple[str, ...] = (
    "tests/test_task_reference_convention.py",
    "tests/test_docs_links.py",
    "tests/test_task_proposals.py",
    "tests/test_active_board.py",
    "tests/test_task_views.py",
    "tests/test_mission_control.py",
    "tests/test_mission_freshness.py",
    "tests/test_validate_repo_auto_sync.py",
)


def _candidate_basetemp_roots(root: Path) -> tuple[Path, ...]:
    """Return temp roots to try for the targeted pytest gate."""
    candidates: list[Path] = []
    override = os.environ.get("APL_PYTEST_BASETEMP_ROOT")
    if override:
        candidates.append(Path(override))
    candidates.extend((Path(tempfile.gettempdir()), root / ".pytest-basetemp"))

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            key = os.path.normcase(str(candidate.resolve()))
        except OSError:
            key = os.path.normcase(str(candidate))
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return tuple(unique)


def allocate_pytest_basetemp(root: Path) -> tuple[Path | None, str | None]:
    """Return a unique pytest basetemp path or an environment blocker."""
    errors: list[str] = []
    for candidate_root in _candidate_basetemp_roots(root):
        try:
            candidate_root.mkdir(parents=True, exist_ok=True)
            probe = Path(tempfile.mkdtemp(prefix="apl-prepush-probe-", dir=str(candidate_root)))
            shutil.rmtree(probe)
            basetemp = candidate_root / (
                f"apl-prepush-pytest-{uuid.uuid4().hex[:12]}"
            )
        except OSError as exc:
            errors.append(f"{candidate_root}: {type(exc).__name__}: {exc}")
            continue
        return basetemp, None
    details = "; ".join(errors) if errors else "no candidate temp roots were available"
    return (
        None,
        "No writable pytest basetemp root was available for the pre-push "
        f"targeted pytest gate. Checked: {details}. Run "
        "`python3 scripts/apl_agent_doctor.py --probe-pytest-runtime --no-gh-auth-check` "
        "and retry in a writable temp environment.",
    )


@dataclass(frozen=True)
class GateCommand:
    """A single named pre-push gate command."""

    name: str
    command: list[str]
    environment_error: str | None = None
    cleanup_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class GateResult:
    """Outcome of running one gate."""

    name: str
    passed: bool
    returncode: int
    environment_error: str | None = None


@dataclass(frozen=True)
class PrepushReport:
    """Aggregate pre-push result."""

    full: bool
    results: tuple[GateResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    @property
    def failed(self) -> tuple[GateResult, ...]:
        return tuple(result for result in self.results if not result.passed)


def build_gate_commands(root: Path, *, full: bool = False) -> tuple[GateCommand, ...]:
    """Return the ordered gate commands to run before pushing.

    ``full=False`` runs ruff, the targeted docs/task tests, and strict repository
    validation (fast; catches structure/convention failures). ``full=True`` runs
    the whole fast suite via ``validate_fast.py`` instead.
    """
    python = resolve_validation_python(root)
    if full:
        return (
            GateCommand(
                name="validate_fast",
                command=[python, "scripts/validate_fast.py"],
            ),
        )
    basetemp, basetemp_error = allocate_pytest_basetemp(root)
    pytest_command = [python, "-m", "pytest", "-q", *TARGETED_TEST_FILES]
    cleanup_paths: tuple[Path, ...] = ()
    if basetemp is not None:
        pytest_command.extend(["--basetemp", str(basetemp)])
        cleanup_paths = (basetemp,)
    return (
        GateCommand(name="ruff", command=[python, "-m", "ruff", "check", "."]),
        GateCommand(
            name="targeted-docs-task-tests",
            command=pytest_command,
            environment_error=basetemp_error,
            cleanup_paths=cleanup_paths,
        ),
        GateCommand(
            name="validate-repo-strict",
            command=[
                python,
                "-m",
                "physics_lab.cli",
                "validate-repo",
                ".",
                "--strict",
                "--fail-on-warnings",
            ],
        ),
    )


def run_prepush_checks(
    root: Path,
    *,
    full: bool = False,
    runner=subprocess.run,
) -> PrepushReport:
    """Run the pre-push gates in order and collect results.

    ``runner`` is injectable for testing; it must accept the subprocess.run
    signature used here and return an object exposing ``returncode``.
    """
    results: list[GateResult] = []
    for gate in build_gate_commands(root, full=full):
        if gate.environment_error is not None:
            results.append(
                GateResult(
                    name=gate.name,
                    passed=False,
                    returncode=2,
                    environment_error=gate.environment_error,
                )
            )
            continue
        completed = runner(gate.command, cwd=root)
        code = int(getattr(completed, "returncode", 1))
        results.append(GateResult(name=gate.name, passed=code == 0, returncode=code))
        for cleanup_path in gate.cleanup_paths:
            shutil.rmtree(cleanup_path, ignore_errors=True)
    return PrepushReport(full=full, results=tuple(results))


def render_prepush_report(report: PrepushReport) -> str:
    """Render a human-readable summary of a pre-push run."""
    mode = "full fast suite" if report.full else "fast targeted gates"
    lines = [f"Pre-push CI-parity check ({mode})"]
    for result in report.results:
        if result.environment_error is not None:
            status = f"ENVIRONMENT BLOCKED (exit {result.returncode})"
        else:
            status = "PASS" if result.passed else f"FAIL (exit {result.returncode})"
        lines.append(f"- {result.name}: {status}")
        if result.environment_error is not None:
            lines.append(f"  {result.environment_error}")
    if report.passed:
        lines.append("Result: PASS — safe to push.")
    else:
        failed = ", ".join(result.name for result in report.failed)
        lines.append(f"Result: FAIL — fix before push: {failed}")
    return "\n".join(lines)
