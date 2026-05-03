from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry import load_claim, load_experiment, load_hypothesis, load_result
from physics_lab.workflows.runner import run_experiment_with_output


def test_run_particle_mass_holdout_with_output(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = tmp_path / "apl-koide-holdout"

    outcome = run_experiment_with_output(
        repo_root / "examples" / "koide_tau_holdout.yaml",
        output_dir=output_dir,
    )

    run_dir = output_dir / "EXP-0005" / "RUN-0005"
    result_payload = load_result(run_dir / "result.yaml")

    assert outcome.result_id == "RESULT-0006"
    assert outcome.run_id == "RUN-0005"
    assert outcome.best_model_id is None
    assert result_payload["best_verdict"] == "VALID"
    assert result_payload["comparison_summary"][0]["target_id"] == "target_tau_mass"
    assert result_payload["uncertainty_summary"]["within_combined_uncertainty"] is True
    assert (run_dir / "inputs" / "dataset.yaml").exists()


def test_cli_run_tau_holdout_smoke(tmp_path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "apl-koide-holdout-cli"

    result = runner.invoke(
        app,
        ["run", "examples/koide_tau_holdout.yaml", "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0, result.output
    assert "Completed: Historical Tau Holdout Prediction" in result.stdout
    assert "Primary comparison: Measured tau mass" in result.stdout
    assert "Predicted tau mass:" in result.stdout
    assert "Absolute difference vs measured tau:" in result.stdout


def test_repository_loads_tau_holdout_registry_memory() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    load_claim(repo_root / "claims" / "CLAIM-0004-koide-tau-holdout.md")
    load_experiment(repo_root / "experiments" / "EXP-0005-koide-tau-holdout.yaml")
    load_hypothesis(repo_root / "hypotheses" / "HYP-0005-koide-tau-holdout.yaml")
