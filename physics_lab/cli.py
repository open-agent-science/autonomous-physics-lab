"""CLI entrypoints for Autonomous Physics Lab."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from physics_lab.registry import (
    infer_kind_from_path,
    load_agent,
    load_agent_run,
    load_claim,
    load_example_config,
    load_experiment,
    load_experiment_proposal,
    load_hypothesis,
    load_hypothesis_proposal,
    load_knowledge,
    load_result,
    load_review_metadata,
    load_task,
    load_task_proposal,
)
from physics_lab.registry.active_board import sync_active_board
from physics_lab.registry.mission_control import (
    SUPPORTED_MODES,
    load_current_missions,
    mission_json,
    render_agent_prompt,
    render_human_mission,
)
from physics_lab.registry.repository import validate_repository
from physics_lab.workflows.runner import run_experiment_with_output

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
    result_paths = sorted((root / "results").glob("*/*/result.yaml"))
    if not result_paths:
        return None
    latest_path: Path | None = None
    latest_generated_at = ""
    latest_mtime = float("-inf")
    for path in result_paths:
        generated_at = ""
        try:
            generated_at = str(load_result(path).get("generated_at", ""))
        except Exception:
            generated_at = ""
        mtime = path.stat().st_mtime
        if generated_at > latest_generated_at or (
            generated_at == latest_generated_at and mtime > latest_mtime
        ):
            latest_path = path
            latest_generated_at = generated_at
            latest_mtime = mtime
    return latest_path


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
    outcome = run_experiment_with_output(
        config_path=Path(config_path),
        output_dir=Path(output_dir) if output_dir is not None else None,
    )
    typer.echo(f"Completed: {outcome.title}")
    if outcome.best_model_id is not None:
        typer.echo(f"Best model: {outcome.best_model_id}")
    for line in outcome.summary_lines:
        typer.echo(line)
    typer.echo(f"Result: {outcome.artifacts.result_path}")
    typer.echo(f"Report: {outcome.artifacts.report_path}")
    typer.echo(f"Metrics: {outcome.artifacts.metrics_path}")
    typer.echo(f"Claim update: {outcome.artifacts.claim_update_path}")
    typer.echo(f"Claim patch: {outcome.artifacts.claim_update_patch_path}")
    typer.echo(f"Knowledge update: {outcome.artifacts.knowledge_update_path}")
    typer.echo(f"Knowledge patch: {outcome.artifacts.knowledge_update_patch_path}")
    typer.echo(f"Review summary: {outcome.artifacts.review_summary_path}")
    typer.echo(f"Review metadata: {outcome.artifacts.review_metadata_path}")


@app.command("validate")
def validate(path: str, kind: Optional[str] = None) -> None:
    """Validate a structured registry artifact against its JSON schema."""
    artifact_path = Path(path)
    resolved_kind = kind or infer_kind_from_path(artifact_path)
    loaders = {
        "agent": load_agent,
        "agent_run": load_agent_run,
        "claim": load_claim,
        "example_config": load_example_config,
        "experiment": load_experiment,
        "experiment_proposal": load_experiment_proposal,
        "hypothesis": load_hypothesis,
        "hypothesis_proposal": load_hypothesis_proposal,
        "knowledge": load_knowledge,
        "result": load_result,
        "review_metadata": load_review_metadata,
        "task": load_task,
        "task_proposal": load_task_proposal,
    }
    try:
        loaders[resolved_kind](artifact_path)
    except KeyError as exc:
        raise typer.BadParameter(f"Unsupported validation kind: {resolved_kind}") from exc
    typer.echo(f"Validated {artifact_path} as {resolved_kind}.")


@app.command("preflight-research-proposal")
def preflight_research_proposal(
    proposal_path: str,
    root: str = typer.Option(
        ".",
        "--root",
        help="Repository root used for campaign profile and path checks.",
    ),
) -> None:
    """Run the autonomous research proposal preflight gate."""
    artifact_path = Path(proposal_path)
    resolved_kind = infer_kind_from_path(artifact_path)
    root_path = Path(root).resolve()
    if resolved_kind == "hypothesis_proposal":
        payload = load_hypothesis_proposal(artifact_path, root=root_path)
    elif resolved_kind == "experiment_proposal":
        payload = load_experiment_proposal(artifact_path, root=root_path)
    else:
        raise typer.BadParameter(
            "preflight-research-proposal only supports hypothesis_proposals/ and experiment_proposals/"
        )
    typer.echo(f"Preflight PASS: {artifact_path}")
    typer.echo(f"Campaign profile: {payload['campaign_profile_id']}")
    typer.echo(f"Verdict: {payload['verdict']}")


@app.command("validate-repo")
def validate_repo(
    root: str = typer.Argument("."),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Enable stricter repository integrity checks and severity reporting.",
    ),
    fail_on_warnings: bool = typer.Option(
        False,
        "--fail-on-warnings",
        help="Exit non-zero when strict validation reports warnings.",
    ),
) -> None:
    """Validate all structured repository artifacts and cross-references."""
    if fail_on_warnings and not strict:
        raise typer.BadParameter("--fail-on-warnings requires --strict")
    summary = validate_repository(Path(root), strict=strict)
    typer.echo(f"Validated repository: {summary.root}")
    for kind, count in summary.counts.items():
        typer.echo(f"- {kind}: {count}")
    typer.echo(f"Total validated files: {summary.total_files}")
    if strict:
        status = "PASS" if summary.error_count == 0 else "FAIL"
        typer.echo(
            "Strict validation: "
            f"{status} "
            f"({summary.error_count} ERROR, {summary.warning_count} WARNING, {summary.info_count} INFO)"
        )
        for issue in summary.issues:
            prefix = f"[{issue.severity}] [{issue.code}]"
            if issue.path:
                typer.echo(f"- {prefix} {issue.path}: {issue.message}")
            else:
                typer.echo(f"- {prefix} {issue.message}")
        if summary.error_count > 0 or (fail_on_warnings and summary.warning_count > 0):
            raise typer.Exit(code=1)


@app.command("sync-active-board")
def sync_active_board_command(root: str = typer.Argument(".")) -> None:
    """Refresh tasks/ACTIVE.md from canonical task YAML files."""
    active_path = sync_active_board(Path(root).resolve())
    typer.echo(f"Synchronized active board: {active_path}")


@app.command("mission")
def mission(
    root: str = typer.Argument("."),
    mode: Optional[str] = typer.Option(
        None,
        "--mode",
        help="Mission mode: research, audit, support, or maintainer.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit machine-readable mission JSON.",
    ),
    agent_prompt: bool = typer.Option(
        False,
        "--agent-prompt",
        help="Emit a copy-paste prompt for a coding agent.",
    ),
) -> None:
    """Print the Agent First mission menu."""
    if mode is not None and mode not in SUPPORTED_MODES:
        raise typer.BadParameter(
            "mode must be one of: " + ", ".join(SUPPORTED_MODES)
        )
    payload = load_current_missions(Path(root).resolve())
    if agent_prompt:
        typer.echo(render_agent_prompt(payload))
    elif json_output:
        typer.echo(mission_json(payload, mode))
    else:
        typer.echo(render_human_mission(payload, mode))


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
    typer.echo(f"Best verdict: {result_payload['best_verdict']}")
    typer.echo(
        "Verification checks: "
        f"{len(verification_checks)} total "
        f"({pass_count} PASS, {fail_count} FAIL, {placeholder_count} PLACEHOLDER)"
    )
    if "best_model_id" in result_payload:
        typer.echo(f"Best model: {result_payload['best_model_id']}")
    if "train_range" in result_payload and "test_range" in result_payload:
        typer.echo(
            "Range: "
            f"train {result_payload['train_range'][0]:.4f}-{result_payload['train_range'][1]:.4f}, "
            f"test {result_payload['test_range'][0]:.4f}-{result_payload['test_range'][1]:.4f}"
        )
    elif result_payload.get("comparison_summary"):
        primary_target = result_payload["comparison_summary"][0]
        typer.echo(
            "Primary comparison: "
            f"{primary_target['label']} observed {primary_target['observed_value']:.10f} "
            f"vs reference {primary_target['reference_value']:.10f}"
        )
        uncertainty = result_payload.get("uncertainty_summary", {})
        if uncertainty:
            if uncertainty.get("combined_uncertainty") is not None:
                typer.echo(
                    "Uncertainty: "
                    f"combined {float(uncertainty['combined_uncertainty']):.10f}, "
                    f"within target uncertainty = {uncertainty.get('within_combined_uncertainty')}"
                )
            else:
                typer.echo(
                    "Uncertainty: "
                    f"{uncertainty.get('notes') or uncertainty.get('method') or 'reported'}"
                )


if __name__ == "__main__":
    app()
