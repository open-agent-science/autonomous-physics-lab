"""CLI entrypoints for Autonomous Physics Lab."""

import typer

app = typer.Typer(help="Autonomous Physics Lab command line interface.")


@app.callback()
def main() -> None:
    """Top-level CLI group for future subcommands."""


@app.command("run")
def run(config_path: str) -> None:
    """Placeholder run command for the first scaffold stage."""
    typer.echo(f"Workflow execution is not implemented yet. Requested config: {config_path}")


if __name__ == "__main__":
    app()
