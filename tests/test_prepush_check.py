"""Tests for the pre-push CI-parity gate (TASK-0726)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

from physics_lab.registry.prepush_check import (
    TARGETED_TEST_FILES,
    build_gate_commands,
    render_prepush_report,
    run_prepush_checks,
)


@dataclass
class _FakeCompleted:
    returncode: int


def test_default_gates_cover_ruff_targeted_tests_and_strict_validation(tmp_path: Path) -> None:
    gates = build_gate_commands(tmp_path, full=False)

    names = [g.name for g in gates]
    assert names == ["ruff", "targeted-docs-task-tests", "validate-repo-strict"]
    # The convention test that caused the missed-CI-failure must be in the set.
    assert "tests/test_task_reference_convention.py" in TARGETED_TEST_FILES
    targeted = next(g for g in gates if g.name == "targeted-docs-task-tests")
    assert "tests/test_task_reference_convention.py" in targeted.command
    assert "tests/test_docs_links.py" in targeted.command


def test_full_mode_runs_validate_fast_only(tmp_path: Path) -> None:
    gates = build_gate_commands(tmp_path, full=True)

    assert [g.name for g in gates] == ["validate_fast"]
    assert gates[0].command[1:] == ["scripts/validate_fast.py"]


def test_gates_use_resolved_interpreter_without_venv(tmp_path: Path) -> None:
    # No repo venv under tmp_path -> falls back to the launching interpreter.
    for gate in build_gate_commands(tmp_path, full=False):
        assert gate.command[0] == sys.executable


def test_gates_prefer_repo_venv_interpreter(tmp_path: Path) -> None:
    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True, exist_ok=True)
    venv_python.write_text("", encoding="utf-8")

    gates = build_gate_commands(tmp_path, full=False)

    assert gates[0].command[0] == str(venv_python.resolve())


def test_run_prepush_checks_passes_when_all_gates_pass(tmp_path: Path) -> None:
    report = run_prepush_checks(tmp_path, runner=lambda command, cwd: _FakeCompleted(0))

    assert report.passed
    assert report.failed == ()
    assert "PASS" in render_prepush_report(report)


def test_run_prepush_checks_fails_and_names_failing_gate(tmp_path: Path) -> None:
    def runner(command, cwd):  # noqa: ANN001
        # Fail only the targeted-tests gate (second command).
        failing = "pytest" in command
        return _FakeCompleted(1 if failing else 0)

    report = run_prepush_checks(tmp_path, runner=runner)

    assert not report.passed
    failed_names = {result.name for result in report.failed}
    assert "targeted-docs-task-tests" in failed_names
    rendered = render_prepush_report(report)
    assert "FAIL" in rendered
    assert "targeted-docs-task-tests" in rendered


def test_cli_main_exit_code_follows_report(tmp_path: Path) -> None:
    import importlib.util
    from unittest.mock import patch

    from physics_lab.registry.prepush_check import GateResult, PrepushReport

    script = Path(__file__).resolve().parents[1] / "scripts" / "apl_prepush_check.py"
    spec = importlib.util.spec_from_file_location("apl_prepush_check_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # main() imports run_prepush_checks from the core module at call time, so
    # patching the core attribute controls what main sees — no real checks run.
    failing = PrepushReport(
        full=False, results=(GateResult(name="ruff", passed=False, returncode=1),)
    )
    passing = PrepushReport(
        full=False, results=(GateResult(name="ruff", passed=True, returncode=0),)
    )
    with patch(
        "physics_lab.registry.prepush_check.run_prepush_checks", return_value=failing
    ):
        assert module.main(["--root", str(tmp_path)]) == 1
    with patch(
        "physics_lab.registry.prepush_check.run_prepush_checks", return_value=passing
    ):
        assert module.main(["--root", str(tmp_path)]) == 0
