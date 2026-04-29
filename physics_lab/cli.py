"""CLI entrypoints for Autonomous Physics Lab."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from physics_lab.registry import infer_kind_from_path, load_agent, load_claim, load_example_config, load_experiment, load_hypothesis, load_knowledge, load_result, load_task
from physics_lab.registry.repository import validate_repository
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


@app.command("validate")
def validate(path: str, kind: Optional[str] = None) -> None:
    """Validate a structured registry artifact against its JSON schema."""
    artifact_path = Path(path)
    resolved_kind = kind or infer_kind_from_path(artifact_path)
    loaders = {
        "agent": load_agent,
        "claim": load_claim,
        "example_config": load_example_config,
        "experiment": load_experiment,
        "hypothesis": load_hypothesis,
        "knowledge": load_knowledge,
        "result": load_result,
        "task": load_task,
    }
    try:
        loaders[resolved_kind](artifact_path)
    except KeyError as exc:
        raise typer.BadParameter(f"Unsupported validation kind: {resolved_kind}") from exc
    typer.echo(f"Validated {artifact_path} as {resolved_kind}.")


@app.command("validate-repo")
def validate_repo(root: str = typer.Argument(".")) -> None:
    """Validate all structured repository artifacts and cross-references."""
    summary = validate_repository(Path(root))
    typer.echo(f"Validated repository: {summary.root}")
    for kind, count in summary.counts.items():
        typer.echo(f"- {kind}: {count}")
    typer.echo(f"Total validated files: {summary.total_files}")


if __name__ == "__main__":
    app()
