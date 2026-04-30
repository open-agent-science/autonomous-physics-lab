"""CLI entrypoints for Autonomous Physics Lab."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from physics_lab.registry import infer_kind_from_path, load_agent, load_claim, load_example_config, load_experiment, load_hypothesis, load_knowledge, load_result, load_task
from physics_lab.registry.repository import validate_repository
from physics_lab.workflows.runner import run_pendulum_experiment_with_output

app = typer.Typer(help="Autonomous Physics Lab command line interface.")


@app.callback()
def main() -> None:
    """Top-level CLI group for future subcommands."""


def _project_stage(root: Path) -> str:
    status_path = root / "docs" / "status.md"
    if not status_path.exists():
        return "unknown"

    lines = status_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Current Stage":
            for candidate in lines[index + 1 :]:
                candidate = candidate.strip()
                if candidate:
                    return candidate.replace("`", "")
    return "unknown"


def _latest_result_path(root: Path) -> Path | None:
    result_paths = sorted(
        (root / "results").glob("*/*/result.yaml"),
        key=lambda path: path.stat().st_mtime,
    )
    if not result_paths:
        return None
    return result_paths[-1]


@app.command("run")
def run(
    config_path: str,
    output_dir: Optional[str] = typer.Option(
        None,
        "--output-dir",
        help="Override the base output directory for generated run artifacts.",
    ),
) -> None:
    """Run a configured experiment workflow."""
    outcome = run_pendulum_experiment_with_output(
        config_path=Path(config_path),
        output_dir=Path(output_dir) if output_dir is not None else None,
    )
    typer.echo(f"Completed: {outcome.title}")
    typer.echo(f"Best model: {outcome.best_model_id}")
    typer.echo(f"Result: {outcome.artifacts.result_path}")
    typer.echo(f"Report: {outcome.artifacts.report_path}")
    typer.echo(f"Metrics: {outcome.artifacts.metrics_path}")
    typer.echo(f"Claim update: {outcome.artifacts.claim_update_path}")
    typer.echo(f"Knowledge update: {outcome.artifacts.knowledge_update_path}")


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


@app.command("status")
def status(root: str = typer.Argument(".")) -> None:
    """Print a compact project status snapshot."""
    root_path = Path(root).resolve()
    summary = validate_repository(root_path)
    stage = _project_stage(root_path)
    latest_result_path = _latest_result_path(root_path)

    typer.echo(f"Stage: {stage}")
    typer.echo(f"Repository: {summary.root}")
    typer.echo(f"Validation: PASS ({summary.total_files} structured files)")
    typer.echo(f"Benchmarks: {summary.counts['examples']} example config(s)")

    if latest_result_path is None:
        typer.echo("Latest result: none")
        return

    result_payload = load_result(latest_result_path)
    verification_checks = result_payload["verification"]["checks"]
    pass_count = sum(1 for check in verification_checks if check["status"] == "PASS")
    fail_count = sum(1 for check in verification_checks if check["status"] == "FAIL")
    placeholder_count = sum(1 for check in verification_checks if check["status"] == "PLACEHOLDER")

    try:
        relative_result = latest_result_path.relative_to(root_path).as_posix()
    except ValueError:
        relative_result = str(latest_result_path)

    typer.echo(f"Latest result: {relative_result}")
    typer.echo(f"Result id: {result_payload['result_id']}")
    typer.echo(f"Run id: {result_payload['run_id']}")
    typer.echo(f"Best model: {result_payload['best_model_id']}")
    typer.echo(f"Best verdict: {result_payload['best_verdict']}")
    typer.echo(
        "Verification checks: "
        f"{len(verification_checks)} total "
        f"({pass_count} PASS, {fail_count} FAIL, {placeholder_count} PLACEHOLDER)"
    )
    typer.echo(
        "Range: "
        f"train {result_payload['train_range'][0]:.4f}-{result_payload['train_range'][1]:.4f} rad, "
        f"test {result_payload['test_range'][0]:.4f}-{result_payload['test_range'][1]:.4f} rad"
    )


if __name__ == "__main__":
    app()
