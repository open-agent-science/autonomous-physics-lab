"""Thin workflow dispatcher for Autonomous Physics Lab."""

from __future__ import annotations

from pathlib import Path

from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.workflows.artifacts import ExperimentOutcome, resolve_path
from physics_lab.workflows.anharmonic_oscillator import run_anharmonic_oscillator_experiment_with_output
from physics_lab.workflows.damped_oscillator import run_damped_oscillator_experiment_with_output
from physics_lab.workflows.dimensional_validator import run_dimensional_validator_with_output
from physics_lab.workflows.gauntlet import run_gauntlet_experiment_with_output
from physics_lab.workflows.koide_neutrino import run_neutrino_koide_experiment
from physics_lab.workflows.koide_quark import run_quark_koide_experiment
from physics_lab.workflows.particle_mass import (
    run_particle_mass_holdout_with_output,
    run_particle_mass_reproduction_with_output,
)
from physics_lab.workflows.g2_formula import run_g2_formula_experiment
from physics_lab.workflows.nuclear_mass_baseline import (
    run_nuclear_mass_baseline_experiment_with_output,
)
from physics_lab.workflows.particle_mass_falsifier import (
    run_particle_mass_falsifier_with_output,
)
from physics_lab.workflows.pendulum import (
    run_pendulum_experiment,
    run_pendulum_experiment_with_output,
)
from physics_lab.workflows.textbook_exact_reference import (
    run_textbook_exact_reference_with_output,
)
from physics_lab.workflows.materials_md0002_formation_energy import (
    run_materials_md0002_formation_energy_with_output,
)
from physics_lab.workflows.stellar_ml_debcat_baseline import (
    run_stellar_ml_debcat_baseline_with_output,
)
from physics_lab.workflows.thermoml_tb_family_transfer import (
    run_thermoml_tb_family_transfer_with_output,
)
from physics_lab.workflows.textbook_firas_wien_peak import (
    run_textbook_firas_wien_peak_with_output,
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
    if workflow == "dimensional_validation":
        return run_dimensional_validator_with_output(config_path=config_path, output_dir=output_dir)
    if workflow == "neutrino_koide":
        return run_neutrino_koide_experiment(config_path=config_path, output_dir=output_dir)
    if workflow == "quark_koide":
        return run_quark_koide_experiment(config_path=config_path, output_dir=output_dir)
    if workflow == "particle_mass_falsifier":
        return run_particle_mass_falsifier_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
    if workflow == "g2_formula_search":
        return run_g2_formula_experiment(config_path=config_path, output_dir=output_dir)
    if workflow == "anharmonic_oscillator":
        return run_anharmonic_oscillator_experiment_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
    if workflow == "nuclear_mass_baseline":
        return run_nuclear_mass_baseline_experiment_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
    if workflow == "materials_md0002_formation_energy_benchmark":
        return run_materials_md0002_formation_energy_with_output(
            config_path=config_path, output_dir=output_dir
        )
    if workflow == "stellar_ml_debcat_baseline_benchmark":
        return run_stellar_ml_debcat_baseline_with_output(
            config_path=config_path, output_dir=output_dir
        )
    if workflow == "thermoml_tb_family_transfer_benchmark":
        return run_thermoml_tb_family_transfer_with_output(
            config_path=config_path, output_dir=output_dir
        )
    if workflow == "textbook_firas_wien_peak_consistency":
        return run_textbook_firas_wien_peak_with_output(
            config_path=config_path, output_dir=output_dir
        )
    if workflow == "textbook_exact_reference":
        return run_textbook_exact_reference_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
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
    if method_type == "dataset_reproduction":
        return run_particle_mass_reproduction_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
    if method_type == "holdout_prediction":
        return run_particle_mass_holdout_with_output(
            config_path=config_path,
            output_dir=output_dir,
        )
    raise ValueError(f"Unsupported experiment method type: {method_type}")


__all__ = [
    "run_experiment",
    "run_experiment_with_output",
    "run_pendulum_experiment",
    "run_pendulum_experiment_with_output",
    "run_anharmonic_oscillator_experiment_with_output",
    "run_nuclear_mass_baseline_experiment_with_output",
    "run_damped_oscillator_experiment_with_output",
    "run_gauntlet_experiment_with_output",
    "run_neutrino_koide_experiment",
    "run_quark_koide_experiment",
    "run_particle_mass_holdout_with_output",
    "run_particle_mass_reproduction_with_output",
    "run_particle_mass_falsifier_with_output",
    "run_g2_formula_experiment",
    "run_dimensional_validator_with_output",
    "run_textbook_exact_reference_with_output",
    "run_textbook_firas_wien_peak_with_output",
    "run_thermoml_tb_family_transfer_with_output",
]
