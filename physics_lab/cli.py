"""CLI entrypoints for Autonomous Physics Lab."""

from pathlib import Path

import typer

from physics_lab.workflows.runner import run_pendulum_experiment

app = typer.Typer(help="Autonomous Physics Lab command line interface.")


@app.callback()
def main() -> None:
    """Top-level CLI group for future subcommands."""


@app.command("run")
def run(config_path: str) -> None:
    """Run a configured experiment workflow."""
    outcome = run_pendulum_experiment(Path(config_path))
    typer.echo(f"Completed: {outcome.title}")
    typer.echo(f"Best model: {outcome.best_model_id}")
    typer.echo(f"Report: {outcome.artifacts.report_path}")
    typer.echo(f"Metrics: {outcome.artifacts.metrics_path}")


if __name__ == "__main__":
    app()
