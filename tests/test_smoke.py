from typer.testing import CliRunner

from physics_lab import __version__
from physics_lab.cli import app


def test_package_version_defined() -> None:
    assert __version__ == "0.1.0"


def test_cli_run_placeholder() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "examples/pendulum.yaml"])

    assert result.exit_code == 0
    assert "Workflow execution is not implemented yet." in result.stdout
