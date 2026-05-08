from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.engines.particle_mass_falsifier import (
    evaluate_family,
    particle_input_from_mapping,
    standard_koide_complexity_penalty,
)
from physics_lab.registry import load_experiment, load_hypothesis, load_result
from physics_lab.workflows.runner import run_experiment_with_output


def test_particle_mass_falsifier_engine_classifies_families() -> None:
    charged = (
        particle_input_from_mapping(
            {
                "particle": "electron",
                "symbol": "e",
                "family": "charged_lepton",
                "mass_value_mev": 0.51099895,
                "uncertainty": {"value": 1.5e-10},
                "mass_type": "pole",
                "scheme": None,
                "scale": None,
                "source": {"citation": "test"},
            }
        ),
        particle_input_from_mapping(
            {
                "particle": "muon",
                "symbol": "mu",
                "family": "charged_lepton",
                "mass_value_mev": 105.6583755,
                "uncertainty": {"value": 2.3e-6},
                "mass_type": "pole",
                "scheme": None,
                "scale": None,
                "source": {"citation": "test"},
            }
        ),
        particle_input_from_mapping(
            {
                "particle": "tau",
                "symbol": "tau",
                "family": "charged_lepton",
                "mass_value_mev": 1776.93,
                "uncertainty": {"value": 0.09},
                "mass_type": "pole",
                "scheme": None,
                "scale": None,
                "source": {"citation": "test"},
            }
        ),
    )
    up_quarks = (
        particle_input_from_mapping(
            {
                "particle": "up quark",
                "symbol": "u",
                "family": "up_quark",
                "mass_value_mev": 2.16,
                "uncertainty": {"plus": 0.49, "minus": 0.26},
                "mass_type": "running",
                "scheme": "MS-bar",
                "scale": "2 GeV",
                "source": {"citation": "test"},
            }
        ),
        particle_input_from_mapping(
            {
                "particle": "charm quark",
                "symbol": "c",
                "family": "up_quark",
                "mass_value_mev": 1270.0,
                "uncertainty": {"value": 20.0},
                "mass_type": "running",
                "scheme": "MS-bar",
                "scale": "mc(mc)",
                "source": {"citation": "test"},
            }
        ),
        particle_input_from_mapping(
            {
                "particle": "top quark",
                "symbol": "t",
                "family": "up_quark",
                "mass_value_mev": 172690.0,
                "uncertainty": {"value": 300.0},
                "mass_type": "direct_measurement",
                "scheme": "direct_measurement",
                "scale": None,
                "source": {"citation": "test"},
            }
        ),
    )

    charged_result = evaluate_family(
        family_id="charged_leptons",
        label="Charged leptons",
        particles=charged,
        mass_min_mev=0.51099895,
        mass_max_mev=172690.0,
        baseline_seed=4040,
        baseline_sample_count=500,
        limitation="test",
    )
    up_result = evaluate_family(
        family_id="up_quarks",
        label="Up-type quarks",
        particles=up_quarks,
        mass_min_mev=0.51099895,
        mass_max_mev=172690.0,
        baseline_seed=4041,
        baseline_sample_count=500,
        limitation="test",
    )

    assert charged_result.verdict == "VALID"
    assert charged_result.within_uncertainty is True
    assert up_result.verdict == "INVALID"
    assert up_result.gap_sigma is not None
    assert up_result.gap_sigma > 100
    assert standard_koide_complexity_penalty().total == 1.0


def test_run_particle_mass_falsifier_with_output(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = tmp_path / "apl-pmf"

    outcome = run_experiment_with_output(
        repo_root / "examples" / "particle_mass_falsifier.yaml",
        output_dir=output_dir,
    )

    run_dir = output_dir / "EXP-0009" / "RUN-0001"
    result_payload = load_result(run_dir / "result.yaml")

    assert outcome.result_id == "RESULT-0011"
    assert outcome.run_id == "RUN-0001"
    assert result_payload["best_verdict"] == "INVALID"
    assert len(result_payload["comparison_summary"]) == 3
    assert result_payload["comparison_summary"][0]["target_id"] == "target_charged_leptons_koide_q"
    assert (run_dir / "inputs" / "dataset.yaml").exists()

    metrics_text = (run_dir / "metrics.json").read_text(encoding="utf-8")
    assert '"random_baseline"' in metrics_text
    assert '"complexity_penalty"' in metrics_text


def test_cli_run_particle_mass_falsifier_smoke(tmp_path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "apl-pmf-cli"

    result = runner.invoke(
        app,
        ["run", "examples/particle_mass_falsifier.yaml", "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0, result.output
    assert "Completed: Particle-Mass Relation Falsifier MVP" in result.stdout
    assert "Families evaluated: 3" in result.stdout
    assert "Global verdict: INVALID" in result.stdout


def test_repository_loads_particle_mass_falsifier_registry_memory() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    load_experiment(repo_root / "experiments" / "EXP-0009-particle-mass-relation-falsifier.yaml")
    load_hypothesis(repo_root / "hypotheses" / "HYP-0009-particle-mass-koide-family-survival.yaml")
