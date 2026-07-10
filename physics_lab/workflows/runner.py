"""Thin workflow dispatcher for Autonomous Physics Lab."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from physics_lab.registry.examples import load_example_config
from physics_lab.registry.experiments import load_experiment
from physics_lab.workflows.artifacts import ExperimentOutcome, resolve_path
from physics_lab.workflows.anharmonic_oscillator import run_anharmonic_oscillator_experiment_with_output
from physics_lab.workflows.damped_oscillator import run_damped_oscillator_experiment_with_output
from physics_lab.workflows.dimensional_validator import run_dimensional_validator_with_output
from physics_lab.workflows.exoplanet_null_baseline_result import (
    run_exoplanet_null_baseline_result_with_output,
)
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
from physics_lab.workflows.stellar_ml_high_mass_transfer import (
    run_stellar_ml_high_mass_transfer_with_output,
)
from physics_lab.workflows.thermoml_tb_family_transfer import (
    run_thermoml_tb_family_transfer_with_output,
)
from physics_lab.workflows.textbook_firas_wien_peak import (
    run_textbook_firas_wien_peak_with_output,
)
from physics_lab.workflows.quantum_znse_contract_transfer import (
    run_quantum_znse_contract_transfer_with_output,
)


# Every workflow handler shares the signature
# ``(config_path, output_dir) -> ExperimentOutcome``. Registering handlers in a
# dispatch table (instead of a hand-edited if/elif chain) means adding a
# workflow is a single dict entry plus its import, and the dispatch order is
# explicit and data-driven.
ExperimentHandler = Callable[..., ExperimentOutcome]

# Primary dispatch: the config's explicit ``workflow`` key. Checked before the
# experiment file is loaded, preserving the historical precedence in which a
# named workflow wins over the experiment method type.
WORKFLOW_DISPATCH: dict[str, ExperimentHandler] = {
    "gauntlet": run_gauntlet_experiment_with_output,
    "dimensional_validation": run_dimensional_validator_with_output,
    "neutrino_koide": run_neutrino_koide_experiment,
    "quark_koide": run_quark_koide_experiment,
    "particle_mass_falsifier": run_particle_mass_falsifier_with_output,
    "g2_formula_search": run_g2_formula_experiment,
    "anharmonic_oscillator": run_anharmonic_oscillator_experiment_with_output,
    "nuclear_mass_baseline": run_nuclear_mass_baseline_experiment_with_output,
    "materials_md0002_formation_energy_benchmark": (
        run_materials_md0002_formation_energy_with_output
    ),
    "stellar_ml_debcat_baseline_benchmark": run_stellar_ml_debcat_baseline_with_output,
    "stellar_ml_high_mass_transfer_benchmark": (
        run_stellar_ml_high_mass_transfer_with_output
    ),
    "thermoml_tb_family_transfer_benchmark": (
        run_thermoml_tb_family_transfer_with_output
    ),
    "textbook_firas_wien_peak_consistency": run_textbook_firas_wien_peak_with_output,
    "quantum_znse_contract_transfer_result": (
        run_quantum_znse_contract_transfer_with_output
    ),
    "exoplanet_null_baseline_result": run_exoplanet_null_baseline_result_with_output,
    "textbook_exact_reference": run_textbook_exact_reference_with_output,
}

# Fallback dispatch: the experiment method type, used when the config does not
# name a recognized workflow (typically ``workflow == "standard"``).
METHOD_TYPE_DISPATCH: dict[str, ExperimentHandler] = {
    "formula_discovery": run_pendulum_experiment_with_output,
    "regime_verification": run_damped_oscillator_experiment_with_output,
    "dataset_reproduction": run_particle_mass_reproduction_with_output,
    "holdout_prediction": run_particle_mass_holdout_with_output,
}


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
    handler = WORKFLOW_DISPATCH.get(workflow)
    if handler is not None:
        return handler(config_path=config_path, output_dir=output_dir)

    experiment_path = resolve_path(config_path, config["experiment_path"])
    experiment = load_experiment(experiment_path)
    method_type = str(experiment["method"]["type"])
    handler = METHOD_TYPE_DISPATCH.get(method_type)
    if handler is not None:
        return handler(config_path=config_path, output_dir=output_dir)
    raise ValueError(f"Unsupported experiment method type: {method_type}")


__all__ = [
    "run_experiment",
    "run_experiment_with_output",
    "WORKFLOW_DISPATCH",
    "METHOD_TYPE_DISPATCH",
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
    "run_exoplanet_null_baseline_result_with_output",
    "run_textbook_exact_reference_with_output",
    "run_textbook_firas_wien_peak_with_output",
    "run_quantum_znse_contract_transfer_with_output",
    "run_stellar_ml_debcat_baseline_with_output",
    "run_stellar_ml_high_mass_transfer_with_output",
    "run_thermoml_tb_family_transfer_with_output",
]
