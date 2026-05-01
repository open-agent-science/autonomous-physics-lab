"""Thin workflow dispatcher for Autonomous Physics Lab."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.workflows.artifacts import ExperimentOutcome, resolve_path
from physics_lab.workflows.damped_oscillator import run_damped_oscillator_experiment_with_output
from physics_lab.workflows.gauntlet import run_gauntlet_experiment_with_output
from physics_lab.workflows.pendulum import (
    run_pendulum_experiment,
    run_pendulum_experiment_with_output,
)


def run_experiment(config_path: str | Path) -> ExperimentOutcome:
    """Execute a configured experiment by dispatching on experiment method type."""
    return run_experiment_with_output(config_path=config_path)


def run_experiment_with_output(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> ExperimentOutcome:
    """Execute a configured experiment, optionally overriding the output root."""
    config_path = Path(config_path).resolve()
    config = load_example_config(config_path)
    workflow = config.get("workflow", "standard")
    if workflow == "gauntlet":
        return run_gauntlet_experiment_with_output(config_path=config_path, output_dir=output_dir)
    experiment_path = resolve_path(config_path, config["experiment_path"])
    experiment = load_experiment(experiment_path)
    method_type = str(experiment["method"]["type"])
    if method_type == "formula_discovery":
        return run_pendulum_experiment_with_output(config_path=config_path, output_dir=output_dir)
    if method_type == "regime_verification":
        return run_damped_oscillator_experiment_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
    raise ValueError(f"Unsupported experiment method type: {method_type}")


__all__ = [
    "run_experiment",
    "run_experiment_with_output",
    "run_pendulum_experiment",
    "run_pendulum_experiment_with_output",
    "run_damped_oscillator_experiment_with_output",
    "run_gauntlet_experiment_with_output",
]
